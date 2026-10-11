"""
Separate Admin Panel - Independent from user interface
"""
import streamlit as st
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db_manager import DatabaseManager
from admin.dashboard import show_admin_dashboard
import pandas as pd

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "826282"


def verify_admin_credentials(username: str, password: str) -> bool:
    """Verify admin credentials"""
    return username == ADMIN_USERNAME and password == ADMIN_PASSWORD


def show_admin_login():
    """Display admin login page"""
    st.set_page_config(
        page_title="Admin Panel",
        page_icon="🔐",
        layout="wide"
    )
    
    st.title("🔐 Admin Panel")
    st.markdown("### Secure Admin Access")
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.form("admin_login_form"):
            st.markdown("#### Login")
            username = st.text_input("Username", placeholder="admin")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            
            submit = st.form_submit_button("🔓 Login", use_container_width=True)
            
            if submit:
                if verify_admin_credentials(username, password):
                    st.session_state.admin_authenticated = True
                    st.session_state.admin_username = username
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")


def show_admin_interface():
    """Display admin interface after authentication"""
    st.set_page_config(
        page_title="Admin Dashboard",
        page_icon="👨‍💼",
        layout="wide"
    )
    
    # Initialize database
    db_manager = DatabaseManager()
    
    # Sidebar
    with st.sidebar:
        st.title("👨‍💼 Admin Panel")
        st.write(f"**Admin:** {st.session_state.get('admin_username', 'admin')}")
        st.divider()
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["📊 Dashboard", "👥 Users", "🔑 API Settings", "⚙️ System"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.admin_authenticated = False
            st.rerun()
    
    # Display selected page
    if page == "📊 Dashboard":
        show_admin_dashboard(db_manager)
    elif page == "👥 Users":
        show_users_management(db_manager)
    elif page == "🔑 API Settings":
        show_api_settings()
    elif page == "⚙️ System":
        show_system_settings()


def show_users_management(db_manager: DatabaseManager):
    """User management interface"""
    st.title("👥 User Management")
    
    # Get all users
    users = db_manager.get_all_users()
    
    if not users:
        st.info("No users registered yet")
        return
    
    st.subheader(f"Total Users: {len(users)}")
    
    # Display users
    for user in users:
        with st.expander(f"👤 {user['username']} ({user['email']})"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**User ID:** {user['id']}")
                st.write(f"**Username:** {user['username']}")
                st.write(f"**Email:** {user['email']}")
            
            with col2:
                st.write(f"**Created:** {user['created_at']}")
                st.write(f"**Last Login:** {user['last_login'] or 'Never'}")
                st.write(f"**Status:** {'Active' if user['is_active'] else 'Inactive'}")
            
            with col3:
                # Get user stats
                docs = db_manager.get_user_documents(user['id'])
                chats = len(db_manager.get_user_chat_history(user['id'], limit=1000))
                mcq_tests = len(db_manager.get_user_mcq_history(user['id'], limit=1000))
                
                st.metric("Documents", len(docs))
                st.metric("Chats", chats)
                st.metric("MCQ Tests", mcq_tests)
            
            # User actions
            st.divider()
            action_col1, action_col2 = st.columns(2)
            
            with action_col1:
                if user['is_active']:
                    if st.button(f"🚫 Deactivate User", key=f"deactivate_{user['id']}"):
                        # Add deactivation logic here
                        st.warning("User deactivation feature coming soon")
                else:
                    if st.button(f"✅ Activate User", key=f"activate_{user['id']}"):
                        # Add activation logic here
                        st.success("User activation feature coming soon")
            
            with action_col2:
                if st.button(f"🗑️ Delete User", key=f"delete_{user['id']}", type="secondary"):
                    st.error("⚠️ User deletion requires confirmation")


def show_api_settings():
    """API settings management"""
    st.title("🔑 API Settings")
    st.markdown("### Groq API Configuration")
    
    # Get current API key from secrets
    current_key = ""
    try:
        if hasattr(st, 'secrets') and 'GROQ_API_KEY' in st.secrets:
            current_key = st.secrets['GROQ_API_KEY']
            masked_key = current_key[:8] + "*" * 20 + current_key[-4:]
            st.success(f"✅ API Key is set: `{masked_key}`")
    except:
        st.warning("⚠️ No API key found in secrets")
    
    st.divider()
    
    # API Key update form
    with st.form("api_key_form"):
        st.subheader("Update Groq API Key")
        
        new_api_key = st.text_input(
            "New API Key",
            type="password",
            placeholder="gsk_...",
            help="Enter your Groq API key"
        )
        
        st.info("""
        **How to update:**
        1. Enter your new Groq API key above
        2. Click 'Save API Key'
        3. The key will be saved to `.streamlit/secrets.toml`
        4. Restart the application for changes to take effect
        
        **Get your API key from:** https://console.groq.com/
        """)
        
        submit = st.form_submit_button("💾 Save API Key", type="primary")
        
        if submit:
            if new_api_key and new_api_key.startswith("gsk_"):
                # Save to secrets file
                success = save_api_key(new_api_key)
                if success:
                    st.success("✅ API Key saved successfully! Please restart the app.")
                else:
                    st.error("❌ Failed to save API key")
            else:
                st.error("❌ Invalid API key format. Key should start with 'gsk_'")
    
    st.divider()
    
    # Model settings
    st.subheader("⚙️ Model Configuration")
    
    from config.settings import GROQ_MODEL, TEMPERATURE, MAX_TOKENS
    
    st.info(f"""
    **Current Settings:**
    - Model: `{GROQ_MODEL}`
    - Temperature: `{TEMPERATURE}`
    - Max Tokens: `{MAX_TOKENS}`
    
    To change these, edit `config/settings.py`
    """)


def save_api_key(api_key: str) -> bool:
    """Save API key to secrets file"""
    try:
        secrets_dir = Path(".streamlit")
        secrets_file = secrets_dir / "secrets.toml"
        
        # Ensure directory exists
        secrets_dir.mkdir(exist_ok=True)
        
        # Read existing content
        existing_content = ""
        if secrets_file.exists():
            with open(secrets_file, 'r') as f:
                existing_content = f.read()
        
        # Update or add GROQ_API_KEY
        if "GROQ_API_KEY" in existing_content:
            # Replace existing key
            import re
            updated_content = re.sub(
                r'GROQ_API_KEY\s*=\s*"[^"]*"',
                f'GROQ_API_KEY = "{api_key}"',
                existing_content
            )
        else:
            # Add new key
            updated_content = existing_content.rstrip() + f'\n\nGROQ_API_KEY = "{api_key}"\n'
        
        # Write back
        with open(secrets_file, 'w') as f:
            f.write(updated_content)
        
        return True
    except Exception as e:
        print(f"Error saving API key: {e}")
        return False


def show_system_settings():
    """System settings and information"""
    st.title("⚙️ System Settings")
    
    # Database info
    st.subheader("🗄️ Database Information")
    from config.settings import DATABASE_PATH, CHROMA_DB_PATH
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**SQLite Database:**")
        st.code(str(DATABASE_PATH))
        if DATABASE_PATH.exists():
            size = DATABASE_PATH.stat().st_size
            st.metric("Database Size", f"{size / 1024:.2f} KB")
    
    with col2:
        st.write("**ChromaDB Path:**")
        st.code(str(CHROMA_DB_PATH))
        if CHROMA_DB_PATH.exists():
            st.success("✅ ChromaDB exists")
    
    st.divider()
    
    # Application info
    st.subheader("📱 Application Information")
    
    from config.settings import APP_TITLE, CHUNK_SIZE, CHUNK_OVERLAP, TOP_K_RESULTS
    
    info_col1, info_col2 = st.columns(2)
    
    with info_col1:
        st.write("**Application:**")
        st.write(f"- Title: {APP_TITLE}")
        st.write(f"- Chunk Size: {CHUNK_SIZE}")
        st.write(f"- Chunk Overlap: {CHUNK_OVERLAP}")
    
    with info_col2:
        st.write("**RAG Settings:**")
        st.write(f"- Top K Results: {TOP_K_RESULTS}")
        from config.settings import EMBEDDING_MODEL
        st.write(f"- Embedding: {EMBEDDING_MODEL}")
    
    st.divider()
    
    # System actions
    st.subheader("🔧 System Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("✅ Cache cleared!")
    
    with col2:
        if st.button("📊 View Logs", use_container_width=True):
            st.info("📋 Log viewing feature coming soon")
    
    with col3:
        if st.button("💾 Backup DB", use_container_width=True):
            st.info("💾 Database backup feature coming soon")


def main():
    """Main admin panel entry point"""
    # Initialize session state
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    # Show login or admin interface
    if not st.session_state.admin_authenticated:
        show_admin_login()
    else:
        show_admin_interface()


if __name__ == "__main__":
    main()
