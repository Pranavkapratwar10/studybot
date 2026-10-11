"""
Create admin user directly in database
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from database.db_manager import DatabaseManager
from auth.authentication import AuthManager

def create_admin_user():
    """Create admin user with username 'admin' and password 'admin123'"""
    print("Creating admin user...")
    
    db = DatabaseManager()
    auth = AuthManager(db)
    
    # Check if admin user already exists
    existing_user = db.get_user_by_username("admin")
    
    if existing_user:
        print("✅ Admin user already exists!")
        print(f"   Username: admin")
        print(f"   You can login with your password")
        return
    
    # Create admin user
    success, message = auth.register_user(
        username="admin",
        email="admin@studybot.local",
        password="admin123"
    )
    
    if success:
        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Password: admin123")
        print(f"   Email: admin@studybot.local")
        print("\nYou can now login at: http://localhost:8501")
    else:
        print(f"❌ Failed to create admin user: {message}")

if __name__ == "__main__":
    create_admin_user()
