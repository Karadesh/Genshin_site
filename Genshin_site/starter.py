from flask import Flask
from Genshin_site.config import Config
from Genshin_site.db import db
from flask_login import LoginManager
from Genshin_site.UserLogin import UserLogin
from datetime import datetime, date
from flask_mail import Mail

mail = Mail()
db = db
login_manager = LoginManager()

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True)
    avatar = db.Column(db.LargeBinary, nullable=True) ###поле для аватарок. Прикрутить позже
    time = db.Column(db.DateTime, default=datetime.utcnow)
    isactive = db.Column(db.Boolean, default=True)
    admin = db.Column(db.String(50), default="user")

    def __repr__(self):
        return f"<users {self.id}>"

class Offmenu(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(200), nullable=False)

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.String, nullable=False)
    url = db.Column(db.String(200), nullable=False)
    character = db.Column(db.String(200), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    isactive = db.Column(db.Boolean, default=True)
    reason = db.Column(db.String, nullable=True)
    changer = db.Column(db.String(50), nullable=True)
    islocked = db.Column(db.Boolean, default=False)
    postOfDay = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<posts {self.id}>"

class PostOfDay(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.String, nullable=False)
    url = db.Column(db.String(200), nullable=False)
    character = db.Column(db.String(200), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    time = db.Column(db.String(50), default=str(date.today()))
    postid = db.Column(db.Integer,nullable=False)

    def __repr__(self):
        return f"<postofday {self.id}>"

class PostsImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Postsid = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String, nullable=True)

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String, nullable=False)
    postname = db.Column(db.String(200), db.ForeignKey('posts.url'))
    username = db.Column(db.String(50), db.ForeignKey('users.login'))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    isactive = db.Column(db.Boolean, default=True)
    changer = db.Column(db.String(50), nullable=True)
    reason = db.Column(db.String, nullable=True)

    def __repr__(self):
        return f"<comments {self.id}>"

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String, nullable=False)
    isactive = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<feedback {self.id}>"

class Feedback_answer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    feedbackid = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String, nullable=False)
    admin_username = db.Column(db.String(50), nullable=False)
    answer = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<feedback_answer {self.id}>"

class Characters(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    image = db.Column(db.String, nullable=True)
    url = db.Column(db.String(60), nullable=True)
    story = db.Column(db.String,nullable=True)

    def __repr__(self):
        return f"<Charname: {self.name}>"

class Admin_requests(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    admin_type = db.Column(db.String(50), nullable=False)
    reason = db.Column(db.String,nullable=False)

    def __repr__(self):
        return f"<Admin_requests: {self.name}>"

class Post_likes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postid = db.Column(db.Integer, nullable=False)
    userid = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Post_likes: {self.postid}>"
    
# def post_of_day_make():
#     schedule.every().day.at("13:20").do(db.post_of_day)
#     while True:
#         schedule.run_pending()
#         sleep(1)
    
@login_manager.user_loader
def load_user(user_id):
    user = Users.query.filter(Users.id== user_id).first()
    return UserLogin().fromDB(user)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)

    from Genshin_site.admin.admin import admin
    from Genshin_site.all_posts.all_posts import all_posts
    from Genshin_site.users.users import users
    from Genshin_site.mainapp.mainapp import mainapp
    from Genshin_site.apperrors.apperrors import apperrors

    
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(all_posts)
    app.register_blueprint(users)
    app.register_blueprint(mainapp)
    app.register_blueprint(apperrors)
    mail.init_app(app)

    app.app_context().push()
    db.create_all()
    return app
