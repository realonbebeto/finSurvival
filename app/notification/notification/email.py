import smtplib
import json
from email.message import EmailMessage
from notification.config import settings


def notification(message):
    # try:
    message = json.loads(message)
    profile_id = message["profile_id"]
    sender_address = settings.GMAIL_ADDRESS
    sender_password = settings.GMAIL_PASSWORD
    receiver_address = message["username"]

    msg = EmailMessage()
    msg.set_content(f"Credit Report of id: {profile_id} is now ready!")
    msg["Subject"] = "View Credit Report"
    msg["From"] = sender_address
    msg["To"] = receiver_address

    session = smtplib.SMTP("smtp.gmail.com", 587)
    session.starttls()
    session.login(sender_address, sender_password)
    session.send_message(msg, sender_address, receiver_address)
    session.quit()
    print("Mail Sent")


# except Exception as err:
# print(err)
# return err
