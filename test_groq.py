"""
Test script to verify Groq API integration
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_groq_connection():
    """Test Groq API connection and model availability"""
    print("=" * 60)
    print("GROQ API TEST")
    print("=" * 60)
    
    # Test 1: Check if API key is set
    print("\n1. Checking API Key...")
    api_key = os.getenv('GROQ_API_KEY')
    
    if not api_key:
        # Try to load from secrets.toml
        try:
            secrets_path = project_root / ".streamlit" / "secrets.toml"
            if secrets_path.exists():
                import toml
                secrets = toml.load(secrets_path)
                api_key = secrets.get('GROQ_API_KEY')
                if api_key:
                    os.environ['GROQ_API_KEY'] = api_key
                    print("✅ API key loaded from secrets.toml")
        except Exception as e:
            print(f"❌ Error loading secrets: {e}")
    else:
        print("✅ API key found in environment")
    
    if not api_key:
        print("❌ GROQ_API_KEY not found!")
        print("\nPlease set it in .streamlit/secrets.toml:")
        print('GROQ_API_KEY = "your-api-key-here"')
        return False
    
    print(f"   API Key: {api_key[:20]}...")
    
    # Test 2: Import Groq library
    print("\n2. Importing Groq library...")
    try:
        from groq import Groq
        print("✅ Groq library imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Groq: {e}")
        print("\nInstall with: pip install groq")
        return False
    
    # Test 3: Initialize Groq client
    print("\n3. Initializing Groq client...")
    try:
        client = Groq(api_key=api_key)
        print("✅ Groq client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize client: {e}")
        return False
    
    # Test 4: Test different Groq models
    print("\n4. Testing Groq Models...")
    
    # List of free Groq models to test (as of 2024-2025)
    models_to_test = [
        "llama-3.3-70b-versatile",  # Current best free model
        "llama-3.1-8b-instant",     # Fast model
        "llama3-70b-8192",          # Legacy model
        "mixtral-8x7b-32768",       # Alternative model
    ]
    
    working_models = []
    
    for model_name in models_to_test:
        print(f"\n   Testing: {model_name}")
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": "Say 'Hello' in one word"}
                ],
                max_tokens=10,
                temperature=0.5
            )
            
            answer = response.choices[0].message.content
            print(f"   ✅ {model_name}: Working!")
            print(f"      Response: {answer}")
            working_models.append(model_name)
            
        except Exception as e:
            print(f"   ❌ {model_name}: Failed - {str(e)[:100]}")
    
    # Test 5: Test current configuration
    print("\n5. Testing Current Configuration...")
    try:
        from config.settings import GROQ_MODEL
        print(f"   Current model in settings: {GROQ_MODEL}")
        
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What is 2+2? Answer briefly."}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        answer = response.choices[0].message.content
        print(f"   ✅ Current model works!")
        print(f"      Question: What is 2+2?")
        print(f"      Answer: {answer}")
        
    except Exception as e:
        print(f"   ❌ Current model failed: {e}")
        if working_models:
            print(f"\n   💡 Suggestion: Update GROQ_MODEL in config/settings.py to: {working_models[0]}")
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    if working_models:
        print(f"✅ {len(working_models)} working model(s) found:")
        for model in working_models:
            print(f"   - {model}")
        print("\n✅ Groq API is working correctly!")
        return True
    else:
        print("❌ No working models found")
        print("\nPossible issues:")
        print("1. Invalid API key")
        print("2. API rate limit exceeded")
        print("3. Network connectivity issues")
        print("4. Model names have changed")
        return False

if __name__ == "__main__":
    success = test_groq_connection()
    sys.exit(0 if success else 1)
