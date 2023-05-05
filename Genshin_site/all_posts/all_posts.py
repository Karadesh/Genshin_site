from flask import Blueprint, request,render_template,flash, url_for, redirect, g, abort, current_app
from flask_login import login_required, current_user
from Genshin_site.FDataBase import FDataBase
import base64
from transliterate import translit
from Genshin_site.forms import PostForm, RegistrationForm, AuthorisationForm
from datetime import datetime
import secrets
import os
from PIL import Image

all_posts = Blueprint('all_posts', __name__, template_folder='templates', static_folder='static')
chars_list = ["Дехья", "Мика", "Аль-Хайтам", "Яо Яо", "Странник", "Фарузан", 
             "Лайла", "Нахида", "Нилу", "Сайно", "Кандакия", "Дори", "Тигнари", 
             "Коллеи", "Хэйдзо", "Куки Синобу", "Е Лань", "Камисато Аято", "Яэ Мико", 
             "Шэнь Хэ", "Юнь Цзинь", "Аратаки Итто", "Горо", "Тома", "Кокоми", "Райдэн", 
             "Элой", "Кудзё Сара", "Ёимия", "Саю", "Камисато Аяка", "Каэдэхара Кадзуха", 
             "Эола", "Янь Фэй", "Розария", "Ху Тао", "Сяо", "Гань Юй", "Альбедо", "Чжун Ли", 
             "Синь Янь", "Тарталья", "Диона", "Кли", "Венти", "Ци Ци", "Мона", "Кэ Цин", 
             "Дилюк", "Джинн", "Эмбер", "Чун Юнь", "Фишль", "Сян Лин", "Син Цю", "Сахароза", 
             "Рэйзор", "Ноэлль", "Нин Гуан", "Лиза", "Кэйа", "Бэй Доу", "Беннет", "Барбара", 
             "Путешественник"]
# Для добавления нового персонажа, в этот список нужно добавить имя персонажа, затем добавить картинку с его транслитным именем в all_posts/images
# и заменить в обработчике characters=dbase.get_chars() на characters=image_maker(chars_list) и просто открыть страницу с постами по персонажам. 
# Не забудьте вернуть обратно!

dbase = None

def save_picture(image, name):
    try:
        full_path = os.path.join(current_app.root_path, 'static', 'images', 'posts')
        print(full_path)
        picture_path=os.path.join(full_path,name)
        output_size = (500,500)
        i=Image.open(image)
        i.thumbnail(output_size)
        i.save(picture_path)
        return True
    except Exception as e:
        print(e)
        return False


def authentificator():
    if not current_user.is_authenticated:
        return False
    else:
        return True

@all_posts.before_request
def before_request():
    """соединение с бд перед выполнением запроса"""
    global dbase
    db =  g.get('link_db')
    dbase = FDataBase()

@all_posts.teardown_request
def teardown_request(request):
    global db
    db =  None
    return request

def how_likes(post_id):
    return dbase.how_likes(post_id)

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

def get_avatars_dict(url):
    try:
        usernames = dbase.getCommentatorsNames(url)
        return dbase.getCommentatorsAvas(usernames)
    except Exception as e:
        print(e)
        return False

def get_postcreator_avatar(url):
    try:
        nameandavatar=dbase.getPostcreatorAvatar(url) 
        return nameandavatar
    except Exception as e:
        print(e)
        return False



@all_posts.route("/posts/<int:page_num>")
def posts(page_num):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    characters=image_maker(chars_list) #Для добавления персонажей в бд
    likes={}
    posts_preview={}
    try:
        posts=dbase.getPostsAnonce(page_num)
        if posts==[]:
            abort(404)
        for i in posts:
            likes[i.id] = how_likes(i.id)
            posts_preview[i.id] = dbase.getPostPreview(i.id)
    except:
        abort(404)
    return render_template("all_posts/posts.html",title = "Список Гайдов", posts=posts, posts_preview=posts_preview, likes=likes, form_auth=form_auth, form_reg=form_reg)

