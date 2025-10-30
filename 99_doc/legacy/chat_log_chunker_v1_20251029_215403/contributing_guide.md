# 🕒 2025-06-28-01-30-30
# CONTRIBUTING.md
# Author: R. A. Carucci
# Purpose: Contribution guidelines for the chunker project

# Contributing to AI Chat Log Chunker

Thank you for your interest in contributing to the AI Chat Log Chunker project! This document provides guidelines and instructions for contributors.

## 🤝 **How to Contribute**

### **🐛 Reporting Issues**
- Use the [GitHub Issues](../../issues) page
- Provide detailed reproduction steps
- Include system information (OS, Python version)
- Attach relevant log files from `logs/watcher.log`

### **💡 Suggesting Features**
- Check existing [feature requests](../../issues?q=is%3Aissue+is%3Aopen+label%3Aenhancement)
- Describe the use case and expected behavior
- Consider backward compatibility implications

### **🔧 Code Contributions**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Test thoroughly with `test_chunker.ps1`
5. Submit a pull request

## 🏗️ **Development Setup**

```bash
# Clone your fork
git clone https://github.com/your-username/ai-chat-chunker.git
cd ai-chat-chunker

# Setup development environment
python setup_chunker_environment.py

# Create test files
.\test_chunker.ps1 -CreateTest

# Run diagnostics
.\test_chunker.ps1 -Diagnostics
```

### **🔍 Linting & Pre-commit Hooks**

We recommend setting up automated code quality tools:

```bash
# Install development tools
pip install black flake8 pre-commit bandit

# Format code automatically
black .

# Check style issues
flake8 . --max-line-length=127 --extend-ignore=E203,W503

# Security scan
bandit -r . -x tests/

# Setup pre-commit hooks (optional but recommended)
pre-commit install
```

**Pre-commit configuration** (`.pre-commit-config.yaml`):
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.1.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=127, --extend-ignore=E203,W503]

  - repo: https://github.com/pycqa/bandit
    rev: 1.7.4
    hooks:
      - id: bandit
        args: [-x, tests/]
```

## 🧪 **Testing Guidelines**

### **Required Tests**
Before submitting a pull request, ensure:

```powershell
# 1. Environment setup works
python setup_chunker_environment.py

# 2. Core functionality works
.\test_chunker.ps1 -CreateTest
python watcher_splitter.py  # Let run for 30 seconds, then Ctrl+C

# 3. No zero-byte files created
.\test_chunker.ps1 -CheckResults

# 4. PowerShell scripts work
.\test_chunker.ps1 -Diagnostics
.\test_chunker.ps1 -MonitorOnly  # Test briefly

# 5. Executable builds (if modified core files)
build_and_run.bat

# 6. Test the resulting executable
if (Test-Path "dist\chunker_hidden.exe") {
  # Run executable briefly to ensure it starts
  $process = Start-Process "dist\chunker_hidden.exe" -PassThru -NoNewWindow
  Start-Sleep 10
  Stop-Process $process -Force
  Write-Host "✅ Executable test completed"
}
```

### **Test Cases to Cover**
- **File Processing**: Various file sizes and content types
- **Error Handling**: Malformed files, permission issues
- **Zero-byte Prevention**: Edge cases that might create empty chunks
- **Cloud Sync**: Network failures, permission issues
- **Configuration**: Invalid settings, missing files

## 📝 **Code Style Guidelines**

### **Python Code**
- Follow PEP 8 style guidelines
- Use descriptive variable names
- Add docstrings for functions
- Include error handling with logging
- Maintain backward compatibility

**Example:**
```python
def process_file(file_path, config):
    """
    Process a single conversation file into chunks.
    
    Args:
        file_path (Path): Path to the input file
        config (dict): Configuration settings
        
    Returns:
        bool: True if processing successful, False otherwise
    """
    logger.info(f"Processing file: {file_path.name}")
    # Implementation...
```

### **PowerShell Code**
- Use approved verbs (Get-, Set-, New-, etc.)
- Include parameter validation
- Add help comments
- Use consistent indentation (4 spaces)

**Example:**
```powershell
function Test-ChunkerEnvironment {
    <#
    .SYNOPSIS
    Validates the chunker system environment
    
    .DESCRIPTION
    Checks for required files, directories, and dependencies
    #>
    
    Write-ColorText "Checking environment..." "Yellow"
    # Implementation...
}
```

## 📋 **Pull Request Process**

### **PR Checklist**
- [ ] Code follows style guidelines and passes linting
- [ ] All tests pass locally and in CI
- [ ] Documentation updated (if applicable)
- [ ] No breaking changes (or clearly documented with migration guide)
- [ ] Commit messages are clear and descriptive
- [ ] Pre-commit hooks pass (if configured)
- [ ] Security considerations reviewed

### **PR Template**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement

## Testing
- [ ] Ran full test suite
- [ ] Tested with sample files
- [ ] Verified zero-byte prevention
- [ ] Checked cloud sync functionality

## Screenshots/Logs
(If applicable)
```

## 🏷️ **Versioning**

We use [Semantic Versioning](https://semver.org/):
- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes

## 📖 **Documentation**

### **Required Documentation Updates**
- Update [README.md](./README.md) for new features
- Add configuration options to config documentation
- Update PowerShell help comments
- Include troubleshooting sections for new issues

### **Documentation Style**
- Use clear, concise language
- Include code examples
- Add screenshots for GUI changes
- Keep cross-references updated

## 🔒 **Security Considerations**

### **Security Review Required For**
- File system access changes
- Network communication modifications
- Configuration handling updates
- Logging of sensitive information

### **Security Guidelines**
- Never log sensitive file contents
- Validate all file paths to prevent directory traversal
- Handle network errors gracefully
- Sanitize configuration inputs

## 🌟 **Recognition**

Contributors will be:
- Listed in the project README
- Mentioned in release notes
- Invited to join the maintainer team (for significant contributions)

## 📞 **Getting Help**

### **Development Questions**
- Check existing [discussions](../../discussions)
- Review [troubleshooting guide](./README.md#troubleshooting-guide)
- Run diagnostics: `.\test_chunker.ps1 -Diagnostics`

### **Contact Maintainers**
- GitHub Issues for bugs/features
- Discussions for general questions
- Email for security issues: [security@example.com]

## 🎯 **Priority Areas**

We're especially looking for contributions in:

### **High Priority**
- 🔧 **GUI Dashboard**: Electron or web-based interface
- 📧 **Email Notifications**: SMTP integration for processing alerts
- 🔄 **Parallel Processing**: Multi-threaded file processing
- 📊 **Advanced Analytics**: Processing metrics and reporting

### **Medium Priority**
- 🐧 **Linux Support**: Cross-platform compatibility
- 🔌 **Plugin System**: Extensible processing pipeline
- 📱 **Mobile Monitoring**: Web interface for mobile devices
- 🎨 **Themes**: Customizable PowerShell output colors

### **Documentation**
- 📹 **Video Tutorials**: Setup and usage demonstrations
- 🌐 **Internationalization**: Multi-language support
- 📚 **Use Case Studies**: Real-world implementation examples

## 🎉 **First-Time Contributors**

Welcome! Here are some good first issues:
- Documentation improvements
- PowerShell script enhancements
- Configuration validation
- Error message improvements
- Test case additions

Look for issues labeled `good-first-issue` in our [issue tracker](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22).

---

**Thank you for contributing to making AI chat log processing more efficient and reliable!** 🚀