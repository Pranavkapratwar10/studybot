"""
List all available models from Groq API
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def list_models():
    """List all available models from Groq"""
    print("=" * 70)
    print("  GROQ AVAILABLE MODELS")
    print("=" * 70)
    
    # Load API key
    api_key = None
    secrets_path = project_root / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        try:
            import toml
            secrets = toml.load(secrets_path)
            api_key = secrets.get('GROQ_API_KEY')
        except Exception as e:
            print(f"Error loading API key: {e}")
            return
    
    if not api_key:
        print("No API key found!")
        return
    
    print(f"\nAPI Key: {api_key[:20]}...\n")
    
    # Import Groq
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        print("Fetching available models from Groq API...\n")
        print("-" * 70)
        
        # List models
        models = client.models.list()
        
        if hasattr(models, 'data'):
            model_list = models.data
        else:
            model_list = list(models)
        
        if not model_list:
            print("No models found!")
            return
        
        print(f"\n✅ Found {len(model_list)} models:\n")
        
        working_models = []
        
        for model in model_list:
            model_id = model.id if hasattr(model, 'id') else str(model)
            active = getattr(model, 'active', True)
            
            if active:
                print(f"✅ {model_id}")
                if hasattr(model, 'owned_by'):
                    print(f"   Owner: {model.owned_by}")
                if hasattr(model, 'context_window'):
                    print(f"   Context: {model.context_window} tokens")
                working_models.append(model_id)
            else:
                print(f"❌ {model_id} (inactive)")
            print()
        
        if working_models:
            print("-" * 70)
            print(f"\n💡 RECOMMENDED MODEL: {working_models[0]}")
            print(f"\nUpdate config/settings.py with:")
            print(f'GROQ_MODEL = "{working_models[0]}"')
            print("\n" + "=" * 70)
            
            # Test the first working model
            print("\nTesting the first available model...\n")
            try:
                response = client.chat.completions.create(
                    model=working_models[0],
                    messages=[{"role": "user", "content": "Say hello"}],
                    max_tokens=10
                )
                result = response.choices[0].message.content
                print(f"✅ Test successful!")
                print(f"Response: {result}")
            except Exception as e:
                print(f"❌ Test failed: {e}")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nTrying alternative approach...")
        
        # Try testing common current models
        test_models = [
            "llama-3.3-70b-versatile",
            "llama-3.1-70b-versatile", 
            "llama-3.1-8b-instant",
            "mixtral-8x7b-32768",
            "gemma2-9b-it"
        ]
        
        print("\nTesting common models manually:\n")
        from groq import Groq
        client = Groq(api_key=api_key)
        
        for model in test_models:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                print(f"✅ {model} works!")
            except Exception as e:
                error = str(e)[:80]
                print(f"❌ {model}: {error}")

if __name__ == "__main__":
    list_models()
