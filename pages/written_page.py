"""
Written Practice Page
"""
import streamlit as st
import json
from pathlib import Path
from typing import List, Dict

from written.written_generator import WrittenGenerator
from rag.document_processor import DocumentProcessor
from database.db_manager import DatabaseManager
from utils.helpers import save_uploaded_file, validate_file_upload
from config.settings import UPLOAD_DIR


def show_written_page(db_manager: DatabaseManager):
    """Display Written Practice page"""
    st.title("✍️ Written Practice")
    st.markdown("Practice written exam questions with AI evaluation!")
    
    # Initialize session state
    if 'written_test_id' not in st.session_state:
        st.session_state.written_test_id = None
    if 'written_questions' not in st.session_state:
        st.session_state.written_questions = []
    if 'written_answers' not in st.session_state:
        st.session_state.written_answers = {}
    if 'written_show_results' not in st.session_state:
        st.session_state.written_show_results = False
    
    # Tabs
    tab1, tab2 = st.tabs(["📝 Practice", "📊 History"])
    
    with tab1:
        show_written_generator(db_manager)
    
    with tab2:
        show_written_history(db_manager)


def show_written_generator(db_manager: DatabaseManager):
    """Written practice generation interface"""
    
    # Check if already in a test
    if st.session_state.written_questions and not st.session_state.written_show_results:
        display_written_test()
        return
    
    # Show results if test is complete
    if st.session_state.written_show_results:
        display_written_results(db_manager)
        return
    
    # File upload section
    st.subheader("Upload Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF, DOCX, or TXT file",
        type=['pdf', 'docx', 'txt'],
        help="Upload your study material for written practice",
        key="written_file_upload"
    )
    
    # Settings
    col1, col2, col3 = st.columns(3)
    
    with col1:
        num_questions = st.slider(
            "Number of Questions",
            min_value=1,
            max_value=10,
            value=5,
            step=1
        )
    
    with col2:
        difficulty = st.selectbox(
            "Difficulty Level",
            options=["easy", "medium", "hard"],
            index=1
        )
    
    with col3:
        marks_per_question = st.selectbox(
            "Marks per Question",
            options=[2, 3, 5, 10, 15, 20],
            index=2  # Default to 5 marks
        )
    
    # Total marks display
    total_marks = num_questions * marks_per_question
    st.info(f"📊 **Total Marks:** {total_marks} marks ({num_questions} questions × {marks_per_question} marks each)")
    
    # Generate button
    if st.button("🚀 Generate Written Questions", type="primary", disabled=uploaded_file is None):
        if uploaded_file:
            with st.spinner("Generating written questions... This may take a moment."):
                success = generate_written_from_file(
                    uploaded_file,
                    num_questions,
                    difficulty,
                    marks_per_question,
                    db_manager
                )
                
                if success:
                    st.success(f"✅ Generated {len(st.session_state.written_questions)} questions!")
                    st.rerun()
                else:
                    st.error("Failed to generate questions. Please try again.")


