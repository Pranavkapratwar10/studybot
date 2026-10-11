"""
Find available Groq models for your API key
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def find_working_models():
    """Test various Groq models to find which ones work"""
    print("=" * 70)
    print("  FINDING AVAILABLE GROQ MODELS")
    print("=" * 70)
    
    # Load API key
    api_key = None
    secrets_path = project_root / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        try:
            import toml
            secrets = toml.load(secrets_path)
            api_key = secrets.get('GROQ_API_KEY')
            os.environ['GROQ_API_KEY'] = api_key
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
    except Exception as e:
        print(f"Failed to initialize Groq client: {e}")
        return
    
    # List of possible model names to test (updated for 2024-2026)
    models_to_test = [
        # LLaMA models
        "llama-3.3-70b-versatile",
        "llama-3.3-70b-specdec",
        "llama-3.2-90b-vision-preview",
        "llama-3.2-11b-vision-preview",
        "llama-3.2-3b-preview",
        "llama-3.2-1b-preview",
        "llama-3.1-70b-versatile",
        "llama-3.1-8b-instant",
        "llama3-groq-70b-8192-tool-use-preview",
        "llama3-groq-8b-8192-tool-use-preview",
        "llama3-70b-8192",
        "llama3-8b-8192",
        
        # Mixtral models
        "mixtral-8x7b-32768",
        
        # Gemma models
        "gemma2-9b-it",
        "gemma-7b-it",
    ]
    
    print("Testing models...\n")
    print("-" * 70)
    
    working_models = []
    
    for model_name in models_to_test:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": "Hi"}],
                max_tokens=5
            )
            
            result = response.choices[0].message.content
            print(f"✅ {model_name}")
            print(f"   Response: {result}")
            working_models.append(model_name)
            
        except Exception as e:
            error_str = str(e)
            if "404" in error_str:
                print(f"❌ {model_name} - Not found/No access")
            elif "400" in error_str and "decommissioned" in error_str:
                print(f"❌ {model_name} - Decommissioned")
            else:
                print(f"❌ {model_name} - {error_str[:60]}")
    
    print("-" * 70)
    print(f"\n✅ WORKING MODELS: {len(working_models)}\n")
    
    if working_models:
        print("Available models for your API key:\n")
        for i, model in enumerate(working_models, 1):
            print(f"  {i}. {model}")
        
        print(f"\n💡 RECOMMENDED MODEL: {working_models[0]}")
        print(f"\nUpdate config/settings.py with:")
        print(f'GROQ_MODEL = "{working_models[0]}"')
    else:
        print("No working models found!")
        print("\nPossible reasons:")
        print("1. API key has limited access")
        print("2. All tested models are not available")
        print("3. Network/connectivity issues")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    find_working_models()
