"""
Viva Practice Page - Interactive viva-voce preparation
"""
import streamlit as st
import json
from pathlib import Path
from typing import List, Dict

from viva.viva_generator import VivaGenerator
from rag.document_processor import DocumentProcessor
from database.db_manager import DatabaseManager
from utils.helpers import save_uploaded_file, validate_file_upload
from config.settings import UPLOAD_DIR


def show_viva_page(db_manager: DatabaseManager):
    """Display Viva Practice page"""
    st.title("🗣️ Viva Practice")
    st.markdown("Practice viva-voce questions interactively! Upload a document and answer questions one by one.")
    
    # Initialize session state
    if 'viva_test_id' not in st.session_state:
        st.session_state.viva_test_id = None
    if 'viva_questions' not in st.session_state:
        st.session_state.viva_questions = []
    if 'viva_user_answers' not in st.session_state:
        st.session_state.viva_user_answers = {}
    if 'viva_current_question' not in st.session_state:
        st.session_state.viva_current_question = 0
    if 'viva_show_results' not in st.session_state:
        st.session_state.viva_show_results = False
    
    # Tabs
    tab1, tab2 = st.tabs(["📤 Practice Viva", "📊 Viva History"])
    
    with tab1:
        show_viva_generator(db_manager)
    
    with tab2:
        show_viva_history(db_manager)


def show_viva_generator(db_manager: DatabaseManager):
    """Viva generation interface"""
    
    # Check if already in a test
    if st.session_state.viva_questions and not st.session_state.viva_show_results:
        display_viva_question()
        return
    
    # Show results if test is complete
    if st.session_state.viva_show_results:
        display_viva_results(db_manager)
        return
    
    # File upload section
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF, DOCX, or TXT file",
        type=['pdf', 'docx', 'txt'],
        help="Upload your study material for viva practice",
        key="viva_file_upload"
    )
    
    # Settings
    col1, col2 = st.columns(2)
    
    with col1:
        num_questions = st.slider(
            "Number of Questions",
            min_value=5,
            max_value=20,
            value=10,
            step=5
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty Level",
            options=["easy", "medium", "hard"],
            index=1
        )
    
    st.info("💡 **Tip:** Answer each question in detail. The AI will evaluate your understanding based on your responses.")
    
    # Generate button
    if st.button("🚀 Start Viva Practice", type="primary", disabled=uploaded_file is None):
        if uploaded_file:
            with st.spinner("Generating viva questions... This may take a moment."):
                success = generate_viva_from_file(
                    uploaded_file,
                    num_questions,
                    difficulty,
                    db_manager
                )
                
                if success:
                    st.success(f"✅ Generated {len(st.session_state.viva_questions)} viva questions!")
                    st.rerun()
                else:
                    st.error("Failed to generate viva questions. Please try again.")


def generate_viva_from_file(uploaded_file, num_questions: int, 
                            difficulty: str, db_manager: DatabaseManager) -> bool:
    """Generate viva questions from uploaded file"""
    try:
        user_id = st.session_state.user_id
        
        # Validate file
        is_valid, message = validate_file_upload(uploaded_file)
        if not is_valid:
            st.error(message)
            return False
        
        # Check if file already exists
        existing_doc = db_manager.get_document_by_filename(user_id, uploaded_file.name)
        
        if existing_doc:
            st.info(f"📄 Document '{uploaded_file.name}' already exists. Using existing file to save space!")
            file_path = existing_doc['file_path']
        else:
            # Save new file
            success, file_path, save_msg = save_uploaded_file(
                uploaded_file, user_id, UPLOAD_DIR
            )
            
            if not success:
                st.error(save_msg)
                return False
        
        # Extract text from document
        doc_processor = DocumentProcessor()
        text = doc_processor.extract_text(file_path)
        
        if not text or len(text.strip()) < 100:
            st.error("Could not extract sufficient text from the document.")
            return False
        
        # Generate viva questions
        viva_generator = VivaGenerator()
        questions = viva_generator.generate_viva_questions(text, num_questions, difficulty)
        
        if not questions:
            st.error("No viva questions were generated. Please try again.")
            return False
        
        # Create test in database
        test_id = db_manager.create_viva_test(
            user_id=user_id,
            filename=uploaded_file.name,
            num_questions=len(questions),
            difficulty=difficulty
        )
        
        if not test_id:
            st.error("Failed to save test to database.")
            return False
        
        # Save questions to database
        for idx, q in enumerate(questions, 1):
            db_manager.save_viva_question(
                test_id=test_id,
                question_number=idx,
                question_text=q['question'],
                expected_points=json.dumps(q.get('key_points', [])),
                difficulty=difficulty
            )
        
        # Update session state
        st.session_state.viva_test_id = test_id
        st.session_state.viva_questions = questions
        st.session_state.viva_user_answers = {}
        st.session_state.viva_current_question = 0
        st.session_state.viva_show_results = False
        
        return True
        
    except Exception as e:
        st.error(f"Error generating viva questions: {str(e)}")
        return False


