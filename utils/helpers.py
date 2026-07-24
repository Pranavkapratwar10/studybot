"""
Utility functions and helpers
"""
import os
from pathlib import Path
from typing import List
from datetime import datetime
import streamlit as st


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp


def validate_file_upload(uploaded_file) -> tuple[bool, str]:
    """
    Validate uploaded file
    Returns: (is_valid, message)
    """
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file extension
    file_ext = Path(uploaded_file.name).suffix.lower()
    allowed_extensions = ['.pdf', '.docx', '.txt']
    
    if file_ext not in allowed_extensions:
        return False, f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}"
    
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024  # 10MB in bytes
    if uploaded_file.size > max_size:
        return False, f"File too large. Maximum size: {format_file_size(max_size)}"
    
    return True, "File is valid"


def save_uploaded_file(uploaded_file, user_id: int, upload_dir: Path) -> tuple[bool, str, str]:
    """
    Save uploaded file to disk
    Returns: (success, file_path, message)
    """
    try:
        # Create user directory
        user_dir = upload_dir / str(user_id)
        user_dir.mkdir(parents=True, exist_ok=True)
        
        # Create unique filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{uploaded_file.name}"
        file_path = user_dir / filename
        
        # Save file
        with open(file_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        return True, str(file_path), "File saved successfully"
    
    except Exception as e:
        return False, "", f"Error saving file: {str(e)}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def get_exam_mode_emoji(mode: str) -> str:
    """Get emoji for exam mode"""
    emojis = {
        "viva": "🗣️",
        "mcq": "✅",
        "short_answer": "📝",
        "long_answer": "📄",
        "revision": "📚"
    }
    return emojis.get(mode, "❓")
