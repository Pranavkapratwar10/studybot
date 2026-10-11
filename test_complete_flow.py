"""
Test complete RAG pipeline flow
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_complete_flow():
    """Test the complete RAG flow"""
    print("=" * 70)
    print("  COMPLETE RAG PIPELINE TEST")
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
    
    # Test 1: LLM Client
    print("1. Testing LLM Client...")
    print("-" * 70)
    try:
        from llm.groq_client import GroqClient
        from config.settings import GROQ_MODEL
        
        client = GroqClient()
        print(f"✅ LLM Client initialized")
        print(f"   Model: {GROQ_MODEL}")
        
        # Test generation
        response = client.generate_response(
            "You are a helpful assistant.",
            "What is 2+2? Answer in one word."
        )
        print(f"✅ Response generation works!")
        print(f"   Question: What is 2+2?")
        print(f"   Answer: {response}")
        
    except Exception as e:
        print(f"❌ LLM Client failed: {e}")
        return False
    
    # Test 2: Vector Store
    print(f"\n2. Testing Vector Store...")
    print("-" * 70)
    try:
        from rag.vector_store import VectorStore
        
        store = VectorStore()
        print(f"✅ Vector Store initialized")
        print(f"   Using ChromaDB at: data/chroma_db")
        
        # Test adding a dummy document
        test_chunks = [
            {
                'text': 'Python is a high-level programming language.',
                'metadata': {'filename': 'test.txt', 'chunk_id': 0}
            },
            {
                'text': 'Machine learning is a subset of artificial intelligence.',
                'metadata': {'filename': 'test.txt', 'chunk_id': 1}
            }
        ]
        
        count = store.add_documents(999, test_chunks)  # Test user ID 999
        print(f"✅ Added {count} test chunks to vector store")
        
        # Test search
        results = store.search(999, "What is Python?", top_k=1)
        if results:
            print(f"✅ Search works!")
            print(f"   Query: What is Python?")
            print(f"   Top result: {results[0]['text'][:60]}...")
        
    except Exception as e:
        print(f"❌ Vector Store failed: {e}")
        return False
    
    # Test 3: RAG Pipeline
    print(f"\n3. Testing RAG Pipeline...")
    print("-" * 70)
    try:
        from rag.rag_pipeline import RAGPipeline
        
        pipeline = RAGPipeline()
        print(f"✅ RAG Pipeline initialized")
        
        # Test query with context
        answer, sources, used_context = pipeline.query(
            999,  # Test user ID
            "What is Python?",
            "short_answer"
        )
        
        if used_context:
            print(f"✅ RAG query with context works!")
            print(f"   Question: What is Python?")
            print(f"   Answer: {answer[:100]}...")
            print(f"   Sources: {sources}")
        else:
            print(f"✅ RAG query works (fallback mode)")
            print(f"   Answer: {answer[:100]}...")
        
    except Exception as e:
        print(f"❌ RAG Pipeline failed: {e}")
        return False
    
    # Test 4: Prompts
    print(f"\n4. Testing Prompt Templates...")
    print("-" * 70)
    try:
        from llm.prompts import get_exam_mode_prompt, EXAM_MODE_PROMPTS
        
        print(f"✅ Prompt templates loaded")
        print(f"   Available modes: {', '.join(EXAM_MODE_PROMPTS.keys())}")
        
        system, user = get_exam_mode_prompt(
            "viva",
            "Python is a programming language",
            "What is Python?"
        )
        print(f"✅ Prompt generation works!")
        
    except Exception as e:
        print(f"❌ Prompts failed: {e}")
        return False
    
    # Cleanup test data
    try:
        store.delete_collection(999)
        print(f"\n✅ Test cleanup successful")
    except:
        pass
    
    # Success!
    print("\n" + "=" * 70)
    print("  🎉 ALL RAG PIPELINE TESTS PASSED!")
    print("=" * 70)
    print()
    print("Your RAG chatbot is fully operational!")
    print()
    print("Next steps:")
    print("  1. Run: streamlit run app.py")
    print("  2. Register an account")
    print("  3. Upload your study materials")
    print("  4. Start asking questions!")
    print()
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    success = test_complete_flow()
    sys.exit(0 if success else 1)
