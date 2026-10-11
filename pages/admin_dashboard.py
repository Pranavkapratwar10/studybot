"""
Admin Dashboard - Special admin-only features
"""
import streamlit as st
import os
from pathlib import Path
from database.db_manager import DatabaseManager


def show_admin_dashboard(db_manager: DatabaseManager):
    """Display admin dashboard"""
    
    st.title("🔐 Admin Dashboard")
    
    # Check if user is admin
    user = st.session_state.get('user', {})
    is_admin = user.get('is_admin', False)
    
    if not is_admin:
        st.error("⛔ Access Denied - Admin Only")
        st.write("Debug - User object:", user)
        st.write("Debug - Is Admin:", is_admin)
        return
    
    st.success("✅ Welcome Admin!")
    st.markdown("### System Administration & Management")
    
    # Simple tabs
    tab1, tab2, tab3 = st.tabs(["👥 All Users", "🔑 API Key", "📊 Stats"])
    
    with tab1:
        st.subheader("👥 All Registered Users")
        
        # Fetch users directly
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT id, username, email, created_at, last_login, is_active
                FROM users
                ORDER BY created_at DESC
            """)
            users = cursor.fetchall()
            
            if not users:
                st.warning("No users found in database")
            else:
                st.success(f"Found {len(users)} users")
                
                # Display in table format
                for user in users:
                    user_dict = dict(user)
                    
                    with st.expander(f"👤 {user_dict['username']}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**ID:** {user_dict['id']}")
                            st.write(f"**Username:** {user_dict['username']}")
                            st.write(f"**Email:** {user_dict['email']}")
                        
                        with col2:
                            st.write(f"**Status:** {'✅ Active' if user_dict['is_active'] else '❌ Inactive'}")
                            st.write(f"**Joined:** {user_dict['created_at'][:16] if user_dict['created_at'] else 'N/A'}")
                            st.write(f"**Last Login:** {user_dict['last_login'][:16] if user_dict['last_login'] else 'Never'}")
                        
                        # Get activity stats
                        cursor.execute("SELECT COUNT(*) as count FROM documents WHERE user_id = ?", (user_dict['id'],))
                        docs = cursor.fetchone()['count']
                        
                        cursor.execute("SELECT COUNT(*) as count FROM chat_history WHERE user_id = ?", (user_dict['id'],))
                        chats = cursor.fetchone()['count']
                        
                        cursor.execute("SELECT COUNT(*) as count FROM mcq_tests WHERE user_id = ?", (user_dict['id'],))
                        mcqs = cursor.fetchone()['count']
                        
                        cursor.execute("SELECT COUNT(*) as count FROM written_tests WHERE user_id = ?", (user_dict['id'],))
                        written = cursor.fetchone()['count']
                        
                        st.markdown("**Activity:**")
                        col1, col2, col3, col4 = st.columns(4)
                        col1.metric("Docs", docs)
                        col2.metric("Chats", chats)
                        col3.metric("MCQs", mcqs)
                        col4.metric("Written", written)
        
        except Exception as e:
            st.error(f"Database error: {e}")
        finally:
            conn.close()
    
    with tab2:
        st.subheader("🔑 Groq API Key Management")
        
        # Load current key
        secrets_path = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"
        
        try:
            import toml
            if secrets_path.exists():
                secrets = toml.load(secrets_path)
                current_key = secrets.get('GROQ_API_KEY', '')
                
                if current_key:
                    masked = current_key[:15] + "..." + current_key[-15:]
                    st.info(f"**Current Key:** `{masked}`")
                else:
                    st.warning("No API key set")
            else:
                st.warning("Secrets file not found")
                current_key = ''
        except Exception as e:
            st.error(f"Error reading secrets: {e}")
            current_key = ''
        
        st.divider()
        
        # Update form
        with st.form("api_key_form"):
            st.markdown("### Update API Key")
            
            new_key = st.text_input(
                "New Groq API Key",
                placeholder="gsk_...",
                type="password",
                help="Get from https://console.groq.com"
            )
            
            submitted = st.form_submit_button("💾 Save New API Key", use_container_width=True)
            
            if submitted:
                if not new_key:
                    st.error("Please enter an API key")
                elif not new_key.startswith("gsk_"):
                    st.error("Invalid format (should start with gsk_)")
                else:
                    # Test it
                    with st.spinner("Testing API key..."):
                        try:
                            from groq import Groq
                            test_client = Groq(api_key=new_key)
                            
                            response = test_client.chat.completions.create(
                                model="openai/gpt-oss-120b",
                                messages=[{"role": "user", "content": "test"}],
                                max_tokens=3
                            )
                            
                            # Works! Save it
                            import toml
                            
                            if secrets_path.exists():
                                secrets = toml.load(secrets_path)
                            else:
                                secrets = {}
                            
                            secrets['GROQ_API_KEY'] = new_key
                            
                            with open(secrets_path, 'w') as f:
                                toml.dump(secrets, f)
                            
                            os.environ['GROQ_API_KEY'] = new_key
                            
                            st.success("✅ API key saved and verified!")
                            st.balloons()
                            st.rerun()
                        
                        except Exception as e:
                            st.error(f"❌ API test failed: {str(e)[:150]}")
    
    with tab3:
        st.subheader("📊 System Statistics")
        
        conn = db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get counts
            cursor.execute("SELECT COUNT(*) as count FROM users")
            user_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM documents")
            doc_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM chat_history")
            chat_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM mcq_tests")
            mcq_count = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM written_tests")
            written_count = cursor.fetchone()['count']
            
            # Display
            col1, col2, col3 = st.columns(3)
            col1.metric("👥 Total Users", user_count)
            col2.metric("📚 Documents", doc_count)
            col3.metric("💬 Chats", chat_count)
            
            col1, col2 = st.columns(2)
            col1.metric("📝 MCQ Tests", mcq_count)
            col2.metric("✍️ Written Tests", written_count)
        
        except Exception as e:
            st.error(f"Error loading stats: {e}")
        finally:
            conn.close()


def show_users_management(db_manager: DatabaseManager):
    """Show all users and management options"""
    st.subheader("👥 User Management")
    
    # Get all users
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, username, email, created_at, last_login, is_active
            FROM users
            ORDER BY created_at DESC
        """)
        users = cursor.fetchall()
        
        if not users:
            st.info("No users registered yet")
            return
        
        st.markdown(f"**Total Users:** {len(users)}")
        st.divider()
        
        # Display users
        for user in users:
            user_dict = dict(user)
            
            with st.expander(f"👤 {user_dict['username']} ({user_dict['email']})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**User ID:** {user_dict['id']}")
                    st.write(f"**Username:** {user_dict['username']}")
                
                with col2:
                    st.write(f"**Email:** {user_dict['email']}")
                    st.write(f"**Status:** {'✅ Active' if user_dict['is_active'] else '❌ Inactive'}")
                
                with col3:
                    st.write(f"**Joined:** {user_dict['created_at'][:16] if user_dict['created_at'] else 'N/A'}")
                    st.write(f"**Last Login:** {user_dict['last_login'][:16] if user_dict['last_login'] else 'Never'}")
                
                # Get user stats
                st.markdown("---")
                st.markdown("**User Activity:**")
                
                # Documents
                cursor.execute("SELECT COUNT(*) as count FROM documents WHERE user_id = ?", (user_dict['id'],))
                doc_count = cursor.fetchone()['count']
                
                # Chat history
                cursor.execute("SELECT COUNT(*) as count FROM chat_history WHERE user_id = ?", (user_dict['id'],))
                chat_count = cursor.fetchone()['count']
                
                # MCQ tests
                cursor.execute("SELECT COUNT(*) as count FROM mcq_tests WHERE user_id = ?", (user_dict['id'],))
                mcq_count = cursor.fetchone()['count']
                
                # Written tests
                cursor.execute("SELECT COUNT(*) as count FROM written_tests WHERE user_id = ?", (user_dict['id'],))
                written_count = cursor.fetchone()['count']
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Documents", doc_count)
                col2.metric("Chats", chat_count)
                col3.metric("MCQ Tests", mcq_count)
                col4.metric("Written Tests", written_count)
                
                # Actions
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    if user_dict['is_active']:
                        if st.button(f"🚫 Deactivate User", key=f"deactivate_{user_dict['id']}"):
                            cursor.execute("UPDATE users SET is_active = 0 WHERE id = ?", (user_dict['id'],))
                            conn.commit()
                            st.success("User deactivated!")
                            st.rerun()
                    else:
                        if st.button(f"✅ Activate User", key=f"activate_{user_dict['id']}"):
                            cursor.execute("UPDATE users SET is_active = 1 WHERE id = ?", (user_dict['id'],))
                            conn.commit()
                            st.success("User activated!")
                            st.rerun()
                
                with col2:
                    if st.button(f"🗑️ Delete User", key=f"delete_{user_dict['id']}", type="secondary"):
                        if st.session_state.get(f"confirm_delete_{user_dict['id']}", False):
                            cursor.execute("DELETE FROM users WHERE id = ?", (user_dict['id'],))
                            conn.commit()
                            st.success("User deleted!")
                            st.rerun()
                        else:
                            st.session_state[f"confirm_delete_{user_dict['id']}"] = True
                            st.warning("⚠️ Click again to confirm deletion")
    
    finally:
        conn.close()


