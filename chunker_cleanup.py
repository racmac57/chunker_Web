# 2025-10-31-03-48-33
# Enterprise_Chunker/chunker_cleanup.py
# Author: R. A. Carucci
# Purpose: Audit, classify, and clean Enterprise Chunker directory structure with documentation normalization and snapshot pruning

import os
import sys
import hashlib
import shutil
import json
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple, Optional
import re

# ============================================================================
# CONFIGURATION
# ============================================================================

ROOT = Path(r"C:\_chunker")  # Adjust if different
DRY_RUN = False  # Set to False after plan review
PROJECT = "Enterprise_Chunker"
NOW = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

# ============================================================================
# CLASSIFICATION RULES
# ============================================================================

# Files/folders to NEVER delete or move
KEEP_FILES = {
    # Core application files
    'celery_tasks.py', 'orchestrator.py', 'chunker_db.py',
    'file_processors.py', 'advanced_celery_config.py',
    'enhanced_watchdog.py',  # Current watcher implementation
    # RAG and integration files
    'automated_eval.py', 'chromadb_crud.py', 'comprehensive_eval.py',
    'embedding_helpers.py', 'install_rag_dependencies.py',
    'langchain_rag_handler.py', 'langsmith_integration.py',
    'manual_process_files.py', 'notification_system.py',
    'ollama_integration.py', 'rag_evaluation.py', 'rag_integration.py',
    'rag_search.py', 'simple_rag_test.py',
    # Testing files (keep for validation)
    'performance_test.py', 'rag_test.py', 'test_celery_integration.py',
    'test_origin_tracking.py', 'test_python_demo.py',
    # Config and docs
    'config.json', 'README.md', 'CHANGELOG.md', 'ENTERPRISE_CHUNKER_SUMMARY.md'
}

KEEP_FILE_PATTERNS = [
    r'^rag_.*\.py$',
    r'^requirements.*\.txt$',
]

KEEP_FOLDERS = {
    '02_data', 'archive', '05_logs', '06_config',
    'source', 'templates', 'static', '99_doc', '01_scripts'
}

# Documentation keywords for detection
DOC_KEYWORDS = [
    'readme', 'changelog', 'summary', 'guide', 'howto', 'usage',
    'notes', 'todo', 'design', 'spec', 'proposal', 'requirements',
    'installation', 'license', 'documentation', 'docs'
]

# Specific files to move to 99_doc/notes
MOVE_TO_NOTES = {
    '2025_10_30_02_39_58_c_drive_clean_cursor_process_input_folder_monitor_scr.md'
}

# Files to move to archive (backups, corrupt, temp files)
MOVE_TO_ARCHIVE = {
    'watcher_splitter.py.backup_20251030_223512',
    'watcher_splitter.py.corrupt',
    'PYTHON_PROCESSING_FIX.md',
    'QUICK_START_ENHANCEMENTS.md',
    'PRE_FLIGHT_CHECKLIST.md',
    'CLEANUP_EXECUTION_REPORT.md',
    'maintenance_report.md'
}

# Delete patterns
DELETE_FOLDERS = {
    'venv', '.venv', 'env', '.conda', '__pycache__', '.pytest_cache',
    '.mypy_cache', '.ipynb_checkpoints', 'dist', 'build', 'node_modules'
}

DELETE_FILES = {
    'Thumbs.db', '.DS_Store', 'desktop.ini', 'package-lock.json'
    # _chunker.code-workspace removed - keeping workspace file
}

DELETE_PATTERNS = [
    r'^test_.*\.py$',
    r'^tmp_.*\.py$',
    r'^scratch_.*\.py$',
    r'^old_.*\.py$',
    r'^backup_.*\.py$',
    r'^playground_.*\.py$',
    r'^experiment_.*\.py$',
    r'.*_backup\.py$',
    r'.*_old\.py$',
    r'.*_copy\.py$',
]

# ============================================================================
# UTILITIES
# ============================================================================

def calculate_sha256(file_path: Path, partial: bool = False) -> str:
    """Calculate SHA-256 hash of file (first 1MB if partial)."""
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path, "rb") as f:
            if partial:
                chunk = f.read(1024 * 1024)  # 1MB
                sha256_hash.update(chunk)
            else:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except Exception as e:
        return f"ERROR: {str(e)}"


