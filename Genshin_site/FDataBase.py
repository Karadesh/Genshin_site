from transliterate import translit
import re
from flask import url_for, current_app, json
from flask_login import current_user
from Genshin_site.models import Comments, Users, Posts, Feedback, Feedback_answer, Characters, Admin_requests, db, PostsImages, Post_likes, PostOfDay, Week_likes, Achievments
import random
from datetime import date, datetime
import operator

class FDataBase:
    def __init__(self):
        self.__db = db
    
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
            element_searcher = Characters.query.filter(Characters.url==character).first()
            element = element_searcher.element
            new_post = Posts(title=title, text=text, url=url, userid=userid, character=character, element=element)
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
                    if i.image==None:
                        images=None
                    else:
                        images.append(i.image)
            except Exception as e:
                print(e)
            post_list = {'id': post_query.id, 'title': post_query.title, 'text': post_query.text, 'url': post_query.url, 'userid': post_query.userid, 'isactive' : post_query.isactive, 'islocked' : post_query.islocked, 'images': images, 'postOfDay': post_query.postOfDay}
            if post_list["id"] == None:
                return None
            return post_list
        except Exception as e:
            print(e)
            return None

    def get_post_id(self, alias):
        try:
            post_query = Posts.query.filter(Posts.title==alias).first()
            post_id = post_query.id
            return post_id
        except:
            print("Ошибка получения id из бд get_post_id")

    def like_post(self, postid, userid, creator):
        week_like = Week_likes.query.filter(Week_likes.userid==creator).first()
        user_searcher = Users.query.filter(Users.id==creator).first()
        if user_searcher==None:
            return False
        user_likes = user_searcher.howlikes
        if week_like==None:
            return False
        likes = week_like.likes
        post_searcher=Posts.query.filter(Posts.id==postid and Posts.userid==userid).first()
        if post_searcher==None:
            return False
        try:
            searcher = Post_likes.query.filter(Post_likes.userid==userid and Post_likes.postid==postid).first()
            db.session.delete(searcher)
            db.session.commit()
            likes=likes-1
            user_likes=user_likes-1
            week_like.likes=likes
            user_searcher.howlikes=user_likes
            db.session.add(week_like)
            db.session.commit()
            db.session.add(user_searcher)
            db.session.commit()
        except:
            post_finder = Posts.query.filter(Posts.id==postid).first()
            creatorid = post_finder.userid
            add_like = Post_likes(userid=userid, postid=postid, creatorid=creatorid)
            db.session.add(add_like)
            db.session.commit()
            likes=likes+1
            user_likes=user_likes+1
            week_like.likes=likes
            user_searcher.howlikes=user_likes
            db.session.add(week_like)
            db.session.commit()
            db.session.add(user_searcher)
            db.session.commit()
            self.likes_achievment(creator)
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
        for _ in searcher:
            like+=1
        return like
    
    def how_comments(self, url):
        post_comments=0
        searcher = Comments.query.filter(Comments.postname==url).all()
        for _ in searcher:
            post_comments+=1
        return post_comments

    def add_images(self, img_string, post_id):
        try:
            add_image = PostsImages(Postsid=post_id, image=img_string)
            db.session.add(add_image)
            db.session.commit()
        except Exception as e:
            print(e)

    def lockpost(self, alias):
        try:
            lockingpost = Posts.query.filter(Posts.url==alias).first()
            if lockingpost==None:
                return False
            if lockingpost.islocked==True:
                lockingpost.islocked=False
            else:
                lockingpost.islocked=True
            db.session.add(lockingpost)
            db.session.commit()
            return True
        except:
            print("Ошибка смены статуса поста lockpost")
            return False

    def delete_post(self, alias):
        post_deleter = Posts.query.filter(Posts.url == alias).first()
        if post_deleter == None:
            return False
        user_checker = current_user.get_id()
        if int(post_deleter.userid)==int(user_checker):
            try:
                post_deleter.isactive=False
                post_deleter.reason='deleted by user'
                post_deleter.changer=current_user.getName()
                db.session.add(post_deleter)
                db.session.commit()
                return True
            except:
                print("Ошибка удаления из бд delete_post")
                return (False, False)

    def getPostsAnonce(self, page_num):
        try:
            anonce = Posts.query.filter(Posts.isactive==True).order_by(Posts.time.desc()).paginate(per_page=5, page=page_num, error_out=True)
            return anonce
        except:
            print("Ошибка получения постов getPostsAnonce")
        return []
    
    def getPostsQuery(self,page_num, query_item):
        try:
            try:
                int(query_item)
                anonce = Posts.query.filter(Posts.userid==query_item, Posts.isactive==True).order_by(Posts.time.desc()).paginate(per_page=5, page=page_num, error_out=True)
            except:
                anonce = Posts.query.filter(Posts.element==query_item, Posts.isactive==True).order_by(Posts.time.desc()).paginate(per_page=5, page=page_num, error_out=True)
            return anonce
        except Exception as e:
            print("Ошибка получения постов getPostsElement" + str(e))
        return []
    
    def getPostPreviews(self, postid):
        try:
            image = PostsImages.query.filter(PostsImages.Postsid==postid).first()
            if image.image==None:
                return None
            else:
                return image.image
        except Exception as e:
            print("previews"+str(e))
            return None
   
    def getPostsAnonceCharacter(self, alias, page_num):
        try:
            posts_searcher=Posts.query.filter(Posts.isactive==True, Posts.character==alias).all()
            if posts_searcher==[]:
                return []
            anonce = Posts.query.filter(Posts.isactive==True, Posts.character==alias).order_by(Posts.time.desc()).paginate(per_page=5, page=page_num, error_out=True)
            return anonce
        except:
            print("Ошибка получения постов getPostsAnonceCharacter")
        return []

    def getPostcreatorAvatar(self, url):
        try:
            posts_query = Posts.query.filter(Posts.url==url).first()
            users_query = Users.query.filter(Users.id==posts_query.userid).first()
            userava = {'username': users_query.login, 'avatar': users_query.avatar, 'userid': users_query.id}
            return userava
        except Exception as e:
            print(e)
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
        avas={}
        try:
            for user in username:
                same_users = Users.query.filter(Users.login==user).all()
                for i in same_users:
                    avas[i.login] = i.avatar
            return avas
        except:
            print("Ошибка получения данных из БД getCommentatorsAvas")
        return False

    def create_comment(self, text, postname):
         try:
             username = current_user.getName()
             c = Comments(text=text, postname=postname, username=username, userid=current_user.get_id())
             db.session.add(c)
             db.session.commit()
         except Exception as e:
             print(e)
             return False
         return True

    def delete_comment(self, id, reason='deleted by user'):
        try:
            creator_checker = current_user.get_id()
            comm_to_delete = Comments.query.filter(Comments.id==id).first()
            if comm_to_delete==None:
                return False
            if reason=='deleted by user':
                try:
                    if int(comm_to_delete.userid) == int(creator_checker):
                        comm_to_delete.isactive = False
                        comm_to_delete.changer = current_user.getName()
                    else: 
                        return False
                except:
                    print('Ошибка при удалении комментария delete_comment')
                    return False
            else:
                admin_checker = Users.query.filter(Users.login==creator_checker).first()
                if admin_checker.admin == 'moderator' or admin_checker.admin == 'god': 
                    comm_to_delete.changer=creator_checker
                    comm_to_delete.isactive = False
            comm_to_delete.reason = reason
            db.session.add(comm_to_delete)
            db.session.commit()
            return True
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
        except Exception as e:
            print(e)
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
    
    def user_recommend(self, userid):
        user_id = current_user.get_id()
        login_owner = Users.query.filter(Users.id==user_id).first()
        if login_owner.authorone==None:
            login_owner.authorone=userid
            db.session.add(login_owner)
            db.session.commit()
            return True
        elif login_owner.authorone==int(userid):
            login_owner.authorone=None
            db.session.add(login_owner)
            db.session.commit()
            return True
        elif login_owner.authortwo==None:
            login_owner.authortwo=userid
            db.session.add(login_owner)
            db.session.commit()
            return True
        elif login_owner.authortwo==int(userid):
            login_owner.authortwo=None
            db.session.add(login_owner)
            db.session.commit()
            return True
        elif login_owner.authorthree==None:
            login_owner.authorthree=userid
            db.session.add(login_owner)
            db.session.commit()
            return True
        elif login_owner.authorthree==int(userid):
            login_owner.authorthree=None
            db.session.add(login_owner)
            db.session.commit()
            return True
        else:
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

    def updateUserAvatar(self, avatar_name, user_id):
        if not avatar_name:
            return False
        try:
            user_table = Users.query.filter(Users.id==user_id).first()
            user_table.avatar = avatar_name
            db.session.add(user_table)
            db.session.commit()
        except Exception as e:
             print("Ошибка обновления аватара в БД: updateUserAvatar"+str(e))
             return False
        return True
    
    def user_likes(self, userid):
        likes = 0
        posts = Post_likes.query.filter(Post_likes.creatorid==userid).all()
        for i in posts:
            likes = likes+1
        return likes

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
                posts_list.append({'id':i.id, 'title' : i.title, 'text': i.text, 'url' : i.url, 'isactive': i.isactive})
            return posts_list
        except:
             print("Ошибка выборки постов в БД: get_admin_posts")
             return False

    def admin_users(self):
        try:
            users_list=[]
            admin_users = Users.query.all()
            for i in admin_users:
                users_list.append({'id': i.id, 'login' : i.login, 'email': i.email, 'isactive': i.isactive, 'avatar': i.avatar})
            return users_list
        except:
             print("Ошибка выборки постов в БД: get_admin_posts")
             return False

    def admin_user_change_active(self, id):
        try:
            status_changer = Users.query.filter(Users.id==id).first()
            if status_changer==None:
                return None
            elif status_changer.isactive==True:
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
            if fb==None:
                return None
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

    def admin_add_character(self, name, url, image=None, story=None, element=None, country=None):
        try:
            char_searcher = Characters.query.filter(Characters.name==name).first()
            if char_searcher == None:
                char_searcher = Characters(name=name, image=image, url=url, story=story, element=element, country=country)
            else:
                if image!=None:
                    char_searcher.image=image
                if story!=None:
                    char_searcher.story=story
                if element!=None:
                    char_searcher.element=element
                if country!=None:
                    char_searcher.country=country
            db.session.add(char_searcher)
            db.session.commit()
        except:
            print("ошибка добавления персонажа admin_add_character")
            
    
    def admin_post_change_active(self, alias, reason):
        admin_checker = current_user.getAdmin()
        if admin_checker == 'moderator' or admin_checker == 'god':
            try:
                status_changer = Posts.query.filter(Posts.url==alias).first()
                if status_changer.isactive==True:
                    status_changer.isactive=False
                else:
                    status_changer.isactive=True
                status_changer.reason=reason
                status_changer.changer=current_user.getName()
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
            if request_to_delete==None:
                return None
            db.session.delete(request_to_delete)
            db.session.commit()
        except:
            print("Ошибка удаления admin_delete_request")

    def add_new_admin(self, username, type):
        try:
            new_admin=Users.query.filter(Users.login==username).first()
            if new_admin==None:
                return None
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
        except Exception as e:
            print(e)
        return []

    def get_chars(self):
        try:
            chars = Characters.query.order_by(Characters.id.desc()).all()
            return chars
        except Exception as e:
            print(e)
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

    def side_bar(self, element=None, userid=None):
        characters_list=[]
        if userid!=None:
            side_posts = Posts.query.filter(Posts.userid==userid, Posts.isactive==True).limit(2).all()
        else:
            side_posts =Posts.query.filter(Posts.element==element, Posts.isactive==True).limit(2).all()
        if side_posts!=[]:
            for i in side_posts:
                likes=0
                posts_likes=Post_likes.query.filter(Post_likes.postid==i.id).all()
                if posts_likes!=[]:
                        for j in posts_likes:
                            likes=likes+1
                comments=0
                posts_comments = Comments.query.filter(Comments.postname==i.url).all()
                if posts_comments!=[]:
                    for _ in posts_comments:
                        comments+=1
                try:
                    guide_image=PostsImages.query.filter(PostsImages.postid==i.id).first()
                    img=f'images/posts/{guide_image.image}'
                except:
                    img=f'images/characters/{i.character}.jpg'
                str_time = datetime.strftime(i.time, "%d/%m/%Y")
                characters_list.append({"guide":i, "image":img, "likes":likes, "comments":comments, "time":str_time})
            return characters_list
        else:
            return []
                    
     
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
                try:
                    randint = random.randint(0, len(all_posts)-1)
                    lucky_post = all_posts[randint]
                    lucky_posts_list.append(lucky_post)
                except:
                    print("Постов, подходящих под критерии, нет")
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
                if post_searcher==None:
                    return None
                post_searcher.postOfDay=True
                db.session.add(post_searcher)
                db.session.commit()
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
        dayposts = []
        try:
            max_daypost= PostOfDay.query.all()
            max_daypost = max_daypost[-1]
            image = PostsImages.query.filter(PostsImages.Postsid == max_daypost.postid).first()
            if image!=None:
                img=image.image
            else:
                img=None
            likes = Post_likes.query.filter(Post_likes.postid==max_daypost.postid).all()
            like = 0
            if likes == None:
                like = 0
            else:
                for i in likes:
                    like = like+1
            comments_counter = 0
            post_comments = Comments.query.filter(Comments.postname==max_daypost.url).all()
            if post_comments!=[]:
                for j in post_comments:
                    comments_counter+=1
            daypost={'title': max_daypost.title, 'text': max_daypost.text, 'url': max_daypost.url, 'character': max_daypost.character, 'userid': max_daypost.userid, 'time': max_daypost.time, 'postid': max_daypost.postid, 'images': img, 'likes': like, 'comments': comments_counter}
            dayposts.append(daypost)
            d = max_daypost.id - 1
            if d <= 6:
                counter=d
            else:
                counter = 6
            for i in range(counter):
                max_daypost = PostOfDay.query.filter(PostOfDay.id==(max_daypost.id-1)).first()
                image = PostsImages.query.filter(PostsImages.Postsid== max_daypost.postid).first()
                if image!=None:
                    daypost={'title': max_daypost.title, 'url': max_daypost.url, 'image': image.image, 'time': max_daypost.time}
                else:
                    daypost={'title': max_daypost.title, 'url': max_daypost.url, 'image': image, 'time': max_daypost.time}
                dayposts.append(daypost)
            return dayposts
        except Exception as e:
            print("Ошибка поиска постов дня dayposts_show" + str(e))
            return []
        
    def dayposts_list(self, page_num):
        try:
            dayposts = PostOfDay.query.order_by(PostOfDay.id.desc()).paginate(per_page=5, page=page_num, error_out=True)
            return dayposts
        except:
            print("Ошибка поиска постов дня dayposts_list")
            return []

    def user_social_sites(self, userid):
        total_list=[]
        try:
            user_searcher=Users.query.filter(Users.id==userid).first()
            websites_string=user_searcher.socialservices
            if websites_string==None:
                return total_list
            else:
                splited_sites=websites_string.split(',')
                counter=0
                for i in splited_sites:
                    i=i.replace('https://', '')
                    i=i.replace('http://', '')
                    i=i.replace('www.', '')
                    total_list.append(i)
                    counter+=1
                    if counter>=5:
                        break
                return total_list
        except Exception as e:
            print('user_social_sites error: ' + str(e))


    def user_best_post(self, userid):
        try:
            posts_dict={}
            user_posts=Posts.query.filter(Posts.userid==userid).all()
            if user_posts!=[]:
                for i in user_posts:
                    likes=Post_likes.query.filter(Post_likes.postid==i.id).all()
                    total_likes=len(likes)
                    posts_dict[i.id]=total_likes
                best_id=max(posts_dict.items(), key=operator.itemgetter(1))
                best_post=Posts.query.filter(Posts.id==best_id[0]).first()
                image=PostsImages.query.filter(PostsImages.Postsid==best_id[0]).first()
                if image!=None:
                    return {"id": best_post.id, "title": best_post.title, "url" : best_post.url, "likes" : best_id[1], "image": image.image}
                else:
                    return {"id": best_post.id, "title": best_post.title, "url" : best_post.url, "likes" : best_id[1], "image": image}
            else:
                return user_posts
        except Exception as e:
            print("user_best_post error"+str(e))
            return False

        
    def choose_character(self, character_name, char_num):
        try:
            user = Users.query.filter(Users.id==current_user.get_id()).first()
            if char_num=="1":
                user.characterone = character_name
            elif char_num=="2":
                user.charactertwo = character_name
            else:
                user.characterthree = character_name
            db.session.add(user)
            db.session.commit()
            return True
        except Exception as e:
            print("Пользователь не найден choose_character"+str(e))
            return False
        
    def delete_character(self, char_num):
        try:
            user = Users.query.filter(Users.id==current_user.get_id()).first()
            if char_num=="1":
                user.characterone = "default"
            elif char_num=="2":
                user.charactertwo = "default"
            else:
                user.characterthree = "default"
            db.session.add(user)
            db.session.commit()
            return True
        except Exception as e:
            print("Пользователь не найден delete_character"+str(e))
            return False
    
    def search_character_names(self, userid):
        try:
            user_searcher = Users.query.filter(Users.id==userid).first()
            characters_dict={}
            characters_list=[]
            character = user_searcher.characterone
            characters_list.append(character)
            character_two = user_searcher.charactertwo
            characters_list.append(character_two)
            character_three = user_searcher.characterthree
            characters_list.append(character_three)
            for i in characters_list:
                if i != "default":
                    character = translit(i, language_code='ru', reversed=True)
                    character = character.replace("'", "")
                    character = character.replace("-", "")
                    character = character.replace(" ", "")
                    character = character.lower()
                else:
                    character=i
                characters_dict[str(characters_list.index(i)+1)]=character
            return characters_dict
        except Exception as e:
            print("Персонаж не найден search_character_names"+ str(e))
            return False
            

    def search_character_image(self, userid):
        try:
            user_searcher = Users.query.filter(Users.id==userid).first()
            characters_dict={}
            character = user_searcher.characterone
            if character != "default":
                character = translit(character, language_code='ru', reversed=True)
                character = character.replace("'", "")
                character = character.replace("-", "")
                character = character.replace(" ", "")
                character = character.lower()
            characters_dict["1"]=character
            character = user_searcher.charactertwo
            if character != "default":
                character = translit(character, language_code='ru', reversed=True)
                character = character.replace("'", "")
                character = character.replace("-", "")
                character = character.replace(" ", "")
                character = character.lower()
            characters_dict["2"]=character
            character = user_searcher.characterthree
            if character != "default":
                character = translit(character, language_code='ru', reversed=True)
                character = character.replace("'", "")
                character = character.replace("-", "")
                character = character.replace(" ", "")
                character = character.lower()
            characters_dict["3"]=character
            return characters_dict
        except Exception as e:
            print("Персонаж не найден search_character_image"+ str(e))
            return False
        
    def search_user(id):
        try:
            user = Users.query.filter(Users.id== id).first()
            return user
        except:
            print("не вышло search_user")

    def search_user_by_email(self, email):
        user = Users.query.filter(Users.email==email).first()
        return user

    def verify_reset_tokens(self, token):
        same_token=token
        user = Users.verify_reset_token(same_token)
        return user
    
    def change_password(self, user, password):
        user.password = password
        db.session.add(user)
        db.session.commit()
        return True
    
    def character_searcher(self):
        chars=Characters.query.all()
        chars_list = []
        for i in chars:
            chars_list.append(i.name)
        return chars_list
    
    def my_guides(self, id, page_num):
        try:
            anonce = Posts.query.filter(Posts.isactive==True, Posts.userid==id).order_by(Posts.time.desc()).paginate(per_page=5, page=page_num, error_out=True)
            return anonce
        except:
            print("Ошибка получения постов my_guides")
            return []

    def add_socials(self, userid, site=None):
        social_string = site
        social_string = social_string.replace(' ', '')
        user_searcher = Users.query.filter(userid==Users.id).first()
        user_searcher.socialservices = user_searcher.socialservices +','+ social_string if user_searcher.socialservices != None else social_string
        db.session.add(user_searcher)
        db.session.commit()
        return True
    
    def del_social(self, site, userid):
        user_searcher = Users.query.filter(userid==Users.id).first()
        sites_string = user_searcher.socialservices
        sites_list = sites_string.split(',')
        try:
            sites_list.remove(site)
            new_sites_string=None
            for i in sites_list:
                new_sites_string=new_sites_string + ',' + i if new_sites_string != None else i
            user_searcher.socialservices = new_sites_string
            db.session.add(user_searcher)
            db.session.commit()
        except Exception as e:
            print('del_social', str(e))
            return False

    def user_data(self, id, app=current_app):
        try:
            udata = Users.query.filter(Users.id==id).first()
            if udata==None:
                return udata    
            str_time = datetime.strftime(udata.time, "%d/%m/%Y %H:%M")
            socials_string = udata.socialservices
            try:
                socials_list = socials_string.split(',') if socials_string != '' else None
            except:
                socials_list = None
            sorted_data = {"id":udata.id, "login":udata.login, "time":str_time, "character":udata.character, "avatar":udata.avatar, "active_background": udata.activebackground, "author_one": udata.authorone, "author_two": udata.authortwo, "author_three": udata.authorthree, "show_authors": udata.showauthors, "showauthors":udata.showauthors, "showcharacters":udata.showcharacters, "bestpostshow":udata.bestpostshow, "socialshow": udata.socialshow, "socialservices" : socials_list}
            return sorted_data
        except Exception as e:
            print("Ошибка поиска профиля user_data" + str(e))
            return None
        
    def show_authors(self):
        user_searcher= Users.query.filter(Users.id==current_user.get_id()).first()
        if user_searcher.showauthors==True:
            user_searcher.showauthors=False
        else:
            user_searcher.showauthors=True
        db.session.add(user_searcher)
        db.session.commit()
        return True

    def show_socials(self):
        user_searcher= Users.query.filter(Users.id==current_user.get_id()).first()
        if user_searcher.socialshow==True:
            user_searcher.socialshow=False
        else:
            user_searcher.socialshow=True
        db.session.add(user_searcher)
        db.session.commit()
        return True
    
    def show_characters(self):
        user_searcher= Users.query.filter(Users.id==current_user.get_id()).first()
        if user_searcher.showcharacters==True:
            user_searcher.showcharacters=False
        else:
            user_searcher.showcharacters=True
        db.session.add(user_searcher)
        db.session.commit()
        return True
    
    def show_best_post(self):
        user_searcher= Users.query.filter(Users.id==current_user.get_id()).first()
        if user_searcher.bestpostshow==True:
            user_searcher.bestpostshow=False
        else:
            user_searcher.bestpostshow=True
        db.session.add(user_searcher)
        db.session.commit()
        return True
    
    def recommended_authors(self, userid, app=current_app):
        authors=[]
        user_data = Users.query.filter(Users.id==userid).first()
        if user_data.authorone!=None:
            author=Users.query.filter(Users.id==user_data.authorone).first()
            author_one = {}
            author_one["id"]= author.id
            author_one["login"] = author.login
            author_one["avatar"] = author.avatar
            authors.append(author_one)
        if user_data.authortwo!=None:
            author=Users.query.filter(Users.id==user_data.authortwo).first()
            author_two = {}
            author_two["id"]= author.id
            author_two["login"] = author.login
            author_two["avatar"] = author.avatar   
            authors.append(author_two)
        if user_data.authorthree!=None:
            author=Users.query.filter(Users.id==user_data.authorthree).first()
            author_three = {}
            author_three["id"]= author.id
            author_three["login"] = author.login
            author_three["avatar"] = author.avatar   
            authors.append(author_three)
        return authors
    
    def del_recommendation(self, userid):
        userid=int(userid)
        user_searcher = Users.query.filter(Users.id==current_user.get_id()).first()
        try:
            if user_searcher.authorone==userid:
                user_searcher.authorone=None
            elif user_searcher.authortwo==userid:
                user_searcher.authortwo=None
            elif user_searcher.authorthree==userid:
                user_searcher.authorthree=None
            db.session.add(user_searcher)
            db.session.commit()
            return True
        except Exception as e:
            print('del_recommendation' + str(e))
            return False

    def choose_background(self, id):
        try:
            user_data = Users.query.filter(Users.id==id).first()
            backgrounds_string = user_data.backgrounds
            if backgrounds_string== None:
                return backgrounds_string
            else:
                backgrounds_list = backgrounds_string.split(",")
                return backgrounds_list
        except Exception:
            print("Ошибка choose_background")
            return None
    
    def add_background(self, id, background):
        try:
            user_searcher= Users.query.filter(Users.id==id).first()
            user_searcher.activebackground=background
            db.session.add(user_searcher)
            db.session.commit()
            return True
        except Exception as e:
            print("Ошибка add_background"+str(e))
            return False
    
    def change_email(self, id, email):
        try:
            user_searcher = Users.query.filter(Users.id==id).first()
            user_searcher.email=email
            db.session.add(user_searcher)
            db.session.commit()
            return True
        except Exception:
            print("change_email error")
            return False



    def user_week_likes(self, email):
        try:
            user_searcher = Users.query.filter(Users.email==email).first()
            table_creator = Week_likes(userid=user_searcher.id)
            db.session.add(table_creator)
            db.session.commit()
            return True
        except Exception:
            print("Ошибка user_week_likes")
            return False 

    def chars_story_add(self, chars_story):
        try:
            for i in chars_story:
                character=Characters.query.filter(Characters.name==chars_story[i][0]["name"]).first()
                character.story=chars_story[i][0]["story"]
                character.country=chars_story[i][0]["country"]
                character.element=chars_story[i][0]["element"]
                db.session.add(character)
                db.session.commit()
        except Exception as e:
            print('chars_story_add'+str(e))


    """Achievments"""
    def add_achievments(self, email, all_achievments):
        try:
            user=Users.query.filter(Users.email==email).first()
            for i in all_achievments:
                add_achievments=Achievments(userid=user.id, name=all_achievments[i][0]["name"], total=int(all_achievments[i][0]["total"]), description=all_achievments[i][0]["description"], reward=all_achievments[i][0]["reward"], rewarddesc=all_achievments[i][0]["rewarddesc"], image=all_achievments[i][0]["image"], achtype=all_achievments[i][0]["achtype"])
                db.session.add(add_achievments)
                db.session.commit()
            return True
        except:
            print("add_achievments error")
            return False

    def ach_newbie(self, login):
        try:
            user_searcher=Users.query.filter(Users.login==login).first()
            achievment_searcher=Achievments.query.filter(Achievments.userid==user_searcher.id and Achievments.name=="Я еще новенький!").first()
            if achievment_searcher.ready==True or achievment_searcher.earned==True:
                return False
            else:
                achievment_searcher.ready=True
                db.session.add(achievment_searcher)
                db.session.commit()
                return True
        except Exception:
            print("ach_newbie error")
            return False

    def user_time(self, userid):
        user_searcher=Users.query.filter(Users.id==userid).first()
        user_time=user_searcher.time
        time_now=datetime.utcnow()
        day_pass_checker = (str(time_now-user_time)).split(" ")
        return day_pass_checker

    def ach_date(self, userid, user_time):
        try:
            year_checker=Achievments.query.filter(Achievments.userid==userid, Achievments.name=="Город мудрости").first()
            thirty_days_checker=Achievments.query.filter(Achievments.userid==userid, Achievments.name=="Мне сегодня 30...").first()
            seven_days_checker=Achievments.query.filter(Achievments.userid==userid, Achievments.name=="Я уже смешарик!").first()
            if user_time[1]=="days,":
                if int(user_time[0])>=365:
                    if year_checker.earned==True or year_checker.ready==True:
                        pass
                    else:
                        year_checker.ready=True
                        db.session.add(year_checker)
                        db.session.commit()
                if int(user_time[0])>=30:
                    if thirty_days_checker.earned==True or thirty_days_checker.ready==True:
                        pass
                    else:
                        thirty_days_checker.ready=True
                        db.session.add(thirty_days_checker)
                        db.session.commit()
                if int(user_time[0])>=7:
                    if seven_days_checker.earned==True or seven_days_checker.ready==True:
                        pass
                    else:
                        seven_days_checker.ready=True
                        db.session.add(seven_days_checker)
                        db.session.commit()
                return True
            return True
        except Exception as e:
            print("ach error"+str(e))
            return False

    def likes_achievment(self, userid):
        user_searcher=Users.query.filter(Users.id==userid).first()
        likes_checker=user_searcher.howlikes
        ten_likes=Achievments.query.filter(Achievments.userid==userid, Achievments.name=="Горячая десяточка").first()
        hundred_likes=Achievments.query.filter(Achievments.userid==userid, Achievments.name=="100 баллов!").first()
        thousand_likes=Achievments.query.filter(Achievments.userid==userid, Achievments.name=="Всем это понравилось").first()
        ten_thousand_likes=Achievments.query.filter(Achievments.userid==userid, Achievments.name=="It's over 9000!").first()
        if ten_thousand_likes.earned==True or ten_thousand_likes.ready==True:
            return True
        elif likes_checker>=ten_thousand_likes.total:
            ten_thousand_likes.ready=True
            db.session.add(ten_thousand_likes)
            db.session.commit()
            return True
        elif thousand_likes.earned==True or thousand_likes.ready==True:
            return True
        elif likes_checker>=thousand_likes.total:
            thousand_likes.ready=True
            db.session.add(thousand_likes)
            db.session.commit()
            return True
        elif hundred_likes.earned==True or hundred_likes.ready==True:
            return True
        elif likes_checker>=hundred_likes.total:
            hundred_likes.ready=True
            db.session.add(hundred_likes)
            db.session.commit()
            return True
        elif ten_likes.earned==True or hundred_likes.ready==True:
            return True
        elif likes_checker>=ten_likes.total:
            ten_likes.ready=True
            db.session.add(ten_likes)
            db.session.commit()
            return True
                
    def ready_ach_searcher(self, id):
            achievment_searcher=Achievments.query.filter(Achievments.userid==id, Achievments.ready==True).all()
            if achievment_searcher==[]:
                return None
            else:
                return achievment_searcher
    
    def list_achievments(self, id, ach_type, if_earned):
        achievment_searcher=Achievments.query.filter(Achievments.userid==id, Achievments.achtype==ach_type, Achievments.earned==if_earned).all()
        if achievment_searcher==[]:
                return None
        else:
            return achievment_searcher

    def how_posts(self,id):
        counter=0
        posts_number=Posts.query.filter(Posts.userid==id).all()
        for i in posts_number:
            counter=counter+1
        return counter
    
    def achievments_posts_checker(self, id, how_posts):
        one_post=Achievments.query.filter(Achievments.userid==id, Achievments.name=="Начало положено").first()
        ten_posts=Achievments.query.filter(Achievments.userid==id, Achievments.name=="Плодотворная работа").first()
        twenty_posts=Achievments.query.filter(Achievments.userid==id, Achievments.name=="По уши в делах").first()
        fifty_posts=Achievments.query.filter(Achievments.userid==id, Achievments.name=="Работать, как Архонт").first()
        hundred_posts=Achievments.query.filter(Achievments.userid==id, Achievments.name=="Моё хобби - работа!").first()
        if hundred_posts.ready==True or hundred_posts.earned==True:
            pass
        else:
            if how_posts>=hundred_posts.total:
                hundred_posts.ready=True
                db.session.add(hundred_posts)
        if fifty_posts.ready==True or fifty_posts.earned==True:
            pass
        else:
            if how_posts>=fifty_posts.total:
                fifty_posts.ready=True
                db.session.add(fifty_posts)
        if twenty_posts.ready==True or twenty_posts.earned==True:
            pass
        else:
            if how_posts>=twenty_posts.total:
                twenty_posts.ready=True
                db.session.add(twenty_posts)
        if ten_posts.ready==True or ten_posts.earned==True:
            pass
        else:
            if how_posts>=ten_posts.total:
                ten_posts.ready=True
                db.session.add(ten_posts)
        if one_post.ready==True or one_post.earned==True:
            pass
        else:
            if how_posts>=one_post.total:
                one_post.ready=True
                db.session.add(one_post)
        db.session.commit()
        return True


    def earn_ready_achievment(self, userid, achievment_name):
        user_searcher=Users.query.filter(Users.id==userid).first()
        if user_searcher==None:
            return False
        ready_achievment=Achievments.query.filter(Achievments.userid==userid, Achievments.name==achievment_name, Achievments.ready==True).first()
        if ready_achievment==None:
            return False
        else:
            ready_achievment.ready=False
            ready_achievment.earned=True
            db.session.add(ready_achievment)
            user_backgrounds = user_searcher.backgrounds
            if user_backgrounds==None:
                user_backgrounds=""
            earned_background = str(user_backgrounds)+","+str(ready_achievment.reward)
            user_searcher.backgrounds = earned_background
            db.session.add(user_searcher)
            db.session.commit()
            return True

    def api_validated_posts(self):
        try:
            pictures_posts=[]
            posts = Posts.query.filter(Posts.isactive==True).all()
            for i in posts:
                pictures = PostsImages.query.filter(PostsImages.Postsid==i.id).all()
                pics_list=[]
                if pictures != []:
                    for j in pictures:
                        pics_list.append(j.image)
                else:
                    pics_list=None
                pictures_posts.append({'id': i.id, 'title': i.title, 'text': i.text, 'character': i.character, 'element': i.element, 'userid': i.userid, 'time' : i.time, 'islocked': i.islocked, 'postofday': i.postOfDay, 'images':pics_list})
            return pictures_posts
        except Exception as e:
            print('api_validated_posts error'+ str(e))
            return False
        
    def api_create_post(self, json_string):
        try:
            userid=current_user.get_id()
            data_json = json.loads(json_string)
            post_searcher = Posts.query.filter(Posts.title==data_json['title']).first()
            if post_searcher == None:
                trans_name = translit(data_json['title'], language_code='ru', reversed=True)
                url = trans_name.replace(" ","_")
                character = translit(json_string['character'], language_code='ru', reversed=True)
                character = character.replace("'", "")
                character = character.replace("-", "")
                character = character.replace(" ", "")
                character = character.lower()
                element_searcher = Characters.query.filter(Characters.url==character).first()
                element = element_searcher.element
                post_creator=Posts(title=data_json['title'], text=data_json['text'], character=character, url=url, element=element, userid=userid)
                db.session.add(post_creator)
                db.session.commit()
                return True
            else:
                return False
        except Exception as e:
            print("api_create_post error" + str(e))
            return "To add new post use post('/posts'), json={'title': 'title','text':'text', 'character':'character'}"
        
    def api_delete_post(self, postid):
        post_searcher=Posts.query.filter(Posts.id==postid).first()
        if post_searcher.isactive==True:
            post_searcher.isactive=False
            post_searcher.reason='deleted by user'
            db.session.add(post_searcher)
            db.session.commit()
            return True
        else:
            return False

