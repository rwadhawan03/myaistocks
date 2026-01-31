import os
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class EmailService:
    """Email service for sending scheduled alerts and notifications."""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("SMTP_USER", "")

    async def send_email(self, to_email: str, subject: str, body: str, html_body: Optional[str] = None) -> bool:
        """Send an email to the specified recipient."""
        if not self.smtp_user or not self.smtp_password:
            print("Email service not configured. Skipping email send.")
            return False
        
        try:
            message = MIMEMultipart("alternative")
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject
            
            text_part = MIMEText(body, "plain")
            message.attach(text_part)
            
            if html_body:
                html_part = MIMEText(html_body, "html")
                message.attach(html_part)
            
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )
            
            return True
        except Exception as e:
            print(f"Failed to send email: {str(e)}")
            return False

    async def send_market_alert(self, to_email: str, user_name: str, alert_content: str, 
                                trigger_time: str, symbols: list = None) -> bool:
        """Send a market alert email."""
        time_label = "Morning Pre-Market" if trigger_time == "morning" else "Evening Post-Market"
        symbols_str = ", ".join(symbols) if symbols else "General Market"
        
        subject = f"Stock AI Alert - {time_label} Update"
        
        body = f"""Hello {user_name},

Here is your {time_label} stock market update:

Symbols: {symbols_str}

{alert_content}

---
This is an automated alert from Stock AI Analyst.
To manage your alerts, visit the Scheduler page in the application.
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
        .symbols {{ background: #e8e8e8; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Stock AI Alert - {time_label}</h2>
        </div>
        <div class="content">
            <p>Hello {user_name},</p>
            <p>Here is your {time_label} stock market update:</p>
            <div class="symbols">
                <strong>Symbols:</strong> {symbols_str}
            </div>
            <div style="white-space: pre-wrap;">{alert_content}</div>
        </div>
        <div class="footer">
            <p>This is an automated alert from Stock AI Analyst.</p>
            <p>To manage your alerts, visit the Scheduler page in the application.</p>
        </div>
    </div>
</body>
</html>
"""
        
        return await self.send_email(to_email, subject, body, html_body)

    async def send_welcome_email(self, to_email: str, user_name: str) -> bool:
        """Send a welcome email to new users."""
        subject = "Welcome to Stock AI Analyst"
        
        body = f"""Hello {user_name},

Welcome to Stock AI Analyst!

Your account has been successfully created. You can now:

1. View the Market Dashboard for real-time market summaries
2. Chat with our AI Analyst for personalized stock insights
3. Explore stocks, ETFs, and funds in the Market Explorer
4. Set up automated alerts in the Scheduler

Get started by logging into your account and exploring the features.

Best regards,
Stock AI Analyst Team
"""
        
        html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
        .content {{ background: #f9f9f9; padding: 20px; border-radius: 0 0 10px 10px; }}
        .feature {{ background: white; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #667eea; }}
        .footer {{ margin-top: 20px; font-size: 12px; color: #666; text-align: center; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Welcome to Stock AI Analyst</h1>
        </div>
        <div class="content">
            <p>Hello {user_name},</p>
            <p>Your account has been successfully created. You can now:</p>
            <div class="feature">
                <strong>Market Dashboard</strong><br>
                View real-time market summaries and indices
            </div>
            <div class="feature">
                <strong>AI Analyst Chat</strong><br>
                Get personalized stock insights and recommendations
            </div>
            <div class="feature">
                <strong>Market Explorer</strong><br>
                Explore stocks, ETFs, and funds with detailed analysis
            </div>
            <div class="feature">
                <strong>Scheduler</strong><br>
                Set up automated morning and evening alerts
            </div>
        </div>
        <div class="footer">
            <p>Best regards,<br>Stock AI Analyst Team</p>
        </div>
    </div>
</body>
</html>
"""
        
        return await self.send_email(to_email, subject, body, html_body)


email_service = EmailService()
