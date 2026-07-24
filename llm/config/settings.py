"""
Configuration settings for the AI Study Assistant application
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Database settings
DATABASE_PATH = BASE_DIR / "data" / "study_assistant.db"
CHROMA_DB_PATH = BASE_DIR / "data" / "chroma_db"

# Upload settings
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
MAX_UPLOAD_SIZE_MB = 10
ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt']

# RAG settings
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_RESULTS = 5
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# LLM settings
# Available free Groq models (as of 2024):
# - llama-3.3-70b-versatile (Best, newest)
# - llama-3.1-8b-instant (Fast)
# - mixtral-8x7b-32768 (Alternative)
GROQ_MODEL = "llama-3.3-70b-versatile"  # Updated to current free model
TEMPERATURE = 0.7
MAX_TOKENS = 2000

# Application settings
APP_TITLE = "AI Study Assistant - TalentTrack"
APP_ICON = "📚"
SESSION_TIMEOUT_MINUTES = 60

# Create necessary directories
def initialize_directories():
    """Create required directories if they don't exist"""
    directories = [
        BASE_DIR / "data",
        DATABASE_PATH.parent,
        CHROMA_DB_PATH,
        UPLOAD_DIR
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Admin credentials
ADMIN_USERNAME = "admin"
# Admin password should be set in environment or secrets
