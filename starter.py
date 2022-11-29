from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g
import sqlite3
import os
from config import Config
from FDataBase import FDataBase
import datetime



app = Flask(__name__)
app.config.from_object(Config)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'gensh.db')))
app.permanent_session_lifetime = datetime.timedelta(days=10)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()
        db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
        return g.link_db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()



@app.route("/index")
@app.route("/")
def index():
    db = get_db()
    dbase = FDataBase(db)
    return render_template("index.html", menu=dbase.getMenu(), off_menu=dbase.getOffmenu())

@app.route("/posts")
def posts():
    db = get_db()
    dbase = FDataBase(db)
    return render_template("posts.html",title = "Список постов", menu=dbase.getMenu(), off_menu=dbase.getOffmenu(), posts=dbase.getPostsAnonce())

@app.route("/post/<alias>")
def show_post(alias):
    db = get_db()
    dbase = FDataBase(db)
    title, post = dbase.get_post(alias)
    if not title:
        abort(404)
    return render_template("post.html",title = title, post=post, menu=dbase.getMenu(), off_menu=dbase.getOffmenu())

@app.route("/my_posts")
def my_posts():
    db = get_db()
    dbase = FDataBase(db)
    return render_template("my_posts.html",title = "My Posts", menu=dbase.getMenu(), off_menu=dbase.getOffmenu())

@app.route("/create_post", methods=['POST', 'GET'])
def create_post():
    db = get_db()
    dbase = FDataBase(db)
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post'])>1: #проверку на свой вкус
            res = dbase.create_post(request.form['name'], request.form['post'])
            if not  res:
                flash('Ошибка добавления статьи', category = 'error')
            else:
                flash('Статья успешно добавлена!', category = 'success')
        else:
            flash('Ошибка добавления статьи', category = 'error')
    return render_template("create_post.html",title = "Create Post", menu=dbase.getMenu(), off_menu=dbase.getOffmenu())

@app.route("/profile/<username>")
def profile(username):
    db = get_db()
    dbase = FDataBase(db)
    if 'userLogged' not in session or session['userLogged'] != username:
        abort(401)
    return render_template("profile.html",title = "Profile", menu=dbase.getMenu())

@app.route("/authorisation", methods=['POST', 'GET'])
def authorisation():
    session.permanent = True
    if 'userLogged' in session:
        return redirect(url_for('profile', username=session['userLogged']))
    elif request.method == 'POST':
        if request.form['username'] == "123" and request.form['password'] == "321": #в дальнейшем эту строчку сделать типа "if пользователь в бд и пароль равен паролю в бд"
            session['userLogged'] = request.form['username']
        elif request.form['username'] != "123": #в дальнейшем сверка с бд
            flash('Неправильный логин', category='error')
        elif request.form['username'] == "123" and request.form['password']!="123":
            flash('Неправильный пароль', category='error')

    return render_template("authorisation.html", title="Authorisation") 

@app.route("/register")
def register():
    return render_template("register.html", title="Registration")

@app.route("/guides")
def guides():
    db = get_db()
    dbase = FDataBase(db)
    return render_template("guides.html",title = "Guides", menu=dbase.getMenu(), off_menu=dbase.getOffmenu())

@app.route("/characters")
def characters():
    db = get_db()
    dbase = FDataBase(db)
    return render_template("characters.html",title = "Characters", menu=dbase.getMenu(), off_menu=dbase.getOffmenu())

@app.route("/feedback", methods=["POST", "GET"])
def feedback():
    if request.method == 'POST':
        if request.form['message'] == '':
            flash('Пожалуйста, напишите ваше сообщение', category='error')
        else:
            flash('Сообщение отправлено', category='success')
            print(request.form['message'])
    db = get_db()
    dbase = FDataBase(db)
    return render_template("feedback.html",title = "Feedback", menu=dbase.getMenu(), off_menu=dbase.getOffmenu())

@app.errorhandler(404)
def pageNotFound(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template("page404.html",title = "Страница не найдена", menu=dbase.getMenu(), off_menu=dbase.getOffmenu()), 404

@app.errorhandler(401)
def pageAbort(error):
    db = get_db()
    dbase = FDataBase(db)
    return render_template("page401.html",title = "Не авторизован", menu=dbase.getMenu(), off_menu=dbase.getOffmenu()), 401

#create_db()

if __name__ == "__main__":
    app.run(debug=True)
