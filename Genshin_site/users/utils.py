from flask_mail import Message
from Genshin_site.starter import mail
from flask import url_for

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Запрос на сброс пароля', sender='', recipients=[user.email])
    msg.body = f'''Чтобы сбросить пароль, перейдите по следующей ссылке: {url_for('users.reset_token', token=token, _external=True)}. Если вы не делали этот запрос, просто проигнорируйте письмо, и никаких изменений не будет.'''
    mail.send(msg)