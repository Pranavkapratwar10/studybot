"""
MCQ Generation Page
"""
import streamlit as st
import json
from pathlib import Path
from typing import List, Dict

from mcq.mcq_generator import MCQGenerator
from rag.document_processor import DocumentProcessor
from database.db_manager import DatabaseManager
from utils.helpers import save_uploaded_file, validate_file_upload
from config.settings import UPLOAD_DIR


def show_mcq_page(db_manager: DatabaseManager):
    """Display MCQ generation page"""
    st.title("📝 MCQ Generator")
    st.markdown("Upload a document and generate Multiple Choice Questions instantly!")
    
    # Initialize session state
    if 'mcq_test_id' not in st.session_state:
        st.session_state.mcq_test_id = None
    if 'mcq_questions' not in st.session_state:
        st.session_state.mcq_questions = []
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    
    # Tabs
    tab1, tab2 = st.tabs(["📤 Generate MCQs", "📊 MCQ History"])
    
    with tab1:
        show_mcq_generator(db_manager)
    
    with tab2:
        show_mcq_history(db_manager)


def show_mcq_generator(db_manager: DatabaseManager):
    """MCQ generation interface"""
    
    # File upload
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF, DOCX, or TXT file",
        type=['pdf', 'docx', 'txt'],
        help="Upload your study material to generate MCQs"
    )
    
    # Settings
    col1, col2 = st.columns(2)
    
    with col1:
        num_questions = st.slider(
            "Number of Questions",
            min_value=5,
            max_value=30,
            value=10,
            step=5
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty Level",
            options=["easy", "medium", "hard"],
            index=1
        )
    
    # Generate button
    if st.button("🚀 Generate MCQs", type="primary", disabled=uploaded_file is None):
        if uploaded_file:
            with st.spinner("Generating MCQs... This may take a moment."):
                success = generate_mcqs_from_file(
                    uploaded_file,
                    num_questions,
                    difficulty,
                    db_manager
                )
                
                if success:
                    st.success(f"✅ Generated {len(st.session_state.mcq_questions)} MCQs!")
                    st.rerun()
                else:
                    st.error("Failed to generate MCQs. Please try again.")
    
    # Display MCQs if generated
    if st.session_state.mcq_questions and not st.session_state.show_results:
        display_mcq_test()
    
    # Display results if submitted
    if st.session_state.show_results:
        display_results(db_manager)


def generate_mcqs_from_file(uploaded_file, num_questions: int, 
                            difficulty: str, db_manager: DatabaseManager) -> bool:
    """Generate MCQs from uploaded file"""
    try:
        user_id = st.session_state.user_id
        
        # Validate file
        is_valid, message = validate_file_upload(uploaded_file)
        if not is_valid:
            st.error(message)
            return False
        
        # Save file
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
        
        # Generate MCQs
        mcq_generator = MCQGenerator()
        mcqs = mcq_generator.generate_mcqs(text, num_questions, difficulty)
        
        if not mcqs:
            st.error("No MCQs were generated. Please try again.")
            return False
        
        # Validate MCQs
        valid_mcqs = mcq_generator.validate_mcqs(mcqs)
        
        if not valid_mcqs:
            st.error("Generated MCQs were invalid. Please try again.")
            return False
        
        # Create test in database
        test_id = db_manager.create_mcq_test(
            user_id=user_id,
            filename=uploaded_file.name,
            num_questions=len(valid_mcqs),
            difficulty=difficulty
        )
        
        if not test_id:
            st.error("Failed to save test to database.")
            return False
        
        # Save questions to database
        for idx, mcq in enumerate(valid_mcqs, 1):
            options_json = json.dumps(mcq['options'])
            explanation = mcq.get('explanation', '')
            
            db_manager.save_mcq_question(
                test_id=test_id,
                question_number=idx,
                question_text=mcq['question'],
                options_json=options_json,
                correct_answer=mcq['correct_answer'],
                explanation=explanation
            )
        
        # Update session state
        st.session_state.mcq_test_id = test_id
        st.session_state.mcq_questions = valid_mcqs
        st.session_state.user_answers = {}
        st.session_state.show_results = False
        
        return True
        
    except Exception as e:
        st.error(f"Error generating MCQs: {str(e)}")
        return False


def display_mcq_test():
    """Display the MCQ test interface"""
    st.divider()
    st.subheader("📝 Answer the Questions")
    
    questions = st.session_state.mcq_questions
    
    for idx, mcq in enumerate(questions, 1):
        st.markdown(f"### Question {idx}")
        st.write(mcq['question'])
        
        # Radio buttons for options
        options = mcq['options']
        option_labels = [f"{key}. {value}" for key, value in options.items()]
        
        selected = st.radio(
            f"Select your answer for Q{idx}:",
            options=list(options.keys()),
            format_func=lambda x: f"{x}. {options[x]}",
            key=f"q_{idx}",
            label_visibility="collapsed"
        )
        
        st.session_state.user_answers[idx] = selected
        st.divider()
    
    # Submit button
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("📊 Submit Test", type="primary", use_container_width=True):
            st.session_state.show_results = True
            st.rerun()


