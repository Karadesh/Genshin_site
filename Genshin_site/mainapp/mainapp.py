from flask import Blueprint, render_template, g, request, flash, redirect, url_for
from Genshin_site.FDataBase import FDataBase
from Genshin_site.db import db
import base64



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
    return render_template("mainapp/index.html", off_menu=dbase.getOffmenu(), dayposts=dbase.dayposts_show(), standart_image=standart_image())

@mainapp.route("/characters")
def characters():
    return render_template("mainapp/characters.html",title = "Персонажи", off_menu=dbase.getOffmenu(), characters=dbase.get_chars())

@mainapp.route("/characters/<alias>")
def character(alias):
    return render_template("mainapp/character.html", off_menu=dbase.getOffmenu(), character=dbase.get_char(alias))

@mainapp.route("/feedback", methods=["POST", "GET"])
def feedback():
    if request.method == 'POST':
        if request.form['message'] == '':
            flash('Пожалуйста, напишите ваше сообщение', category='error')
        else:
            flash('Сообщение отправлено', category='success')
            dbase.feedback_save(request.form['username'], request.form['email'], request.form['message'])
            #print(request.form['message'])
    return render_template("mainapp/feedback.html",title = "Feedback", off_menu=dbase.getOffmenu())

@mainapp.route("/all_postofdays")
def all_postsofday():
    likes={}
    images={}
    posts = dbase.dayposts_list()
    for i in posts:
        likes[i.id] = dbase.how_likes(i.postid)
        images[i.id] = dbase.getPostPreview(i.postid)
    return render_template("mainapp/postsofday.html",title = "Посты дня", off_menu=dbase.getOffmenu(), posts=posts, likes=likes, images=images)