def is_doc_file(file_path: Path) -> bool:
    """Check if file is documentation based on name and content."""
    if file_path.suffix.lower() not in ['.md', '.txt', '.rst']:
        return False
    
    # Check filename
    name_lower = file_path.stem.lower()
    if any(kw in name_lower for kw in DOC_KEYWORDS):
        return True
    
    # Check first 200 chars of content
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(200).lower()
            if any(kw in content for kw in DOC_KEYWORDS):
                return True
    except:
        pass
    
    return False


def matches_pattern(name: str, patterns: List[str]) -> bool:
    """Check if name matches any regex pattern."""
    return any(re.match(pattern, name) for pattern in patterns)


def should_keep(path: Path, rel_path: Path) -> bool:
    """Determine if path should be kept (never deleted/moved)."""
    # Check if in keep folders
    if any(kf in rel_path.parts for kf in KEEP_FOLDERS):
        # But allow pruning in specific legacy folders
        if 'legacy' in rel_path.parts:
            return False
        return True
    
    # Check keep files
    if path.name in KEEP_FILES:
        return True
    
    # Check keep patterns
    if matches_pattern(path.name, KEEP_FILE_PATTERNS):
        return True
    
    # Special: .origin.json files in SendTo
    if path.suffix == '.json' and 'origin' in path.name and 'SendTo' in rel_path.parts:
        return True
    
    return False


def should_delete(path: Path) -> bool:
    """Determine if path should be deleted."""
    # Folders
    if path.is_dir() and path.name in DELETE_FOLDERS:
        return True
    
    # Files
    if path.is_file():
        if path.name in DELETE_FILES:
            return True
        if matches_pattern(path.name, DELETE_PATTERNS):
            return True
    
    return False


def extract_snapshot_info(path: Path) -> Optional[Tuple[str, str]]:
    """Extract project name and timestamp from snapshot filename.
    Returns (project_name, timestamp) or None.
    Expected formats: 
    - ProjectName_YYYY_MM_DD_HH_MM_SS.*
    - config.json.backup_YYYY_MM_DD_HH_MM_SS
    """
    name = path.name
    
    # Handle config.json.backup_* pattern
    if name.startswith('config.json.backup_'):
        timestamp = name.replace('config.json.backup_', '')
        return ('config', timestamp)
    
    # Handle standard ProjectName_timestamp pattern
    # Match pattern: word chars, underscore, then timestamp
    match = re.match(r'^([A-Za-z0-9_]+?)_(\d{4}_\d{2}_\d{2}_\d{2}_\d{2}_\d{2})', name)
    if match:
        return (match.group(1), match.group(2))
    
    return None


def is_legacy_snapshot(path: Path, rel_path: Path) -> bool:
    """Check if file is a legacy snapshot in a legacy folder."""
    if not path.is_file():
        return False
    
    # Must be in a legacy folder or be a config backup
    in_legacy = 'legacy' in rel_path.parts
    is_config_backup = path.name.startswith('config.json.backup_')
    
    if not (in_legacy or is_config_backup):
        return False
    
    # Must match snapshot pattern
    return extract_snapshot_info(path) is not None


# ============================================================================
# MAIN CLASSES
# ============================================================================

