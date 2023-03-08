from transliterate import translit
import re
from flask import url_for
from flask_login import current_user
from Genshin_site.starter import Comments, Users, Offmenu, Posts, Feedback, Feedback_answer, Characters, Admin_requests, db, PostsImages, Post_likes, PostOfDay
import random
from datetime import date
from sqlalchemy import func


class FDataBase:
    def __init__(self):
        self.__db = db
    
    def getOffmenu(self):
        sql = Offmenu.query.all()
        return sql
    
    def create_post(self, title, text, userid, character):
        trans_name = translit(title, language_code='ru', reversed=True)
        url = trans_name.replace(" ","_") 
        try:
            same_postname = Posts.query.filter(Posts.url==url).first()
            if same_postname:
                print("Статья с таким url уже существует")
                return False
            base = url_for('static', filename='images_html')
            text=re.sub(r"(?P<tag><img\s+[^>]*src=)(?P<quote>[\"'])(?P<url>.+?)(?P=quote)>", "\\g<tag>" + base + "/\\g<url>>", text)
            character = translit(character, language_code='ru', reversed=True)
            character = character.replace("'", "")
            character = character.replace("-", "")
            character = character.replace(" ", "")
            character = character.lower()
            new_post = Posts(title=title, text=text, url=url, userid=userid, character=character)
            db.session.add(new_post)
            db.session.commit()
        except:
            print("DB insertation error create_post")
            return False

    def get_post(self, alias):
        try:
            post_query = Posts.query.filter(Posts.url==alias).first()
            images=[]
            try:
                db_images = PostsImages.query.filter(PostsImages.Postsid==post_query.id).all()
                for i in db_images:
                    images.append(i.image)
            except:
                print("no images")
            post_list = {'id': post_query.id, 'title': post_query.title, 'text': post_query.text, 'url': post_query.url, 'userid': post_query.userid, 'isactive' : post_query.isactive, 'islocked' : post_query.islocked, 'images': images, 'postOfDay': post_query.postOfDay}
            return post_list
        except:
            print("Ошибка получения статьи из бд get_post")

    def get_post_id(self, alias):
        try:
            post_query = Posts.query.filter(Posts.title==alias).first()
            post_id = post_query.id
            return post_id
        except:
            print("Ошибка получения id из бд get_post_id")

    def like_post(self, postid,userid):
        try:
            searcher = Post_likes.query.filter(Post_likes.userid==userid and Post_likes.postid==postid).first()
            db.session.delete(searcher)
            db.session.commit()
        except:
            add_like = Post_likes(userid=userid, postid=postid)
            db.session.add(add_like)
            db.session.commit()
        return True

    def show_like(self, post_id, userid):
        try:
            searcher = Post_likes.query.filter(Post_likes.userid==userid and Post_likes.postid==post_id).first()
            if searcher == None:
                return False
            else:
                return True
        except:
            print('Ошибка выборки show_like')
    
    def how_likes(self, post_id):
        like=0
        searcher = Post_likes.query.filter(Post_likes.postid== post_id).all()
        for i in searcher:
            like+=1
        return like

    def add_images(self, img_string, post_id):
        try:
            add_image = PostsImages(Postsid=post_id, image=img_string)
            db.session.add(add_image)
            db.session.commit()
        except:
            print("Ошибка добавления в бд add_images")

    def lockpost(self, alias):
        try:
            lockingpost = Posts.query.filter(Posts.url==alias).first()
            if lockingpost.islocked==True:
                lockingpost.islocked=False
            else:
                lockingpost.islocked=True
            db.session.add(lockingpost)
            db.session.commit()
        except:
            print("Ошибка смены статуса поста lockpost")

    def delete_post(self, alias):
        try:
            delete_post = Posts.query.filter(Posts.url == alias).first()
            delete_post.isactive=False
            delete_post.reason='deleted by user'
            delete_post.changer=current_user.getName()
            db.session.add(delete_post)
            db.session.commit()
        except:
            print("Ошибка удаления из бд delete_post")
        return (False, False)

    def getPostsAnonce(self):
        try:
            anonce = Posts.query.filter(Posts.isactive==True).order_by(Posts.time.desc()).all()
            return anonce
        except:
            print("Ошибка получения постов getPostsAnonce")
        return []
    
    def getPostPreview(self, postid):
        try:
            image = PostsImages.query.filter(PostsImages.Postsid==postid).first()
            return image.image
        except:
            print("Не удалось найти изображение getPostPreview")
            return []
    
    def getPostsAnonceCharacter(self, alias):
        try:
            anonce = Posts.query.filter(Posts.isactive==True, Posts.character==alias).order_by(Posts.time.desc()).all()
            return anonce
        except:
            print("Ошибка получения постов getPostsAnonceCharacter")
        return []

    def getPostcreatorAvatar(self, url):
        try:
            posts_query = Posts.query.filter(Posts.url==url).first()
            users_query = Users.query.filter(Users.id==posts_query.userid).first()
            userava = {'username': users_query.login, 'avatar': users_query.avatar}
            return userava
        except:
            print("Ошибка получения аватаров getPostcreatorAvatar")
            return False
    
    def getCommentsAnonce(self, url):
        try:
            comments_anonce = Comments.query.filter(Comments.isactive==True, Comments.postname==url).order_by(Comments.time).all()
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

    def delete_comment(self, id, reason='deleted by user'):
        try:
            comm_to_delete = Comments.query.filter(Comments.id==id).first()
            comm_to_delete.isactive = False
            if reason=='deleted by user':
                try:
                    comm_to_delete.changer = current_user.getName()
                except:
                    print('Ошибка при удалении комментария delete_comment')
            else:
                comm_to_delete.changer='admin'
            comm_to_delete.reason = reason
            db.session.add(comm_to_delete)
            db.session.commit()
        except:
            print("Ошибка удаления из бд delete_comment")
        return (False, False)

    def add_user(self, name, hpsh, email, admin="user"):
        try:
            same_user = Users.query.filter(Users.email==email or Users.login==name).all()
            if same_user:
                print("Пользователь с таким e-mail или именем пользователя уже существует")
                return False
            if name=="karadesh":
                admin="god"
            user_add = Users(login=name, password=hpsh, email=email, admin=admin)
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
    
    def add_admin_request(self, name, admin_type, reason):
        try:
            same_request = Admin_requests.query.filter(Admin_requests.name==name).first()
            if same_request:
                return False
            else:
                try:
                    adm_request=Admin_requests(name=name, admin_type=admin_type, reason=reason)
                    db.session.add(adm_request)
                    db.session.commit()
                    return True
                except:
                    print('ошибка в добавлении реквеста add_admin_request')
        except:
            print('ошибка поиска реквеста add_admin_request')

    def get_admin_posts(self):
        try:
            posts_list=[]
            admin_posts = Posts.query.all()
            for i in admin_posts:
                posts_list.append({'title' : i.title, 'text': i.text, 'url' : i.url, 'isactive': i.isactive})
            return posts_list
        except:
             print("Ошибка выборки постов в БД: get_admin_posts")
             return False

    def admin_users(self):
        try:
            users_list=[]
            admin_users = Users.query.all()
            for i in admin_users:
                users_list.append({'id': i.id, 'login' : i.login, 'email': i.email, 'isactive': i.isactive})
            return users_list
        except:
             print("Ошибка выборки постов в БД: get_admin_posts")
             return False

    def admin_user_change_active(self, id):
        try:
            status_changer = Users.query.filter(Users.id==id).first()
            if status_changer.isactive==True:
                status_changer.isactive=False
            else:
                status_changer.isactive=True
            db.session.add(status_changer)
            db.session.commit()
            return True
        except:
            print("Ошибка изменения статуса: admin_user_change_active")
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

    def find_answer(self, feedback_id):
        try:
            answer = Feedback_answer.query.filter(Feedback_answer.feedbackid==feedback_id).first()
            return {'username': answer.username, 'email': answer.email, 'answer': answer.answer, 'admin_username': answer.admin_username}
        except:
            print('No answers find_answer')
            return ''

    def admin_add_character(self, name, url, image=None, story=None):
        try:
            char_searcher = Characters.query.filter(Characters.name==name).first()
            if char_searcher == None:
                char_searcher = Characters(name=name, image=image, url=url, story=story)
            else:
                if image!=None:
                    char_searcher.image=image
                if story!=None:
                    char_searcher.story=story
            db.session.add(char_searcher)
            db.session.commit()
        except:
            print("ошибка добавления персонажа admin_add_character")
            
    
    def admin_post_change_active(self, alias, reason):
        try:
            status_changer = Posts.query.filter(Posts.url==alias).first()
            if status_changer.isactive==True:
                status_changer.isactive=False
            else:
                status_changer.isactive=True
            status_changer.reason=reason
            status_changer.changer='admin'
            db.session.add(status_changer)
            db.session.commit()
            return True
        except:
            print("Ошибка изменения статуса: admin_post_change_active")
            return False
        
    def admin_list_requests(self):
        request_list=[]
        try:
            requests = Admin_requests.query.all()
            for i in requests:
                request_list.append({'name': i.name, 'type':i.admin_type, 'reason': i.reason})
            return request_list
        except:
            print("Ошибка выборки admin_list_request")
    
    def admin_delete_request(self,name):
        try:
            request_to_delete = Admin_requests.query.filter(Admin_requests.name==name).first()
            db.session.delete(request_to_delete)
            db.session.commit()
        except:
            print("Ошибка удаления admin_delete_request")

    def add_new_admin(self, username, type):
        try:
            new_admin=Users.query.filter(Users.login==username).first()
            new_admin.admin=type
            db.session.add(new_admin)
            db.session.commit()
            delete_request=Admin_requests.query.filter(Admin_requests.name==username).first()
            db.session.delete(delete_request)
            db.session.commit()
            return True
        except:
            print("Ошибка добавления админа add_new_admin")
            return False

    def getAdminCommentsAnonce(self, url):
        try:
            comments_anonce = Comments.query.filter(Comments.postname==url).order_by(Comments.time).all()
            return comments_anonce
        except:
            print("Ошибка получения постов getCommentsAnonce")
        return []
    
    def add_character(self, chars_dict):
        try:
            same_character = Characters.query.filter(Characters.name==chars_dict['name']).first()
            if same_character:
                print('Такой персонаж уже есть')
            else:
                addchar = Characters(name=chars_dict['name'], image=chars_dict['img'], url=chars_dict['url'])
                db.session.add(addchar)
                db.session.commit()
        except:
            print("Ошибка добавления персонажа add_character")
        return []

    def get_chars(self):
        chars_list = []
        try:
            chars = Characters.query.all()
            for i in chars:
                chars_list.append({'id': i.id, 'name': i.name, 'image': i.image, 'url': i.url, 'story': i.story})
            return chars_list
        except:
            print("Ошибка поиска списка в бд get_chars")
            return False

    def get_chars_names(self):
        chars_list = []
        try:
            chars = Characters.query.all()
            for i in chars:
                chars_list.append(i.name)
            return chars_list
        except:
            print("Ошибка поиска списка в бд get_chars_names")
            return False
    
    def get_char(self, url):
        try:
            char = Characters.query.filter(Characters.url==url).first()
            return char
        except:
            print("Ошибка поиска персонажа в бд get_char")
            return False
        
    def post_of_day(self):
        try:
            active_posts = Posts.query.filter(Posts.isactive==True, Posts.postOfDay==False).all()
            randint = random.randint(0, len(active_posts)-1)
            todays_post = active_posts[randint]
            post_adding = PostOfDay(title=todays_post.title, text=todays_post.text, url=todays_post.url, character=todays_post.character, userid=todays_post.userid,time=todays_post.time)
            db.session.add(post_adding)
            db.session.commit()
            return True
        except:
            print("Ошибка в добавлении поста дня")
            return False
        
    def make_daypost(self):
        current_date=str(date.today())
        todays_post =  PostOfDay.query.filter(PostOfDay.time==current_date).first()
        if todays_post==None:
            lucky_posts_list = []
            all_posts = Posts.query.filter(Posts.isactive==True, Posts.postOfDay==False).all()
            if (len(all_posts)+1)>5:
                counter=5
            else:
                counter=len(all_posts)+1
            for i in range(counter):
                randint = random.randint(0, len(all_posts)-1)
                lucky_post = all_posts[randint]
                lucky_posts_list.append(lucky_post)
            lucky_posts_list = set(lucky_posts_list)
            lucky_posts_list = list(lucky_posts_list)
            return lucky_posts_list
        else:
            return []

    def choose_daypost(self, id):
        current_date = str(date.today())
        same_post_of_day = PostOfDay.query.filter(PostOfDay.time == current_date).first()
        if same_post_of_day == None:
            try:
                post_searcher = Posts.query.filter(Posts.id==id).first()
                post_searcher.postOfDay=True
                db.session.add(post_searcher)
                db.session.commit()
                print(post_searcher)
                post_of_day = PostOfDay(title=post_searcher.title, text=post_searcher.text, url=post_searcher.url, character=post_searcher.character, userid=post_searcher.userid, postid=post_searcher.id, time=current_date)
                db.session.add(post_of_day)
                db.session.commit()
                return True
            except:
                print("Ошибка добавления поста дня choose_daypost")
                return False
        else:
            print("Пост дня уже существует")
            return False
    
    def show_post_of_day(self):
        current_date = str(date.today())
        images = []
        try:
            daypost = PostOfDay.query.filter(PostOfDay.time==current_date).first()
            image = PostsImages.query.filter(PostsImages.Postsid==daypost.postid).all()
            for i in image:
                images.append(i.image)
            post_of_day={'title': daypost.title, 'text': daypost.text, 'url': daypost.url, 'character': daypost.character, 'userid': daypost.userid, 'time': daypost.time, 'postid': daypost.postid, 'images': images}
            return post_of_day
        except:
            return []
    
    def dayposts_show(self):
        current_date = str(date.today())
        dayposts = []
        try:
            max_daypost= PostOfDay.query.filter(PostOfDay.time==current_date).first()
            if (max_daypost.id - 1) <3:
                counter=max_daypost.id
            else:
                counter = 3
            for i in range(counter-1):
                max_daypost = PostOfDay.query.filter(PostOfDay.id==(max_daypost.id-1)).first()
                image = PostsImages.query.filter(PostsImages.Postsid== max_daypost.postid).first()
                daypost={'title': max_daypost.title, 'url': max_daypost.url, 'image': image.image, 'time': max_daypost.time}
                dayposts.append(daypost)
            return dayposts
        except:
            print("Ошибка поиска постов дня dayposts_show")
            return []
        
    def dayposts_list(self):
        try:
            dayposts = PostOfDay.query.all()
            return dayposts
        except:
            print("Ошибка поиска постов дня dayposts_list")
            return []