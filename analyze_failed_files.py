#!/usr/bin/env python3
"""
Analyze failed files in 03_archive/failed directory.

Categorizes failed files by:
- Failure date/time patterns
- File types/extensions
- Common error signatures in logs (if available)
- File sizes (too large? encoding issues?)
- Reprocessing potential
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import re

# Load config to get failed directory path
try:
    with open("config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # Expand environment variables
    failed_dir_str = config.get("failed_dir", "03_archive/failed")
    failed_dir_str = os.path.expandvars(failed_dir_str)
    failed_dir = Path(failed_dir_str)
except Exception as e:
    print(f"Warning: Could not load config.json, using default path: {e}")
    failed_dir = Path("03_archive/failed")

# Check both OneDrive and local paths
local_failed = Path("03_archive/failed")
onedrive_failed = failed_dir

# Use the one with more files (or local if OneDrive doesn't exist)
if onedrive_failed.exists() and local_failed.exists():
    onedrive_count = len([f for f in onedrive_failed.iterdir() if f.is_file()])
    local_count = len([f for f in local_failed.iterdir() if f.is_file()])
    if local_count > onedrive_count:
        print(f"Both paths exist. Local has more files ({local_count:,} vs {onedrive_count:,}), using local.")
        failed_dir = local_failed
elif not onedrive_failed.exists() and local_failed.exists():
    print(f"OneDrive path not found, using local: {local_failed}")
    failed_dir = local_failed

def get_file_info(file_path: Path) -> Dict:
    """Extract information from a failed file."""
    stat = file_path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime)
    age_days = (datetime.now() - mtime).total_seconds() / 86400
    age_hours = (datetime.now() - mtime).total_seconds() / 3600
    
    return {
        "name": file_path.name,
        "extension": file_path.suffix.lower(),
        "size": stat.st_size,
        "size_mb": stat.st_size / (1024 * 1024),
        "mtime": mtime,
        "age_days": age_days,
        "age_hours": age_hours,
        "is_reprocess": "reprocess" in file_path.name.lower(),
    }

def analyze_file_types(files: List[Dict]) -> Dict:
    """Analyze file types and extensions."""
    extensions = Counter([f["extension"] for f in files])
    sizes_by_ext = defaultdict(list)
    
    for f in files:
        sizes_by_ext[f["extension"]].append(f["size_mb"])
    
    return {
        "extensions": dict(extensions.most_common()),
        "avg_sizes_by_ext": {
            ext: sum(sizes) / len(sizes) if sizes else 0
            for ext, sizes in sizes_by_ext.items()
        },
        "max_sizes_by_ext": {
            ext: max(sizes) if sizes else 0
            for ext, sizes in sizes_by_ext.items()
        },
    }

def analyze_time_patterns(files: List[Dict]) -> Dict:
    """Analyze failure time patterns."""
    hour_groups = Counter()
    day_groups = Counter()
    month_groups = Counter()
    
    for f in files:
        mtime = f["mtime"]
        hour_key = mtime.strftime("%Y-%m-%d %H:00")
        day_key = mtime.strftime("%Y-%m-%d")
        month_key = mtime.strftime("%Y-%m")
        
        hour_groups[hour_key] += 1
        day_groups[day_key] += 1
        month_groups[month_key] += 1
    
    return {
        "hourly_distribution": dict(hour_groups.most_common(20)),
        "daily_distribution": dict(day_groups.most_common(30)),
        "monthly_distribution": dict(month_groups.most_common(12)),
        "oldest": min(f["mtime"] for f in files) if files else None,
        "newest": max(f["mtime"] for f in files) if files else None,
        "today_count": len([f for f in files if f["age_days"] < 1]),
        "this_week_count": len([f for f in files if 1 <= f["age_days"] < 7]),
        "this_month_count": len([f for f in files if 7 <= f["age_days"] < 30]),
        "older_count": len([f for f in files if f["age_days"] >= 30]),
    }

def analyze_sizes(files: List[Dict]) -> Dict:
    """Analyze file sizes for patterns."""
    sizes = [f["size"] for f in files]
    
    # Categorize by size
    tiny = len([s for s in sizes if s < 100])  # < 100 bytes
    small = len([s for s in sizes if 100 <= s < 1024])  # 100 bytes - 1 KB
    medium = len([s for s in sizes if 1024 <= s < 1024 * 1024])  # 1 KB - 1 MB
    large = len([s for s in sizes if 1024 * 1024 <= s < 10 * 1024 * 1024])  # 1 MB - 10 MB
    huge = len([s for s in sizes if s >= 10 * 1024 * 1024])  # >= 10 MB
    
    return {
        "total_size_mb": sum(f["size_mb"] for f in files),
        "avg_size_mb": sum(f["size_mb"] for f in files) / len(files) if files else 0,
        "min_size": min(sizes) if sizes else 0,
        "max_size": max(sizes) if sizes else 0,
        "size_categories": {
            "tiny (<100B)": tiny,
            "small (100B-1KB)": small,
            "medium (1KB-1MB)": medium,
            "large (1MB-10MB)": large,
            "huge (>=10MB)": huge,
        },
    }

def analyze_reprocessing_potential(files: List[Dict]) -> Dict:
    """Assess which files might be worth reprocessing."""
    reprocess_files = [f for f in files if f["is_reprocess"]]
    
    # Files that might succeed with updated code:
    # - Small to medium size (not too large)
    # - Recent (failed recently, might be code-related)
    # - Common extensions (likely supported)
    
    supported_extensions = {".txt", ".md", ".csv", ".json", ".py", ".m", ".dax", ".ps1", ".sql"}
    
    potentially_repairable = []
    likely_permanent = []
    
    for f in files:
        is_supported = f["extension"] in supported_extensions
        is_reasonable_size = f["size"] < 10 * 1024 * 1024  # < 10 MB
        is_recent = f["age_days"] < 90  # Failed within last 90 days
        
        if is_supported and is_reasonable_size:
            if is_recent:
                potentially_repairable.append(f)
            else:
                likely_permanent.append(f)
        elif not is_supported:
            likely_permanent.append(f)  # Unsupported extensions
        elif not is_reasonable_size:
            likely_permanent.append(f)  # Too large
    
    return {
        "total_reprocess_files": len(reprocess_files),
        "potentially_repairable": len(potentially_repairable),
        "likely_permanent": len(likely_permanent),
        "sample_repairable": [
            {"name": f["name"][:60], "size_mb": round(f["size_mb"], 2), "age_days": round(f["age_days"], 1)}
            for f in potentially_repairable[:10]
        ],
    }

def main():
    """Main analysis function."""
    print("="*70)
    print("FAILED FILES ANALYSIS")
    print("="*70)
    print(f"\nAnalyzing: {failed_dir}")
    
    if not failed_dir.exists():
        print(f"\n❌ Failed directory does not exist: {failed_dir}")
        return
    
    # Get all files
    all_files = [f for f in failed_dir.iterdir() if f.is_file()]
    
    if not all_files:
        print(f"\n✅ No failed files found in {failed_dir}")
        return
    
    print(f"\nTotal failed files: {len(all_files):,}")
    
    # Extract file information
    print("\nExtracting file information...")
    file_info = [get_file_info(f) for f in all_files]
    
    # Run analyses
    print("Analyzing file types...")
    type_analysis = analyze_file_types(file_info)
    
    print("Analyzing time patterns...")
    time_analysis = analyze_time_patterns(file_info)
    
    print("Analyzing file sizes...")
    size_analysis = analyze_sizes(file_info)
    
    print("Assessing reprocessing potential...")
    reprocess_analysis = analyze_reprocessing_potential(file_info)
    
    # Print results
    print("\n" + "="*70)
    print("FILE TYPE ANALYSIS")
    print("="*70)
    print(f"\nFile types (top 10):")
    for ext, count in list(type_analysis["extensions"].items())[:10]:
        avg_size = type_analysis["avg_sizes_by_ext"].get(ext, 0)
        max_size = type_analysis["max_sizes_by_ext"].get(ext, 0)
        print(f"  {ext or '(no ext)':15s}: {count:6,} files  (avg: {avg_size:.2f} MB, max: {max_size:.2f} MB)")
    
    print("\n" + "="*70)
    print("TIME PATTERN ANALYSIS")
    print("="*70)
    print(f"\nFailure timeline:")
    print(f"  Oldest failure: {time_analysis['oldest'].strftime('%Y-%m-%d %H:%M:%S') if time_analysis['oldest'] else 'N/A'}")
    print(f"  Newest failure: {time_analysis['newest'].strftime('%Y-%m-%d %H:%M:%S') if time_analysis['newest'] else 'N/A'}")
    print(f"\nAge distribution:")
    print(f"  Today (< 1 day):      {time_analysis['today_count']:6,} files")
    print(f"  This week (1-7 days): {time_analysis['this_week_count']:6,} files")
    print(f"  This month (7-30 days): {time_analysis['this_month_count']:6,} files")
    print(f"  Older (30+ days):     {time_analysis['older_count']:6,} files")
    
    print(f"\nTop 10 failure periods (by hour):")
    for hour, count in list(time_analysis["hourly_distribution"].items())[:10]:
        print(f"  {hour}: {count:,} files")
    
    print("\n" + "="*70)
    print("FILE SIZE ANALYSIS")
    print("="*70)
    print(f"\nTotal size: {size_analysis['total_size_mb']:.2f} MB")
    print(f"Average size: {size_analysis['avg_size_mb']:.3f} MB")
    print(f"Size range: {size_analysis['min_size']:,} bytes - {size_analysis['max_size']:,} bytes")
    print(f"\nSize categories:")
    for category, count in size_analysis["size_categories"].items():
        print(f"  {category:20s}: {count:6,} files")
    
    print("\n" + "="*70)
    print("REPROCESSING POTENTIAL")
    print("="*70)
    print(f"\nReprocessing assessment:")
    print(f"  Files with 'reprocess' in name: {reprocess_analysis['total_reprocess_files']:,}")
    print(f"  Potentially repairable: {reprocess_analysis['potentially_repairable']:,} files")
    print(f"  Likely permanent failures: {reprocess_analysis['likely_permanent']:,} files")
    
    if reprocess_analysis["sample_repairable"]:
        print(f"\n  Sample of potentially repairable files:")
        for f in reprocess_analysis["sample_repairable"]:
            print(f"    {f['name']:60s} ({f['size_mb']:.2f} MB, {f['age_days']:.1f} days old)")
    
    print("\n" + "="*70)
    print("RECOMMENDATIONS")
    print("="*70)
    
    if reprocess_analysis["potentially_repairable"] > 0:
        print(f"\n✅ {reprocess_analysis['potentially_repairable']:,} files are good candidates for reprocessing")
        print("   These files are:")
        print("   - Supported file types")
        print("   - Reasonable size (< 10 MB)")
        print("   - Failed recently (< 90 days)")
        print("\n   Consider running reprocessing script on these files.")
    else:
        print("\n⚠️  No files identified as good reprocessing candidates")
        print("   Most failures appear to be:")
        print("   - Unsupported file types")
        print("   - Very large files")
        print("   - Very old failures")
    
    if time_analysis["older_count"] > time_analysis["today_count"] + time_analysis["this_week_count"]:
        print(f"\n📊 {time_analysis['older_count']:,} files are 30+ days old")
        print("   These are historical failures, likely from before code updates.")
        print("   Consider archiving or reviewing separately from recent failures.")
    
    # Save analysis to JSON
    output_file = Path("05_logs/failed_files_analysis.json")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    analysis_result = {
        "timestamp": datetime.now().isoformat(),
        "failed_dir": str(failed_dir),
        "total_files": len(all_files),
        "file_types": type_analysis,
        "time_patterns": {
            k: (v.isoformat() if isinstance(v, datetime) else v)
            for k, v in time_analysis.items()
        },
        "sizes": size_analysis,
        "reprocessing": reprocess_analysis,
    }
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(analysis_result, f, indent=2)
    
    print(f"\n💾 Analysis saved to: {output_file}")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()

