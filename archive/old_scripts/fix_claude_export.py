# 🕒 2025-10-26-14-45-00
# fix_claude_export.py
# Author: R. A. Carucci
# Purpose: Fix Claude export validation errors by adding missing file metadata

import json
import uuid
from datetime import datetime
from pathlib import Path
import shutil

def fix_file_metadata(conversations):
    """
    Fix missing file_uuid and created_at in file attachments
    """
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
                                # Use conversation created_at or current timestamp
                                file_obj['created_at'] = conversation.get(
                                    'created_at', 
                                    datetime.utcnow().isoformat() + 'Z'
                                )
                                has_errors = True
                                fixed_count += 1
        
        if has_errors:
            error_conversations.append(conv_name)
    
    return fixed_count, error_conversations

def process_claude_export(input_file, output_file=None):
    """
    Process Claude export and fix validation errors
    """
    print(f"[INFO] Reading: {input_file}")
    
    # Read the original file
    with open(input_file, 'r', encoding='utf-8') as f:
        conversations = json.load(f)
    
    original_count = len(conversations)
    print(f"[INFO] Found {original_count} conversations")
    
    # Backup original
    backup_file = input_file.replace('.json', '_backup.json')
    print(f"[INFO] Creating backup: {backup_file}")
    shutil.copy2(input_file, backup_file)
    
    # Fix the issues
    print(f"[INFO] Fixing validation errors...")
    fixed_count, error_conversations = fix_file_metadata(conversations)
    
    # Determine output file
    if output_file is None:
        output_file = input_file.replace('.json', '_fixed.json')
    
    # Write fixed version
    print(f"[INFO] Writing fixed file: {output_file}")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, indent=2, ensure_ascii=False)
    
    # Report results
    print(f"\n{'='*60}")
    print(f"[SUCCESS] PROCESSING COMPLETE")
    print(f"{'='*60}")
    print(f"Original conversations: {original_count}")
    print(f"Fixed file metadata fields: {fixed_count}")
    print(f"Conversations with fixes: {len(error_conversations)}")
    print(f"\n[FILES] Files created:")
    print(f"  - Backup: {backup_file}")
    print(f"  - Fixed:  {output_file}")
    
    if error_conversations:
        print(f"\n[FIXED] Conversations that were fixed:")
        for conv_name in error_conversations[:10]:  # Show first 10
            print(f"  * {conv_name}")
        if len(error_conversations) > 10:
            print(f"  ... and {len(error_conversations) - 10} more")
    
    print(f"\n{'='*60}")
    print(f"[NEXT STEPS]")
    print(f"{'='*60}")
    print(f"1. Upload the FIXED file to Claude Chat Viewer:")
    print(f"   {output_file}")
    print(f"2. If issues persist, check the GitHub issues:")
    print(f"   https://github.com/osteele/claude-chat-viewer/issues")
    print(f"{'='*60}\n")
    
    return output_file

if __name__ == "__main__":
    # Configuration
    input_file = r"C:\Users\carucci_r\Downloads\data-2025-10-26-02-11-36-batch-0000\conversations.json"
    
    # Check if file exists
    if not Path(input_file).exists():
        print(f"[ERROR] File not found: {input_file}")
        print(f"\nPlease update the 'input_file' path in the script.")
        exit(1)
    
    # Process the file
    fixed_file = process_claude_export(input_file)
    
    print(f"[DONE] Upload this file to the viewer:")
    print(f"   {fixed_file}")

