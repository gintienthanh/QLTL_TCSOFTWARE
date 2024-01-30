from django.core.mail import EmailMessage
import os
from dotenv import load_dotenv
# Load biến môi trường từ tệp .env
load_dotenv()
class Util:
  @staticmethod
  def send_email(data):
    email = EmailMessage(
      subject=data['subject'],
      body=data['body'],
      from_email=os.environ.get('EMAIL_USER'),
      to=[data['to_email']]
    )
    email.send()