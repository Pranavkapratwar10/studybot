"""
Test MCQ Generation
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_mcq_generation():
    """Test MCQ generation with sample text"""
    print("=" * 70)
    print("  TESTING MCQ GENERATION")
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
    Python is a high-level, interpreted programming language known for its simplicity and readability.
    Created by Guido van Rossum and first released in 1991, Python has become one of the most popular
    programming languages in the world.
    
    Key features of Python include:
    1. Easy to learn and read syntax
    2. Dynamic typing
    3. Automatic memory management
    4. Extensive standard library
    5. Support for multiple programming paradigms
    
    Python is widely used in web development, data science, artificial intelligence, scientific computing,
    and automation. Popular frameworks include Django and Flask for web development, and NumPy and Pandas
    for data analysis.
    """
    
    print("Sample Text:")
    print("-" * 70)
    print(sample_text[:200] + "...")
    print()
    
    # Test MCQ generation
    print("Generating MCQs...")
    print("-" * 70)
    
    try:
        from mcq.mcq_generator import MCQGenerator
        
        generator = MCQGenerator()
        mcqs = generator.generate_mcqs(sample_text, num_questions=3, difficulty="medium")
        
        if not mcqs:
            print("❌ No MCQs generated!")
            print("\nThis could be due to:")
            print("1. API response not in JSON format")
            print("2. Model not following instructions")
            print("3. Parsing issues")
            return False
        
        print(f"✅ Generated {len(mcqs)} MCQs\n")
        
        # Display MCQs
        for idx, mcq in enumerate(mcqs, 1):
            print(f"Question {idx}:")
            print(f"  Q: {mcq['question']}")
            print(f"  Options:")
            for key, value in mcq['options'].items():
                marker = "✓" if key == mcq['correct_answer'] else " "
                print(f"    {marker} {key}. {value}")
            if 'explanation' in mcq:
                print(f"  Explanation: {mcq['explanation']}")
            print()
        
        # Validate MCQs
        print("-" * 70)
        print("Validating MCQs...")
        
        valid_mcqs = generator.validate_mcqs(mcqs)
        print(f"✅ {len(valid_mcqs)}/{len(mcqs)} MCQs are valid")
        
        if len(valid_mcqs) == len(mcqs):
            print("\n🎉 MCQ generation is working perfectly!")
            return True
        else:
            print(f"\n⚠️  {len(mcqs) - len(valid_mcqs)} MCQs failed validation")
            return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_mcq_generation()
    sys.exit(0 if success else 1)
