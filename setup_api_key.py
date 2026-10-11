"""
Interactive API Key Setup Script
Helps users configure their Groq API key easily
"""
import os
from pathlib import Path

def setup_api_key():
    """Interactive setup for Groq API key"""
    print("=" * 70)
    print("  🔑 GROQ API KEY SETUP")
    print("=" * 70)
    print()
    print("This script will help you set up your FREE Groq API key.")
    print()
    
    # Step 1: Instructions
    print("📋 Step 1: Get Your FREE API Key")
    print("-" * 70)
    print()
    print("1. Open your browser and go to: https://console.groq.com")
    print("2. Sign up or log in (it's FREE, no credit card needed!)")
    print("3. Click on 'API Keys' in the sidebar")
    print("4. Click 'Create API Key'")
    print("5. Copy your new API key (it starts with 'gsk_')")
    print()
    print("💡 Tip: Keep the browser tab open so you can paste the key!")
    print()
    
    input("Press Enter when you have your API key ready...")
    print()
    
    # Step 2: Get API key from user
    print("📝 Step 2: Enter Your API Key")
    print("-" * 70)
    print()
    
    while True:
        api_key = input("Paste your Groq API key here: ").strip()
        
        # Validate format
        if not api_key:
            print("❌ No key entered. Please try again.")
            continue
        
        if not api_key.startswith("gsk_"):
            print("⚠️  Warning: Groq API keys typically start with 'gsk_'")
            confirm = input("Continue anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                continue
        
        if len(api_key) < 20:
            print("⚠️  Warning: This key seems too short.")
            confirm = input("Continue anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                continue
        
        break
    
    print()
    print("✅ API key received!")
    print()
    
    # Step 3: Update secrets.toml
    print("💾 Step 3: Saving Configuration")
    print("-" * 70)
    print()
    
    project_root = Path(__file__).parent
    secrets_dir = project_root / ".streamlit"
    secrets_file = secrets_dir / "secrets.toml"
    
    # Create directory if needed
    secrets_dir.mkdir(exist_ok=True)
    
    # Read existing admin password if file exists
    admin_password = "admin123"  # default
    if secrets_file.exists():
        try:
            with open(secrets_file, 'r') as f:
                content = f.read()
                for line in content.split('\n'):
                    if line.strip().startswith('ADMIN_PASSWORD'):
                        admin_password = line.split('=')[1].strip().strip('"')
                        break
        except:
            pass
    
    # Write secrets file
    try:
        with open(secrets_file, 'w') as f:
            f.write("# Streamlit Secrets Configuration\n")
            f.write("# This file should NOT be committed to version control\n\n")
            f.write("# Groq API Key\n")
            f.write(f'GROQ_API_KEY = "{api_key}"\n\n')
            f.write("# Admin Password\n")
            f.write(f'ADMIN_PASSWORD = "{admin_password}"\n')
        
        print(f"✅ Configuration saved to: {secrets_file}")
        print()
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        print()
        print("Please manually update .streamlit/secrets.toml with:")
        print(f'GROQ_API_KEY = "{api_key}"')
        return False
    
    # Step 4: Test the API key
    print("🧪 Step 4: Testing API Key")
    print("-" * 70)
    print()
    print("Testing your API key with Groq...")
    print()
    
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        
        # Test with simple query
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": "Say 'Hello' in one word"}],
            max_tokens=5
        )
        
        result = response.choices[0].message.content
        print("✅ API key is VALID and WORKING!")
        print(f"✅ Test response from AI: {result}")
        print()
        
    except Exception as e:
        error_str = str(e)
        print("❌ API key test failed!")
        print(f"Error: {error_str[:100]}")
        print()
        
        if "401" in error_str or "Invalid API Key" in error_str:
            print("⚠️  The API key appears to be invalid.")
            print("Please double-check you copied the entire key correctly.")
            print("You can run this script again to try a different key.")
        elif "rate_limit" in error_str.lower():
            print("⚠️  Rate limit hit (this is normal if you just created the key).")
            print("Wait a minute and the key should work!")
        
        return False
    
    # Success!
    print("=" * 70)
    print("  🎉 SETUP COMPLETE!")
    print("=" * 70)
    print()
    print("Your RAG chatbot is now ready to use!")
    print()
    print("Next steps:")
    print("  1. Run: streamlit run app.py")
    print("  2. Register a new account")
    print("  3. Upload your study materials (PDF, DOCX, TXT)")
    print("  4. Start asking questions!")
    print()
    print("For full diagnostics, run: python diagnose_and_fix.py")
    print()
    print("=" * 70)
    
    return True

if __name__ == "__main__":
    import sys
    try:
        success = setup_api_key()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)