class FileInventory:
    """Handles directory traversal and inventory creation."""
    
    def __init__(self, root: Path):
        self.root = root
        self.items = []
        self.duplicates = defaultdict(list)
        
    def scan(self) -> List[Dict]:
        """Walk directory tree and collect all items."""
        print(f"Scanning {self.root}...")
        
        for item in self.root.rglob('*'):
            try:
                rel_path = item.relative_to(self.root)
                
                if item.is_file():
                    size = item.stat().st_size
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    
                    # Calculate hashes
                    sha256_partial = calculate_sha256(item, partial=True)
                    sha256_full = calculate_sha256(item, partial=False) if size < 10 * 1024 * 1024 else "SKIPPED_LARGE"
                    
                    entry = {
                        'path': str(item),
                        'rel_path': str(rel_path),
                        'type': 'file',
                        'size': size,
                        'mtime': mtime.isoformat(),
                        'sha256_partial': sha256_partial,
                        'sha256_full': sha256_full,
                        'category': 'UNKNOWN'
                    }
                    
                    self.items.append(entry)
                    
                    # Track duplicates
                    if sha256_full not in ["SKIPPED_LARGE", "ERROR"] and size > 0:
                        self.duplicates[sha256_full].append(entry)
                        
                elif item.is_dir():
                    entry = {
                        'path': str(item),
                        'rel_path': str(rel_path),
                        'type': 'dir',
                        'size': 0,
                        'mtime': datetime.fromtimestamp(item.stat().st_mtime).isoformat(),
                        'sha256_partial': 'N/A',
                        'sha256_full': 'N/A',
                        'category': 'UNKNOWN'
                    }
                    self.items.append(entry)
                    
            except Exception as e:
                print(f"Error processing {item}: {e}")
                
        print(f"Scanned {len(self.items)} items")
        return self.items
    
    def get_duplicates(self) -> Dict:
        """Return only files that have duplicates."""
        return {k: v for k, v in self.duplicates.items() if len(v) > 1}


class FileClassifier:
    """Classifies files based on rules."""
    
    def __init__(self, root: Path, items: List[Dict]):
        self.root = root
        self.items = items
        self.snapshots_by_project = defaultdict(list)
        
    def classify(self) -> List[Dict]:
        """Classify each item."""
        print("Classifying items...")
        
        for item in self.items:
            path = Path(item['path'])
            rel_path = Path(item['rel_path'])
            
            # Default
            category = 'KEEP'
            action = 'NONE'
            destination = ''
            reason = ''
            
            # Rule 1: Check KEEP rules first (highest priority)
            if should_keep(path, rel_path):
                category = 'KEEP'
                reason = 'Core file/folder'
                
            # Rule 2: Check if it's a legacy snapshot
            elif is_legacy_snapshot(path, rel_path):
                category = 'SNAPSHOT'
                action = 'PRUNE_CHECK'
                reason = 'Legacy snapshot - check if latest'
                
                snapshot_info = extract_snapshot_info(path)
                if snapshot_info:
                    project_name, timestamp = snapshot_info
                    self.snapshots_by_project[project_name].append({
                        'path': path,
                        'timestamp': timestamp,
                        'item': item
                    })
                    
            # Rule 3a: Files to move to archive (check BEFORE generic doc detection)
            elif path.name in MOVE_TO_ARCHIVE:
                category = 'MOVE_ARCHIVE'
                action = 'MOVE'
                destination = str(self.root / 'archive' / 'cleanup_items')
                reason = 'Archive: backup/corrupt/temp file'
                
            # Rule 3b: Specific transcript to notes
            elif path.name in MOVE_TO_NOTES:
                category = 'MOVE_DOC'
                action = 'MOVE'
                destination = str(self.root / '99_doc' / 'notes')
                reason = 'Transcript/note'
                
            # Rule 3: Check if should be moved (documentation)
            elif path.is_file() and is_doc_file(path):
                if path.name in ['README.md', 'CHANGELOG.md', 'ENTERPRISE_CHUNKER_SUMMARY.md']:
                    category = 'KEEP'
                    reason = 'Root documentation'
                else:
                    category = 'MOVE_DOC'
                    action = 'MOVE'
                    destination = str(self.root / '99_doc')
                    reason = 'Documentation file'
                
            # Rule 4: Check if should be deleted
            elif should_delete(path):
                category = 'DELETE'
                action = 'DELETE'
                reason = f'Cruft: {path.name}'
                
            # Rule 5: Empty directories
            elif item['type'] == 'dir':
                try:
                    if not any(path.iterdir()):
                        category = 'DELETE'
                        action = 'DELETE'
                        reason = 'Empty directory'
                except:
                    pass
                    
            item['category'] = category
            item['action'] = action
            item['destination'] = destination
            item['reason'] = reason
            
        # Process snapshots - keep only latest per project
        for project_name, snapshots in self.snapshots_by_project.items():
            if len(snapshots) <= 1:
                continue
                
            # Sort by timestamp descending
            snapshots.sort(key=lambda x: x['timestamp'], reverse=True)
            
            # Keep newest, mark others for deletion
            for i, snap in enumerate(snapshots):
                if i == 0:
                    snap['item']['category'] = 'SNAPSHOT_KEEP'
                    snap['item']['action'] = 'NONE'
                    snap['item']['reason'] = f'Latest snapshot for {project_name}'
                else:
                    snap['item']['category'] = 'SNAPSHOT_PRUNE'
                    snap['item']['action'] = 'DELETE'
                    snap['item']['reason'] = f'Older snapshot for {project_name} (keeping {snapshots[0]["timestamp"]})'
                    
        print("Classification complete")
        return self.items


