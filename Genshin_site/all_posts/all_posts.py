from flask import Blueprint, request,render_template,flash, url_for, redirect, g, abort
from flask_login import login_required, current_user
from Genshin_site.FDataBase import FDataBase
import base64
from transliterate import translit
from Genshin_site.forms import PostForm
from PIL import Image
from io import BytesIO

all_posts = Blueprint('all_posts', __name__, template_folder='templates', static_folder='static')
# chars_list = ["Дехья", "Мика", "Аль-Хайтам", "Яо Яо", "Странник", "Фарузан", 
#             "Лайла", "Нахида", "Нилу", "Сайно", "Кандакия", "Дори", "Тигнари", 
#             "Коллеи", "Хэйдзо", "Куки Синобу", "Е Лань", "Камисато Аято", "Яэ Мико", 
#             "Шэнь Хэ", "Юнь Цзинь", "Аратаки Итто", "Горо", "Тома", "Кокоми", "Райдэн", 
#             "Элой", "Кудзё Сара", "Ёимия", "Саю", "Камисато Аяка", "Каэдэхара Кадзуха", 
#             "Эола", "Янь Фэй", "Розария", "Ху Тао", "Сяо", "Гань Юй", "Альбедо", "Чжун Ли", 
#             "Синь Янь", "Тарталья", "Диона", "Кли", "Венти", "Ци Ци", "Мона", "Кэ Цин", 
#             "Дилюк", "Джинн", "Эмбер", "Чун Юнь", "Фишль", "Сян Лин", "Син Цю", "Сахароза", 
#             "Рэйзор", "Ноэлль", "Нин Гуан", "Лиза", "Кэйа", "Бэй Доу", "Беннет", "Барбара", 
#             "Путешественник"]
# Для добавления нового персонажа, в этот список нужно добавить имя персонажа, затем добавить картинку с его транслитным именем в all_posts/images
# и заменить в обработчике characters=dbase.get_chars() на characters=image_maker(chars_list) и просто открыть страницу с постами по персонажам. 
# Не забудьте вернуть обратно!

dbase = None

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

def image_maker(chars_list, app=all_posts):
    chars_dict_list = []
    for i in chars_list:
        url = translit(i, language_code='ru', reversed=True)
        url = url.replace("'", "")
        url = url.replace("-", "")
        url = url.replace(" ", "")
        url = url.lower()
        with app.open_resource(app.root_path + url_for('.static', filename= f'images/{url}.jpg'), "rb") as f:
            base64_string=base64.b64encode(f.read()).decode('utf-8')
            img=f'data:image/png;base64,{base64_string}'
        chars_dict={'url': url, 'name': i, 'img': img}
        chars_dict_list.append(chars_dict)
        #dbase.add_character(chars_dict) для добавления нового персонажа в бд
    return chars_dict_list

def get_avatars_dict(url, app=all_posts):
    try:
        usernames = dbase.getCommentatorsNames(url)
        avas_dict = {}
        for i in dbase.getCommentatorsAvas(usernames):
            for j, k in i.items():
                if k == None:
                    with app.open_resource(app.root_path + url_for('.static', filename= 'images/default.jpeg'), "rb") as f:
                        base64_string=base64.b64encode(f.read()).decode('utf-8')
                else:
                    base64_string = base64.b64encode(k).decode('utf-8')
                img_url=f'data:image/png;base64,{base64_string}'
                avas_dict[j] = img_url
    except:
        pass
    return avas_dict

def get_postcreator_avatar(url, app=all_posts):
    try:
        nameandavatar=dbase.getPostcreatorAvatar(url) #словарь формата { 'username': username, 'avatar: useravatar }
        if nameandavatar['avatar'] == None:
            with app.open_resource(app.root_path + url_for('.static', filename= 'images/default.jpeg'), "rb") as f:
                        base64_string=base64.b64encode(f.read()).decode('utf-8')
        else:
            base64_string = base64.b64encode(nameandavatar['avatar']).decode('utf-8')
        img_url=f'data:image/png;base64,{base64_string}'
        nameandavatar['avatar']=img_url
        return nameandavatar
    except:
        print(' Ошибка аватара get_postcreator_avatar')
        return False



@all_posts.route("/posts")
def posts():
    likes={}
    posts=dbase.getPostsAnonce()
    for i in posts:
        likes[i.id] = how_likes(i.id)
    return render_template("all_posts/posts.html",title = "Список Гайдов", off_menu=dbase.getOffmenu(), posts=posts, likes=likes, characters=dbase.get_chars())

@all_posts.route("/posts_character/<alias>")
def posts_character(alias):
    likes={}
    images={}
    posts=dbase.getPostsAnonceCharacter(alias)
    for i in posts:
        likes[i.id] = how_likes(i.id)
        images[i.id] = dbase.getPostPreview(i.id)
    return render_template("all_posts/posts_character.html",title = "Список гайдов", off_menu=dbase.getOffmenu(), posts=posts, likes=likes, images=images)

@all_posts.route("/post/<alias>", methods=['POST', 'GET'])
def show_post(alias):
    get_post = dbase.get_post(alias)
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
    return render_template("all_posts/post.html",likes=likes, islike=islike, post_id=post_id, title = title, post=post, post_image=post_image, isactive=isactive, userid=str(userid), off_menu=dbase.getOffmenu(), comments=dbase.getCommentsAnonce(url), url=[url], avatars=get_avatars_dict(url), islocked=islocked, creator=get_postcreator_avatar(url))

@all_posts.route("/post_like/<post_id>?<userid>?<post_url>")
@login_required
def like_post_inside(post_id, userid, post_url):
    dbase.like_post(post_id,userid)
    return redirect(url_for('.show_post', alias=post_url))

@all_posts.route("/confirm_delete/<alias>")
@login_required
def confirm_delete(alias):
    return render_template("all_posts/confirm_delete.html", alias=alias)

@all_posts.route("/delete_post/<alias>", methods=['GET','DELETE'])
@login_required
def delete_post(alias):
        dbase.delete_post(alias)
        return(redirect(url_for('.posts')))

@all_posts.route("/delete_comment/<alias>?<id>", methods=['GET', 'DELETE'])
@login_required
def delete_comment(alias, id):
    dbase.delete_comment(id)
    return(redirect(url_for('.show_post', alias=alias)))

@all_posts.route("/create_post", methods=['POST', 'GET'])
def create_post():
    form = PostForm()
    if authentificator():
        # if request.method == "POST":
        #     if len(request.form['name']) > 4 and len(request.form['post'])>1: #проверку на свой вкус
        if form.validate_on_submit():
                userid = int(current_user.get_id())
                try:
                    dbase.create_post(form.title.data, form.text.data, userid, form.character.data)
                    if form.image.data:
                        post_id = dbase.get_post_id(form.title.data)
                        for i in form.image.data:
                            img=i.read()
                            base64_string=base64.b64encode(img).decode('utf-8')
                            img_string=f'data:image/png;base64,{base64_string}'
                            dbase.add_images(img_string, post_id)
                    return redirect(url_for('.posts'))
                except:
                     flash('Ошибка добавления статьи', category = 'error')
    else:
        return redirect(url_for('users.authorisation'))
    return render_template("all_posts/create_post.html",title = "Create Post", off_menu=dbase.getOffmenu(), characters=dbase.get_chars(), form=form)

@all_posts.route("/lock_post/<alias>")
@login_required
def lock_post(alias):
    try:
        dbase.lockpost(alias)
    except:
        print("Ошибка закрытия поста lock_post")
    return(redirect(url_for('.show_post', alias=alias)))


