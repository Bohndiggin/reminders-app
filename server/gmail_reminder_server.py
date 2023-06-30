import smtplib
import os
import json
from dotenv import load_dotenv

load_dotenv()

def gmail_bot_main(subject, message):
    with open('secrets.json', 'r') as f:
        secret_list = json.load(f)
    for i in secret_list['emails']:
        target_email = i
        email_content = message
        sending_email = os.getenv('GMAIL_ACCOUNT')
        sending_email_password = os.getenv('GMAIL_PASSWORD')
        email_subject = subject
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(sending_email, sending_email_password)
            server.sendmail(sending_email, target_email, f"Subject: {email_subject}\n\n{email_content}")
            server.quit()
            print("Email sent successfully")
        except Exception as e:
            print(f'error with gmail: {e}')

if __name__ == '__main__':
    gmail_bot_main('test boiii', 'testMsg')