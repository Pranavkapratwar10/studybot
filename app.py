"""
AI Study Assistant - Main Streamlit Application
"""
import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from config.settings import APP_TITLE, APP_ICON, initialize_directories, UPLOAD_DIR
from database.db_manager import DatabaseManager
from auth.authentication import AuthManager
from rag.document_processor import DocumentProcessor
from rag.rag_pipeline import RAGPipeline
from utils.helpers import (
    validate_file_upload, save_uploaded_file, format_file_size,
    format_timestamp, get_exam_mode_emoji
)

# Initialize directories
initialize_directories()

# Page configuration
st.set_page_config(
    page_title="📚 AI Study Assistant - StudyBot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize components
@st.cache_resource
def init_components():
    """Initialize database, auth, and RAG components"""
    db = DatabaseManager()
    auth = AuthManager(db)
    doc_processor = DocumentProcessor()
    rag = RAGPipeline()
    return db, auth, doc_processor, rag

db_manager, auth_manager, doc_processor, rag_pipeline = init_components()

# Initialize session state
auth_manager.init_session_state()

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_mode' not in st.session_state:
    st.session_state.current_mode = "viva"


def show_login_page():
    """Display login/registration page with beautiful centered cards"""
    
    # Custom CSS for centered cards
    st.markdown("""
        <style>
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Center content */
        .main .block-container {
            max-width: 500px;
            padding-top: 3rem;
            padding-bottom: 3rem;
        }
        
        /* Card styling */
        .auth-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            margin-bottom: 2rem;
        }
        
        .auth-title {
            color: white;
            text-align: center;
            font-size: 2.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        
        .auth-subtitle {
            color: rgba(255,255,255,0.9);
            text-align: center;
            font-size: 1.1rem;
            margin-bottom: 2rem;
        }
        
        /* Form card */
        .form-card {
            background: rgba(30, 30, 40, 0.95);
            padding: 2.5rem;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        /* Remove white strip - Tab container background */
        .stTabs {
            background: transparent !important;
        }
        
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            justify-content: center;
            background: transparent !important;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            background-color: transparent !important;
            border: none;
            color: rgba(255,255,255,0.6);
            font-size: 1.1rem;
            font-weight: 600;
        }
        
        .stTabs [aria-selected="true"] {
            color: white;
            border-bottom: 3px solid white;
            background-color: transparent !important;
        }
        
        /* Tab panel background */
        .stTabs [data-baseweb="tab-panel"] {
            background: transparent !important;
            padding-top: 2rem;
        }
        
        /* Form headings */
        .form-card h3 {
            color: white;
            margin-bottom: 0.5rem;
        }
        
        .form-card p {
            color: rgba(255,255,255,0.7);
        }
        
        /* Input styling */
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 2px solid rgba(255,255,255,0.1);
            padding: 0.75rem;
            font-size: 1rem;
            background-color: rgba(255,255,255,0.05);
            color: white;
        }
        
        .stTextInput > div > div > input:focus {
            border-color: #667eea;
            box-shadow: 0 0 0 2px rgba(102,126,234,0.3);
            background-color: rgba(255,255,255,0.08);
        }
        
        .stTextInput > div > div > input::placeholder {
            color: rgba(255,255,255,0.4);
        }
        
        .stTextInput label {
            color: rgba(255,255,255,0.9) !important;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.75rem 2rem;
            font-size: 1.1rem;
            font-weight: 600;
            box-shadow: 0 4px 15px rgba(102,126,234,0.4);
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102,126,234,0.6);
        }
        
        /* Success/Error messages */
        .stSuccess, .stError, .stInfo {
            border-radius: 10px;
            padding: 1rem;
            margin-top: 1rem;
            background-color: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Header Card
    st.markdown("""
        <div class="auth-card">
            <div class="auth-title">📚 StudyBot</div>
            <div class="auth-subtitle">Your AI-Powered Study Companion</div>
        </div>
    """, unsafe_allow_html=True)
    
    # Form Card
    st.markdown('<div class="form-card">', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "✨ Register"])
    
    with tab1:
        st.markdown("### Welcome Back!")
        st.markdown("Login to access your study materials")
        st.markdown("")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            st.markdown("")
            submit = st.form_submit_button("🚀 Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("⚠️ Please enter both username and password")
                else:
                    success, message, user = auth_manager.login_user(username, password)
                    if success:
                        st.session_state.user_id = user['id']
                        st.session_state.username = user['username']
                        st.session_state.user = user
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    with tab2:
        st.markdown("### Create Account")
        st.markdown("Join StudyBot and start learning smarter!")
        st.markdown("")
        
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_username", placeholder="Choose a username")
            new_email = st.text_input("Email", key="reg_email", placeholder="your.email@example.com")
            new_password = st.text_input("Password", type="password", key="reg_password", placeholder="Create a strong password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm", placeholder="Re-enter your password")
            
            st.markdown("")
            submit = st.form_submit_button("🎉 Create Account", use_container_width=True)
            
            if submit:
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.error("⚠️ Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("⚠️ Passwords do not match")
                elif len(new_password) < 6:
                    st.error("⚠️ Password must be at least 6 characters long")
                else:
                    success, message = auth_manager.register_user(
                        new_username, new_email, new_password
                    )
                    if success:
                        st.success(f"✅ {message}")
                        st.balloons()
                        st.info("👉 Please switch to the Login tab to sign in")
                    else:
                        st.error(f"❌ {message}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("")
    st.markdown("")
    st.markdown("""
        <div style='text-align: center; color: #888; font-size: 0.9rem;'>
            <p>Powered by AI • Secure • Free to Use</p>
        </div>
    """, unsafe_allow_html=True)


def show_document_upload():
    """Document upload section"""
    st.subheader("📤 Upload Study Materials")
    
    uploaded_files = st.file_uploader(
        "Upload your study materials (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload multiple documents to create your study database"
    )
    
    if uploaded_files:
        if st.button("Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                user_id = st.session_state.user_id
                success_count = 0
                total_chunks = 0
                
                for uploaded_file in uploaded_files:
                    # Validate file
                    is_valid, message = validate_file_upload(uploaded_file)
                    if not is_valid:
                        st.error(f"{uploaded_file.name}: {message}")
                        continue
                    
                    # Save file
                    success, file_path, save_msg = save_uploaded_file(
                        uploaded_file, user_id, UPLOAD_DIR
                    )
                    
                    if not success:
                        st.error(f"{uploaded_file.name}: {save_msg}")
                        continue
                    
                    try:
                        # Process document
                        chunks = doc_processor.process_document(
                            file_path, uploaded_file.name, user_id
                        )
                        
                        # Add to vector store
                        chunks_added = rag_pipeline.add_documents_to_store(user_id, chunks)
                        
                        # Save to database
                        db_manager.add_document(
                            user_id=user_id,
                            filename=uploaded_file.name,
                            file_path=file_path,
                            file_size=uploaded_file.size,
                            file_type=Path(uploaded_file.name).suffix,
                            chunks_count=chunks_added
                        )
                        
                        success_count += 1
                        total_chunks += chunks_added
                        st.success(f"✅ {uploaded_file.name}: {chunks_added} chunks processed")
                    
                    except Exception as e:
                        st.error(f"❌ {uploaded_file.name}: {str(e)}")
                
                if success_count > 0:
                    st.success(f"🎉 Successfully processed {success_count} documents with {total_chunks} total chunks!")
                    st.rerun()


def show_my_documents():
    """Display user's uploaded documents"""
    st.subheader("📚 My Documents")
    
    user_id = st.session_state.user_id
    documents = db_manager.get_user_documents(user_id)
    
    if not documents:
        st.info("No documents uploaded yet. Upload your study materials to get started!")
        return
    
    # Display documents in a table-like format
    for doc in documents:
        with st.expander(f"📄 {doc['filename']}"):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Type:** {doc['file_type']}")
                st.write(f"**Size:** {format_file_size(doc['file_size'])}")
            with col2:
                st.write(f"**Chunks:** {doc['chunks_count']}")
                st.write(f"**Uploaded:** {format_timestamp(doc['upload_date'])}")
            with col3:
                if st.button(f"🗑️ Delete", key=f"del_{doc['id']}"):
                    if db_manager.delete_document(doc['id'], user_id):
                        st.success("Document deleted!")
                        st.rerun()
    
    # Show total stats
    total_docs = len(documents)
    total_chunks = sum(doc['chunks_count'] for doc in documents)
    st.info(f"📊 Total: {total_docs} documents, {total_chunks} chunks")


def show_chat_interface():
    """Main chat interface with integrated document upload"""
    st.subheader("💬 Ask Questions")
    
    # Document upload section (collapsed by default)
    with st.expander("📤 Upload Study Materials", expanded=False):
        uploaded_files = st.file_uploader(
            "Upload your study materials (PDF, DOCX, TXT)",
            type=['pdf', 'docx', 'txt'],
            accept_multiple_files=True,
            help="Upload multiple documents to create your study database",
            key="chat_upload"
        )
        
        if uploaded_files:
            if st.button("Process Documents", type="primary", key="process_docs"):
                with st.spinner("Processing documents..."):
                    user_id = st.session_state.user_id
                    success_count = 0
                    total_chunks = 0
                    
                    for uploaded_file in uploaded_files:
                        # Validate file
                        is_valid, message = validate_file_upload(uploaded_file)
                        if not is_valid:
                            st.error(f"{uploaded_file.name}: {message}")
                            continue
                        
                        # Save file
                        success, file_path, save_msg = save_uploaded_file(
                            uploaded_file, user_id, UPLOAD_DIR
                        )
                        
                        if not success:
                            st.error(f"{uploaded_file.name}: {save_msg}")
                            continue
                        
                        try:
                            # Process document
                            chunks = doc_processor.process_document(
                                file_path, uploaded_file.name, user_id
                            )
                            
                            # Add to vector store
                            chunks_added = rag_pipeline.add_documents_to_store(user_id, chunks)
                            
                            # Save to database
                            db_manager.add_document(
                                user_id=user_id,
                                filename=uploaded_file.name,
                                file_path=file_path,
                                file_size=uploaded_file.size,
                                file_type=Path(uploaded_file.name).suffix,
                                chunks_count=chunks_added
                            )
                            
                            success_count += 1
                            total_chunks += chunks_added
                            st.success(f"✅ {uploaded_file.name}: {chunks_added} chunks processed")
                        
                        except Exception as e:
                            st.error(f"❌ {uploaded_file.name}: {str(e)}")
                    
                    if success_count > 0:
                        st.success(f"🎉 Successfully processed {success_count} documents with {total_chunks} total chunks!")
                        st.rerun()
    
    st.divider()
    
    # Exam mode selector
    col1, col2 = st.columns([3, 1])
    with col1:
        exam_mode = st.selectbox(
            "Select Exam Mode",
            options=["viva", "short_answer", "long_answer", "revision"],
            format_func=lambda x: f"{get_exam_mode_emoji(x)} {x.replace('_', ' ').title()}",
            key="exam_mode_selector"
        )
        st.session_state.current_mode = exam_mode
    
    with col2:
        st.write("")
        st.write("")
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    # Display chat history
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message and message["sources"]:
                st.caption(f"📚 Sources: {', '.join(message['sources'])}")
    
    # Chat input
    if question := st.chat_input("Ask a question about your study materials..."):
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": question})
        
        with st.chat_message("user"):
            st.markdown(question)
        
        # Generate answer
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                user_id = st.session_state.user_id
                
                # Query RAG pipeline
                answer, sources, used_context = rag_pipeline.query(
                    user_id, question, st.session_state.current_mode
                )
                
                # Display answer
                st.markdown(answer)
                if sources:
                    st.caption(f"📚 Sources: {', '.join(sources)}")
                
                # Save to database
                db_manager.add_chat_message(
                    user_id, question, answer, 
                    st.session_state.current_mode, sources
                )
                
                # Add to session
                st.session_state.chat_history.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources
                })