def generate_written_from_file(uploaded_file, num_questions: int, 
                               difficulty: str, marks_per_question: int,
                               db_manager: DatabaseManager) -> bool:
    """Generate written questions from uploaded file"""
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
            st.info(f"📄 Using existing document: '{uploaded_file.name}'")
            file_path = existing_doc['file_path']
        else:
            # Save new file and add to documents
            success, file_path, save_msg = save_uploaded_file(
                uploaded_file, user_id, UPLOAD_DIR
            )
            
            if not success:
                st.error(save_msg)
                return False
            
            # Add to documents database
            doc_processor = DocumentProcessor()
            try:
                chunks = doc_processor.process_document(
                    file_path, uploaded_file.name, user_id
                )
                
                # Add to vector store
                from rag.rag_pipeline import RAGPipeline
                rag = RAGPipeline()
                chunks_added = rag.add_documents_to_store(user_id, chunks)
                
                # Save to database
                db_manager.add_document(
                    user_id=user_id,
                    filename=uploaded_file.name,
                    file_path=file_path,
                    file_size=uploaded_file.size,
                    file_type=Path(uploaded_file.name).suffix,
                    chunks_count=chunks_added
                )
                st.success(f"✅ Document added to your library!")
            except:
                pass  # Continue even if chunking fails
        
        # Extract text from document
        doc_processor = DocumentProcessor()
        text = doc_processor.extract_text(file_path)
        
        if not text or len(text.strip()) < 100:
            st.error("Could not extract sufficient text from the document.")
            return False
        
        # Generate questions
        written_generator = WrittenGenerator()
        questions = written_generator.generate_questions(
            text, num_questions, difficulty, marks_per_question
        )
        
        if not questions:
            st.error("No questions were generated. Please try again.")
            return False
        
        # Validate questions
        valid_questions = written_generator.validate_questions(questions)
        
        if not valid_questions:
            st.error("Generated questions were invalid. Please try again.")
            return False
        
        # Create test in database
        total_marks = sum(q['marks'] for q in valid_questions)
        test_id = db_manager.create_written_test(
            user_id=user_id,
            filename=uploaded_file.name,
            num_questions=len(valid_questions),
            total_marks=total_marks,
            difficulty=difficulty
        )
        
        if not test_id:
            st.error("Failed to save test to database.")
            return False
        
        # Save questions to database
        for idx, q in enumerate(valid_questions, 1):
            key_points_json = json.dumps(q.get('key_points', []))
            
            db_manager.save_written_question(
                test_id=test_id,
                question_number=idx,
                question_text=q['question'],
                marks=q['marks'],
                key_points_json=key_points_json
            )
        
        # Update session state
        st.session_state.written_test_id = test_id
        st.session_state.written_questions = valid_questions
        st.session_state.written_answers = {}
        st.session_state.written_show_results = False
        
        return True
        
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def display_written_test():
    """Display the written test interface"""
    st.divider()
    st.subheader("✍️ Answer the Questions")
    
    questions = st.session_state.written_questions
    total_marks = sum(q['marks'] for q in questions)
    
    st.info(f"📊 Total Marks: {total_marks} | Questions: {len(questions)}")
    
    # Answer form
    with st.form("written_test_form"):
        for idx, question in enumerate(questions, 1):
            st.markdown(f"### Question {idx} ({question['marks']} marks)")
            st.write(question['question'])
            
            # Text area for answer
            answer = st.text_area(
                f"Your answer for Q{idx}:",
                height=150,
                key=f"written_q_{idx}",
                placeholder="Write your detailed answer here...",
                label_visibility="collapsed"
            )
            
            st.session_state.written_answers[idx] = answer
            st.divider()
        
        # Submit button
        submitted = st.form_submit_button("📊 Submit Test", type="primary", use_container_width=True)
        
        if submitted:
            # Check if all questions are answered
            unanswered = [i for i in range(1, len(questions) + 1) 
                         if not st.session_state.written_answers.get(i, "").strip()]
            
            if unanswered:
                st.error(f"⚠️ Please answer all questions! Unanswered: Q{', Q'.join(map(str, unanswered))}")
            else:
                st.session_state.written_show_results = True
                st.rerun()