class CleanupExecutor:
    """Executes the cleanup plan."""
    
    def __init__(self, root: Path, items: List[Dict], dry_run: bool, timestamp: str):
        self.root = root
        self.items = items
        self.dry_run = dry_run
        self.timestamp = timestamp
        self.log_dir = root / '05_logs' / 'maintenance' / timestamp
        self.moved_files = []
        self.deleted_files = []
        
    def execute(self):
        """Execute the cleanup plan."""
        if self.dry_run:
            print("\n=== DRY RUN MODE - NO CHANGES WILL BE MADE ===\n")
        else:
            print("\n=== EXECUTING CLEANUP ===\n")
            
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create 99_doc structure
        doc_dir = self.root / '99_doc'
        doc_dir.mkdir(exist_ok=True)
        (doc_dir / 'notes').mkdir(exist_ok=True)
        
        # Filter items by action
        to_move = [i for i in self.items if i['action'] == 'MOVE']
        to_delete = [i for i in self.items if i['action'] == 'DELETE']
        
        print(f"Items to move: {len(to_move)}")
        print(f"Items to delete: {len(to_delete)}")
        
        if not self.dry_run:
            # Execute moves
            for item in to_move:
                self._move_file(item)
                
            # Execute deletes
            for item in to_delete:
                self._delete_item(item)
                
        return self.moved_files, self.deleted_files
    
    def _move_file(self, item: Dict):
        """Move a file to its destination."""
        try:
            src = Path(item['path'])
            dest_dir = Path(item['destination'])
            dest = dest_dir / src.name
            
            # Handle conflicts
            counter = 1
            while dest.exists():
                dest = dest_dir / f"{src.stem}_{counter}{src.suffix}"
                counter += 1
                
            dest_dir.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            
            self.moved_files.append({
                'source': str(src),
                'destination': str(dest),
                'reason': item['reason']
            })
            print(f"Moved: {src.name} -> {dest}")
            
        except Exception as e:
            print(f"Error moving {item['path']}: {e}")
            
    def _delete_item(self, item: Dict):
        """Delete a file or directory."""
        try:
            path = Path(item['path'])
            
            # Try to use recycle bin on Windows
            if sys.platform == 'win32':
                try:
                    import winshell
                    winshell.delete_file(str(path), no_confirm=True, allow_undo=True)
                    print(f"Deleted (to recycle bin): {path.name}")
                except:
                    # Fallback: move to trash folder
                    trash_dir = self.root / 'archive' / 'trash' / self.timestamp
                    trash_dir.mkdir(parents=True, exist_ok=True)
                    
                    dest = trash_dir / path.name
                    counter = 1
                    while dest.exists():
                        dest = trash_dir / f"{path.stem}_{counter}{path.suffix if path.is_file() else ''}"
                        counter += 1
                        
                    shutil.move(str(path), str(dest))
                    print(f"Deleted (to trash): {path.name}")
            else:
                # Unix: just delete
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(str(path))
                print(f"Deleted: {path.name}")
                
            self.deleted_files.append({
                'path': str(path),
                'reason': item['reason']
            })
            
        except Exception as e:
            print(f"Error deleting {item['path']}: {e}")


# ============================================================================
# REPORTING
# ============================================================================

