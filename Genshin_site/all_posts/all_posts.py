from flask import Blueprint, request,render_template,flash, url_for, redirect, g, abort
from flask_login import login_required, current_user
from Genshin_site.FDataBase import FDataBase
from transliterate import translit
from Genshin_site.forms import PostForm, RegistrationForm, AuthorisationForm
from Genshin_site.all_posts.utils import save_picture
from datetime import datetime
import secrets
import os
from PIL import Image
import random

all_posts = Blueprint('all_posts', __name__, template_folder='templates', static_folder='static')
'''Список всех персонажей для быстрой загрузки в бд'''
chars_list = ["Путешественник","Барбара","Беннет","Бэй Доу","Кэйа","Лиза","Нин Гуан","Ноэлль",
             "Рэйзор","Сахароза","Син Цю","Сян Лин","Фишль","Чун Юнь","Эмбер","Джинн","Дилюк",
             "Кэ Цин","Мона","Ци Ци","Венти","Кли","Диона","Тарталья","Синь Янь","Чжун Ли",
             "Альбедо","Гань Юй","Сяо","Ху Тао","Розария","Янь Фэй","Эола","Каэдэхара Кадзуха",
             "Камисато Аяка","Саю","Ёимия","Кудзё Сара","Элой","Райдэн","Кокоми","Тома","Горо",
             "Аратаки Итто","Юнь Цзинь","Шэнь Хэ","Яэ Мико","Камисато Аято","Е Лань","Куки Синобу",
             "Хэйдзо","Коллеи","Тигнари","Дори","Кандакия","Сайно","Нилу","Нахида","Лайла","Фарузан",
             "Странник","Яо Яо","Аль-Хайтам","Мика","Дехья","Бай Чжу","Кавех","Кирара"]
# Для добавления нового персонажа, в этот список нужно добавить имя персонажа, затем добавить картинку с его транслитным именем в all_posts/images
# и заменить в обработчике characters=dbase.get_chars() на characters=image_maker(chars_list) и просто открыть страницу с постами по персонажам. 
# Не забудьте вернуть обратно!

dbase = None

'''Проверка авторизации'''
def authentificator():
    if not current_user.is_authenticated:
        return False
    else:
        return True

'''Соединение с бд перед выполнением запроса'''
@all_posts.before_request
def before_request():
    global dbase
    db =  g.get('link_db')
    dbase = FDataBase()

'''Отключение от бд после выполнения запроса'''
@all_posts.teardown_request
def teardown_request(request):
    global db
    db =  None
    return request

'''Количество лайков поста'''
def how_likes(post_id):
    return dbase.how_likes(post_id) #Поиск в бд количества лайков поста

'''Редактирование имени изображений персонажей для поиска в директории'''
def image_maker(chars_list):
    chars_dict_list = []
    for i in chars_list:
        url = translit(i, language_code='ru', reversed=True)
        url = url.replace("'", "")
        url = url.replace("-", "")
        url = url.replace(" ", "")
        url = url.lower()
        chars_dict={'url': url, 'name': i, 'img': url}
        chars_dict_list.append(chars_dict)
        #dbase.add_character(chars_dict) для добавления нового персонажа в бд
    return chars_dict_list

'''Поиск аватаров пользователей-комментаторов'''
def get_avatars_dict(url):
    try:
        usernames = dbase.getCommentatorsNames(url) #Поиск имен комментаторов постав бд
        return dbase.getCommentatorsAvas(usernames) #Поиск имен аватаров комментаторов в бд
    except Exception as e:
        print(e)
        return False
'''Поиск имени аватара создателя поста'''
def get_postcreator_avatar(url):
    try:
        nameandavatar=dbase.getPostcreatorAvatar(url) #Поиск названия аватара в бд
        return nameandavatar
    except Exception as e:
        print(e)
        return False