def display_results(db_manager: DatabaseManager):
    """Display test results with score"""
    st.divider()
    st.subheader("🎯 Test Results")
    
    questions = st.session_state.mcq_questions
    user_answers = st.session_state.user_answers
    
    # Calculate score
    correct_count = 0
    total_questions = len(questions)
    
    # Get questions from database
    db_questions = db_manager.get_mcq_questions(st.session_state.mcq_test_id)
    
    for idx, mcq in enumerate(questions, 1):
        user_answer = user_answers.get(idx, "")
        correct_answer = mcq['correct_answer']
        is_correct = (user_answer == correct_answer)
        
        if is_correct:
            correct_count += 1
        
        # Update database with user answer
        if db_questions and idx <= len(db_questions):
            question_id = db_questions[idx - 1]['id']
            db_manager.update_user_answer(
                question_id=question_id,
                user_answer=user_answer,
                is_correct=1 if is_correct else 0
            )
    
    # Update test completion
    score = correct_count
    db_manager.complete_mcq_test(st.session_state.mcq_test_id, score)
    
    # Display score card
    percentage = (correct_count / total_questions) * 100
    
    # Score card styling
    if percentage >= 80:
        color = "green"
        emoji = "🌟"
        message = "Excellent!"
    elif percentage >= 60:
        color = "blue"
        emoji = "👍"
        message = "Good job!"
    else:
        color = "orange"
        emoji = "📚"
        message = "Keep practicing!"
    
    st.markdown(f"""
    <div style='background-color: #{color}20; padding: 20px; border-radius: 10px; text-align: center;'>
        <h1 style='color: {color};'>{emoji} {message}</h1>
        <h2>Score: {correct_count}/{total_questions}</h2>
        <h3>{percentage:.1f}%</h3>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Detailed results
    st.subheader("📋 Detailed Results")
    
    for idx, mcq in enumerate(questions, 1):
        user_answer = user_answers.get(idx, "Not answered")
        correct_answer = mcq['correct_answer']
        is_correct = (user_answer == correct_answer)
        
        # Question card
        with st.expander(
            f"{'✅' if is_correct else '❌'} Question {idx}" + 
            (f" - Your answer: {user_answer}" if user_answer != "Not answered" else "")
        ):
            st.write(f"**Question:** {mcq['question']}")
            st.write("")
            
            # Show all options
            for key, value in mcq['options'].items():
                if key == correct_answer:
                    st.success(f"✅ **{key}. {value}** (Correct Answer)")
                elif key == user_answer and not is_correct:
                    st.error(f"❌ {key}. {value} (Your Answer)")
                else:
                    st.write(f"{key}. {value}")
            
            # Show explanation if available
            if 'explanation' in mcq and mcq['explanation']:
                st.info(f"💡 **Explanation:** {mcq['explanation']}")
    
    st.divider()
    
    # Buttons
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Generate New Test", use_container_width=True):
            reset_mcq_state()
            st.rerun()
    
    with col2:
        if st.button("📊 View History", use_container_width=True):
            reset_mcq_state()
            st.rerun()


def show_mcq_history(db_manager: DatabaseManager):
    """Display MCQ test history"""
    st.subheader("📊 Your MCQ Test History")
    
    user_id = st.session_state.user_id
    history = db_manager.get_user_mcq_history(user_id, limit=50)
    
    if not history:
        st.info("No test history yet. Generate your first MCQ test!")
        return
    
    # Display history
    for test in history:
        with st.expander(
            f"📝 {test['filename']} - {test['difficulty'].title()} " +
            f"({test['created_at'][:16]})"
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Questions", test['total_questions'])
            
            with col2:
                if test['score'] is not None:
                    percentage = (test['score'] / test['total_questions']) * 100
                    st.metric("Score", f"{test['score']}/{test['total_questions']}")
                else:
                    st.metric("Status", "Incomplete")
            
            with col3:
                if test['score'] is not None:
                    percentage = (test['score'] / test['total_questions']) * 100
                    st.metric("Percentage", f"{percentage:.1f}%")
            
            # View details button
            if test['score'] is not None:
                if st.button(f"View Details", key=f"view_{test['id']}"):
                    view_test_details(test['id'], db_manager)


def view_test_details(test_id: int, db_manager: DatabaseManager):
    """View detailed results of a completed test"""
    test = db_manager.get_mcq_test(test_id)
    questions = db_manager.get_mcq_questions(test_id)
    
    if not test or not questions:
        st.error("Test details not found.")
        return
    
    st.subheader(f"Test Details: {test['filename']}")
    
    for q in questions:
        options = json.loads(q['options_json'])
        
        with st.expander(
            f"{'✅' if q['is_correct'] else '❌'} Q{q['question_number']}"
        ):
            st.write(f"**Question:** {q['question_text']}")
            st.write("")
            
            for key, value in options.items():
                if key == q['correct_answer']:
                    st.success(f"✅ **{key}. {value}** (Correct)")
                elif key == q['user_answer'] and not q['is_correct']:
                    st.error(f"❌ {key}. {value} (Your Answer)")
                else:
                    st.write(f"{key}. {value}")
            
            if q['explanation']:
                st.info(f"💡 {q['explanation']}")


def reset_mcq_state():
    """Reset MCQ session state"""
    st.session_state.mcq_test_id = None
    st.session_state.mcq_questions = []
    st.session_state.user_answers = {}
    st.session_state.show_results = False
