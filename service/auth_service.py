from infrastructure.repositories.userRepo import UserRepository

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register_user(self, username, email, password):
        return self.user_repo.register_user(username, email, password)

    def login_user(self, email, password):
        return self.user_repo.login_user(email, password)
    
    def add_workspace_to_user(self, user_id, workspace_id):
        return self.user_repo.add_workspace_to_user(user_id, workspace_id)
    
    def remove_workspace_from_user(self, user_id, workspace_id):
        return self.user_repo.remove_workspace_from_user(user_id, workspace_id)

# Example usage:
# auth_service = AuthService()
# register_response = auth_service.register_user('username', 'email@example.com', 'password')
# print(register_response)
# login_response = auth_service.login_user('email@example.com', 'password')
# print(login_response)