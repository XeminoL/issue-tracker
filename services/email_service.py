import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from html import escape


class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', 587))
        self.sender_email = os.getenv('SENDER_EMAIL', 'noreply@issue-tracker.com')
        self.sender_password = os.getenv('SENDER_PASSWORD', '')

    def send_email(self, recipient_email, subject, html_content):
        if not self.sender_password:
            print(f"[EMAIL] Skipping email (no SENDER_PASSWORD configured): {subject}")
            return True

        try:
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = recipient_email

            part = MIMEText(html_content, 'html')
            message.attach(part)

            with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())

            print(f"[EMAIL] Sent to {recipient_email}: {subject}")
            return True
        except (smtplib.SMTPException, OSError, TimeoutError) as e:
            print(f"[EMAIL] Failed to send to {recipient_email}: {str(e)}")
            return False

    def send_issue_created_email(self, recipient_email, issue_title, issue_description, tenant_name):
        subject = f"[{escape(tenant_name)}] New Issue: {escape(issue_title)}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>New Issue Created</h2>
                <p>A new issue has been created in your workspace <strong>{escape(tenant_name)}</strong>:</p>
                <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #007bff;">
                    <h3>{escape(issue_title)}</h3>
                    <p>{escape(issue_description or 'No description')}</p>
                </div>
                <p><a href="#" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">View Issue</a></p>
                <hr>
                <p style="color: #666; font-size: 12px;">Issue Tracker</p>
            </body>
        </html>
        """
        return self.send_email(recipient_email, subject, html_content)

    def send_issue_assigned_email(self, recipient_email, issue_title, assigner_name, tenant_name):
        subject = f"[{escape(tenant_name)}] Issue Assigned: {escape(issue_title)}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Issue Assigned to You</h2>
                <p><strong>{escape(assigner_name)}</strong> assigned you an issue in <strong>{escape(tenant_name)}</strong>:</p>
                <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #28a745;">
                    <h3>{escape(issue_title)}</h3>
                </div>
                <p><a href="#" style="background-color: #28a745; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">View Issue</a></p>
                <hr>
                <p style="color: #666; font-size: 12px;">Issue Tracker</p>
            </body>
        </html>
        """
        return self.send_email(recipient_email, subject, html_content)

    def send_welcome_email(self, recipient_email, user_name, workspace_name):
        subject = f"Welcome to {workspace_name}"
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>Welcome, {user_name}!</h2>
                <p>Your workspace <strong>{workspace_name}</strong> has been created successfully.</p>
                <p>You can now:</p>
                <ul>
                    <li>Create and manage issues</li>
                    <li>Assign issues to team members</li>
                    <li>Track issue status</li>
                </ul>
                <p><a href="#" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 4px;">Go to Dashboard</a></p>
                <hr>
                <p style="color: #666; font-size: 12px;">Issue Tracker</p>
            </body>
        </html>
        """
        return self.send_email(recipient_email, subject, html_content)


email_service = EmailService()
