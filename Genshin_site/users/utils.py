from flask_mail import Message
from Genshin_site.starter import mail
from flask import url_for, current_app, json
import base64
import os
from PIL import Image

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Запрос на сброс пароля', sender='', recipients=[user.email])
    msg.body = f'''Чтобы сбросить пароль, перейдите по следующей ссылке: {url_for('users.reset_token', token=token, _external=True)}. Если вы не делали этот запрос, просто проигнорируйте письмо, и никаких изменений не будет.'''
    mail.send(msg)

def background_maker(image_string, app=current_app):
    if image_string== None:
        return image_string
    else:
        try:
            image_string=image_string.replace(" ", "_")
            with app.open_resource(app.root_path + url_for('static', filename= f'images/backgrounds/{image_string}.jpeg'), "rb") as f:
                base64_string=base64.b64encode(f.read()).decode('utf-8')
                image=f'data:image/png;base64,{base64_string}'
                return image  
        except FileNotFoundError as e:
            print("Не найден аватар по умолчанию" +str(e))
            return None
        
def save_avatar(file,image_name):
    try:
        full_path = os.path.join(current_app.root_path, 'static', 'images', 'avatars')
        picture_path=os.path.join(full_path,image_name)
        output_size = (150,150)
        i=Image.open(file)
        i.thumbnail(output_size)
        i.save(picture_path)
        return True
    except Exception as e:
        print(e)
        return False
    
def ach_imagemaker(image_name):
    with current_app.open_resource(current_app.root_path + url_for('static', filename= image_name), "rb") as f:
        base64_string=base64.b64encode(f.read()).decode('utf-8')
        img=f'data:image/png;base64,{base64_string}'
    return img
        