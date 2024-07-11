import smtplib
from email.mime.text import MIMEText

def send_email(sender, password, recipient, subject, body):
    """
    Отправка email уведомления.

    Args:
        sender (str): Адрес отправителя.
        password (str): Пароль отправителя.
        recipient (str): Адрес получателя.
        subject (str): Тема письма.
        body (str): Тело письма.
    """
    message = MIMEText(body)
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = recipient

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(sender, password)
            smtp.sendmail(sender, recipient, message.as_string())
        print('Email отправлен успешно.')
    except Exception as e:
        print('Ошибка отправки email:', e)
