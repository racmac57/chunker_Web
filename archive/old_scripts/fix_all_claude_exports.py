# 🕒 2025-10-26-15-00-00
# fix_all_claude_exports.py
# Author: R. A. Carucci
# Purpose: Fix all Claude export JSON files - conversations, projects, and users

import json
import uuid
from datetime import datetime
from pathlib import Path
import shutil

def fix_file_metadata(data, data_type="conversation"):
    """Fix missing file_uuid and created_at in file attachments"""
    fixed_count = 0
    error_items = []
    
    if not isinstance(data, list):
        data = [data]
    
    for idx, item in enumerate(data):
        item_name = item.get('name', f'{data_type.capitalize()} {idx}')
        has_errors = False
        
        # Check chat_messages for file attachments (conversations)
        if 'chat_messages' in item:
            for msg_idx, message in enumerate(item['chat_messages']):
                if 'files' in message and isinstance(message['files'], list):
                    for file_idx, file_obj in enumerate(message['files']):
                        if isinstance(file_obj, dict):
                            # Add missing file_uuid
                            if 'file_uuid' not in file_obj:
                                file_obj['file_uuid'] = str(uuid.uuid4())
                                has_errors = True
                                fixed_count += 1
                            
                            # Add missing created_at
                            if 'created_at' not in file_obj:
                                file_obj['created_at'] = item.get(
                                    'created_at', 
                                    datetime.now().isoformat() + 'Z'
                                )
                                has_errors = True
                                fixed_count += 1
                            
                            # Ensure file_name exists
                            if 'file_name' not in file_obj:
                                file_obj['file_name'] = f"attachment_{file_idx}"
                                has_errors = True
                                fixed_count += 1
        
        # Check attachments in messages (alternative structure)
        if 'attachments' in item and isinstance(item['attachments'], list):
            for att_idx, attachment in enumerate(item['attachments']):
                if isinstance(attachment, dict):
                    if 'file_uuid' not in attachment:
                        attachment['file_uuid'] = str(uuid.uuid4())
                        has_errors = True
                        fixed_count += 1
                    
                    if 'created_at' not in attachment:
                        attachment['created_at'] = item.get(
                            'created_at',
                            datetime.now().isoformat() + 'Z'
                        )
                        has_errors = True
                        fixed_count += 1
        
        # Check files array (direct files)
        if 'files' in item and isinstance(item['files'], list):
            for file_idx, file_obj in enumerate(item['files']):
                if isinstance(file_obj, dict):
                    if 'file_uuid' not in file_obj:
                        file_obj['file_uuid'] = str(uuid.uuid4())
                        has_errors = True
                        fixed_count += 1
                    
                    if 'created_at' not in file_obj:
                        file_obj['created_at'] = item.get(
                            'created_at',
                            datetime.now().isoformat() + 'Z'
                        )
                        has_errors = True
                        fixed_count += 1
                    
                    if 'file_name' not in file_obj:
                        file_obj['file_name'] = f"file_{file_idx}"
                        has_errors = True
                        fixed_count += 1
        
        # Check docs array (projects)
        if 'docs' in item and isinstance(item['docs'], list):
            for doc_idx, doc in enumerate(item['docs']):
                if isinstance(doc, dict):
                    if 'uuid' not in doc:
                        doc['uuid'] = str(uuid.uuid4())
                        has_errors = True
                        fixed_count += 1
                    
                    if 'created_at' not in doc:
                        doc['created_at'] = item.get(
                            'created_at',
                            datetime.now().isoformat() + 'Z'
                        )
                        has_errors = True
                        fixed_count += 1
        
        if has_errors:
            error_items.append(item_name)
    
    return fixed_count, error_items

