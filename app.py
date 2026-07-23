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
    page_title=APP_TITLE,
    page_icon=APP_ICON,
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
    """Display login/registration page"""
    st.title(f"{APP_ICON} {APP_TITLE}")
    st.markdown("### Your AI-Powered Study Companion")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("Please enter both username and password")
                else:
                    success, message, user = auth_manager.login_user(username, password)
                    if success:
                        st.session_state.user_id = user['id']
                        st.session_state.username = user['username']
                        st.session_state.user = user
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("register_form"):
            new_username = st.text_input("Username", key="reg_username")
            new_email = st.text_input("Email", key="reg_email")
            new_password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="reg_confirm")
            submit = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                if not all([new_username, new_email, new_password, confirm_password]):
                    st.error("Please fill in all fields")
                elif new_password != confirm_password:
                    st.error("Passwords do not match")
                else:
                    success, message = auth_manager.register_user(
                        new_username, new_email, new_password
                    )
                    if success:
                        st.success(message)
                    else:
                        st.error(message)


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
    """Main chat interface"""
    st.subheader("💬 Ask Questions")
    
    # Exam mode selector (MCQ removed - use dedicated MCQ Generator page)
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
        st.title(f"{APP_ICON} {APP_TITLE}")
        st.write(f"👤 Welcome, **{st.session_state.username}**!")
        
        st.divider()
        
        # Navigation
        page = st.radio(
            "Navigation",
            ["💬 Chat", "📝 MCQ Generator", "📤 Upload", "📚 My Documents", "📜 History"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Quick stats
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
    
    # Display selected page
    if page == "💬 Chat":
        show_chat_interface()
    elif page == "📝 MCQ Generator":
        from pages.mcq_page import show_mcq_page
        show_mcq_page(db_manager)
    elif page == "📤 Upload":
        show_document_upload()
    elif page == "📚 My Documents":
        show_my_documents()
    elif page == "📜 History":
        show_chat_history_page()


if __name__ == "__main__":
    main()
