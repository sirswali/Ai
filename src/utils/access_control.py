import os

class AccessControl:
    def __init__(self):
        self.allowed_users = set(os.environ.get("ALLOWED_USERS", "").split(","))

    def check_access(self, user_id):
        return user_id in self.allowed_users

    def add_user(self, user_id):
        self.allowed_users.add(user_id)

    def remove_user(self, user_id):
        self.allowed_users.discard(user_id)

    def get_allowed_users(self):
        return list(self.allowed_users)

# Usage example
if __name__ == "__main__":
    access_control = AccessControl()
    
    # Check access
    print(access_control.check_access("user123"))  # False
    
    # Add user
    access_control.add_user("user123")
    print(access_control.check_access("user123"))  # True
    
    # Remove user
    access_control.remove_user("user123")
    print(access_control.check_access("user123"))  # False
    
    # Get allowed users
    print(access_control.get_allowed_users())  # []