def display_viva_question():
    """Display current viva question"""
    questions = st.session_state.viva_questions
    current_idx = st.session_state.viva_current_question
    total_questions = len(questions)
    
    # Progress bar
    progress = (current_idx) / total_questions
    st.progress(progress, text=f"Question {current_idx + 1} of {total_questions}")
    
    st.divider()
    
    # Display question
    current_q = questions[current_idx]
    
    st.markdown(f"### Question {current_idx + 1}")
    st.markdown(f"**{current_q['question']}**")
    
    st.divider()
    
    # Answer input area
    st.markdown("### 📝 Your Answer")
    user_answer = st.text_area(
        "Type your answer here (minimum 50 characters):",
        height=200,
        key=f"viva_answer_{current_idx}",
        value=st.session_state.viva_user_answers.get(current_idx + 1, ""),
        placeholder="Write a detailed answer to demonstrate your understanding..."
    )
    
    # Character count
    char_count = len(user_answer.strip())
    if char_count < 50:
        st.caption(f"⚠️ {char_count}/50 characters (minimum required)")
    else:
        st.caption(f"✅ {char_count} characters")
    
    st.divider()
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if current_idx > 0:
            if st.button("⬅️ Previous", use_container_width=True):
                st.session_state.viva_current_question -= 1
                st.rerun()
    
    with col2:
        if current_idx < total_questions - 1:
            if st.button("Next ➡️", type="primary", use_container_width=True, 
                        disabled=char_count < 50):
                # Save answer
                st.session_state.viva_user_answers[current_idx + 1] = user_answer
                st.session_state.viva_current_question += 1
                st.rerun()
    
    with col3:
        if current_idx == total_questions - 1:
            if st.button("🎯 Submit Test", type="primary", use_container_width=True, 
                        disabled=char_count < 50):
                # Save last answer
                st.session_state.viva_user_answers[current_idx + 1] = user_answer
                st.session_state.viva_show_results = True
                st.rerun()


