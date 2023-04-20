from Genshin_site.db import db
import datetime
from flask import current_app
import jwt

db=db

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), unique=True)
    avatar = db.Column(db.LargeBinary, nullable=True) ###поле для аватарок. Прикрутить позже
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    isactive = db.Column(db.Boolean, default=True)
    admin = db.Column(db.String(50), default="user")
    character = db.Column(db.String(60), default="Путешественник")
    backgrounds = db.Column(db.String, nullable=True)
    activebackground = db.Column(db.String(60), nullable=True)

    def get_reset_token(self, expires_sec=1800):
        reset_token = jwt.encode({'user_id': self.id, 'exp': datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=expires_sec)},
                                 current_app.config['SECRET_KEY'],
                                 algorithm='HS256')
        return reset_token
    
    @staticmethod
    def verify_reset_token(token):
        try:
            data = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                leeway = datetime.timedelta(seconds=10),
                algorithms=['HS256']
            )
        except:
            return False
        userid = data.get('user_id')
        return Users.query.get(userid)

    def __repr__(self):
        return f"<users {self.id}>"

class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    text = db.Column(db.String, nullable=False)
    url = db.Column(db.String(200), nullable=False)
    character = db.Column(db.String(200), nullable=False)
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
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
    time = db.Column(db.String(50), default=str(datetime.date.today()))
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
    userid = db.Column(db.Integer, db.ForeignKey('users.id'))
    time = db.Column(db.DateTime, default=datetime.datetime.utcnow)
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
    element = db.Column(db.String(50), nullable=True)

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
    creatorid = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Post_likes: {self.postid}>"