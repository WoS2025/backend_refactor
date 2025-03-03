from infrastructure.repositories.userRepo import UserRepository
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class AuthService:
    def __init__(self):
        self.user_repo = UserRepository()

    def register_user(self, username, email, password):
        return self.user_repo.register_user(username, email, password)

    def login_user(self, email, password):
        return self.user_repo.login_user(email, password)
    
    def update_password(self, email, password):
        return self.user_repo.update_password(email, password)
    
    def add_workspace_to_user(self, user_id, workspace_id):
        return self.user_repo.add_workspace_to_user(user_id, workspace_id)
    
    def remove_workspace_from_user(self, user_id, workspace_id):
        return self.user_repo.remove_workspace_from_user(user_id, workspace_id)

    def forgot_password(self, email):
        user = self.user_repo.find_user_by_email(email)
        if not user:
            return {"status": "error", "message": "Email not found"}

        # Generate a reset password link or token (for simplicity, using a dummy link here)
        reset_link = f"http://backend-refactor-nqz1.onrender.com/reset-password?email={email}"

        # Send email
        self.send_reset_email(email, reset_link)

        return {"status": "success", "message": "Password reset email sent"}

    def send_reset_email(self, to_email, reset_link):
        from_email = "noreply@backend-refactor-nqz1.onrender.com"
        gmail_user = "cengjianzhi18@gmail.com"
        # gmail_password = os.getenv('GMAIL_PASSWORD')  # Use an environment variable for the password
        gmail_app_password = os.getenv('GMAIL_APP_PASSWORD')
        subject = "Password Reset Request"
        body = f"Click the link to reset your password: {reset_link}"

        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        try:
            print("Connecting to SMTP server...")
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            print("Logging in to SMTP server...")
            server.login(gmail_user, gmail_app_password)
            text = msg.as_string()
            print("Sending email...")
            server.sendmail(from_email, to_email, text)
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            print(f"Failed to send email: {e}")

# Example usage:
# auth_service = AuthService()
# auth_service.forgot_password('user@example.com')