def show_api_settings():
    """Manage API settings"""
    st.subheader("🔑 API Key Management")
    
    # Load current API key
    secrets_path = Path(__file__).parent.parent / ".streamlit" / "secrets.toml"
    
    try:
        import toml
        if secrets_path.exists():
            secrets = toml.load(secrets_path)
            current_key = secrets.get('GROQ_API_KEY', '')
        else:
            current_key = ''
    except:
        current_key = ''
    
    # Display current key (masked)
    if current_key:
        masked_key = current_key[:10] + "..." + current_key[-10:] if len(current_key) > 20 else current_key
        st.info(f"**Current API Key:** `{masked_key}`")
    else:
        st.warning("⚠️ No API key configured!")
    
    st.divider()
    
    # Update API key
    st.markdown("### Update API Key")
    
    with st.form("update_api_key"):
        new_api_key = st.text_input(
            "New Groq API Key",
            type="password",
            placeholder="gsk_...",
            help="Get your free API key from https://console.groq.com"
        )
        
        st.markdown("")
        submit = st.form_submit_button("💾 Save API Key", use_container_width=True)
        
        if submit:
            if not new_api_key:
                st.error("⚠️ Please enter an API key")
            elif not new_api_key.startswith("gsk_"):
                st.error("⚠️ Invalid API key format (should start with 'gsk_')")
            else:
                # Test the API key
                with st.spinner("Testing API key..."):
                    try:
                        from groq import Groq
                        client = Groq(api_key=new_api_key)
                        
                        # Quick test
                        response = client.chat.completions.create(
                            model="openai/gpt-oss-120b",
                            messages=[{"role": "user", "content": "Hi"}],
                            max_tokens=5
                        )
                        
                        # API key works, save it
                        try:
                            import toml
                            
                            # Read existing secrets
                            if secrets_path.exists():
                                secrets = toml.load(secrets_path)
                            else:
                                secrets = {}
                            
                            # Update API key
                            secrets['GROQ_API_KEY'] = new_api_key
                            
                            # Write back
                            with open(secrets_path, 'w') as f:
                                toml.dump(secrets, f)
                            
                            # Update environment variable
                            os.environ['GROQ_API_KEY'] = new_api_key
                            
                            st.success("✅ API key saved and verified!")
                            st.info("💡 The new key will be used immediately")
                            st.balloons()
                            
                        except Exception as e:
                            st.error(f"❌ Error saving API key: {e}")
                    
                    except Exception as e:
                        st.error(f"❌ API key test failed: {str(e)[:100]}")
                        st.warning("The key may be invalid or the API service is unavailable")


