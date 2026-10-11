# 🚀 Deploy RAG Chatbot to PythonAnywhere - Complete Guide

## 📋 Overview
This guide will help you deploy your Streamlit RAG Chatbot application to PythonAnywhere **directly from your local folder** (not from GitHub).

---

## ⚠️ IMPORTANT LIMITATIONS

**PythonAnywhere does NOT support Streamlit natively!**

### Why PythonAnywhere is Not Ideal for This App:
1. ❌ PythonAnywhere is designed for **WSGI web apps** (Flask, Django)
2. ❌ Streamlit requires **WebSocket support** (not available on PythonAnywhere)
3. ❌ Streamlit runs on its own server (port 8501) which PythonAnywhere doesn't support
4. ❌ Free tier has very limited resources for AI/ML applications

### ✅ RECOMMENDED ALTERNATIVES:

#### **Option 1: Streamlit Community Cloud (BEST & FREE)**
- ✅ Specifically designed for Streamlit apps
- ✅ Free hosting with GitHub integration
- ✅ Automatic deployments
- ✅ SSL certificates included
- **Setup Time:** 5-10 minutes

#### **Option 2: Hugging Face Spaces**
- ✅ Free tier available
- ✅ Great for ML applications
- ✅ GPU support available
- **Setup Time:** 10-15 minutes

#### **Option 3: Render.com**
- ✅ Free tier for Streamlit apps
- ✅ Easy deployment from GitHub
- ✅ Automatic SSL
- **Setup Time:** 10 minutes

#### **Option 4: AWS EC2 / Google Cloud / Azure (Production)**
- ✅ Full control
- ✅ Scalable
- ❌ Requires payment (but free tiers available)
- **Setup Time:** 30-60 minutes

---

## 🔄 IF YOU STILL WANT TO TRY PYTHONANYWHERE

I'll provide the steps, but **this is NOT recommended** and will require significant modifications.

---

## 📦 STEP 1: Prepare Your Files Locally

### 1.1 Create a Deployment Package

1. Open Command Prompt in your project folder:
```cmd
cd d:\pranav__all_projects\rag_chatbot
```

2. Create a ZIP file of your entire project:
```cmd
# If you have 7-Zip installed
7z a rag_chatbot_deploy.zip * -xr!venv -xr!__pycache__ -xr!*.pyc -xr!.git

# OR using PowerShell
powershell Compress-Archive -Path * -DestinationPath rag_chatbot_deploy.zip -Force -Exclude venv,__pycache__,*.pyc,.git
```

### 1.2 Essential Files Checklist
Make sure your ZIP includes:
- ✅ `app.py`
- ✅ `requirements.txt`
- ✅ `.streamlit/secrets.toml` (with API keys)
- ✅ All Python modules (auth/, config/, database/, llm/, rag/, etc.)
- ✅ Empty `data/` folder structure
- ❌ DO NOT include: `venv/`, `__pycache__/`, `.git/`

---

## 🌐 STEP 2: Setup PythonAnywhere Account

### 2.1 Create Account
1. Go to: https://www.pythonanywhere.com/registration/register/beginner/
2. Choose **Free Beginner Account**
3. Verify your email

