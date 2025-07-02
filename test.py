import smtplib
from email.message import EmailMessage

msg = EmailMessage()
msg['Subject'] = 'Test Email from Python'
msg['From'] = 'jevanchahal1@gmail.com'
msg['To'] = 'jevanchahal1@gmail.com'
msg.set_content('This is a plain text email sent using Python!')

with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login('jevanchahal1@gmail.com', 'kkvgjiswpgqzwqcj')
    smtp.send_message(msg)

print("Email sent!")