'''Страница постов'''
@all_posts.route("/posts/<int:page_num>")
def posts(page_num):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    #characters=image_maker(chars_list) Для добавления персонажей в бд и истории персонажей в бд
    #with all_posts.open_resource(all_posts.root_path + url_for('static', filename='characters_story.json')) as json_file:
    #    data = json.load(json_file)
    #    dbase.chars_story_add(data)
    likes={}
    post_date={}
    posts_preview={}
    comments_num={}
    try:
        posts=dbase.getPostsAnonce(page_num) #Поиск списка постов в бд
        if posts==[]:
            abort(404)
        for i in posts:
            likes[i.id] = how_likes(i.id)
            comments_num[i.url] = dbase.how_comments(i.url) #Поиск количества комментариев в бд
            posts_preview[i.id] = dbase.getPostPreviews(i.id) #Поиск изображения-превью в бд
            post_date[i.id] = datetime.strftime(i.time, "%d/%m/%Y") 
    except:
        abort(404)
    elements_list=['anemo', 'cryo', 'pyro', 'geo', 'dendro', 'hydro', 'electro']
    element=random.choice(elements_list)
    side_guides = dbase.side_bar(element=element) #Поиск 2 постов в сайдбар по рандомной стихии
    return render_template("all_posts/posts.html",title = "Список Гайдов", posts=posts, posts_preview=posts_preview, likes=likes, comments_num=comments_num, form_auth=form_auth, form_reg=form_reg, side_guides=side_guides, post_date=post_date, element=element)

'''Страница постов по выборке из сайдбара(query_item - стихия или id пользователя)'''
@all_posts.route("/posts/<query_item>?<int:page_num>")
def posts_query(page_num,query_item):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    likes={}
    post_date={}
    posts_preview={}
    comments_num={}
    try:
        posts=dbase.getPostsQuery(page_num, query_item=query_item) #Поиск постов в бд
        if posts==[]:
            abort(404)
        for i in posts:
            likes[i.id] = how_likes(i.id)
            comments_num[i.url] = dbase.how_comments(i.url) #Поиск количества комментариев в бд
            posts_preview[i.id] = dbase.getPostPreviews(i.id) #Поиск изображения-превью в бд
            post_date[i.id] = datetime.strftime(i.time, "%d/%m/%Y")
    except:
        abort(404)
    elements_list=['anemo', 'cryo', 'pyro', 'geo', 'dendro', 'hydro', 'electro']
    element=random.choice(elements_list)
    side_guides = dbase.side_bar(element=element) #Поиск 2 постов в сайдбар по рандомной стихии
    return render_template("all_posts/posts_query.html",title = f"Список Гайдов", posts=posts, posts_preview=posts_preview, likes=likes, comments_num=comments_num, form_auth=form_auth, form_reg=form_reg, side_guides=side_guides, post_date=post_date, elem=query_item, element=element)

'''Посты по выборке персонажа'''
@all_posts.route("/posts_character/<alias>?<int:page_num>")
def posts_character(alias, page_num):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    post_date={}
    likes={}
    images={}
    comments_num={}
    posts=dbase.getPostsAnonceCharacter(alias, page_num) #Список постов из бд
    if posts==[]:
        abort(404)
    for i in posts:
        likes[i.id] = how_likes(i.id)
        comments_num[i.url] = dbase.how_comments(i.url) #Поиск количества комментариев в бд
        images[i.id] = dbase.getPostPreviews(i.id) #Поиск изображения-превью в бд
        post_date[i.id] = datetime.strftime(i.time, "%d/%m/%Y")
    character = dbase.get_char(alias)
    element = character.element
    side_guides = dbase.side_bar(element=element) #Поиск 2 постов в сайдбар по рандомной стихии
    return render_template("all_posts/posts_character.html",title = "Список гайдов", posts=posts, likes=likes, comments_num=comments_num, images=images, character=character, form_auth=form_auth, form_reg=form_reg, element=element, side_guides=side_guides, post_date=post_date)

