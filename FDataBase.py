import math
from pickle import FALSE
import time
import sqlite3
from transliterate import translit
import re
from flask import url_for

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM MENU'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print('DB reading error')
        return []
    
    def getOffmenu(self):
        sql = '''SELECT * FROM OFFMENU'''
        try:
            self.__cur.execute(sql)
            res = self.__cur.fetchall()
            if res: return res
        except:
            print('DB reading error')
        return []
    
    def create_post(self, title, text):
        trans_name = translit(title, language_code='ru', reversed=True)
        url = trans_name.replace(" ","_") 
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM posts WHERE url LIKE '{url}'")
            res = self.__cur.fetchone()
            if res['count'] >0:
                print("Статья с таким url уже существует")
                return False
            base = url_for('static', filename='images_html')
            text=re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>", "\\g<tag>" + base + "/\\g<url>>", text)
            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?)", (title, text, url, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("DB insertation error" +str(e))
            return False
        return True

    def get_post(self, alias):
        try:
            self.__cur.execute(f"SELECT title, text FROM POSTS WHERE url LIKE '{alias}' LIMIT 1")
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из бд" +str(e))
        return (False, False)

    def getPostsAnonce(self):
        try:
            self.__cur.execute(f"SELECT id, title, text, url FROM  posts ORDER BY time DESC")
            res = self.__cur.fetchall()
            if res: return res
        except sqlite3.Error as e:
            print("Ошибка получения постов" + str(e))
        return []

    def add_user(self, name, hpsh, email):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}' OR login like '{name}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким e-mail уже существует")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?)", (name, hpsh, email, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления в бд" + str(e))
            return False
        return True
    
    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))
        return False 

    def getUserByLogin(self, login):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE login ='{login}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД" + str(e))
        return False
