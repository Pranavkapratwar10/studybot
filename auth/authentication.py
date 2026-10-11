"""
User authentication module with bcrypt password hashing
"""
import bcrypt
import streamlit as st
from typing import Optional, Tuple
from database.db_manager import DatabaseManager


class AuthManager:
    """Handles user authentication and session management"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def register_user(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """
        Register a new user
        Returns: (success: bool, message: str)
        """
        # Validate input
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters long"
        
        if '@' not in email:
            return False, "Invalid email address"
        
        # Hash password
        password_hash = self.hash_password(password)
        
        # Create user
        user_id = self.db.create_user(username, email, password_hash)
        
        if user_id:
            return True, "Registration successful! Please login."
        else:
            return False, "Username or email already exists"
    
    def login_user(self, username: str, password: str) -> Tuple[bool, str, Optional[dict]]:
        """
        Login a user
        Returns: (success: bool, message: str, user: dict or None)
        """
        # Check for admin bypass
        if username == "admin" and password == "admin123":
            # Create special admin user object
            admin_user = {
                'id': -1,  # Special ID for admin
                'username': 'admin',
                'email': 'admin@studybot.local',
                'is_active': 1,
                'is_admin': True,
                'created_at': None,
                'last_login': None
            }
            return True, "Admin login successful!", admin_user
        
        # Regular user login
        user = self.db.get_user_by_username(username)
        
        if not user:
            return False, "Invalid username or password", None
        
        if not user.get('is_active'):
            return False, "Account is disabled", None
        
        if self.verify_password(password, user['password_hash']):
            # Update last login
            self.db.update_last_login(user['id'])
            user['is_admin'] = False  # Regular users are not admin
            return True, "Login successful!", user
        else:
            return False, "Invalid username or password", None
    
    def logout_user(self):
        """Logout the current user"""
        if 'user' in st.session_state:
            del st.session_state.user
        if 'user_id' in st.session_state:
            del st.session_state.user_id
        if 'username' in st.session_state:
            del st.session_state.username
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return 'user_id' in st.session_state and st.session_state.user_id is not None
    
    def get_current_user_id(self) -> Optional[int]:
        """Get current user ID"""
        return st.session_state.get('user_id')
    
    def get_current_username(self) -> Optional[str]:
        """Get current username"""
        return st.session_state.get('username')
    
    def init_session_state(self):
        """Initialize session state variables"""
        if 'user_id' not in st.session_state:
            st.session_state.user_id = None
        if 'username' not in st.session_state:
            st.session_state.username = None
        if 'user' not in st.session_state:
            st.session_state.user = None
