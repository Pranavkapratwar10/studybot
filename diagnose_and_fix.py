"""
Comprehensive Diagnostic and Quick Fix Script
Checks all components and provides actionable fixes
"""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def print_header(title):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_section(title):
    """Print section header"""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print(f"{'─' * 70}")

def check_dependencies():
    """Check if all required packages are installed"""
    print_section("1. Checking Dependencies")
    
    required_packages = {
        'streamlit': 'streamlit',
        'chromadb': 'chromadb',
        'sentence_transformers': 'sentence-transformers',
        'groq': 'groq',
        'bcrypt': 'bcrypt',
        'docx': 'python-docx',
        'pypdf': 'pypdf',
        'pandas': 'pandas',
        'plotly': 'plotly',
        'langchain_text_splitters': 'langchain-text-splitters',
        'toml': 'toml'
    }
    
    missing = []
    installed = []
    
    for package, install_name in required_packages.items():
        try:
            __import__(package)
            print(f"  ✅ {install_name}")
            installed.append(install_name)
        except ImportError:
            print(f"  ❌ {install_name} - NOT INSTALLED")
            missing.append(install_name)
    
    if missing:
        print(f"\n  ⚠️  Missing {len(missing)} package(s)")
        print(f"\n  Fix: Run this command:")
        print(f"  pip install {' '.join(missing)}")
        return False
    else:
        print(f"\n  ✅ All {len(installed)} packages installed!")
        return True

def check_directories():
    """Check if required directories exist"""
    print_section("2. Checking Directories")
    
    required_dirs = [
        "data",
        "data/chroma_db",
        "data/uploads",
        ".streamlit"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        full_path = project_root / dir_path
        if full_path.exists():
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} - MISSING")
            all_exist = False
    
    if not all_exist:
        print(f"\n  ⚠️  Some directories missing")
        print(f"  Fix: Run Python and execute:")
        print(f"  >>> from config.settings import initialize_directories")
        print(f"  >>> initialize_directories()")
        return False
    else:
        print(f"\n  ✅ All directories exist!")
        return True

def check_api_key():
    """Check Groq API key"""
    print_section("3. Checking Groq API Key")
    
    api_key = None
    
    # Check secrets.toml
    secrets_path = project_root / ".streamlit" / "secrets.toml"
    if secrets_path.exists():
        try:
            import toml
            secrets = toml.load(secrets_path)
            api_key = secrets.get('GROQ_API_KEY')
            
            if api_key:
                if api_key == "gsk_REPLACE_WITH_YOUR_API_KEY_FROM_console.groq.com":
                    print(f"  ❌ API key is placeholder - NOT CONFIGURED")
                    print(f"  📍 Location: .streamlit/secrets.toml")
                elif api_key.startswith("gsk_"):
                    print(f"  ✅ API key found: {api_key[:20]}...")
                    os.environ['GROQ_API_KEY'] = api_key
                else:
                    print(f"  ⚠️  API key format looks wrong")
                    print(f"  Expected format: gsk_...")
            else:
                print(f"  ❌ No API key in secrets.toml")
        except Exception as e:
            print(f"  ❌ Error reading secrets: {e}")
    else:
        print(f"  ❌ secrets.toml not found")
    
    # Check environment variable
    env_key = os.getenv('GROQ_API_KEY')
    if env_key:
        print(f"  ℹ️  API key also in environment")
        api_key = env_key
    
    if not api_key or api_key == "gsk_REPLACE_WITH_YOUR_API_KEY_FROM_console.groq.com":
        print(f"\n  ⚠️  API key NOT configured")
        print(f"\n  Fix:")
        print(f"  1. Visit: https://console.groq.com")
        print(f"  2. Sign up for FREE (no credit card)")
        print(f"  3. Create an API key")
        print(f"  4. Update .streamlit/secrets.toml with your key")
        return False
    
    return True

def test_groq_api():
    """Test Groq API connection"""
    print_section("4. Testing Groq API")
    
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
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
    
    if not api_key or api_key == "gsk_REPLACE_WITH_YOUR_API_KEY_FROM_console.groq.com":
        print(f"  ⏭️  Skipped - No valid API key configured")
        return False
    
    try:
        from groq import Groq
        from config.settings import GROQ_MODEL
        
        client = Groq(api_key=api_key)
        
        # Test with simple query using the configured model
        print(f"  🔄 Testing API call with model: {GROQ_MODEL}...")
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": "Say hi in one word"}],
            max_tokens=5
        )
        
        result = response.choices[0].message.content
        print(f"  ✅ API is working!")
        print(f"  📝 Test response: {result}")
        return True
        
    except Exception as e:
        error_str = str(e)
        print(f"  ❌ API test failed")
        print(f"  Error: {error_str[:100]}")
        
        if "401" in error_str or "Invalid API Key" in error_str:
            print(f"\n  ⚠️  Invalid API key!")
            print(f"  Fix: Get a new key from https://console.groq.com")
        elif "404" in error_str or "does not exist" in error_str:
            print(f"\n  ⚠️  Model not found!")
            print(f"  Fix: Run 'python list_available_models.py' to find working models")
        elif "rate_limit" in error_str.lower():
            print(f"\n  ⚠️  Rate limit exceeded")
            print(f"  Fix: Wait a few minutes and try again")
        
        return False