@all_posts.route("/posts_character/<alias>?<int:page_num>")
def posts_character(alias, page_num):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    likes={}
    images={}
    posts=dbase.getPostsAnonceCharacter(alias, page_num)
    if posts==[]:
        abort(404)
    for i in posts:
        likes[i.id] = how_likes(i.id)
        images[i.id] = dbase.getPostPreview(i.id)
    return render_template("all_posts/posts_character.html",title = "Список гайдов", posts=posts, likes=likes, images=images, character=dbase.get_char(alias), form_auth=form_auth, form_reg=form_reg)

@all_posts.route("/post/<alias>", methods=['POST', 'GET'])
def show_post(alias):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    get_post = dbase.get_post(alias)
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
    islike = dbase.show_like(post_id, current_user.get_id())
    likes = how_likes(post_id)
    date_list=[]
    comments=dbase.getCommentsAnonce(url)
    for i in comments:
        t=datetime.strftime(i.time, "%d/%m/%Y %H:%M")
        date_list.append(t)
    if not title:
        abort(404)
    if request.method == "POST":
        if len(request.form['comment'])> 1:
            c = dbase.create_comment(request.form['comment'], alias)
            if not c:
                flash('Ошибка добавления комментария', category = 'error')
            else:
                return(redirect(url_for('.show_post', alias=url)))
        else:
            flash('Ошибка добавления комментария', category = 'error')
    return render_template("all_posts/post.html",date_list=date_list,likes=likes, islike=islike, post_id=post_id, title = title, post=post, post_image=post_image, isactive=isactive, userid=str(userid), comments=comments, url=[url], avatars=get_avatars_dict(url), islocked=islocked, creator=get_postcreator_avatar(url), form_auth=form_auth, form_reg=form_reg)

@all_posts.route("/post_like/<post_id>?<userid>?<post_url>?<creator>")
@login_required
def like_post_inside(post_id, userid, post_url, creator):
    like = dbase.like_post(post_id,userid,creator)
    if like == False:
        abort(404)
    return redirect(url_for('.show_post', alias=post_url))

@all_posts.route("/confirm_delete/<alias>")
@login_required
def confirm_delete(alias):
    return render_template("all_posts/confirm_delete.html", alias=alias)

@all_posts.route("/delete_post/<alias>", methods=['GET','DELETE'])
@login_required
def delete_post(alias):
        deleter = dbase.delete_post(alias)
        if deleter == False:
            abort(404)
        return(redirect(url_for('.posts', page_num=1)))

@all_posts.route("/delete_comment/<alias>?<id>", methods=['GET', 'DELETE'])
@login_required
def delete_comment(alias, id):
    comment_deleter=dbase.delete_comment(id)
    if comment_deleter==False:
        abort(404)
    return(redirect(url_for('.show_post', alias=alias)))

@all_posts.route("/create_post", methods=['POST', 'GET'])
def create_post():
    form = PostForm()
    if authentificator():
        # if request.method == "POST":
        #     if len(request.form['name']) > 4 and len(request.form['post'])>1: #проверку на свой вкус
        select_chars = dbase.character_searcher()
        if request.method == "POST":
            if form.validate_on_submit():
                userid = int(current_user.get_id())
                try:
                    dbase.create_post(form.title.data, form.text.data, userid, request.form['character'])
                    for j in form.image.data:
                        null_checker=j.filename
                    if null_checker != '':
                        post_id = dbase.get_post_id(form.title.data)
                        for i in form.image.data:
                            image_name = secrets.token_hex(16)
                            _, f_ext = os.path.splitext(i.filename)
                            print(f_ext)
                            image_name=image_name+f_ext
                            save_picture(i, image_name)
                            dbase.add_images(image_name, post_id)
                    return redirect(url_for('.posts', page_num=1))
                except:
                     flash('Ошибка добавления статьи', category = 'error')
    else:
        return redirect(url_for('users.authorisation'))
    return render_template("all_posts/create_post.html",title = "Create Post", characters=dbase.get_chars(), form=form, select_chars=select_chars)

@all_posts.route("/lock_post/<alias>")
@login_required
def lock_post(alias):
    try:
        post_locker = dbase.lockpost(alias)
        if post_locker==False:
            abort(404)
    except:
        print("Ошибка закрытия поста lock_post")
    return(redirect(url_for('.show_post', alias=alias)))


