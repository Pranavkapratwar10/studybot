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
# Available free Groq models (as of 2026):
# - openai/gpt-oss-120b (Best, 120B parameters, 131k context)
# - qwen/qwen3.8-27b (Good alternative)
# - openai/gpt-oss-20b (Smaller, faster)
GROQ_MODEL = "openai/gpt-oss-120b"  # Updated to current free model
TEMPERATURE = 0.7
MAX_TOKENS = 2000

# Application settings
APP_TITLE = "📚 AI Study Assistant - StudyBot"
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
