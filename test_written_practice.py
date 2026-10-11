"""
Test Written Practice Generation
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_written_practice():
    """Test written practice generation"""
    print("=" * 70)
    print("  TESTING WRITTEN PRACTICE GENERATION")
    print("=" * 70)
    print()
    
    # Load API key
    secrets_path = project_root / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        try:
            import toml
            secrets = toml.load(secrets_path)
            api_key = secrets.get('GROQ_API_KEY')
            if api_key:
                os.environ['GROQ_API_KEY'] = api_key
        except:
            pass
    
    # Sample text
    sample_text = """
    Artificial Intelligence (AI) is the simulation of human intelligence by machines, especially 
    computer systems. These processes include learning (acquiring information and rules for using it), 
    reasoning (using rules to reach approximate or definite conclusions), and self-correction.
    
    Machine Learning is a subset of AI that provides systems the ability to automatically learn and 
    improve from experience without being explicitly programmed. Machine learning focuses on the 
    development of computer programs that can access data and use it to learn for themselves.
    
    Deep Learning is a subset of machine learning based on artificial neural networks. The learning 
    process is deep because the structure of artificial neural networks consists of multiple input, 
    output, and hidden layers. Each layer contains units that transform the input data into information 
    that the next layer can use for a certain predictive task.
    """
    
    print("Sample Text:")
    print("-" * 70)
    print(sample_text[:200] + "...")
    print()
    
    # Test question generation
    print("Generating Written Practice Questions...")
    print("-" * 70)
    
    try:
        from written.written_generator import WrittenGenerator
        
        generator = WrittenGenerator()
        questions = generator.generate_questions(
            sample_text, 
            num_questions=3, 
            difficulty="medium",
            marks_per_question=5
        )
        
        if not questions:
            print("❌ No questions generated!")
            return False
        
        print(f"✅ Generated {len(questions)} questions\n")
        
        # Display questions
        total_marks = 0
        for idx, q in enumerate(questions, 1):
            marks = q.get('marks', 5)
            total_marks += marks
            print(f"Question {idx} ({marks} marks):")
            print(f"  {q['question']}")
            if 'key_points' in q and q['key_points']:
                print(f"  Key Points:")
                for point in q['key_points']:
                    print(f"    - {point}")
            print()
        
        print("-" * 70)
        print(f"Total Marks: {total_marks}")
        
        # Test evaluation
        print("\n" + "-" * 70)
        print("Testing Answer Evaluation...")
        print("-" * 70)
        
        sample_answer = """
        Artificial Intelligence is the simulation of human intelligence by machines. It includes
        processes like learning, reasoning, and self-correction. Machine Learning is a subset of AI
        that allows systems to learn from experience without explicit programming.
        """
        
        if questions:
            score, feedback = generator.evaluate_answer(
                questions[0]['question'],
                sample_answer,
                questions[0].get('key_points', []),
                questions[0].get('marks', 5)
            )
            
            print(f"\nSample Answer Evaluation:")
            print(f"Score: {score}/{questions[0].get('marks', 5)} marks")
            print(f"Feedback: {feedback}")
        
        print("\n🎉 Written Practice generation is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_written_practice()
    sys.exit(0 if success else 1)
