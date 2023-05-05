from flask import Blueprint, render_template, g, request, flash, redirect, url_for, abort
from Genshin_site.FDataBase import FDataBase
from Genshin_site.db import db
import base64
from Genshin_site.forms import AuthorisationForm, RegistrationForm



mainapp = Blueprint('mainapp', __name__, template_folder='templates', static_folder='static')

def standart_image(app=mainapp):
    with app.open_resource(app.root_path + url_for('.static', filename= 'images/watch_all.png'), "rb") as f:
        base64_string=base64.b64encode(f.read()).decode('utf-8')
        based_string = f'data:image/png;base64,{base64_string}'
    return based_string

dbase = None
@mainapp.before_request
def before_request():
    """соединение с бд перед выполнением запроса"""
    global dbase
    #db =  g.get('link_db')
    dbase = FDataBase()

@mainapp.teardown_request
def teardown_request(request):
    global db
    db =  None
    return request

@mainapp.route("/index")
@mainapp.route("/")
def index():
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    return render_template("mainapp/index.html", dayposts=dbase.dayposts_show(), standart_image=standart_image(), form_auth=form_auth, form_reg=form_reg)

@mainapp.route("/characters")
def characters():
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    return render_template("mainapp/characters.html",title = "Персонажи", characters=dbase.get_chars(), form_auth=form_auth, form_reg=form_reg)

@mainapp.route("/characters/<alias>")
def character(alias):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    character=dbase.get_char(alias)
    if character==None:
        abort(404)
    return render_template("mainapp/character.html", character=character, form_auth=form_auth, form_reg=form_reg)

@mainapp.route("/feedback", methods=["POST", "GET"])
def feedback():
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    if request.method == 'POST':
        if request.form['message'] == '':
            flash('Пожалуйста, напишите ваше сообщение', category='error')
        else:
            flash('Сообщение отправлено', category='success')
            dbase.feedback_save(request.form['username'], request.form['email'], request.form['message'])
            #print(request.form['message'])
    return render_template("mainapp/feedback.html",title = "Feedback", form_auth=form_auth, form_reg=form_reg)

@mainapp.route("/all_postofdays/<int:page_num>")
def all_postsofday(page_num):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    likes={}
    images={}
    posts = dbase.dayposts_list(page_num)
    if posts==[]:
        abort(404)
    for i in posts:
        likes[i.id] = dbase.how_likes(i.postid)
        images[i.id] = dbase.getPostPreview(i.postid)
    return render_template("mainapp/postsofday.html",title = "Посты дня", posts=posts, likes=likes, images=images, form_auth=form_auth, form_reg=form_reg)
