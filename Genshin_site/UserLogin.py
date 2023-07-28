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

    def getAvatar(self):
        try:
            return self.__user.avatar
        except FileNotFoundError as e:
            print("Не найден аватар по умолчанию" +str(e))

    def getAdmin(self):
        return self.__user.admin if self.__user else "Без администраторства"

    def verifyExt(self, filename):
        ext = filename.rsplit('.', 1)[1]
        if ext.upper() == "PNG" or ext.upper() == "JPEG" or ext.upper() == "JPG":
            return True
        return False
    
    def getProfileAvatar(self,app=current_app):
        img=None
        try:
            return self.__user.avatar  
        except FileNotFoundError as e:
                print("Не найден аватар по умолчанию" +str(e))
                return False
        
    def getAuthors(self):
        authors=[]
        if self.__user.authorone != None:
            authors.append(self.__user.authorone)
        if self.__user.authortwo != None:
            authors.append(self.__user.authortwo)
        if self.__user.authorthree != None:
            authors.append(self.__user.authorthree)
        return authors
    
    def charChecker(self, char_num):
        if char_num=="1":
            if self.__user.characterone=="default":
                return False
            else:
                return True
        elif char_num=="2":
            if self.__user.charactertwo=="default":
                return False
            else:
                return True
        elif char_num=="3":
            if self.__user.characterthree=="default":
                return False
            else:
                return True
