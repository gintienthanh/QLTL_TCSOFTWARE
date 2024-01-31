import os
from django.core.mail import EmailMultiAlternatives
from dotenv import load_dotenv
from django.utils.html import strip_tags
# Load biến môi trường từ tệp .env
load_dotenv()
class Util:
  @staticmethod
  def send_email(data):
    html_content = data['body']
    text_content = strip_tags(html_content)
    msg = EmailMultiAlternatives(data['subject'], text_content, os.environ.get('EMAIL_USER'), [data['to_email']])
    msg.attach_alternative(html_content, "text/html")
    msg.send()