def display_written_results(db_manager: DatabaseManager):
    """Display test results with AI evaluation"""
    st.divider()
    st.subheader("🎯 Test Results & Evaluation")
    
    questions = st.session_state.written_questions
    user_answers = st.session_state.written_answers
    
    # Evaluate answers
    written_generator = WrittenGenerator()
    
    with st.spinner("🤖 AI is evaluating your answers... Please wait."):
        scores = []
        evaluations = []
        
        for idx, question in enumerate(questions, 1):
            user_answer = user_answers.get(idx, "")
            key_points = question.get('key_points', [])
            marks = question['marks']
            
            # Get AI evaluation
            score, feedback = written_generator.evaluate_answer(
                question['question'],
                user_answer,
                key_points,
                marks
            )
            
            scores.append(score)
            evaluations.append({
                'score': score,
                'feedback': feedback,
                'user_answer': user_answer
            })
            
            # Save to database
            db_questions = db_manager.get_written_questions(st.session_state.written_test_id)
            if db_questions and idx <= len(db_questions):
                question_id = db_questions[idx - 1]['id']
                db_manager.update_written_answer(
                    question_id=question_id,
                    user_answer=user_answer,
                    score=score,
                    feedback=feedback
                )
    
    # Calculate total score
    total_score = sum(scores)
    max_score = sum(q['marks'] for q in questions)
    percentage = (total_score / max_score) * 100
    
    # Update test completion
    db_manager.complete_written_test(st.session_state.written_test_id, total_score)
    
    # Display score card
    if percentage >= 80:
        color = "green"
        emoji = "🌟"
        grade = "A"
        message = "Outstanding Performance!"
    elif percentage >= 70:
        color = "blue"
        emoji = "👏"
        grade = "B"
        message = "Very Good!"
    elif percentage >= 60:
        color = "orange"
        emoji = "👍"
        grade = "C"
        message = "Good Effort!"
    else:
        color = "red"
        emoji = "📚"
        grade = "D"
        message = "Keep Practicing!"
    
    st.markdown(f"""
    <div style='background-color: #{color}20; padding: 30px; border-radius: 15px; text-align: center; border: 3px solid #{color}80;'>
        <h1 style='color: {color}; font-size: 48px;'>{emoji}</h1>
        <h2 style='color: {color};'>{message}</h2>
        <h1 style='font-size: 56px; margin: 20px 0;'>{total_score:.1f}/{max_score}</h1>
        <h2 style='color: {color};'>Grade: {grade} ({percentage:.1f}%)</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.divider()
    
    # Detailed evaluation
    st.subheader("📋 Detailed Evaluation")
    
    for idx, (question, evaluation) in enumerate(zip(questions, evaluations), 1):
        score = evaluation['score']
        max_marks = question['marks']
        feedback = evaluation['feedback']
        user_answer = evaluation['user_answer']
        
        # Score percentage for this question
        q_percentage = (score / max_marks) * 100
        
        # Score color
        if q_percentage >= 80:
            score_color = "green"
            score_icon = "🟢"
        elif q_percentage >= 60:
            score_color = "blue"
            score_icon = "🔵"
        else:
            score_color = "orange"
            score_icon = "🟡"
        
        with st.expander(f"{score_icon} Question {idx} - Score: {score:.1f}/{max_marks} marks"):
            st.markdown(f"**Question ({max_marks} marks):**")
            st.write(question['question'])
            
            st.markdown("**Your Answer:**")
            st.info(user_answer)
            
            st.markdown(f"**Score:** :{score_color}[{score:.1f}/{max_marks} marks ({q_percentage:.1f}%)]")
            
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
        if st.button("🔄 New Practice Test", use_container_width=True):
            reset_written_state()
            st.rerun()
    
    with col2:
        if st.button("📊 View History", use_container_width=True):
            reset_written_state()
            st.rerun()


def show_written_history(db_manager: DatabaseManager):
    """Display written practice history"""
    st.subheader("📊 Your Written Practice History")
    
    user_id = st.session_state.user_id
    history = db_manager.get_user_written_history(user_id, limit=50)
    
    if not history:
        st.info("No written practice history yet. Start your first test!")
        return
    
    # Display history
    for test in history:
        with st.expander(
            f"✍️ {test['filename']} - {test['difficulty'].title()} " +
            f"({test['created_at'][:16]})"
        ):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Questions", test['num_questions'])
            
            with col2:
                if test['score'] is not None:
                    st.metric("Score", f"{test['score']:.1f}/{test['total_marks']}")
                else:
                    st.metric("Status", "Incomplete")
            
            with col3:
                if test['score'] is not None:
                    percentage = (test['score'] / test['total_marks']) * 100
                    st.metric("Percentage", f"{percentage:.1f}%")
            
            # View details button
            if test['score'] is not None:
                if st.button(f"View Details", key=f"written_view_{test['id']}"):
                    view_written_test_details(test['id'], db_manager)


def view_written_test_details(test_id: int, db_manager: DatabaseManager):
    """View detailed results of a completed test"""
    test = db_manager.get_written_test(test_id)
    questions = db_manager.get_written_questions(test_id)
    
    if not test or not questions:
        st.error("Test details not found.")
        return
    
    st.subheader(f"Test Details: {test['filename']}")
    
    for q in questions:
        with st.expander(f"Q{q['question_number']} - Score: {q['score']:.1f}/{q['marks']} marks"):
            st.markdown(f"**Question ({q['marks']} marks):**")
            st.write(q['question_text'])
            
            st.markdown("**Your Answer:**")
            st.info(q['user_answer'] if q['user_answer'] else "Not answered")
            
            if q['score'] is not None:
                st.markdown(f"**Score:** {q['score']:.1f}/{q['marks']} marks")
            
            if q['feedback']:
                st.markdown("**Feedback:**")
                st.success(q['feedback'])


def reset_written_state():
    """Reset written test session state"""
    st.session_state.written_test_id = None
    st.session_state.written_questions = []
    st.session_state.written_answers = {}
    st.session_state.written_show_results = False
