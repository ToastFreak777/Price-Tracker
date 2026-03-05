import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from dotenv import load_dotenv
import os

load_dotenv()


class EmailService:
    def __init__(self):
        self.app_email = os.getenv("APP_EMAIL", "")
        self.app_password = os.getenv("APP_PASSWORD", "")
        self.smtp_server = "smtp.gmail.com"
        self.port = 465

    def send_email(
        self,
        receiver: str,
        subject: str = "Price Alert",
        text_body: str = None,
        html_body: str = None,
    ) -> bool:
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"Price Tracker <{self.app_email}>"
            message["To"] = receiver

            text = text_body or """\
            Hi there,
            One of your tracked items has dropped below your target price. Log in to your account to check it out!
            """

            html = html_body or """\
            <html>
                <body>
                    <p style="font-family: Arial, sans-serif;">
                    Hi there,<br><br>
                    <strong>
                        One of your tracked items has dropped below your target price.
                    </strong><br>
                    Log in to your account to check it out!
                    </p>
                </body>
            </html>
            """

            part1 = MIMEText(text, "plain")
            part2 = MIMEText(html, "html")

            message.attach(part1)
            message.attach(part2)

            ctx = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.smtp_server, self.port, context=ctx) as server:
                server.login(self.app_email, self.app_password)
                server.sendmail(self.app_email, receiver, message.as_string())
                return True
        except smtplib.SMTPAuthenticationError:
            print("Authentication failed - check app credentials")
            return False
        except Exception as e:
            print(f"Email failed: {e}")
            return False
