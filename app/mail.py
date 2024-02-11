import os
import smtplib
import tempfile
import configparser
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from app import settings

# Load SMTP server details from .env file
smtp_server = settings.EMAIL_SERVER
smtp_port = int(settings.EMAIL_PORT)  # Use 465 for SSL
smtp_username = settings.EMAIL_USERNAME
smtp_password = settings.EMAIL_PASSWORD

# send an email when user account is created
def send_welcome_email(user_name, user_password, user_email, user_credit):
    
    
    subject = 'Welcome to Audio Transcription'
    message = f"""
    Dear {user_name},

    Welcome to our service. Here are your login credentials:

    Username: {user_name}
    Password: {user_password}

    You have {user_credit} credits in your account.

    Please keep this information safe and do not share it with anyone.

    Thank you,
    Your Service Team
    """

    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = user_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))

    # Connect to the server, login, and send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Remove this line if using SSL
    server.login(smtp_username, smtp_password)
    server.send_message(msg)
    server.quit()
    print("Email sent successfully")

# Send an email to the user when the transcription is complete
def send_email(user_name, user_email, filename, file_content):
        
    subject = 'Transcription Complete'
    message = f'Dear {user_name}, Your audio transcription is complete. Please find the transcription file attached.\n\nThank you.'

    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = user_email
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    # Create a temporary file and attach it to the email
    with tempfile.NamedTemporaryFile(delete=False, mode='w') as temp_file:
        temp_file.write(str(file_content))
        temp_file.close()
        with open(temp_file.name, "r", encoding="utf-8-sig") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read().encode('utf-8'))  # Convert the string to bytes
        # encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}.txt",
        )
        msg.attach(part)
        os.unlink(temp_file.name)


    # Connect to the server, login, and send the email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Remove this line if using SSL
    server.login(smtp_username, smtp_password)
    server.send_message(msg)
    server.quit()
    print("Email sent successfully")

