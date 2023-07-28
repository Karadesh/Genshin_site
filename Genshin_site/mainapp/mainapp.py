from flask import Blueprint, render_template, g, request, flash, redirect, url_for, abort, current_app
from Genshin_site.FDataBase import FDataBase
from Genshin_site.db import db
from Genshin_site.forms import AuthorisationForm, RegistrationForm



mainapp = Blueprint('mainapp', __name__, template_folder='templates', static_folder='static')

dbase = None
'''Соединение с бд перед выполнением запроса'''
@mainapp.before_request
def before_request():
    global dbase
    #db =  g.get('link_db')
    dbase = FDataBase()

'''Отключение от бд после выполнения запроса'''
@mainapp.teardown_request
def teardown_request(request):
    global db
    db =  None
    return request

'''Главная страница сайта'''
@mainapp.route("/index")
@mainapp.route("/")
def index():
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    dayposts=dbase.dayposts_show() #Поиск постов дня в бд
    return render_template("mainapp/index.html", dayposts=dayposts, form_auth=form_auth, form_reg=form_reg)

'''Страница персонажей'''
@mainapp.route("/characters")
def characters():
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    '''dbase.get_chars() - возвращает список словарей персонажей из бд'''
    return render_template("mainapp/characters.html",title = "Персонажи", characters=dbase.get_chars(), form_auth=form_auth, form_reg=form_reg)

'''Страница отправки фидбека'''
@mainapp.route("/feedback", methods=["POST", "GET"])
def feedback():
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    if request.method == 'POST':
        if request.form['message'] == '':
            flash('Пожалуйста, напишите ваше сообщение', category='error')
        else:
            flash('Сообщение отправлено', category='success')
            '''Добавление фидбека в бд'''
            dbase.feedback_save(request.form['username'], request.form['email'], request.form['message'])
    return render_template("mainapp/feedback.html",title = "Feedback", form_auth=form_auth, form_reg=form_reg)

'''Страница со всеми постами дня за каждый день'''
@mainapp.route("/all_postofdays/<int:page_num>")
def all_postsofday(page_num):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    likes={}
    images={}
    comments_num={}
    posts = dbase.dayposts_list(page_num) #список постов дня из бд
    if posts==[]:
        abort(404)
    for i in posts:
        likes[i.id] = dbase.how_likes(i.postid) #Поиск количества лайков в бд
        images[i.id] = dbase.getPostPreviews(i.postid) #Поиск изображения-превью в бд
        comments_num[i.url] = dbase.how_comments(i.url) #Поиск количества комментариев в бд
    return render_template("mainapp/postsofday.html",title = "Посты дня", posts=posts, likes=likes, comments_num=comments_num, images=images, form_auth=form_auth, form_reg=form_reg)