def show_statistics(db_manager: DatabaseManager):
    """Show system statistics"""
    st.subheader("📊 System Statistics")
    
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    try:
        # Overall stats
        col1, col2, col3, col4 = st.columns(4)
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        col1.metric("👥 Total Users", total_users)
        
        # Total documents
        cursor.execute("SELECT COUNT(*) as count FROM documents")
        total_docs = cursor.fetchone()['count']
        col2.metric("📚 Documents", total_docs)
        
        # Total chats
        cursor.execute("SELECT COUNT(*) as count FROM chat_history")
        total_chats = cursor.fetchone()['count']
        col3.metric("💬 Chat Messages", total_chats)
        
        # Total tests
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM mcq_tests) + 
                (SELECT COUNT(*) FROM written_tests) as total
        """)
        total_tests = cursor.fetchone()['total']
        col4.metric("📝 Total Tests", total_tests)
        
        st.divider()
        
        # Recent activity
        st.markdown("### 📈 Recent Activity")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Recent Users:**")
            cursor.execute("""
                SELECT username, created_at 
                FROM users 
                ORDER BY created_at DESC 
                LIMIT 5
            """)
            recent_users = cursor.fetchall()
            for user in recent_users:
                st.write(f"• {user['username']} - {user['created_at'][:16]}")
        
        with col2:
            st.markdown("**Recent Activity:**")
            cursor.execute("""
                SELECT username, last_login 
                FROM users 
                WHERE last_login IS NOT NULL
                ORDER BY last_login DESC 
                LIMIT 5
            """)
            recent_logins = cursor.fetchall()
            for user in recent_logins:
                st.write(f"• {user['username']} - {user['last_login'][:16]}")
    
    finally:
        conn.close()


def show_system_management(db_manager: DatabaseManager):
    """System management tools"""
    st.subheader("⚙️ System Management")
    
    # Database info
    st.markdown("### 💾 Database")
    
    from config.settings import DATABASE_PATH, CHROMA_DB_PATH
    
    if DATABASE_PATH.exists():
        size = DATABASE_PATH.stat().st_size
        st.info(f"**Database Size:** {size / 1024:.2f} KB")
        st.info(f"**Location:** {DATABASE_PATH}")
    
    if CHROMA_DB_PATH.exists():
        st.info(f"**Vector DB:** ChromaDB at {CHROMA_DB_PATH}")
    
    st.divider()
    
    # Cache management
    st.markdown("### 🗑️ Cache Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Clear Streamlit Cache", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("✅ Cache cleared!")
    
    with col2:
        if st.button("🔄 Restart App", use_container_width=True):
            st.info("💡 Restart the app manually from terminal")
    
    st.divider()
    
    # System info
    st.markdown("### 🖥️ System Information")
    
    import sys
    from config.settings import GROQ_MODEL, EMBEDDING_MODEL
    
    st.write(f"**Python Version:** {sys.version.split()[0]}")
    st.write(f"**LLM Model:** {GROQ_MODEL}")
    st.write(f"**Embedding Model:** {EMBEDDING_MODEL}")
