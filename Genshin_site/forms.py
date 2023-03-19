from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, TextAreaField, MultipleFileField, ValidationError
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileField, FileAllowed
from Genshin_site.FDataBase import FDataBase as dbase
from Genshin_site.models import Users
from flask_ckeditor import CKEditorField

class AuthorisationForm(FlaskForm):
    name = StringField("Логин: ", validators=[DataRequired(), Length(min=1, max=50)])
    password = PasswordField("Пароль: ", validators=[DataRequired()])
    remember = BooleanField("Запомнить", default=False)
    submit=SubmitField("Войти")

class RegistrationForm(FlaskForm):
    name = StringField("Логин:", validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField("E-mail: ", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль: ", validators=[DataRequired()])
    password2= PasswordField("Подтвердите пароль: ", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Зарегистрироваться")

class PostForm(FlaskForm):
    title = StringField("Название статьи:", validators=[DataRequired(), Length(min=1, max=100)])
    text = CKEditorField("Текст статьи:", validators=[DataRequired(), Length(min=10)])
    image = MultipleFileField("Изображение (png, jpg, jpeg)", render_kw={'multiple':True}, validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    submit = SubmitField("Опубликовать")

class AddCharForm(FlaskForm):
    name = StringField("Имя персонажа:", validators=[DataRequired(), Length(min=1, max=100)])
    image = FileField("Изображение (png, jpg, jpeg)", validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    story = TextAreaField("История персонажа:", validators=[DataRequired(), Length(min=10)])
    submit = SubmitField("Добавить")

class AddImageForm(FlaskForm):
    image = FileField("Изображение (png, jpg, jpeg)", validators=[FileAllowed(['png', 'jpg', 'jpeg'])])
    submit = SubmitField("Добавить")

class AddStoryForm(FlaskForm):
    story = TextAreaField("История персонажа:", validators=[DataRequired(), Length(min=10)])
    submit = SubmitField("Добавить")

class RequestResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Изменить пароль')

    def validate_email(self, email):
        email_searcher = email.data
        user = Users.query.filter(Users.email==email_searcher).first()
        if user is None:
            raise ValidationError('Аккаунт с данным адресом''отсутствует''Вы можете зарегистрировать его')
        
class ResetPasswordForm(FlaskForm):
    password = PasswordField("Пароль: ", validators=[DataRequired()])
    password2= PasswordField("Подтвердите пароль: ", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Изменить пароль')