def process_json_file(json_path, data_type="unknown"):
    """Process a single JSON file and fix validation errors"""
    
    print(f"\n{'='*70}")
    print(f"[PROCESSING] {json_path.name}")
    print(f"{'='*70}")
    
    if not json_path.exists():
        print(f"[SKIP] File not found: {json_path}")
        return None
    
    print(f"[INFO] Reading file...")
    
    # Read the original file
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    original_count = len(data) if isinstance(data, list) else 1
    print(f"[INFO] Found {original_count} {data_type}(s)")
    
    # Backup original
    backup_file = str(json_path).replace('.json', '_backup.json')
    
    if not Path(backup_file).exists():
        print(f"[INFO] Creating backup: {backup_file}")
        shutil.copy2(json_path, backup_file)
    else:
        print(f"[INFO] Backup already exists: {backup_file}")
    
    # Fix the issues
    print(f"[INFO] Fixing validation errors...")
    fixed_count, error_items = fix_file_metadata(data, data_type)
    
    if fixed_count == 0:
        print(f"[OK] No fixes needed - file is valid!")
        return None
    
    # Determine output file
    output_file = str(json_path).replace('.json', '_fixed.json')
    
    # Write fixed version
    print(f"[INFO] Writing fixed file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Report
    print(f"\n[SUCCESS] Fixed {data_type}:")
    print(f"  - Total {data_type}s: {original_count}")
    print(f"  - Fields fixed: {fixed_count}")
    print(f"  - Items with fixes: {len(error_items)}")
    
    if error_items and len(error_items) <= 10:
        print(f"\n[FIXED] Items that were fixed:")
        for item_name in error_items:
            print(f"  * {item_name}")
    elif error_items:
        print(f"\n[FIXED] Sample of fixed items (first 10):")
        for item_name in error_items[:10]:
            print(f"  * {item_name}")
        print(f"  ... and {len(error_items) - 10} more")
    
    print(f"\n[OUTPUT] {output_file}")
    
    return output_file

def process_all_exports(export_dir):
    """Process all Claude export JSON files in a directory"""
    
    export_path = Path(export_dir)
    
    if not export_path.exists():
        print(f"[ERROR] Directory not found: {export_dir}")
        return
    
    print(f"\n{'='*70}")
    print(f"[CLAUDE EXPORT FIXER - ALL FILES]")
    print(f"{'='*70}")
    print(f"Export directory: {export_path}")
    print(f"{'='*70}")
    
    # Define files to process
    files_to_process = [
        ('conversations.json', 'conversation'),
        ('projects.json', 'project'),
        ('users.json', 'user')
    ]
    
    results = {}
    
    for filename, data_type in files_to_process:
        file_path = export_path / filename
        output_file = process_json_file(file_path, data_type)
        results[filename] = {
            'processed': output_file is not None,
            'output': output_file
        }
    
    # Final summary
    print(f"\n\n{'='*70}")
    print(f"[SUMMARY] ALL FILES PROCESSED")
    print(f"{'='*70}")
    
    fixed_files = []
    skipped_files = []
    
    for filename, result in results.items():
        if result['processed']:
            fixed_files.append(result['output'])
            print(f"[FIXED] {filename}")
            print(f"        -> {Path(result['output']).name}")
        else:
            skipped_files.append(filename)
            print(f"[OK]    {filename} (no fixes needed)")
    
    print(f"\n{'='*70}")
    print(f"[NEXT STEPS]")
    print(f"{'='*70}")
    
    if fixed_files:
        print(f"\n1. Upload these FIXED files to Claude Chat Viewer:")
        for fixed_file in fixed_files:
            print(f"   - {Path(fixed_file).name}")
        print(f"\n2. URL: https://tools.osteele.com/claude-chat-viewer")
        
        # Create a combined folder with all fixed files
        fixed_folder = export_path / "all_fixed_files"
        fixed_folder.mkdir(exist_ok=True)
        
        for fixed_file in fixed_files:
            shutil.copy2(fixed_file, fixed_folder / Path(fixed_file).name)
        
        # Also copy non-fixed files
        for filename in ['conversations.json', 'projects.json', 'users.json']:
            original = export_path / filename
            backup = export_path / filename.replace('.json', '_backup.json')
            fixed = export_path / filename.replace('.json', '_fixed.json')
            
            if fixed.exists():
                # Use fixed version
                dest_file = fixed_folder / filename
                if not dest_file.exists():
                    shutil.copy2(fixed, dest_file)
            elif original.exists() and not backup.exists():
                # Use original (no fixes were needed)
                dest_file = fixed_folder / filename
                if not dest_file.exists():
                    shutil.copy2(original, dest_file)
        
        print(f"\n3. OR use the combined folder:")
        print(f"   {fixed_folder}")
        print(f"\n   This folder contains all files ready to upload:")
        for file in sorted(fixed_folder.glob('*.json')):
            print(f"   - {file.name}")
    else:
        print(f"\nAll files are valid! No fixes needed.")
        print(f"You can upload the original files directly.")
    
    print(f"\n{'='*70}\n")

if __name__ == "__main__":
    # Configuration
    export_dir = r"C:\Users\carucci_r\Downloads\data-2025-10-26-02-11-36-batch-0000"
    
    # Process all files
    process_all_exports(export_dir)

