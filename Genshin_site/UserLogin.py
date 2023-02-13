from fileinput import filename
from flask_login import UserMixin
from flask import  url_for

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

    def getAvatar(self,app):
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

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext.upper() == "PNG" or ext.upper() == "JPEG" or ext.upper() == "JPG":
            return True
        return False
        