def check_config():
    """Check configuration settings"""
    print_section("5. Checking Configuration")
    
    try:
        from config.settings import (
            GROQ_MODEL, DATABASE_PATH, CHROMA_DB_PATH,
            UPLOAD_DIR, EMBEDDING_MODEL
        )
        
        print(f"  ✅ Config loaded successfully")
        print(f"\n  Current Settings:")
        print(f"    • LLM Model: {GROQ_MODEL}")
        print(f"    • Embedding Model: {EMBEDDING_MODEL}")
        print(f"    • Database: {DATABASE_PATH.name}")
        print(f"    • Vector DB: {CHROMA_DB_PATH.name}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Config error: {e}")
        return False

def check_database():
    """Check database setup"""
    print_section("6. Checking Database")
    
    try:
        from database.db_manager import DatabaseManager
        
        db = DatabaseManager()
        print(f"  ✅ Database initialized")
        
        # Check if database file exists
        from config.settings import DATABASE_PATH
        if DATABASE_PATH.exists():
            size = DATABASE_PATH.stat().st_size
            print(f"  ✅ Database file exists ({size} bytes)")
        else:
            print(f"  ℹ️  Database will be created on first use")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database error: {e}")
        return False

def check_imports():
    """Check if all modules can be imported"""
    print_section("7. Checking Module Imports")
    
    modules_to_check = [
        ('config.settings', 'Configuration'),
        ('database.db_manager', 'Database Manager'),
        ('auth.authentication', 'Authentication'),
        ('rag.document_processor', 'Document Processor'),
        ('rag.vector_store', 'Vector Store'),
        ('rag.rag_pipeline', 'RAG Pipeline'),
        ('llm.groq_client', 'Groq Client'),
        ('llm.prompts', 'Prompts'),
        ('utils.helpers', 'Helpers'),
    ]
    
    all_good = True
    for module_name, display_name in modules_to_check:
        try:
            __import__(module_name)
            print(f"  ✅ {display_name}")
        except Exception as e:
            print(f"  ❌ {display_name}: {str(e)[:50]}")
            all_good = False
    
    if all_good:
        print(f"\n  ✅ All modules can be imported!")
    else:
        print(f"\n  ⚠️  Some modules have import errors")
    
    return all_good

def run_full_diagnostic():
    """Run all diagnostic checks"""
    print_header("RAG CHATBOT - DIAGNOSTIC TOOL")
    print("This tool will check your setup and identify any issues.")
    
    results = {}
    
    # Run all checks
    results['dependencies'] = check_dependencies()
    results['directories'] = check_directories()
    results['api_key'] = check_api_key()
    results['groq_api'] = test_groq_api()
    results['config'] = check_config()
    results['database'] = check_database()
    results['imports'] = check_imports()
    
    # Summary
    print_header("DIAGNOSTIC SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n  Tests Passed: {passed}/{total}\n")
    
    for check_name, status in results.items():
        status_icon = "✅" if status else "❌"
        print(f"  {status_icon} {check_name.replace('_', ' ').title()}")
    
    if passed == total:
        print("\n" + "🎉" * 35)
        print("  ALL CHECKS PASSED! Your setup is ready to go!")
        print("🎉" * 35)
        print("\n  Next steps:")
        print("  1. Run: streamlit run app.py")
        print("  2. Register an account")
        print("  3. Upload study materials")
        print("  4. Start chatting!")
    else:
        print("\n" + "⚠️ " * 35)
        print("  ISSUES FOUND - Please fix them:")
        print("⚠️ " * 35)
        
        if not results['dependencies']:
            print("\n  📦 Install missing packages:")
            print("     pip install -r requirements.txt")
        
        if not results['api_key'] or not results['groq_api']:
            print("\n  🔑 Get Groq API Key:")
            print("     1. Visit: https://console.groq.com")
            print("     2. Sign up (FREE, no credit card)")
            print("     3. Create API key")
            print("     4. Update .streamlit/secrets.toml")
        
        if not results['directories']:
            print("\n  📁 Create directories:")
            print("     python -c \"from config.settings import initialize_directories; initialize_directories()\"")
        
        print("\n  📖 For detailed instructions, see: FIX_GUIDE.md")
    
    print("\n" + "=" * 70 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = run_full_diagnostic()
    sys.exit(0 if success else 1)
