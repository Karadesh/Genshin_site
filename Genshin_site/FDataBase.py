from transliterate import translit
import re
from flask import url_for
from flask_login import current_user
from Genshin_site.starter import Comments, Users, Offmenu, Posts, Feedback, Feedback_answer, db

class FDataBase:
    def __init__(self):
        self.__db = db
    
    def getOffmenu(self):
        sql = Offmenu.query.all()
        return sql
    
    def create_post(self, title, text, userid):
        trans_name = translit(title, language_code='ru', reversed=True)
        url = trans_name.replace(" ","_") 
        try:
            same_postname = Posts.query.filter(Posts.url==url).first()
            if same_postname:
                print("Статья с таким url уже существует")
                return False
            base = url_for('static', filename='images_html')
            text=re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>", "\\g<tag>" + base + "/\\g<url>>", text)
            new_post = Posts(title=title, text=text, url=url, userid=userid)
            db.session.add(new_post)
            db.session.commit()
        except:
            print("DB insertation error create_post")
            return False

    def get_post(self, alias):
        try:
            post_querry = Posts.query.filter(Posts.url==alias).first()
            post_list = {'title': post_querry.title, 'text': post_querry.text, 'url': post_querry.url, 'userid': post_querry.userid}
            return post_list
        except:
            print("Ошибка получения статьи из бд get_post")

    def delete_post(self, alias):
        try:
            delete_post = Posts.query.filter(Posts.url == alias).first()
            delete_comments = Comments.query.filter(Comments.postname == alias).all()
            db.session.delete(delete_post)
            db.session.commit()
            db.session.delete(delete_comments)
            db.session.commit()
        except:
            print("Ошибка удаления из бд delete_post")
        return (False, False)

    def getPostsAnonce(self):
        try:
            anonce = Posts.query.order_by(Posts.time.desc()).all()
            return anonce
        except:
            print("Ошибка получения постов getPostsAnonce")
        return []
    
    def getCommentsAnonce(self, url):
        try:
            comments_anonce = Comments.query.filter(Comments.postname==url).order_by(Comments.time).all()
            return comments_anonce
        except:
            print("Ошибка получения постов getCommentsAnonce")
        return []

    def getCommentatorsNames(self, alias):
        names_list = []
        try:
            commentator_names  = Comments.query.filter(Comments.postname==alias).all()
            for i in commentator_names:
                names_list.append(i.username)
            if names_list: return names_list
        except:
            print("Ошибка получения постов getCommentatorsNames")
        return []

    def getCommentatorsAvas(self, username):
        avas=[]
        try:
            for user in username:
                same_users = Users.query.filter(Users.login==user).all()
                for i in same_users:
                    avas.append({i.login : i.avatar})
            return avas
        except:
            print("Ошибка получения данных из БД getCommentatorsAvas")
        return False

    def create_comment(self, text, postname):
         try:
             username = current_user.getName()
             c = Comments(text=text, postname=postname, username=username)
             db.session.add(c)
             db.session.commit()
         except:
             print("DB insertation error create_comment")
             return False
         return True

    def delete_comment(self, id):
        try:
            comm_to_delete = Comments.query.filter(Comments.id==id).first()
            db.session.delete(comm_to_delete)
            db.session.commit()
        except:
            print("Ошибка удаления из бд delete_comment")
        return (False, False)

    def add_user(self, name, hpsh, email):
        try:
            same_user = Users.query.filter(Users.email==email or Users.login==name).all()
            if same_user:
                print("Пользователь с таким e-mail или именем пользователя уже существует")
                return False
            user_add = Users(login=name, password=hpsh, email=email)
            db.session.add(user_add)
            db.session.commit()
        except:
            print("Ошибка добавления в бд add_user")
            return False
        return True

    def getUser(self, user_id):
        try:
            get_user = Users.query.filter(Users.id==user_id).limit(1).first()
            if not get_user:
                print("Пользователь не найден")
                return False
            return get_user
        except:
            print("Ошибка получения данных из БД getUser")
        return False 

    def getUserByLogin(self, login):
        try:
            get_user = Users.query.filter(Users.login==login).limit(1).first()
            if not get_user:
                print("Пользователь не найден")
                return False
            return get_user
        except:
            print("Ошибка получения данных из БД getUserByLogin")
        return False 

    def updateUserAvatar(self, avatar, user_id):
        if not avatar:
            return False
        try:
            binary = bytearray(avatar)
            print(binary)
            user_table = Users.query.filter(Users.id==user_id).first()
            user_table.avatar = binary
            db.session.add(user_table)
            db.session.commit()
        except:
             print("Ошибка обновления аватара в БД: updateUserAvatar")
             return False
        return True
    
    def get_admin_posts(self):
        try:
            posts_list=[]
            admin_posts = Posts.query.all()
            for i in admin_posts:
                posts_list.append({'title' : i.title, 'text': i.text, 'url' : i.url})
            return posts_list
        except:
             print("Ошибка выборки постов в БД: get_admin_posts")
             return False

    def admin_users(self):
        try:
            users_list=[]
            admin_users = Users.query.all()
            for i in admin_users:
                users_list.append({'login' : i.login, 'email': i.email})
            return users_list
        except:
             print("Ошибка выборки постов в БД: get_admin_posts")
             return False
        
    def feedback_save(self, username, email, message):
        try:
            feedback_to_database = Feedback(email=email, username=username, message=message)
            db.session.add(feedback_to_database)
            db.session.commit()
            return True
        except:
             print("Ошибка добавления в БД: feedback_save")
             return False

    def admin_feedback(self):
        feedbacks = []
        try:
            admin_feedback_show = Feedback.query.filter(Feedback.isactive==True).all()
            print(admin_feedback_show)
            for i in admin_feedback_show:
                feedbacks.append({'id' : i.id, 'username' : i.username, 'email': i.email, 'message' : i.message})
            return feedbacks
        except:
             print("Ошибка выборки: admin_feedback")
             return False

    def get_feedback(self, id):
        try:
            fb = Feedback.query.filter(Feedback.id==id).first()
            feedback_dict = {'id' : fb.id, 'username': fb.username, 'email' : fb.email, 'message' : fb.message}
            return feedback_dict
        except:
             print("Ошибка выборки: get_feedback")
             return False

    def create_answer(self, feedbackid, username, email, message, admin_username, admin_message):
        try:
            answer_to_database = Feedback_answer(feedbackid=feedbackid, username=username, email=email, message=message, admin_username = admin_username, answer = admin_message)
            db.session.add(answer_to_database)
            db.session.commit()
            feedback_query = Feedback.query.filter(Feedback.id==feedbackid).first()
            feedback_query.isactive = False
            db.session.add(feedback_query)
            db.session.commit()
            return True
        except:
             print("Ошибка добавления в БД: create_answer")
             return False

            

