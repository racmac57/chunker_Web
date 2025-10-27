# 🕒 2025-10-26-14-50-00
# fix_claude_export_advanced.py
# Author: R. A. Carucci
# Purpose: Fix Claude ZIP exports - handles both conversations.json and projects.json

import json
import uuid
import zipfile
import shutil
from datetime import datetime
from pathlib import Path
import sys

def fix_file_metadata(conversations):
    """Fix missing file_uuid and created_at in file attachments"""
    fixed_count = 0
    error_conversations = []
    
    for conv_idx, conversation in enumerate(conversations):
        conv_name = conversation.get('name', f'Conversation {conv_idx}')
        has_errors = False
        
        # Check chat_messages for file attachments
        if 'chat_messages' in conversation:
            for msg_idx, message in enumerate(conversation['chat_messages']):
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
                                file_obj['created_at'] = conversation.get(
                                    'created_at', 
                                    datetime.utcnow().isoformat() + 'Z'
                                )
                                has_errors = True
                                fixed_count += 1
                            
                            # Ensure file_name exists
                            if 'file_name' not in file_obj:
                                file_obj['file_name'] = f"attachment_{file_idx}"
                                has_errors = True
        
        if has_errors:
            error_conversations.append(conv_name)
    
    return fixed_count, error_conversations

def process_zip_export(zip_path, output_dir=None):
    """Process Claude ZIP export and fix all JSON files"""
    
    print(f"📦 Processing ZIP: {zip_path}")
    
    if output_dir is None:
        output_dir = Path(zip_path).parent / f"{Path(zip_path).stem}_fixed"
    
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)
    
    results = {}
    
    # Extract and process ZIP
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # List all JSON files
        json_files = [f for f in zip_ref.namelist() if f.endswith('.json')]
        
        print(f"📋 Found {len(json_files)} JSON files in ZIP")
        
        for json_file in json_files:
            print(f"\n🔍 Processing: {json_file}")
            
            # Read JSON from ZIP
            with zip_ref.open(json_file) as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"  ❌ JSON parsing error: {e}")
                    continue
            
            # Process based on file type
            if 'conversations' in json_file.lower():
                fixed_count, error_conversations = fix_file_metadata(data)
                results[json_file] = {
                    'total': len(data),
                    'fixed_fields': fixed_count,
                    'conversations_fixed': len(error_conversations)
                }
                print(f"  ✅ Fixed {fixed_count} fields in {len(error_conversations)} conversations")
            else:
                results[json_file] = {
                    'total': len(data) if isinstance(data, list) else 1,
                    'status': 'validated'
                }
                print(f"  ✅ Validated ({len(data) if isinstance(data, list) else 1} records)")
            
            # Write fixed version
            output_file = output_dir / json_file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Create new ZIP with fixed files
    fixed_zip = output_dir.parent / f"{Path(zip_path).stem}_fixed.zip"
    print(f"\n📦 Creating fixed ZIP: {fixed_zip}")
    
    with zipfile.ZipFile(fixed_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in output_dir.rglob('*'):
            if file_path.is_file():
                arcname = file_path.relative_to(output_dir)
                zipf.write(file_path, arcname)
    
    # Report results
    print(f"\n{'='*70}")
    print(f"✅ PROCESSING COMPLETE")
    print(f"{'='*70}")
    
    for json_file, stats in results.items():
        print(f"\n📄 {json_file}:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    print(f"\n📁 Output:")
    print(f"  - Fixed JSON files: {output_dir}")
    print(f"  - Fixed ZIP: {fixed_zip}")
    print(f"\n{'='*70}")
    print(f"🎯 Next Steps:")
    print(f"{'='*70}")
    print(f"Upload the FIXED ZIP to Claude Chat Viewer:")
    print(f"  {fixed_zip}")
    print(f"{'='*70}\n")
    
    return fixed_zip

def process_json_file(json_path, output_file=None):
    """Process standalone JSON file"""
    
    print(f"📖 Reading: {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    
    original_count = len(conversations) if isinstance(conversations, list) else 1
    print(f"📊 Found {original_count} conversations")
    
    # Backup
    backup_file = str(json_path).replace('.json', '_backup.json')
    print(f"💾 Creating backup: {backup_file}")
    shutil.copy2(json_path, backup_file)
    
    # Fix
    print(f"🔧 Fixing validation errors...")
    fixed_count, error_conversations = fix_file_metadata(conversations)
    
    # Output
    if output_file is None:
        output_file = str(json_path).replace('.json', '_fixed.json')
    
    print(f"💾 Writing fixed file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, indent=2, ensure_ascii=False)
    
    # Report
    print(f"\n{'='*70}")
    print(f"✅ COMPLETE")
    print(f"{'='*70}")
    print(f"Fixed fields: {fixed_count}")
    print(f"Conversations fixed: {len(error_conversations)}")
    print(f"Output: {output_file}")
    print(f"{'='*70}\n")
    
    return output_file

if __name__ == "__main__":
    # Auto-detect file type
    input_path = r"C:\Users\carucci_r\Downloads\data-2025-10-26-02-11-36-batch-0000"
    
    # Check for ZIP file first
    zip_files = list(Path(input_path).parent.glob("data-*.zip"))
    
    if zip_files:
        print(f"🔍 Found ZIP export: {zip_files[0]}")
        choice = input("Process ZIP file? (y/n): ")
        if choice.lower() == 'y':
            process_zip_export(zip_files[0])
            sys.exit(0)
    
    # Otherwise process conversations.json
    conversations_file = Path(input_path) / "conversations.json"
    
    if conversations_file.exists():
        process_json_file(conversations_file)
    else:
        print(f"❌ Error: Could not find conversations.json or ZIP file")
        print(f"\nSearched:")
        print(f"  - {conversations_file}")
        print(f"  - {Path(input_path).parent / 'data-*.zip'}")

