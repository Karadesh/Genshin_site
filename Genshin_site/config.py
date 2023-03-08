class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///Ginshin.db'
    #DATABASE = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'askwqifdslk5iasd951jask5iaslkglasj595'
    DEBUG = True
    MAX_CONTENT_LENGTH = 1024 * 1024
    MAIL_SERVER = 'smtp.yandex.ru'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = '' #почта 
    MAIL_PASSWORD = '' #пароль приложения