### 2.2 Account Limitations (Free Tier)
- CPU seconds per day: 100 seconds
- Disk space: 512 MB
- One web app
- Python 3.10 available
- **NO WebSocket support** (breaks Streamlit's live updates)

---

## 📤 STEP 3: Upload Your Files

### 3.1 Upload via Web Interface

1. **Login to PythonAnywhere Dashboard**

2. **Go to Files tab**
   - URL: `https://www.pythonanywhere.com/user/YOUR_USERNAME/files/`

3. **Upload your ZIP file**
   - Click "Upload a file" button
   - Select `rag_chatbot_deploy.zip`
   - Wait for upload to complete

4. **Extract the ZIP**
   - Click "Open Bash console here"
   - Run:
   ```bash
   unzip rag_chatbot_deploy.zip -d rag_chatbot
   cd rag_chatbot
   ```

### 3.2 Verify File Structure
```bash
ls -la
# Should see: app.py, requirements.txt, auth/, config/, database/, etc.
```

---

## 🐍 STEP 4: Create Virtual Environment

### 4.1 Open Bash Console
1. Go to: **Consoles** tab → **Bash**

### 4.2 Setup Virtual Environment
```bash
# Navigate to your project
cd ~/rag_chatbot

# Create virtual environment with Python 3.10
mkvirtualenv --python=/usr/bin/python3.10 rag_chatbot_env

# Activate it (should auto-activate after creation)
workon rag_chatbot_env

# Verify Python version
python --version  # Should show Python 3.10.x
```

---

## 📦 STEP 5: Install Dependencies

### 5.1 Install Requirements
```bash
# Make sure you're in the project directory
cd ~/rag_chatbot

# Activate virtual environment
workon rag_chatbot_env

# Install all dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 5.2 Handle Installation Issues

**If you get memory errors:**
```bash
# Install packages one by one
pip install streamlit
pip install chromadb
pip install sentence-transformers
pip install groq
pip install bcrypt
pip install python-docx
pip install pypdf
pip install pdfplumber
pip install pandas
pip install plotly
pip install pypdfium2
```

**Common Issues:**
- ⚠️ `sentence-transformers` is LARGE (~500MB) - may fail on free tier
- ⚠️ `chromadb` requires significant disk space
- ⚠️ Installation may take 10-15 minutes

---

## ⚙️ STEP 6: Configure Secrets

### 6.1 Create Secrets File
```bash
cd ~/rag_chatbot
mkdir -p .streamlit
nano .streamlit/secrets.toml
```

### 6.2 Add Your API Keys
```toml
GROQ_API_KEY = "your-actual-groq-api-key-here"
ADMIN_PASSWORD = "your-admin-password-here"
```

Press `Ctrl+X`, then `Y`, then `Enter` to save.

---

## 🔧 STEP 7: Create WSGI Wrapper (Required!)

Since PythonAnywhere doesn't support Streamlit natively, you need a workaround.

### 7.1 Create Flask Wrapper
```bash
cd ~/rag_chatbot
nano wsgi_wrapper.py
```

### 7.2 Add This Code:
```python
"""
WSGI wrapper to run Streamlit on PythonAnywhere
WARNING: This is a workaround and NOT recommended for production
"""
import os
import sys
import subprocess
from flask import Flask, redirect

# Add project directory to path
project_home = '/home/YOUR_USERNAME/rag_chatbot'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

app = Flask(__name__)

@app.route('/')
def index():
    return """
    <html>
        <body>
            <h1>Streamlit App</h1>
            <p><strong>ERROR:</strong> Streamlit cannot run directly on PythonAnywhere.</p>
            <p>PythonAnywhere does not support WebSocket connections required by Streamlit.</p>
            <h2>Recommended Solutions:</h2>
            <ul>
                <li>Deploy to <a href="https://streamlit.io/cloud">Streamlit Community Cloud</a> (FREE & EASY)</li>
                <li>Use Hugging Face Spaces</li>
                <li>Use Render.com</li>
                <li>Convert to Flask/Django app</li>
            </ul>
        </body>
    </html>
    """

if __name__ == '__main__':
    app.run()
```

**Replace `YOUR_USERNAME` with your actual PythonAnywhere username!**

Save: `Ctrl+X` → `Y` → `Enter`

---

## 🌐 STEP 8: Configure Web App

### 8.1 Create Web App
1. Go to **Web** tab
2. Click **Add a new web app**
3. Choose **Manual configuration**
4. Select **Python 3.10**

### 8.2 Configure Settings

**Source code:**
```
/home/YOUR_USERNAME/rag_chatbot
```

**Virtualenv:**
```
/home/YOUR_USERNAME/.virtualenvs/rag_chatbot_env
```

**WSGI configuration file:**
Click to edit, then replace content with:
```python
import sys
import os

# Add project directory
project_home = '/home/YOUR_USERNAME/rag_chatbot'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Import Flask app
from wsgi_wrapper import app as application
```

**Replace `YOUR_USERNAME`!**

### 8.3 Reload Web App
Click the big green **Reload** button

---

## 🧪 STEP 9: Test Deployment

### 9.1 Access Your Site
Visit: `https://YOUR_USERNAME.pythonanywhere.com`

### 9.2 Expected Result
❌ You'll see the error page explaining Streamlit can't run on PythonAnywhere

---

## 🔄 ALTERNATIVE SOLUTION: Convert to Flask

If you MUST use PythonAnywhere, you need to **rewrite your app** as a Flask application.

### Required Changes:
1. ❌ Remove all Streamlit code
2. ✅ Create Flask routes for each page
3. ✅ Use HTML templates instead of Streamlit components
4. ✅ Handle sessions manually
5. ✅ Rewrite chat interface with AJAX/WebSockets alternative

**Estimated Effort:** 40-60 hours of work

---

## ✅ RECOMMENDED: Deploy to Streamlit Cloud Instead

### Quick Steps:

#### 1. Push to GitHub
```bash
cd d:\pranav__all_projects\rag_chatbot

# Initialize git (if not done)
git init

# Create .gitignore
echo venv/ > .gitignore
echo __pycache__/ >> .gitignore
echo *.pyc >> .gitignore
echo data/ >> .gitignore
echo .streamlit/secrets.toml >> .gitignore

# Commit
git add .
git commit -m "Initial commit for Streamlit Cloud deployment"

# Add remote (create empty repo on GitHub first)
git remote add origin https://github.com/YOUR_USERNAME/rag-chatbot.git
git branch -M main
git push -u origin main
```

#### 2. Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Sign in with GitHub
3. Click **New app**
4. Select your repository
5. Main file: `app.py`
6. Click **Advanced settings**
7. Add secrets:
```toml
GROQ_API_KEY = "your-key"
ADMIN_PASSWORD = "your-password"
```
8. Click **Deploy**

**Done! Your app will be live in 2-3 minutes!**

---

## 🆘 Troubleshooting PythonAnywhere

### Issue 1: Can't Install sentence-transformers
**Solution:** Free tier disk space too small
```bash
# Try lightweight alternative
pip install sentence-transformers --no-cache-dir
# OR use smaller embedding model
```

### Issue 2: Import Errors
```bash
workon rag_chatbot_env
pip list  # Check installed packages
pip install missing-package
```

### Issue 3: Permission Errors
```bash
chmod +x ~/rag_chatbot/*.py
```

### Issue 4: Streamlit Won't Start
**Expected:** Streamlit requires WebSocket support which PythonAnywhere doesn't provide.

**Solution:** Use Streamlit Cloud, Hugging Face Spaces, or Render.com instead.

---

## 📊 Comparison Table

| Platform | Streamlit Support | Free Tier | Setup Time | Recommended |
|----------|------------------|-----------|------------|-------------|
| **Streamlit Cloud** | ✅ Native | ✅ Yes | 5 min | ⭐⭐⭐⭐⭐ |
| **Hugging Face** | ✅ Yes | ✅ Yes | 10 min | ⭐⭐⭐⭐ |
| **Render.com** | ✅ Yes | ✅ Yes | 10 min | ⭐⭐⭐⭐ |
| **PythonAnywhere** | ❌ No | ✅ Yes | N/A | ❌ |
| **Heroku** | ✅ Yes | ❌ No | 15 min | ⭐⭐⭐ |
| **AWS EC2** | ✅ Yes | ⚠️ Limited | 60 min | ⭐⭐⭐⭐ |

---

## 🎯 Final Recommendation

### For Your RAG Chatbot:
**Use Streamlit Community Cloud**

### Why?
1. ✅ **FREE forever**
2. ✅ **Built for Streamlit** - zero configuration needed
3. ✅ **Automatic deployments** from GitHub
4. ✅ **SSL certificates** included
5. ✅ **Easy secrets management**
6. ✅ **Much better resources** than PythonAnywhere free tier
7. ✅ **WebSocket support** for real-time chat
8. ✅ **No code changes** required

### Setup Time:
- PythonAnywhere (with Flask rewrite): **40-60 hours**
- Streamlit Cloud: **5-10 minutes**

**The choice is clear! 🚀**

---

## 📞 Need Help?

### Streamlit Cloud Deployment Issues?
- Check: https://docs.streamlit.io/streamlit-community-cloud
- Community: https://discuss.streamlit.io/

### Want Step-by-Step Streamlit Cloud Guide?
Just ask! I can provide a detailed guide specifically for Streamlit Cloud deployment.

---

## ✅ Next Steps

**What would you like to do?**

1. **Deploy to Streamlit Cloud** (RECOMMENDED)
   - I'll create a detailed guide with screenshots
   - Takes only 5-10 minutes
   - Your app will be live and shareable

2. **Deploy to Hugging Face Spaces**
   - Good alternative with GPU support
   - I'll create deployment guide

3. **Deploy to Render.com**
   - Another good free option
   - I'll create deployment guide

4. **Still try PythonAnywhere**
   - Follow steps above (will hit limitations)
   - May need to convert to Flask

**Let me know which option you prefer!** 🚀
