from flask_mail import Message
from Genshin_site.starter import mail
from Genshin_site.FDataBase import FDataBase

def send_feedback_answer(feedback_answer):
    find_request = feedback_answer
    answer = find_request['answer']
    email = find_request['email']
    admin_user = find_request['admin_username']
    username = find_request['username']
    msg = Message('Ответ на обратную связь Genshin Guides',
                  sender='sender', #yandex лучше. Почта на яндексе
                  recipients=[email])
    msg.body = f'''Здравствуйте, {username}! {answer} Спасибо за обратную связь! {admin_user}'''
    mail.send(msg)