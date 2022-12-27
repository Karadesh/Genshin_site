from flask import Flask, render_template, request, flash, g
import sqlite3
import os
from config import Config
from FDataBase import FDataBase
import datetime
from flask_login import LoginManager
from UserLogin import UserLogin
from admin.admin import admin
from all_posts.all_posts import all_posts
from users.users import users


app = Flask(__name__)
app.config.from_object(Config)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'gensh.db')))
#app.permanent_session_lifetime = datetime.timedelta(days=10) #для запоминания сессии. Потом включить
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(all_posts)
app.register_blueprint(users)

login_manager = LoginManager(app)
login_manager.login_view = 'authorisation'
login_manager.login_message='Авторизуйтесь, чтобы просматривать эту страницу'
login_manager.login_message_category = "success"



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

dbase = None
@app.before_request
def before_request():
    """соединение с бд перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase=FDataBase(db)

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html", off_menu=dbase.getOffmenu())

@app.route("/guides")
def guides():
    return render_template("guides.html",title = "Guides", off_menu=dbase.getOffmenu())

@app.route("/characters")
def characters():
    return render_template("characters.html",title = "Characters", off_menu=dbase.getOffmenu())

@app.route("/feedback", methods=["POST", "GET"])
def feedback():
    if request.method == 'POST':
        if request.form['message'] == '':
            flash('Пожалуйста, напишите ваше сообщение', category='error')
        else:
            flash('Сообщение отправлено', category='success')
            print(request.form['message'])
    return render_template("feedback.html",title = "Feedback", off_menu=dbase.getOffmenu())

@app.errorhandler(404)
def pageNotFound(error):
    return render_template("page404.html",title = "Страница не найдена", off_menu=dbase.getOffmenu()), 404

@app.errorhandler(401)
def pageAbort(error):
    return render_template("page401.html",title = "Не авторизован", off_menu=dbase.getOffmenu()), 401



#create_db()

if __name__ == "__main__":
    app.run(debug=True)
