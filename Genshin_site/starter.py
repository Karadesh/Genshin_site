from flask import Flask
from Genshin_site.config import Config
from Genshin_site.db import db
from flask_login import LoginManager
from Genshin_site.UserLogin import UserLogin
from flask_mail import Mail
from Genshin_site.FDataBase import FDataBase as dbase
from flask_ckeditor import CKEditor

mail = Mail()
db = db
login_manager = LoginManager()
ckeditor = CKEditor()
    
@login_manager.user_loader
def load_user(user_id):
    user = dbase.search_user(user_id)
    return UserLogin().fromDB(user)

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    ckeditor.init_app(app)

    from Genshin_site.admin.admin import admin
    from Genshin_site.all_posts.all_posts import all_posts
    from Genshin_site.users.users import users
    from Genshin_site.mainapp.mainapp import mainapp
    from Genshin_site.apperrors.apperrors import apperrors
    from Genshin_site.api.api import api

    
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(api, url_prefix='/api')
    app.register_blueprint(all_posts)
    app.register_blueprint(users)
    app.register_blueprint(mainapp)
    app.register_blueprint(apperrors)
    mail.init_app(app)

    app.app_context().push()
    db.create_all()
    return app
