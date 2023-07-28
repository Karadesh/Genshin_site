from flask_mail import Message
from Genshin_site.starter import mail
import os
from PIL import Image
from flask import current_app

'''Отправка фидбека пользователю по e-mail'''
def send_feedback_answer(feedback_answer):
    find_request = feedback_answer
    answer = find_request['answer']
    email = find_request['email']
    admin_user = find_request['admin_username']
    username = find_request['username']
    msg = Message('Ответ на обратную связь Genshin Guides',
                  sender='', #yandex лучше. Почта на яндексе
                  recipients=[email])
    msg.body = f'''Здравствуйте, {username}! {answer} Спасибо за обратную связь! {admin_user}'''
    mail.send(msg)

'''Сохранение изображения персонажа'''
def save_character_image(image, image_name, checker):
    print(checker)
    if checker==False:
        return True
    else:
        try:
            full_path = os.path.join(current_app.root_path, 'static', 'images', 'posts')
            picture_path=os.path.join(full_path,image_name)
            i=Image.open(image)
            i.save(picture_path)
            return True
        except Exception as e:
            print("save_character_image"+str(e))
            return False