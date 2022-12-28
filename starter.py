from flask import Flask, g
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
from mainapp.mainapp import mainapp
from apperrors.apperrors import apperrors


app = Flask(__name__)
app.config.from_object(Config)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'gensh.db')))
#app.permanent_session_lifetime = datetime.timedelta(days=10) #для запоминания сессии. Потом включить
app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(all_posts)
app.register_blueprint(users)
app.register_blueprint(mainapp)
app.register_blueprint(apperrors)

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

#create_db()

if __name__ == "__main__":
    app.run(debug=True)
