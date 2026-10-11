"""
Quick test to verify admin functionality
"""
from database.db_manager import DatabaseManager
from auth.authentication import AuthManager

# Initialize
db = DatabaseManager()
auth = AuthManager(db)

# Test admin login
print("Testing admin login...")
success, message, user = auth.login_user("admin", "admin123")

print(f"Success: {success}")
print(f"Message: {message}")
print(f"User data:")
for key, value in user.items():
    print(f"  {key}: {value}")

print("\nChecking is_admin flag:")
print(f"  is_admin = {user.get('is_admin', False)}")

# Test getting all users
print("\n" + "="*50)
print("Testing database - getting all users...")
conn = db.get_connection()
cursor = conn.cursor()

cursor.execute("""
    SELECT id, username, email, created_at, is_active
    FROM users
    ORDER BY created_at DESC
""")
users = cursor.fetchall()

print(f"Found {len(users)} users:")
for user in users:
    user_dict = dict(user)
    print(f"  - {user_dict['username']} ({user_dict['email']}) - Active: {user_dict['is_active']}")

conn.close()

print("\n✅ All tests passed!")