'''Страница поста'''
@all_posts.route("/post/<alias>", methods=['POST', 'GET'])
def show_post(alias):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    get_post = dbase.get_post(alias) #Поиск поста в бд
    if get_post==None:
        abort(404)
    title = get_post['title'] 
    post = get_post['text']
    url = get_post['url']
    userid = get_post['userid']
    isactive = get_post['isactive']
    islocked = get_post['islocked']
    post_image=get_post['images']
    post_id = get_post['id']
    side_guides=dbase.side_bar(userid=userid) #Поиск 2 постов в сайдбар с гайдами того же пользователя
    islike = dbase.show_like(post_id, current_user.get_id()) #Количество лайков из бд
    likes = how_likes(post_id)
    comments_num = dbase.how_comments(url) #Поиск количества комментариев в бд
    date_list=[]
    comments=dbase.getCommentsAnonce(url) #Поиск комментариев из бд
    for i in comments:
        t=datetime.strftime(i.time, "%d/%m/%Y %H:%M")
        date_list.append(t)
    if not title:
        abort(404)
    if request.method == "POST":
        if len(request.form['comment'])> 1:
            c = dbase.create_comment(request.form['comment'], alias) #Создание комментария
            if not c:
                flash('Ошибка добавления комментария', category = 'error')
            else:
                return(redirect(url_for('.show_post', alias=url)))
        else:
            flash('Ошибка добавления комментария', category = 'error')
    return render_template("all_posts/post.html",date_list=date_list, likes=likes, comments_num=comments_num, islike=islike, post_id=post_id, title = title, post=post, post_image=post_image, isactive=isactive, userid=str(userid), comments=comments, url=[url], avatars=get_avatars_dict(url), islocked=islocked, creator=get_postcreator_avatar(url), form_auth=form_auth, form_reg=form_reg, side_guides=side_guides)

#Обработчик для лайка поста
@all_posts.route("/post_like/<post_id>?<userid>?<post_url>?<creator>")
@login_required
def like_post_inside(post_id, userid, post_url, creator):
    like = dbase.like_post(post_id,userid,creator) #Добавить/убрать отметку о лайке от пользователя в бд
    if like == False:
        abort(404)
    return redirect(url_for('.show_post', alias=post_url))

'''Подтверждение удаления поста пользователя'''
@all_posts.route("/confirm_delete/<alias>")
@login_required
def confirm_delete(alias):
    return render_template("all_posts/confirm_delete.html", alias=alias)

'''Удаление поста'''
@all_posts.route("/delete_post/<alias>", methods=['GET','DELETE'])
@login_required
def delete_post(alias):
        deleter = dbase.delete_post(alias) #Добавить пометку в бд о том, что пост удален
        if deleter == False:
            abort(404)
        return(redirect(url_for('.posts', page_num=1)))

'''Удаление комментария'''
@all_posts.route("/delete_comment/<alias>?<id>", methods=['GET', 'DELETE'])
@login_required
def delete_comment(alias, id):
    comment_deleter=dbase.delete_comment(id) #Удалить комментарий из бд
    if comment_deleter==False:
        abort(404)
    return(redirect(url_for('.show_post', alias=alias)))

'''Создать пост'''
@all_posts.route("/create_post", methods=['POST', 'GET'])
def create_post():
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    form = PostForm()
    if authentificator():
        # if request.method == "POST":
        #     if len(request.form['name']) > 4 and len(request.form['post'])>1: #проверку на свой вкус
        select_chars = dbase.character_searcher() #Поиск списка персонажей
        if request.method == "POST":
            if form.validate_on_submit():
                userid = int(current_user.get_id())
                '''Добавление поста в бд'''
                try:
                    dbase.create_post(form.title.data, form.text.data, userid, request.form['character'])
                    for j in form.image.data:
                        null_checker=j.filename
                    if null_checker != '':
                        post_id = dbase.get_post_id(form.title.data)
                        for i in form.image.data:
                            image_name = secrets.token_hex(16)
                            _, f_ext = os.path.splitext(i.filename)
                            image_name=image_name+f_ext
                            '''Добавление имени изображения и сохранение изображения'''
                            save_picture(i, image_name)
                            dbase.add_images(image_name, post_id)
                    return redirect(url_for('.posts', page_num=1))
                except:
                     flash('Ошибка добавления статьи', category = 'error')
    else:
        return redirect(url_for('users.authorisation'))
    return render_template("all_posts/create_post.html",title = "Create Post", form=form, select_chars=select_chars, form_auth=form_auth, form_reg=form_reg)

'''Закрыть возможность комментировать пост'''
@all_posts.route("/lock_post/<alias>")
@login_required
def lock_post(alias):
    try:
        post_locker = dbase.lockpost(alias) #Добавление в бд отметки о закрытии/открытии поста для комментариев
        if post_locker==False:
            abort(404)
    except:
        print("Ошибка закрытия поста lock_post")
    return(redirect(url_for('.show_post', alias=alias)))


