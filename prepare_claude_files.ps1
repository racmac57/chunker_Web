# PowerShell script to prepare files for Claude collaboration
# Creates a package with all necessary files for GUI and AI interface development

$packageDir = "claude_gui_package"
$docsDir = "$packageDir/Documentation"
$coreDir = "$packageDir/Core_Files"
$examplesDir = "$packageDir/Examples"

Write-Host "Preparing Claude Collaboration Package..." -ForegroundColor Cyan
Write-Host ""

# Create directories
New-Item -ItemType Directory -Path $packageDir -Force | Out-Null
New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
New-Item -ItemType Directory -Path $coreDir -Force | Out-Null
New-Item -ItemType Directory -Path $examplesDir -Force | Out-Null

Write-Host "[+] Created package directory structure" -ForegroundColor Green

# Core files (essential)
$coreFiles = @(
    "rag_integration.py",
    "rag_search.py",
    "config.json",
    "backfill_knowledge_base.py"
)

foreach ($file in $coreFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $coreDir -Force
        Write-Host "  [OK] Copied $file" -ForegroundColor Gray
    } else {
        Write-Host "  [WARNING] File not found: $file" -ForegroundColor Yellow
    }
}

# Documentation files
$docFiles = @(
    "README.md",
    "CHANGELOG.md",
    "SUMMARY.md",
    "CLAUDE_GUI_COLLABORATION_PROMPT.md"
)

foreach ($file in $docFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $docsDir -Force
        Write-Host "  [OK] Copied $file" -ForegroundColor Gray
    } else {
        Write-Host "  [WARNING] File not found: $file" -ForegroundColor Yellow
    }
}

# Example files
$exampleFiles = @(
    "verify_chunk_completeness.py",
    "verify_backfill.py"
)

foreach ($file in $exampleFiles) {
    if (Test-Path $file) {
        Copy-Item $file -Destination $examplesDir -Force
        Write-Host "  [OK] Copied $file" -ForegroundColor Gray
    } else {
        Write-Host "  [WARNING] File not found: $file" -ForegroundColor Yellow
    }
}

# Create README for package
$packageReadme = @"
# Claude GUI Collaboration Package

This package contains all files needed for Claude to help build:
1. Modern GUI application for knowledge base management
2. AI access interface for RAG workflows

## Package Contents

### Core Files (Essential)
- `rag_integration.py` - ChromaRAG class and search methods
- `rag_search.py` - Current CLI search interface
- `config.json` - System configuration
- `backfill_knowledge_base.py` - Knowledge base structure and metadata

### Documentation
- `README.md` - System overview
- `CHANGELOG.md` - Version history
- `SUMMARY.md` - Project summary
- `CLAUDE_GUI_COLLABORATION_PROMPT.md` - Detailed prompt for Claude

### Examples
- `verify_chunk_completeness.py` - Example KB access patterns
- `verify_backfill.py` - Verification script

## How to Use

1. Share the `CLAUDE_GUI_COLLABORATION_PROMPT.md` with Claude
2. Provide all files in this package
3. Claude will review the architecture and create the GUI + API

## Current System State

- **Version**: 2.1.6
- **Knowledge Base**: ChromaDB with 3,201 chunks
- **Database Location**: `./chroma_db/`
- **Collection**: `chunker_knowledge_base`
- **Status**: All chunks verified and complete

## Next Steps

1. Review `CLAUDE_GUI_COLLABORATION_PROMPT.md` for full requirements
2. Share files with Claude
3. Collaborate on GUI framework selection
4. Implement and test both components

---
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

$packageReadme | Out-File -FilePath "$packageDir/README.md" -Encoding UTF8

Write-Host ""
Write-Host "[+] Package created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Package Location: $packageDir" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Review CLAUDE_GUI_COLLABORATION_PROMPT.md"
Write-Host "  2. Share the package with Claude"
Write-Host "  3. Use the prompt template to request GUI and AI interface"
Write-Host ""