def show_chat_history_page():
    """Display chat history"""
    st.subheader("📜 Chat History")
    
    user_id = st.session_state.user_id
    history = db_manager.get_user_chat_history(user_id, limit=50)
    
    if not history:
        st.info("No chat history yet. Start asking questions!")
        return
    
    # Filter by exam mode
    modes = ["All"] + list(set(h['exam_mode'] for h in history if h['exam_mode']))
    selected_mode = st.selectbox("Filter by Exam Mode", modes)
    
    # Display history
    for item in history:
        if selected_mode != "All" and item['exam_mode'] != selected_mode:
            continue
        
        with st.expander(f"{get_exam_mode_emoji(item['exam_mode'])} {item['question'][:100]}..."):
            st.write(f"**Mode:** {item['exam_mode']}")
            st.write(f"**Time:** {format_timestamp(item['timestamp'])}")
            st.write(f"**Question:** {item['question']}")
            st.write(f"**Answer:** {item['answer']}")
            if item['sources']:
                st.write(f"**Sources:** {', '.join(item['sources'])}")


def show_sidebar():
    """Display sidebar navigation"""
    with st.sidebar:
        st.title("📚 AI Study Assistant - StudyBot")
        
        # Check if admin
        is_admin = st.session_state.get('user', {}).get('is_admin', False)
        
        if is_admin:
            st.write("🔐 **Admin Mode**")
        else:
            st.write(f"👤 Welcome, **{st.session_state.username}**!")
        
        st.divider()
        
        # Navigation - use clean keys with format_func for display
        if is_admin:
            page = st.radio(
                "Navigation",
                ["admin_dashboard", "user_stats"],
                format_func=lambda x: {"admin_dashboard": "🔐 Admin Dashboard", "user_stats": "👥 User Stats"}[x],
                label_visibility="collapsed"
            )
        else:
            page = st.radio(
                "Navigation",
                ["chat", "mcq", "written", "documents", "history"],
                format_func=lambda x: {
                    "chat": "💬 Chat",
                    "mcq": "📝 MCQ Generator",
                    "written": "✍️ Written Practice",
                    "documents": "📚 My Documents",
                    "history": "📜 History"
                }[x],
                label_visibility="collapsed"
            )
        
        st.divider()
        
        # Quick stats (only for regular users)
        if not is_admin:
            user_id = st.session_state.user_id
            docs = db_manager.get_user_documents(user_id)
            chunks = sum(doc['chunks_count'] for doc in docs)
            
            st.metric("My Documents", len(docs))
            st.metric("Total Chunks", chunks)
            
            st.divider()
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True):
            auth_manager.logout_user()
            st.rerun()
        
        return page


def main():
    """Main application"""
    # Check authentication
    if not auth_manager.is_authenticated():
        show_login_page()
        return
    
    # Show sidebar and get selected page
    page = show_sidebar()
    
    # Check if admin
    is_admin = st.session_state.get('user', {}).get('is_admin', False)
    
    # Display selected page
    if is_admin:
        # Admin pages - use clean string keys
        if page == "admin_dashboard":
            from pages.admin_dashboard import show_admin_dashboard
            show_admin_dashboard(db_manager)
        elif page == "user_stats":
            show_admin_user_stats()
    else:
        # Regular user pages - use clean string keys
        if page == "chat":
            show_chat_interface()
        elif page == "mcq":
            from pages.mcq_page import show_mcq_page
            show_mcq_page(db_manager)
        elif page == "written":
            from pages.written_page import show_written_page
            show_written_page(db_manager)
        elif page == "documents":
            show_my_documents()
        elif page == "history":
            show_chat_history_page()


def show_admin_user_stats():
    """Show admin statistics about users"""
    st.title("👥 User Statistics")
    st.info("View all user activity and statistics here")
    # This can be expanded with more details


if __name__ == "__main__":
    main()
