from fileinput import filename
from flask_login import UserMixin
from flask import  url_for, current_app
import base64

class UserLogin(UserMixin):
    def fromDB(self, username):
        self.__user = username
        return self
    
    def create(self, user):
        self.__user = user
        return self
  
    def get_id(self):
        return str(self.__user.id)

    def getName(self):
        return self.__user.login if self.__user else "Без имени"
    
    def isActive(self):
        return self.__user.isactive if self.__user else "Не залогинен"
    
    def getEmail(self):
        return self.__user.email if self.__user else "Без email"
    
    def getCharacter(self):
        return self.__user.character if self.__user else "Без персонажа"

    def getAvatar(self,app=current_app):
        img=None
        if not self.__user.avatar:
            try:
                with app.open_resource(app.root_path + url_for('static', filename= 'images/default.jpeg'), "rb") as f:
                    img=f.read()
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию" +str(e))
        else:
            img = self.__user.avatar
        return img

    def getAdmin(self):
        return self.__user.admin if self.__user else "Без администраторства"

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext.upper() == "PNG" or ext.upper() == "JPEG" or ext.upper() == "JPG":
            return True
        return False
    
    def getProfileAvatar(self,app=current_app):
        img=None
        if not self.__user.avatar:
            try:
                with app.open_resource(app.root_path + url_for('static', filename= 'images/default.jpeg'), "rb") as f:
                    base64_string=base64.b64encode(f.read()).decode('utf-8')
                    img=f'data:image/png;base64,{base64_string}'  
            except FileNotFoundError as e:
                print("Не найден аватар по умолчанию" +str(e))
        else:
            img_ava = self.__user.avatar
            base64_string = base64.b64encode(img_ava).decode('utf-8')
            img=f'data:image/png;base64,{base64_string}'
        return img
        