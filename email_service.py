import smtplib
from email.mime.text import MIMEText
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_email(to_email, subject, body, config):
    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = config['EMAIL_USER']
        msg['To'] = to_email

        with smtplib.SMTP(config['EMAIL_SERVER'], config['EMAIL_PORT']) as server:
            server.starttls()
            server.login(config['EMAIL_USER'], config['EMAIL_PASSWORD'])
            server.send_message(msg)
        logger.info(f"Email sent successfully to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        return False