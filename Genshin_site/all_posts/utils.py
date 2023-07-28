import os
from PIL import Image
from flask import current_app
from datetime import datetime

'''Сохранение изображения'''
def save_picture(image, name):
    try:
        full_path = os.path.join(current_app.root_path, 'static', 'images', 'posts')
        picture_path=os.path.join(full_path,name)
        output_size = (500,500)
        i=Image.open(image)
        i.thumbnail(output_size)
        i.save(picture_path)
        return True
    except Exception as e:
        print(e)
        return False