def display_viva_results(db_manager: DatabaseManager):
    """Display viva test results with scoring"""
    st.divider()
    st.subheader("🎯 Viva Results & Evaluation")
    
    questions = st.session_state.viva_questions
    user_answers = st.session_state.viva_user_answers
    total_questions = len(questions)
    
    # Evaluate answers
    viva_generator = VivaGenerator()
    
    with st.spinner("🤖 AI is evaluating your answers... Please wait."):
        scores = []
        evaluations = []
        
        for idx, question in enumerate(questions, 1):
            user_answer = user_answers.get(idx, "")
            expected_points = question.get('key_points', [])
            
            # Get AI evaluation
            score, feedback = viva_generator.evaluate_answer(
                question['question'],
                user_answer,
                expected_points
            )
            
            scores.append(score)
            evaluations.append({
                'score': score,
                'feedback': feedback,
                'user_answer': user_answer
            })
            
            # Save to database
            db_questions = db_manager.get_viva_questions(st.session_state.viva_test_id)
            if db_questions and idx <= len(db_questions):
                question_id = db_questions[idx - 1]['id']
                db_manager.update_viva_answer(
                    question_id=question_id,
                    user_answer=user_answer,
                    score=score,
                    feedback=feedback
                )
    
    # Calculate total score
    total_score = sum(scores)
    max_score = total_questions * 10
    percentage = (total_score / max_score) * 100
    
    # Update test completion
    db_manager.complete_viva_test(st.session_state.viva_test_id, total_score)
    
    # Display score card
    if percentage >= 80:
        color = "green"
        emoji = "🌟"
        message = "Excellent Performance!"
    elif percentage >= 60:
        color = "blue"
        emoji = "👍"
        message = "Good Effort!"
    else:
        color = "orange"
        emoji = "📚"
        message = "Keep Practicing!"
    
    st.markdown(f"""
    <div style='background-color: #{color}20; padding: 20px; border-radius: 10px; text-align: center;'>
        <h1 style='color: {color};'>{emoji} {message}</h1>
        <h2>Score: {total_score}/{max_score}</h2>
        <h3>{percentage:.1f}%</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Detailed evaluation
    st.subheader("📋 Detailed Evaluation")
    
    for idx, (question, evaluation) in enumerate(zip(questions, evaluations), 1):
        score = evaluation['score']
        feedback = evaluation['feedback']
        user_answer = evaluation['user_answer']
        
        # Score color
        if score >= 8:
            score_color = "green"
            score_icon = "🟢"
        elif score >= 5:
            score_color = "blue"
            score_icon = "🔵"
        else:
            score_color = "orange"
            score_icon = "🟡"
        
        with st.expander(f"{score_icon} Question {idx} - Score: {score}/10"):
            st.markdown(f"**Question:** {question['question']}")
            
            st.markdown("**Your Answer:**")
            st.info(user_answer)
            
            st.markdown(f"**Score:** :{score_color}[{score}/10]")
            
            st.markdown("**AI Feedback:**")
            st.success(feedback)
            
            # Show key points if available
            if 'key_points' in question and question['key_points']:
                st.markdown("**Key Points to Cover:**")
                for point in question['key_points']:
                    st.write(f"• {point}")
    
    st.divider()
    
    # Action buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 New Viva Practice", use_container_width=True):
            reset_viva_state()
            st.rerun()
    
    with col2:
        if st.button("📊 View History", use_container_width=True):
            reset_viva_state()
            st.rerun()


def show_viva_history(db_manager: DatabaseManager):
    """Display viva practice history"""
    st.subheader("📊 Your Viva Practice History")
    
    user_id = st.session_state.user_id
    history = db_manager.get_user_viva_history(user_id, limit=50)
    
    if not history:
        st.info("No viva practice history yet. Start your first viva session!")
        return
    
    # Display history
    for test in history:
        with st.expander(
            f"🗣️ {test['filename']} - {test['difficulty'].title()} " +
            f"({test['created_at'][:16]})"
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Questions", test['total_questions'])
            
            with col2:
                if test['score'] is not None:
                    max_score = test['total_questions'] * 10
                    st.metric("Score", f"{test['score']}/{max_score}")
                else:
                    st.metric("Status", "Incomplete")
            
            with col3:
                if test['score'] is not None:
                    max_score = test['total_questions'] * 10
                    percentage = (test['score'] / max_score) * 100
                    st.metric("Percentage", f"{percentage:.1f}%")
            
            # View details button
            if test['score'] is not None:
                if st.button(f"View Details", key=f"viva_view_{test['id']}"):
                    view_viva_test_details(test['id'], db_manager)


def view_viva_test_details(test_id: int, db_manager: DatabaseManager):
    """View detailed results of a completed viva test"""
    test = db_manager.get_viva_test(test_id)
    questions = db_manager.get_viva_questions(test_id)
    
    if not test or not questions:
        st.error("Test details not found.")
        return
    
    st.subheader(f"Test Details: {test['filename']}")
    
    for q in questions:
        with st.expander(f"Q{q['question_number']} - Score: {q['score']}/10"):
            st.markdown(f"**Question:** {q['question_text']}")
            
            st.markdown("**Your Answer:**")
            st.info(q['user_answer'] if q['user_answer'] else "Not answered")
            
            if q['score'] is not None:
                st.markdown(f"**Score:** {q['score']}/10")
            
            if q['feedback']:
                st.markdown("**Feedback:**")
                st.success(q['feedback'])


def reset_viva_state():
    """Reset viva session state"""
    st.session_state.viva_test_id = None
    st.session_state.viva_questions = []
    st.session_state.viva_user_answers = {}
    st.session_state.viva_current_question = 0
    st.session_state.viva_show_results = False
