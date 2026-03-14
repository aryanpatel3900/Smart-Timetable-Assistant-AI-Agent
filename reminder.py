import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_reminder(to_email, event_name, event_date, start_time):
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_PASSWORD")
    
    if not sender_email or not sender_password:
        return False, "Email credentials not set in .env file"
    
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = to_email
        msg["Subject"] = f"⏰ Reminder: {event_name}"
        
        body = f"""
        Hello!
        
        This is a reminder for your upcoming event:
        
        📌 Event: {event_name}
        📅 Date: {event_date}
        ⏰ Time: {start_time}
        
        Stay organized with Smart Timetable Assistant!
        """
        
        msg.attach(MIMEText(body, "plain"))
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()
        
        return True, "Reminder sent successfully!"
    except Exception as e:
        return False, f"Error: {str(e)}"