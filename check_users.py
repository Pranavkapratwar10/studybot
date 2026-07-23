from database.db_manager import DatabaseManager

db = DatabaseManager()
users = db.get_all_users()

print(f"Total registered users: {len(users)}")
print("-" * 50)

if users:
    for user in users:
        print(f"Username: {user['username']}")
        print(f"Email: {user['email']}")
        print(f"Active: {user['is_active']}")
        print(f"Created: {user['created_at']}")
        print("-" * 50)
else:
    print("No users found in database.")
    print("\nYou need to REGISTER a new account first!")
    print("Click the 'Register' tab in the app to create an account.")
