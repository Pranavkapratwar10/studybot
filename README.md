# StudyBot - AI-Powered Study Assistant

> An intelligent study assistant powered by Retrieval-Augmented Generation (RAG) that helps students prepare for exams through interactive Q&A, MCQ generation, and multiple exam preparation modes.

## 📋 Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Admin Panel](#admin-panel)
- [Project Structure](#project-structure)
- [Deployment](#deployment)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## ✨ Features

### For Students
- 🔐 **Secure Authentication** - User registration and login with bcrypt password hashing
- 📚 **Multi-Document Upload** - Support for PDF, DOCX, and TXT files
- 🤖 **AI-Powered Q&A** - Natural language question answering using RAG pipeline
- 📝 **5 Exam Modes**:
  - 🗣️ **Viva** - Conversational Q&A format
  - 📝 **Short Answer** - Concise 2-4 sentence answers
  - 📄 **Long Answer** - Detailed explanations with examples
  - 📚 **Revision** - Structured notes with key points
  - ✅ **MCQ Generator** - Dedicated page for MCQ generation with interactive testing and scoring
- 💬 **Chat History** - Persistent conversation tracking per user with filters
- 🔍 **Smart Search** - ChromaDB-powered vector search with intelligent fallbacks

### For Administrators
- 👨‍💼 **Separate Admin Panel** - Independent interface on port 8502
- 📊 **Dashboard** - System statistics, user metrics, and visual charts
- 👥 **User Management** - View all registered users with activity statistics
- 🔑 **API Settings** - Update Groq API key with validation
- ⚙️ **System Management** - Database info, ChromaDB status, cache control

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection (for dependencies and API)

### 1. Clone and Setup

```bash
# Navigate to project directory
cd rag_chatbot

# Run automated setup
setup.bat         # Windows
./setup.sh        # Linux/Mac
```

### 2. Configure API Key

Create or edit `.streamlit/secrets.toml`:

```toml
GROQ_API_KEY = "your-groq-api-key-here"
ADMIN_PASSWORD = "your-secure-password"
```

Get your free Groq API key from: https://console.groq.com/

### 3. Run the Application

**Student Interface (Port 8501):**
```bash
run.bat           # Windows
./run.sh          # Linux/Mac
```

**Admin Panel (Port 8502):**
```bash
run_admin.bat     # Windows
./run_admin.sh    # Linux/Mac
```

**Admin Credentials:**
- Username: `admin`
- Password: `826282`

### 4. First-Time Usage

1. Open http://localhost:8501
2. Register a new student account
3. Upload study materials (PDF, DOCX, or TXT)
4. Start asking questions!

---

## 🛠️ Tech Stack

### Frontend
- **Streamlit** - Web interface

### Backend
- **Python 3.8+** - Core language
- **LangChain** - RAG framework
- **ChromaDB** - Vector database for embeddings
- **Groq API** - LLM (Llama 3.1 70B)
- **Sentence Transformers** - Text embeddings (all-MiniLM-L6-v2)

### Database
- **SQLite** - User data, documents, chat history
- **ChromaDB** - Vector embeddings for semantic search

### Document Processing
- **pdfplumber** - PDF text extraction
- **python-docx** - DOCX text extraction
- **pytesseract** - OCR support

### Security
- **bcrypt** - Password hashing
- **Session-based authentication**

---

## 📦 Installation

### Manual Installation

1. **Create Virtual Environment**
   ```bash
   python -m venv venv
   
   # Activate it
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Linux/Mac
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create Required Directories**
   ```bash
   mkdir data\uploads
   mkdir data\chroma_db
   ```

4. **Configure Secrets**
   - Create `.streamlit/secrets.toml`
   - Add your GROQ_API_KEY and ADMIN_PASSWORD

### Quick Installation

Use the provided setup scripts:

```bash
# Windows
setup.bat

# Linux/Mac
chmod +x setup.sh && ./setup.sh
```

---

## 📖 Usage

### Student Workflow

1. **Register & Login**
   - Create account with username, email, and password
   - Login to access features

2. **Upload Documents**
   - Navigate to "📤 Upload" page
   - Select PDF/DOCX/TXT files (max 10MB each)
   - Click "Process Documents"
   - Wait for confirmation

3. **Ask Questions**
   - Go to "💬 Chat" page
   - Select exam mode from dropdown
   - Type your question
   - Get AI-powered answer with source citations

4. **Use MCQ Generator**
   - Navigate to "📝 MCQ Generator" page
   - Upload a document for MCQ generation
   - Choose number of questions (5-30)
   - Select difficulty level (Easy/Medium/Hard)
   - Take interactive test with radio buttons
   - Submit for automatic scoring with detailed explanations

5. **View History**
   - Check "📜 History" page
   - Filter by exam mode
   - Review past conversations and MCQ results

### Admin Workflow

1. **Access Admin Panel**
   - Run admin panel on port 8502
   - Login with admin credentials

2. **Monitor Dashboard**
   - View total users, documents, chats
   - See activity charts and statistics
   - Track uploads and usage trends

3. **Manage Users**
   - View all registered users
   - Check user statistics (documents, chats, MCQs per user)
   - Monitor user activity

4. **Configure API**
   - Update Groq API key
   - Validate and save changes
   - Auto-updates secrets.toml

---

## 👨‍💼 Admin Panel

### Features

#### Dashboard (📊)
- Total users and active users (7-day window)
- Document statistics with upload trends
- Chat activity metrics
- Visual charts (user registration timeline, document distribution)
- Real-time system health

#### User Management (👥)
- Complete user list with details
- User statistics (docs, chats, MCQs per user)
- Registration and last login tracking
- Account status monitoring

#### API Settings (🔑)
- View current API key (masked for security)
- Update Groq API key with validation
- Automatic secrets.toml update
- Model configuration display

#### System (⚙️)
- Database information and stats
- ChromaDB status and collection count
- Application settings overview
- Clear cache functionality
- System maintenance tools

### Access Control
- Password-protected interface
- Separate authentication from student interface
- Secure session management
- Admin-only features

---

## 📁 Project Structure

```
rag_chatbot/
├── app.py                      # Main student interface
├── admin/
│   ├── admin_panel.py          # Admin panel application (port 8502)
│   └── dashboard.py            # Admin dashboard components
├── pages/
│   ├── mcq_page.py             # Dedicated MCQ generator page
│   └── viva_page.py            # Viva practice mode page
├── auth/
│   └── authentication.py       # User authentication logic
├── config/
│   └── settings.py             # Configuration and constants
├── database/
│   ├── db_manager.py           # SQLite database operations
│   └── models.py               # Database schema definitions
├── llm/
│   ├── groq_client.py          # Groq API integration
│   └── prompts.py              # Prompt templates for exam modes
├── mcq/
│   └── mcq_generator.py        # MCQ generation logic
├── rag/
│   ├── document_processor.py   # Document parsing and chunking
│   ├── vector_store.py         # ChromaDB vector store
│   └── rag_pipeline.py         # Complete RAG pipeline
├── utils/
│   └── helpers.py              # Utility functions
├── viva/
│   └── viva_generator.py       # Viva question generation
├── data/
│   ├── uploads/                # User-uploaded documents
│   ├── chroma_db/              # Vector database storage
│   └── study_assistant.db      # SQLite database
├── .streamlit/
│   └── secrets.toml            # API keys and secrets
├── requirements.txt            # Python dependencies
├── run.bat / run.sh            # Student interface launcher
├── run_admin.bat / run_admin.sh # Admin panel launcher
├── setup.bat / setup.sh        # Automated setup scripts
└── README.md                   # This file
```

---

## 🌐 Deployment

### Streamlit Cloud Deployment

1. **Prepare Repository**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: StudyBot"
   git branch -M main
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud**
   - Visit https://share.streamlit.io
   - Sign in with GitHub account
   - Click "New app"
   - Select your repository
   - Set main file: `app.py`
   - Choose Python version: 3.10+

3. **Configure Secrets**
   - Click "Advanced settings"
   - Add secrets in TOML format:
   ```toml
   GROQ_API_KEY = "your-groq-api-key"
   ADMIN_PASSWORD = "your-secure-admin-password"
   ```

4. **Deploy Admin Panel Separately**
   - Create another app deployment
   - Set main file: `admin/admin_panel.py`
   - Use same secrets configuration
   - Different subdomain for admin access

### Admin Panel Access After Deployment

**Option 1: Integrated (Current Setup)**
- Main app includes admin in sidebar
- Access via: `https://your-app.streamlit.app` → Sidebar → Admin Panel → Login

**Option 2: Separate Deployment**
- Deploy admin panel as separate app
- Main App: `https://studybot.streamlit.app`
- Admin Panel: `https://studybot-admin.streamlit.app`

**Option 3: Multi-Page App**
- Create `pages/🔐_Admin_Panel.py`
- Access via: `https://your-app.streamlit.app/🔐_Admin_Panel`

### Deployment Notes
- SQLite and ChromaDB use temporary storage on Streamlit Cloud
- For production, consider external database services
- Free tier has resource limits (1GB RAM, 1 CPU core)
- Groq API free tier has rate limits

---

## ⚙️ Configuration

### config/settings.py

```python
# Database
DATABASE_PATH = "data/study_assistant.db"
CHROMA_DB_PATH = "data/chroma_db"

# RAG Settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 3

# Embedding Model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# LLM Settings
LLM_MODEL = "llama-3.1-70b-versatile"
TEMPERATURE = 0.7
MAX_TOKENS = 2000

# Upload Settings
UPLOAD_DIR = "data/uploads"
MAX_FILE_SIZE_MB = 10
ALLOWED_EXTENSIONS = [".pdf", ".docx", ".txt"]
```

### Environment Variables

Set in `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your-groq-api-key"
ADMIN_PASSWORD = "your-admin-password"
```

Or as environment variables:
```bash
export GROQ_API_KEY="your-groq-api-key"
export ADMIN_PASSWORD="your-admin-password"
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Windows - Kill process on port 8501
netstat -ano | findstr :8501
taskkill /PID <PID> /F

# Linux/Mac
lsof -i :8501
kill -9 <PID>
```

#### 2. Import Errors
```bash
pip install -r requirements.txt --force-reinstall
```

#### 3. Database Locked
- Close all app instances
- Delete `data/study_assistant.db`
- Restart the application

#### 4. ChromaDB Schema Error
```bash
# Backup and reset ChromaDB
ren data\chroma_db chroma_db_backup
mkdir data\chroma_db
# Restart app - documents need re-upload
```

#### 5. API Key Not Working
- Verify key at https://console.groq.com/
- Check format (must start with `gsk_`)
- Update via admin panel
- **Restart both applications after update**

#### 6. Upload Fails
- Check file is PDF, DOCX, or TXT
- Ensure file size < 10MB
- Verify `data/uploads/<user_id>` folder exists

#### 7. No AI Responses
- Check internet connection
- Verify API key is valid
- Check Groq API rate limits
- Review error messages in app

### Performance Issues

#### App Running Slow
1. Reduce `TOP_K_RESULTS` in config/settings.py
2. Use smaller chunks (reduce `CHUNK_SIZE`)
3. Clear ChromaDB and re-upload fewer documents

#### Memory Issues
1. Clear browser cache
2. Restart the application
3. Delete old documents from database
4. Use smaller PDF files

### Reset Everything

```bash
# Windows
rmdir /s data
rmdir /s venv
setup.bat
```

```bash
# Linux/Mac
rm -rf data venv
./setup.sh
```

---

## 🔒 Security Features

- **Password Hashing**: Bcrypt with salt
- **Session Management**: Secure session-based auth
- **Per-User Isolation**: Data separated by user ID
- **SQL Injection Prevention**: Parameterized queries
- **File Validation**: Type and size checking
- **Admin Protection**: Password-protected dashboard
- **API Key Security**: Stored in secrets, never exposed

---

## 📊 Key Statistics

| Metric | Value |
|--------|-------|
| Total Features | 108+ |
| Python Modules | 9 |
| Exam Modes | 5 |
| Supported File Types | 3 (PDF, DOCX, TXT) |
| Database Systems | 2 (SQLite, ChromaDB) |
| Authentication Methods | 2 (Student, Admin) |

---

## 🎯 Use Cases

### For Students
- Exam preparation and revision
- Quick concept clarification
- MCQ practice and self-testing
- Viva practice with AI
- Note summarization

### For Teachers
- Monitor student progress
- Track study material usage
- Analyze common questions
- Provide targeted help

### For Institutions
- Self-service study platform
- Reduce teacher workload
- 24/7 availability
- Scalable solution

---

## 📝 Sample Questions to Try

After uploading study materials:

**General:**
- "Summarize this document"
- "What are the main topics covered?"

**Viva Mode:**
- "Explain the key concept"
- "What questions might an examiner ask?"

**Short Answer:**
- "Give a brief answer about [topic]"
- "Explain [concept] concisely"

**Long Answer:**
- "Provide a detailed explanation of [topic]"
- "Write a comprehensive answer about [concept]"

**Revision Mode:**
- "Give me revision notes for [topic]"
- "Summarize key points to remember"

**MCQ Generator:**
- Upload document → Generate 10 medium questions → Take test!

---

## 🤝 Contributing

This is a complete, production-ready project. If you want to extend it:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## 📄 License

MIT License - Feel free to use for personal or commercial projects.

---

## 👤 Author

Developed as a flagship AI project showcasing:
- Full-stack ML application development
- RAG pipeline implementation
- LLM integration with real-world use case
- Vector database management
- Production-ready code with deployment guide
- Comprehensive documentation

---

## 🙏 Acknowledgments

- **Groq** - for providing fast LLM inference
- **ChromaDB** - for vector database
- **Sentence Transformers** - for embeddings
- **Streamlit** - for web framework
- **LangChain** - for RAG framework

---

## 📞 Support

For issues or questions:
1. Check this README
2. Review error messages in the app
3. Ensure all dependencies are installed
4. Verify Python version is 3.8+
5. Check API key is valid and active

---

## ✅ Quick Reference

### Run Commands
```bash
# Setup (one time)
setup.bat / ./setup.sh

# Student interface (port 8501)
run.bat / ./run.sh

# Admin panel (port 8502)
run_admin.bat / ./run_admin.sh

# Manual start
streamlit run app.py
streamlit run admin/admin_panel.py --server.port=8502
```

### Default Access
- **Student Interface:** http://localhost:8501
- **Admin Panel:** http://localhost:8502
- **Admin Username:** admin
- **Admin Password:** 826282

### Important Files
- `.streamlit/secrets.toml` - API keys and secrets
- `config/settings.py` - Application configuration
- `data/study_assistant.db` - SQLite database
- `data/chroma_db/` - Vector embeddings
- `requirements.txt` - Python dependencies

---

**🎉 Ready to transform your study experience with AI!**

*Built with ❤️ using Python, Streamlit, and RAG Technology*
