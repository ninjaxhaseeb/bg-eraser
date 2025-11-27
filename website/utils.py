import smtplib
from email.mime.text import MIMEText
import os
import json

current_file = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file)
FILE_PATH = os.path.join(current_dir,"..", "users.json")
FILE_PATH = os.path.abspath(FILE_PATH)

def load_users():
    try:
        with open(FILE_PATH, "r") as f:
            content = f.read().strip()
            if not content:   # file is empty
                return []
            return json.loads(content)
    except FileNotFoundError:
        return []

def save_users(users):
    with open(FILE_PATH, "w") as f:
        json.dump(users, f, indent=4)

def send_email(to_email, otp):
    sender = "background.eraser12@gmail.com"
    password = "xtld zhos vimb pvsa"

    msg = MIMEText(f"Hey there \n Your verification code is: {otp}")
    msg["Subject"] = "Verify Your Email"
    msg["From"] = sender
    msg["To"] = to_email

    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(sender, password)
    server.sendmail(sender, [to_email], msg.as_string())
    server.quit()
