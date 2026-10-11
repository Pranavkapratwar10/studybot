"""
Admin dashboard module
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database.db_manager import DatabaseManager
from utils.helpers import format_file_size, format_timestamp


def verify_admin_password(password: str) -> bool:
    """Verify admin password"""
    admin_password = None
    
    # Try to get from secrets
    try:
        if hasattr(st, 'secrets') and 'ADMIN_PASSWORD' in st.secrets:
            admin_password = st.secrets['ADMIN_PASSWORD']
    except:
        pass
    
    # Default password if not set
    if not admin_password:
        admin_password = "admin123"
    
    return password == admin_password


def show_admin_dashboard(db_manager: DatabaseManager):
    """Display admin dashboard"""
    st.title("👨‍💼 Admin Dashboard")
    
    # Password protection
    if 'admin_authenticated' not in st.session_state:
        st.session_state.admin_authenticated = False
    
    if not st.session_state.admin_authenticated:
        st.subheader("🔒 Admin Login")
        password = st.text_input("Enter Admin Password", type="password")
        if st.button("Login"):
            if verify_admin_password(password):
                st.session_state.admin_authenticated = True
                st.success("Access granted!")
                st.rerun()
            else:
                st.error("Invalid password")
        return
    
    # Logout button
    if st.button("🚪 Logout", key="admin_logout"):
        st.session_state.admin_authenticated = False
        st.rerun()
    
    # Get statistics
    stats = db_manager.get_statistics()
    
    # Display metrics
    st.subheader("📊 System Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Users", stats['total_users'])
        st.metric("Active Users (7d)", stats['active_users'])
    
    with col2:
        st.metric("Total Documents", stats['total_documents'])
        st.metric("Docs Today", stats['documents_today'])
    
    with col3:
        st.metric("Total Chats", stats['total_chats'])
        st.metric("Chats Today", stats['chats_today'])
    
    with col4:
        avg_docs_per_user = stats['total_documents'] / max(stats['total_users'], 1)
        st.metric("Avg Docs/User", f"{avg_docs_per_user:.1f}")
        avg_chats_per_user = stats['total_chats'] / max(stats['total_users'], 1)
        st.metric("Avg Chats/User", f"{avg_chats_per_user:.1f}")
    
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["👥 Users", "📄 Documents", "💬 Chat Activity"])
    
    with tab1:
        show_users_tab(db_manager)
    
    with tab2:
        show_documents_tab(db_manager)
    
    with tab3:
        show_chat_activity_tab(db_manager)


def show_users_tab(db_manager: DatabaseManager):
    """Display users information"""
    st.subheader("Registered Users")
    
    users = db_manager.get_all_users()
    
    if not users:
        st.info("No users registered yet")
        return
    
    # Create DataFrame
    df = pd.DataFrame(users)
    df['created_at'] = pd.to_datetime(df['created_at'])
    df['last_login'] = pd.to_datetime(df['last_login'])
    
    # Display table
    st.dataframe(
        df[['id', 'username', 'email', 'created_at', 'last_login', 'is_active']],
        use_container_width=True,
        hide_index=True
    )
    
    # User registration chart
    if len(df) > 0:
        fig = px.histogram(
            df, x='created_at',
            title='User Registrations Over Time',
            labels={'created_at': 'Registration Date'}
        )
        st.plotly_chart(fig, use_container_width=True)



def show_documents_tab(db_manager: DatabaseManager):
    """Display documents information"""
    st.subheader("All Documents")
    
    documents = db_manager.get_all_documents()
    
    if not documents:
        st.info("No documents uploaded yet")
        return
    
    # Display documents
    for doc in documents:
        with st.expander(f"📄 {doc['filename']} (by {doc['username']})"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**User:** {doc['username']}")
                st.write(f"**File Type:** {doc['file_type']}")
                st.write(f"**Size:** {format_file_size(doc['file_size'])}")
            with col2:
                st.write(f"**Chunks:** {doc['chunks_count']}")
                st.write(f"**Uploaded:** {format_timestamp(doc['upload_date'])}")
    
    # Document statistics
    df = pd.DataFrame(documents)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Documents by type
        type_counts = df['file_type'].value_counts()
        fig = px.pie(
            values=type_counts.values,
            names=type_counts.index,
            title='Documents by Type'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Documents by user
        user_counts = df['username'].value_counts().head(10)
        fig = px.bar(
            x=user_counts.values,
            y=user_counts.index,
            orientation='h',
            title='Top 10 Users by Document Count',
            labels={'x': 'Documents', 'y': 'User'}
        )
        st.plotly_chart(fig, use_container_width=True)


def show_chat_activity_tab(db_manager: DatabaseManager):
    """Display chat activity information"""
    st.subheader("Chat Activity")
    st.info("📊 Detailed chat analytics coming soon!")
    
    stats = db_manager.get_statistics()
    st.metric("Total Chats", stats['total_chats'])
    st.metric("Chats Today", stats['chats_today'])
