# 📥 Download Chunker Project to Your Work Desktop

## Overview
This guide will help you download the **chunker_Web** project from GitHub to your work desktop computer.

---

## Prerequisites

### ✅ Step 1: Install Git on Your Work Desktop

**Check if Git is already installed:**
1. Open **Command Prompt** or **PowerShell**
2. Type: `git --version`
3. If you see a version number (e.g., `git version 2.x.x`), Git is installed ✅
4. If you get an error, proceed to install Git below ⬇️

**Install Git (if needed):**
1. Go to the official Git download page: [https://git-scm.com/download/win](https://git-scm.com/download/win)
2. The download should start automatically (64-bit version)
3. Run the downloaded installer (`Git-x.xx.x-64-bit.exe`)
4. Use these recommended settings during installation:
   - ✅ Use Visual Studio Code as Git's default editor (or Notepad++)
   - ✅ Git from the command line and also from 3rd-party software
   - ✅ Use bundled OpenSSH
   - ✅ Use the OpenSSL library
   - ✅ Checkout Windows-style, commit Unix-style line endings
   - ✅ Use MinTTY (the default terminal of MSYS2)
   - ✅ Default (fast-forward or merge)
   - ✅ Git Credential Manager
   - ✅ Enable file system caching
5. Click **Install** and then **Finish**
6. Restart your Command Prompt/PowerShell

---

## 📦 Clone the Repository

### Step 2: Choose a Location

Decide where you want to store the project on your work desktop. Common locations:
- `C:\Users\YourUsername\Documents\Projects\`
- `C:\Projects\`
- `D:\Dev\`

### Step 3: Open Terminal/Command Prompt

1. Press **Windows Key + R**
2. Type: `cmd` or `powershell`
3. Press **Enter**

### Step 4: Navigate to Your Desired Location

```bash
cd C:\Users\YourUsername\Documents\Projects
```
*(Replace with your chosen location)*

### Step 5: Clone the Repository

**Copy and paste this command:**

```bash
git clone https://github.com/racmac57/chunker_Web.git
```

**What happens:**
- Git will download all 42 files from GitHub
- A new folder called `chunker_Web` will be created
- You'll see progress like:
  ```
  Cloning into 'chunker_Web'...
  remote: Enumerating objects: 41, done.
  remote: Counting objects: 100% (41/41), done.
  Receiving objects: 100% (41/41), done.
  ```

### Step 6: Navigate into the Project

```bash
cd chunker_Web
```

---

## 🐍 Set Up Python Environment

### Step 7: Install Python (if needed)

**Check if Python is installed:**
```bash
python --version
```

If not installed:
1. Download from: [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Run installer
3. ⚠️ **IMPORTANT:** Check "Add Python to PATH" during installation
4. Click **Install Now**

### Step 8: Create Virtual Environment (Recommended)

```bash
python -m venv venv
```

### Step 9: Activate Virtual Environment

**On Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**On Windows (Command Prompt):**
```bash
venv\Scripts\activate.bat
```

You should see `(venv)` appear in your terminal prompt.

### Step 10: Install Required Packages

```bash
pip install -r requirements.txt
```

This will install all necessary Python packages:
- Flask (web framework)
- Watchdog (file monitoring)
- NLTK (text processing)
- And other dependencies

---

## 🚀 Run the Application

### Step 11: Start the Dashboard

```bash
python start_dashboard.py
```

### Step 12: Access the Web Dashboard

1. Open your web browser
2. Go to: [http://localhost:5000](http://localhost:5000)
3. You should see the Chunker Dashboard! 🎉

---

## 📚 Project Structure

```
chunker_Web/
├── 01_scripts/           # Additional scripts and utilities
├── 02_data/              # Input data directory
├── 03_archive/           # Archived files
├── 04_output/            # Processed output files
├── 05_logs/              # Application logs
├── 06_config/            # Configuration files
├── static/               # CSS and JavaScript files
├── templates/            # HTML templates
├── watcher_splitter.py   # Main file watcher and processor
├── web_dashboard.py      # Web dashboard application
├── start_dashboard.py    # Dashboard launcher
├── requirements.txt      # Python dependencies
└── README.md             # Project documentation
```

---

## 🔄 Keeping Your Code Updated

When changes are made to the GitHub repository, update your local copy:

```bash
git pull origin main
```

---

## 🔗 Quick Links

- **GitHub Repository:** [https://github.com/racmac57/chunker_Web](https://github.com/racmac57/chunker_Web)
- **Git Documentation:** [https://git-scm.com/doc](https://git-scm.com/doc)
- **Python Download:** [https://www.python.org/downloads/](https://www.python.org/downloads/)
- **Flask Documentation:** [https://flask.palletsprojects.com/](https://flask.palletsprojects.com/)

---

## ❓ Troubleshooting

### Git not recognized
- Restart your terminal after installing Git
- Make sure Git was added to PATH during installation
- Try opening a new Command Prompt/PowerShell window

### Python not recognized
- Restart your terminal after installing Python
- Reinstall Python and check "Add Python to PATH"
- Try `py` instead of `python`

### Permission Denied when activating virtual environment
**PowerShell only:**
```bash
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port 5000 already in use
- Close other applications using port 5000
- Or modify the port in `start_dashboard.py`

---

## 💡 Need Help?

- Check the project's README.md file
- Review the ENTERPRISE_CHUNKER_SUMMARY.md for detailed documentation
- Visit the repository's Issues page: [https://github.com/racmac57/chunker_Web/issues](https://github.com/racmac57/chunker_Web/issues)

---

**Last Updated:** October 14, 2025  
**Repository:** racmac57/chunker_Web