class Reporter:
    """Generate reports and update documentation."""
    
    def __init__(self, root: Path, items: List[Dict], moved: List[Dict], deleted: List[Dict], 
                 duplicates: Dict, timestamp: str, dry_run: bool):
        self.root = root
        self.items = items
        self.moved = moved
        self.deleted = deleted
        self.duplicates = duplicates
        self.timestamp = timestamp
        self.dry_run = dry_run
        self.log_dir = root / '05_logs' / 'maintenance' / timestamp
        
    def generate_all_reports(self):
        """Generate all reports and update docs."""
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self._write_inventory()
        self._write_actions_plan()
        self._write_duplicates()
        self._write_moved_files()
        self._write_deleted_files()
        self._write_summary()
        self._generate_tree()
        
        if not self.dry_run:
            self._update_readme()
            self._update_summary()
            self._update_changelog()
            
        print(f"\nReports saved to: {self.log_dir}")
        
    def _write_inventory(self):
        """Write inventory.csv."""
        with open(self.log_dir / 'inventory.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'path', 'rel_path', 'type', 'size', 'mtime', 
                'sha256_partial', 'category', 'action', 'reason'
            ])
            writer.writeheader()
            for item in self.items:
                writer.writerow({
                    'path': item['path'],
                    'rel_path': item['rel_path'],
                    'type': item['type'],
                    'size': item['size'],
                    'mtime': item['mtime'],
                    'sha256_partial': item['sha256_partial'],
                    'category': item['category'],
                    'action': item['action'],
                    'reason': item['reason']
                })
                
    def _write_actions_plan(self):
        """Write actions_plan.json."""
        plan = {
            'timestamp': self.timestamp,
            'dry_run': self.dry_run,
            'root': str(self.root),
            'summary': {
                'total_items': len(self.items),
                'files': len([i for i in self.items if i['type'] == 'file']),
                'dirs': len([i for i in self.items if i['type'] == 'dir']),
                'keep': len([i for i in self.items if i['category'] == 'KEEP']),
                'move': len([i for i in self.items if i['action'] == 'MOVE']),
                'delete': len([i for i in self.items if i['action'] == 'DELETE']),
                'snapshot_prune': len([i for i in self.items if i['category'] == 'SNAPSHOT_PRUNE']),
            },
            'actions': {
                'move': [i for i in self.items if i['action'] == 'MOVE'],
                'delete': [i for i in self.items if i['action'] == 'DELETE']
            }
        }
        
        with open(self.log_dir / 'actions_plan.json', 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2)
            
    def _write_duplicates(self):
        """Write duplicates.csv."""
        with open(self.log_dir / 'duplicates.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['sha256', 'count', 'paths'])
            for sha256, items in self.duplicates.items():
                paths = ' | '.join([i['path'] for i in items])
                writer.writerow([sha256, len(items), paths])
                
    def _write_moved_files(self):
        """Write moved_files.csv."""
        with open(self.log_dir / 'moved_files.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['source', 'destination', 'reason'])
            writer.writeheader()
            writer.writerows(self.moved)
            
    def _write_deleted_files(self):
        """Write deleted_files.csv."""
        with open(self.log_dir / 'deleted_files.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['path', 'reason'])
            writer.writeheader()
            writer.writerows(self.deleted)
            
    def _write_summary(self):
        """Write maintenance_report.md."""
        summary = f"""# Enterprise Chunker Directory Cleanup Report
**Timestamp:** {self.timestamp}  
**Mode:** {'DRY RUN' if self.dry_run else 'EXECUTED'}  
**Root:** {self.root}

## Summary Statistics

- **Total Items Scanned:** {len(self.items)}
- **Files:** {len([i for i in self.items if i['type'] == 'file'])}
- **Directories:** {len([i for i in self.items if i['type'] == 'dir'])}
- **Kept:** {len([i for i in self.items if i['category'] == 'KEEP'])}
- **Moved:** {len([i for i in self.items if i['action'] == 'MOVE'])}
- **Deleted:** {len([i for i in self.items if i['action'] == 'DELETE'])}
- **Snapshots Pruned:** {len([i for i in self.items if i['category'] == 'SNAPSHOT_PRUNE'])}
- **Duplicate Groups:** {len(self.duplicates)}

## Actions Taken

### Files Moved ({len(self.moved)})
"""
        # Preview first 50 moves
        for item in self.moved[:50]:
            summary += f"- `{Path(item['source']).name}` → `{item['destination']}`\n"
        if len(self.moved) > 50:
            summary += f"\n*...and {len(self.moved) - 50} more (see moved_files.csv)*\n"
            
        summary += f"\n### Files Deleted ({len(self.deleted)})\n"
        for item in self.deleted[:50]:
            summary += f"- `{Path(item['path']).name}` - {item['reason']}\n"
        if len(self.deleted) > 50:
            summary += f"\n*...and {len(self.deleted) - 50} more (see deleted_files.csv)*\n"
            
        summary += "\n## Files Generated\n\n"
        summary += "- `inventory.csv` - Complete inventory\n"
        summary += "- `actions_plan.json` - Detailed action plan\n"
        summary += "- `duplicates.csv` - Duplicate files\n"
        summary += "- `moved_files.csv` - All moved files\n"
        summary += "- `deleted_files.csv` - All deleted files\n"
        summary += "- `final_tree.txt` - Directory structure\n"
        
        with open(self.log_dir / 'maintenance_report.md', 'w', encoding='utf-8') as f:
            f.write(summary)
            
    def _generate_tree(self):
        """Generate directory tree."""
        tree_output = []
        
        def walk_tree(path: Path, prefix: str = "", is_last: bool = True):
            if path.name.startswith('.') or path.name == '__pycache__':
                return
                
            connector = "└── " if is_last else "├── "
            tree_output.append(f"{prefix}{connector}{path.name}")
            
            if path.is_dir():
                try:
                    children = sorted(list(path.iterdir()), key=lambda x: (not x.is_dir(), x.name))
                    for i, child in enumerate(children):
                        is_last_child = i == len(children) - 1
                        extension = "    " if is_last else "│   "
                        walk_tree(child, prefix + extension, is_last_child)
                except PermissionError:
                    pass
                    
        tree_output.append(str(self.root.name))
        try:
            children = sorted(list(self.root.iterdir()), key=lambda x: (not x.is_dir(), x.name))
            for i, child in enumerate(children):
                walk_tree(child, "", i == len(children) - 1)
        except:
            pass
            
        with open(self.log_dir / 'final_tree.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(tree_output))
            
    def _update_readme(self):
        """Update README.md with directory health section."""
        readme_path = self.root / 'README.md'
        if not readme_path.exists():
            return
            
        try:
            content = readme_path.read_text(encoding='utf-8')
            
            health_section = f"""
## Directory Health

**Last Cleanup:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Items Scanned:** {len(self.items)}  
**Items Moved:** {len(self.moved)}  
**Items Deleted:** {len(self.deleted)}  
**Snapshots Pruned:** {len([i for i in self.items if i['category'] == 'SNAPSHOT_PRUNE'])}

**Snapshot Policy:** Keep only the latest legacy snapshot per project. Older snapshots are pruned during maintenance. Config backups follow the same policy.

**Log Location:** `05_logs/maintenance/{self.timestamp}/`
"""
            
            # Remove old health section if exists
            if '## Directory Health' in content:
                parts = content.split('## Directory Health')
                before = parts[0]
                after = ''
                if len(parts) > 1:
                    # Find next section
                    remaining = parts[1]
                    next_section = remaining.find('\n## ')
                    if next_section != -1:
                        after = remaining[next_section:]
                content = before + health_section + after
            else:
                content += '\n' + health_section
                
            readme_path.write_text(content, encoding='utf-8')
            
        except Exception as e:
            print(f"Error updating README: {e}")
            
    def _update_summary(self):
        """Update ENTERPRISE_CHUNKER_SUMMARY.md."""
        summary_path = self.root / 'ENTERPRISE_CHUNKER_SUMMARY.md'
        if not summary_path.exists():
            return
            
        try:
            content = summary_path.read_text(encoding='utf-8')
            
            doc_section = """
## Documentation Locations

- **Root Documentation:** README.md, CHANGELOG.md, ENTERPRISE_CHUNKER_SUMMARY.md
- **Additional Docs:** `99_doc/` - All supporting documentation and notes
- **Notes & Transcripts:** `99_doc/notes/` - Conversation transcripts and analysis notes
- **Maintenance Logs:** `05_logs/maintenance/` - Directory cleanup and health reports

## Snapshot Policy

Legacy snapshots are stored in `**/legacy/` folders and follow a naming convention of `ProjectName_YYYY_MM_DD_HH_MM_SS`. 

**Policy:** Only the latest snapshot per project is retained. Older snapshots are automatically pruned during directory maintenance.

**Config Backups:** Files matching `config.json.backup_*` follow the same policy - only the most recent backup is kept.
"""
            
            if '## Documentation Locations' in content:
                parts = content.split('## Documentation Locations')
                before = parts[0]
                after = ''
                if len(parts) > 1:
                    remaining = parts[1]
                    next_section = remaining.find('\n## ')
                    if next_section != -1:
                        after = remaining[next_section:]
                content = before + doc_section + after
            else:
                content += '\n' + doc_section
                
            summary_path.write_text(content, encoding='utf-8')
            
        except Exception as e:
            print(f"Error updating summary: {e}")
            
    def _update_changelog(self):
        """Append maintenance entry to CHANGELOG.md."""
        changelog_path = self.root / 'CHANGELOG.md'
        if not changelog_path.exists():
            return
            
        try:
            content = changelog_path.read_text(encoding='utf-8')
            
            entry = f"""
## [{datetime.now().strftime('%Y-%m-%d')}] - Directory Maintenance

### Changed
- Directory cleanup and normalization
- Documentation moved to `99_doc/` structure
- Legacy snapshot pruning (kept latest per project)
- Removed development cruft and temporary files

### Metrics
- Items scanned: {len(self.items)}
- Files moved: {len(self.moved)}
- Items deleted: {len(self.deleted)}
- Snapshots pruned: {len([i for i in self.items if i['category'] == 'SNAPSHOT_PRUNE'])}

**Maintenance Log:** `05_logs/maintenance/{self.timestamp}/`

"""
            
            # Insert after first header
            lines = content.split('\n')
            insert_pos = 0
            for i, line in enumerate(lines):
                if line.startswith('# '):
                    insert_pos = i + 1
                    break
                    
            lines.insert(insert_pos, entry)
            changelog_path.write_text('\n'.join(lines), encoding='utf-8')
            
        except Exception as e:
            print(f"Error updating changelog: {e}")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main execution function."""
    print(f"{'='*80}")
    print(f"Enterprise Chunker Directory Cleanup")
    print(f"{'='*80}")
    print(f"Root: {ROOT}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'EXECUTE'}")
    print(f"Timestamp: {NOW}")
    print(f"{'='*80}\n")
    
    if not ROOT.exists():
        print(f"ERROR: Root directory does not exist: {ROOT}")
        return
        
    # Step 1: Inventory
    inventory = FileInventory(ROOT)
    items = inventory.scan()
    duplicates = inventory.get_duplicates()
    
    print(f"\nFound {len(duplicates)} duplicate groups\n")
    
    # Step 2: Classify
    classifier = FileClassifier(ROOT, items)
    items = classifier.classify()
    
    # Step 3: Execute (or dry run)
    executor = CleanupExecutor(ROOT, items, DRY_RUN, NOW)
    moved, deleted = executor.execute()
    
    # Step 4: Report
    reporter = Reporter(ROOT, items, moved, deleted, duplicates, NOW, DRY_RUN)
    reporter.generate_all_reports()
    
    # Summary
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"Items scanned:     {len(items)}")
    print(f"Items kept:        {len([i for i in items if i['category'] == 'KEEP'])}")
    print(f"Items moved:       {len(moved)}")
    print(f"Items deleted:     {len(deleted)}")
    print(f"Snapshots pruned:  {len([i for i in items if i['category'] == 'SNAPSHOT_PRUNE'])}")
    print(f"Duplicate groups:  {len(duplicates)}")
    print(f"{'='*80}\n")
    
    if DRY_RUN:
        print("*** DRY RUN COMPLETE - Review reports in 05_logs/maintenance/{}/".format(NOW))
        print("*** Set DRY_RUN=False and run again to execute cleanup")
    else:
        print("*** CLEANUP COMPLETE")
        
    print(f"\nReports: {ROOT / '05_logs' / 'maintenance' / NOW}")


if __name__ == '__main__':
    main()
