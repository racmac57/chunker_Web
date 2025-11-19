#!/usr/bin/env python3
"""
Migration script to safely move local output/archive directories to OneDrive.

This script:
1. Checks for existing content in OneDrive directories
2. Identifies duplicates and conflicts
3. Moves non-duplicate files to OneDrive
4. Creates a migration report
"""
import os
import shutil
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set, Optional
import json

def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA256 hash of file content."""
    sha256 = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return sha256.hexdigest()
    except Exception as e:
        print(f"  Error hashing {file_path}: {e}")
        return ""

def get_all_files(directory: Path) -> Dict[str, Path]:
    """Get all files recursively, keyed by relative path."""
    files = {}
    if not directory.exists():
        return files
    
    for root, dirs, filenames in os.walk(directory):
        root_path = Path(root)
        for filename in filenames:
            file_path = root_path / filename
            try:
                # Get relative path from directory root
                rel_path = file_path.relative_to(directory)
                files[str(rel_path).replace('\\', '/')] = file_path
            except ValueError:
                # Skip if path can't be made relative
                continue
    return files

def compare_directories(local_dir: Path, onedrive_dir: Path, sample_size: Optional[int] = None) -> Dict:
    """
    Compare local and OneDrive directories.
    
    Args:
        local_dir: Local directory to compare
        onedrive_dir: OneDrive directory to compare
        sample_size: If set, only hash first N common files for speed (None = hash all)
    
    Returns:
        Dictionary with comparison results and file listings
    """
    print(f"\nScanning {local_dir.name}...")
    local_files = get_all_files(local_dir)
    print(f"  Found {len(local_files)} files in local directory")
    
    print(f"\nScanning OneDrive equivalent...")
    onedrive_files = get_all_files(onedrive_dir)
    print(f"  Found {len(onedrive_files)} files in OneDrive directory")
    
    # Find matches by path
    local_paths = set(local_files.keys())
    onedrive_paths = set(onedrive_files.keys())
    
    common_paths = local_paths & onedrive_paths
    only_local = local_paths - onedrive_paths
    only_onedrive = onedrive_paths - local_paths
    
    print(f"\n  Common paths: {len(common_paths)}")
    print(f"  Only in local: {len(only_local)}")
    print(f"  Only in OneDrive: {len(only_onedrive)}")
    
    # Compare content of common files
    identical_content = []
    different_content = []
    
    paths_to_check = list(common_paths)
    
    if sample_size is not None and len(paths_to_check) > sample_size:
        print(f"\nComparing content of first {sample_size} common files (sample mode)...")
        paths_to_check = paths_to_check[:sample_size]
        remaining_count = len(common_paths) - sample_size
        print(f"  Note: {remaining_count} remaining files will be assumed different")
    else:
        print(f"\nComparing content of {len(common_paths)} common files...")
    
    # Progress tracking
    checked = 0
    total = len(paths_to_check)
    
    for rel_path in paths_to_check:
        checked += 1
        if checked % 50 == 0 or checked == total:
            print(f"  Progress: {checked}/{total} files checked...", end='\r')
        
        local_file = local_files[rel_path]
        onedrive_file = onedrive_files[rel_path]
        
        # Fast path: compare file sizes first
        try:
            local_size = local_file.stat().st_size
            onedrive_size = onedrive_file.stat().st_size
        except (OSError, FileNotFoundError):
            different_content.append(rel_path)
            continue
        
        if local_size != onedrive_size:
            different_content.append(rel_path)
            continue
        
        # Sizes match, compare hashes
        local_hash = calculate_file_hash(local_file)
        onedrive_hash = calculate_file_hash(onedrive_file)
        
        if local_hash and onedrive_hash and local_hash == onedrive_hash:
            identical_content.append(rel_path)
        else:
            different_content.append(rel_path)
    
    print(f"  Progress: {total}/{total} files checked... done!")
    
    # Add remaining files as different if in sample mode
    if sample_size is not None and len(common_paths) > sample_size:
        remaining = common_paths - set(paths_to_check)
        different_content.extend(list(remaining))
    
    return {
        'local_files': local_files,
        'onedrive_files': onedrive_files,
        'common_paths': common_paths,
        'only_local': only_local,
        'only_onedrive': only_onedrive,
        'identical_content': identical_content,
        'different_content': different_content,
    }

def migrate_directory(local_dir: Path, onedrive_dir: Path, dry_run: bool = True, 
                      sample_size: Optional[int] = None, delete_after_move: bool = False) -> Dict:
    """
    Migrate local directory to OneDrive.
    
    Args:
        local_dir: Local directory to migrate
        onedrive_dir: OneDrive destination directory
        dry_run: If True, don't actually move files (default: True)
        sample_size: If set, only hash first N common files (None = hash all)
        delete_after_move: If True, delete local directory after successful migration (default: False)
    
    Returns:
        Dictionary with migration results and statistics
    """
    print("="*70)
    print(f"MIGRATING: {local_dir.name}")
    print("="*70)
    
    if not local_dir.exists():
        print(f"Local directory doesn't exist: {local_dir}")
        return {'moved': 0, 'skipped': 0, 'errors': 0, 'total_size_bytes': 0}
    
    if not onedrive_dir.exists():
        print(f"Creating OneDrive directory: {onedrive_dir}")
        if not dry_run:
            onedrive_dir.mkdir(parents=True, exist_ok=True)
    
    comparison = compare_directories(local_dir, onedrive_dir, sample_size=sample_size)
    
    moved_count = 0
    skipped_count = 0
    error_count = 0
    path_too_long_count = 0
    total_size_bytes = 0
    moved_files = []
    skipped_files = []
    error_files = []
    path_too_long_files = []
    
    # Windows MAX_PATH limit is 260 characters (including drive letter and null terminator)
    # Use 240 as safe threshold to account for variations
    MAX_PATH_LENGTH = 240
    
    print(f"\n{'DRY RUN: ' if dry_run else ''}Processing files...")
    
    # Calculate total size to be moved
    print("\nCalculating total size...")
    for rel_path in comparison['only_local']:
        local_file = comparison['local_files'][rel_path]
        try:
            total_size_bytes += local_file.stat().st_size
        except (OSError, FileNotFoundError):
            pass
    
    for rel_path in comparison['different_content']:
        local_file = comparison['local_files'][rel_path]
        try:
            total_size_bytes += local_file.stat().st_size
        except (OSError, FileNotFoundError):
            pass
    
    # Format size for display
    if total_size_bytes < 1024:
        size_str = f"{total_size_bytes} bytes"
    elif total_size_bytes < 1024 * 1024:
        size_str = f"{total_size_bytes / 1024:.2f} KB"
    elif total_size_bytes < 1024 * 1024 * 1024:
        size_str = f"{total_size_bytes / (1024 * 1024):.2f} MB"
    else:
        size_str = f"{total_size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
    print(f"  Total size to move: {size_str} ({total_size_bytes:,} bytes)")
    
    # Move files that only exist locally
    for rel_path in comparison['only_local']:
        local_file = comparison['local_files'][rel_path]
        # Ensure local_file is absolute path (required for cross-filesystem moves)
        if not local_file.is_absolute():
            local_file = local_file.resolve()
        onedrive_file = onedrive_dir / rel_path
        
        try:
            # Skip if file no longer exists (may have been moved/deleted)
            if not local_file.exists():
                error_files.append({'path': rel_path, 'error': 'File no longer exists'})
                error_count += 1
                continue
            
            # Check destination path length (Windows MAX_PATH limit is 260 chars)
            dest_path_str = str(onedrive_file)
            if len(dest_path_str) > MAX_PATH_LENGTH:
                path_too_long_files.append({
                    'path': rel_path,
                    'destination': dest_path_str,
                    'length': len(dest_path_str)
                })
                path_too_long_count += 1
                print(f"  [SKIP] {rel_path[:80]}... (path too long: {len(dest_path_str)} chars, max {MAX_PATH_LENGTH})")
                continue
            
            # Create parent directory if needed
            onedrive_file.parent.mkdir(parents=True, exist_ok=True)
            
            if dry_run:
                print(f"  [WOULD MOVE] {rel_path}")
                moved_files.append(rel_path)
                moved_count += 1
            else:
                # Verify file still exists right before move (may have been deleted by active chunker)
                if not local_file.exists():
                    error_files.append({'path': rel_path, 'error': 'File disappeared before move (likely deleted by active chunker)'})
                    error_count += 1
                    continue
                
                # Use os.replace() for atomic moves on same filesystem, shutil.move() for cross-filesystem
                try:
                    # Try atomic move first (same filesystem)
                    os.replace(str(local_file), str(onedrive_file))
                except OSError as e1:
                    # Fallback to shutil.move() for cross-filesystem moves
                    try:
                        shutil.move(str(local_file), str(onedrive_file))
                    except Exception as e2:
                        # Both methods failed - file may be locked/in use or path too long
                        raise Exception(f"Both os.replace() and shutil.move() failed: os.replace()={e1}, shutil.move()={e2}")
                print(f"  [MOVED] {rel_path}")
                moved_files.append(rel_path)
                moved_count += 1
        except Exception as e:
            print(f"  [ERROR] {rel_path}: {e}")
            error_files.append({'path': rel_path, 'error': str(e)})
            error_count += 1
    
    # Skip files that already exist with identical content
    for rel_path in comparison['identical_content']:
        skipped_files.append(rel_path)
        skipped_count += 1
    
    # Handle files with same path but different content
    for rel_path in comparison['different_content']:
        local_file = comparison['local_files'][rel_path]
        # Ensure local_file is absolute path (required for cross-filesystem moves)
        if not local_file.is_absolute():
            local_file = local_file.resolve()
        onedrive_file = onedrive_dir / rel_path
        
        # Append timestamp to avoid overwriting
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_parts = onedrive_file.name.rsplit('.', 1)
        if len(name_parts) == 2:
            new_name = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
        else:
            new_name = f"{onedrive_file.name}_{timestamp}"
        new_path = onedrive_file.parent / new_name
        
        try:
            # Skip if file no longer exists (may have been moved/deleted)
            if not local_file.exists():
                error_files.append({'path': rel_path, 'error': 'File no longer exists'})
                error_count += 1
                continue
            
            # Check destination path length (Windows MAX_PATH limit is 260 chars)
            # Note: new_path with timestamp will be longer than onedrive_file
            dest_path_str = str(new_path)
            if len(dest_path_str) > MAX_PATH_LENGTH:
                path_too_long_files.append({
                    'path': rel_path,
                    'destination': dest_path_str,
                    'length': len(dest_path_str)
                })
                path_too_long_count += 1
                print(f"  [SKIP] {rel_path[:80]}... (path too long: {len(dest_path_str)} chars, max {MAX_PATH_LENGTH})")
                continue
            
            # Verify file still exists right before move
            if not local_file.exists():
                error_files.append({'path': rel_path, 'error': 'File disappeared before move (likely deleted by active chunker)'})
                error_count += 1
                continue
            
            onedrive_file.parent.mkdir(parents=True, exist_ok=True)
            
            if dry_run:
                print(f"  [WOULD MOVE AS] {new_name} (different content)")
                moved_files.append(f"{rel_path} -> {new_name}")
                moved_count += 1
            else:
                # Use os.replace() for atomic moves on same filesystem, shutil.move() for cross-filesystem
                try:
                    os.replace(str(local_file), str(new_path))
                except OSError as e1:
                    try:
                        shutil.move(str(local_file), str(new_path))
                    except Exception as e2:
                        raise Exception(f"Both os.replace() and shutil.move() failed: os.replace()={e1}, shutil.move()={e2}")
                print(f"  [MOVED AS] {new_name} (different content)")
                moved_files.append(f"{rel_path} -> {new_name}")
                moved_count += 1
        except Exception as e:
            print(f"  [ERROR] {rel_path}: {e}")
            error_files.append({'path': rel_path, 'error': str(e)})
            error_count += 1
    
    # Clean up empty directories
    if not dry_run and local_dir.exists():
        try:
            # Try to remove empty directories
            for root, dirs, files in os.walk(local_dir, topdown=False):
                try:
                    if not os.listdir(root):
                        os.rmdir(root)
                except OSError:
                    pass
        except Exception as e:
            print(f"  Note: Could not clean up empty directories: {e}")
    
    # Delete local directory after successful migration if requested
    if delete_after_move and not dry_run and error_count == 0 and moved_count > 0:
        if local_dir.exists():
            try:
                # Check if directory is empty or contains only empty subdirectories
                remaining_files = list(local_dir.rglob('*'))
                remaining_files = [f for f in remaining_files if f.is_file()]
                
                if not remaining_files:
                    print(f"\nDeleting local directory after successful migration: {local_dir}")
                    shutil.rmtree(local_dir)
                    print(f"  [DELETED] {local_dir}")
                else:
                    print(f"\nWarning: Cannot delete local directory - {len(remaining_files)} files remain")
            except Exception as e:
                print(f"\nWarning: Could not delete local directory: {e}")
    
    return {
        'moved': moved_count,
        'skipped': skipped_count,
        'errors': error_count,
        'path_too_long': path_too_long_count,
        'total_size_bytes': total_size_bytes,
        'moved_files': moved_files,
        'skipped_files': list(comparison['identical_content']),
        'error_files': error_files,
        'path_too_long_files': path_too_long_files,
        'comparison': comparison,
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Migrate local output/archive directories to OneDrive',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python migrate_to_onedrive.py                           # Dry-run (preview)
  python migrate_to_onedrive.py --execute                 # Actually migrate
  python migrate_to_onedrive.py --execute --output-only   # Migrate only output
  python migrate_to_onedrive.py --execute --sample-size 100  # Hash first 100 common files
  python migrate_to_onedrive.py --execute --delete-local-after-move  # Clean up after migration
        """
    )
    parser.add_argument(
        '--execute',
        action='store_true',
        help='Actually perform the migration (default is dry-run)'
    )
    parser.add_argument(
        '--output-only',
        action='store_true',
        help='Only migrate output directory'
    )
    parser.add_argument(
        '--archive-only',
        action='store_true',
        help='Only migrate archive directory'
    )
    parser.add_argument(
        '--sample-size',
        type=int,
        default=None,
        help='Only hash first N common files for speed (None = hash all). Use this for large datasets.'
    )
    parser.add_argument(
        '--delete-local-after-move',
        action='store_true',
        help='Delete local directory after successful migration (only if --execute and no errors)'
    )
    
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    print("="*70)
    print("MIGRATION TO ONEDRIVE")
    print("="*70)
    print(f"Mode: {'DRY RUN (use --execute to actually migrate)' if dry_run else 'EXECUTING'}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if args.sample_size:
        print(f"Sample size: {args.sample_size} files (hashing limited)")
    else:
        print("Sample size: None (hashing all common files)")
    if args.delete_local_after_move:
        print("Delete local after move: ENABLED (local directories will be deleted if migration succeeds)")
    
    # Paths
    local_output = Path("C:\\_chunker\\04_output")
    local_archive = Path("C:\\_chunker\\03_archive")
    
    onedrive_output = Path(os.path.expandvars(r'%OneDriveCommercial%\KB_Shared\04_output'))
    onedrive_archive = Path(os.path.expandvars(r'%OneDriveCommercial%\KB_Shared\03_archive'))
    
    results = {}
    
    # Migrate output directory
    if not args.archive_only:
        results['output'] = migrate_directory(
            local_output, 
            onedrive_output, 
            dry_run=dry_run,
            sample_size=args.sample_size,
            delete_after_move=args.delete_local_after_move
        )
    
    # Migrate archive directory
    if not args.output_only:
        results['archive'] = migrate_directory(
            local_archive, 
            onedrive_archive, 
            dry_run=dry_run,
            sample_size=args.sample_size,
            delete_after_move=args.delete_local_after_move
        )
    
    # Summary
    print("\n" + "="*70)
    print("MIGRATION SUMMARY")
    print("="*70)
    
    total_moved = 0
    total_skipped = 0
    total_errors = 0
    total_path_too_long = 0
    total_size_bytes = 0
    
    for dir_name, result in results.items():
        print(f"\n{dir_name.upper()}:")
        print(f"  Moved: {result['moved']}")
        print(f"  Skipped (already exists): {result['skipped']}")
        path_too_long = result.get('path_too_long', 0)
        if path_too_long > 0:
            print(f"  Skipped (path too long >240 chars): {path_too_long}")
            total_path_too_long += path_too_long
        print(f"  Errors: {result['errors']}")
        size_bytes = result.get('total_size_bytes', 0)
        total_size_bytes += size_bytes
        
        # Format size for display
        if size_bytes < 1024:
            size_str = f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            size_str = f"{size_bytes / 1024:.2f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
        print(f"  Total size: {size_str} ({size_bytes:,} bytes)")
        
        total_moved += result['moved']
        total_skipped += result['skipped']
        total_errors += result['errors']
    
    print(f"\nTOTAL:")
    print(f"  Moved: {total_moved}")
    print(f"  Skipped (already exists): {total_skipped}")
    if total_path_too_long > 0:
        print(f"  Skipped (path too long >240 chars): {total_path_too_long}")
    print(f"  Errors: {total_errors}")
    
    # Format total size for display
    if total_size_bytes < 1024:
        total_size_str = f"{total_size_bytes} bytes"
    elif total_size_bytes < 1024 * 1024:
        total_size_str = f"{total_size_bytes / 1024:.2f} KB"
    elif total_size_bytes < 1024 * 1024 * 1024:
        total_size_str = f"{total_size_bytes / (1024 * 1024):.2f} MB"
    else:
        total_size_str = f"{total_size_bytes / (1024 * 1024 * 1024):.2f} GB"
    
    print(f"  Total size: {total_size_str} ({total_size_bytes:,} bytes)")
    
    # Estimate OneDrive sync time (rough estimate: 1 MB/s on average connection)
    if total_size_bytes > 0 and not dry_run:
        estimated_sync_seconds = total_size_bytes / (1024 * 1024)  # ~1 MB/s
        if estimated_sync_seconds < 60:
            sync_time_str = f"{estimated_sync_seconds:.0f} seconds"
        elif estimated_sync_seconds < 3600:
            sync_time_str = f"{estimated_sync_seconds / 60:.1f} minutes"
        else:
            sync_time_str = f"{estimated_sync_seconds / 3600:.1f} hours"
        print(f"  Estimated OneDrive sync time: ~{sync_time_str} (rough estimate)")
    
    # Save report
    report_file = Path("migration_report.json")
    report = {
        'timestamp': datetime.now().isoformat(),
        'dry_run': dry_run,
        'sample_size': args.sample_size,
        'delete_local_after_move': args.delete_local_after_move,
        'total_size_bytes': total_size_bytes,
        'total_size_formatted': total_size_str if total_size_bytes > 0 else "0 bytes",
        'totals': {
            'moved': total_moved,
            'skipped': total_skipped,
            'path_too_long': total_path_too_long,
            'errors': total_errors,
        },
        'results': {
            k: {
                'moved': v['moved'],
                'skipped': v['skipped'],
                'path_too_long': v.get('path_too_long', 0),
                'errors': v['errors'],
                'total_size_bytes': v.get('total_size_bytes', 0),
                'error_files': v['error_files'],
                'path_too_long_files': v.get('path_too_long_files', []),
            }
            for k, v in results.items()
        }
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    print(f"\nReport saved to: {report_file}")
    
    if dry_run:
        print("\n" + "="*70)
        print("This was a DRY RUN. Use --execute to actually migrate files.")
        print("="*70)

if __name__ == '__main__':
    main()

