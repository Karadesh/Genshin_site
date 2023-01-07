from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class AuthorisationForm(FlaskForm):
    name = StringField("Логин: ", validators=[DataRequired(), Length(min=1, max=50)])
    password = PasswordField("Пароль: ", validators=[DataRequired()])
    remember = BooleanField("Запомнить", default=False)
    submit=SubmitField("Войти")

class RegistrationForm(FlaskForm):
    name = StringField("Логин:", validators=[DataRequired(), Length(min=1, max=50)])
    email = StringField("E-mail: ", validators=[DataRequired(), Email()])
    password = PasswordField("Пароль: ", validators=[DataRequired()])
    password2= PasswordField("Повторите пароль: ", validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField("Зарегистрироваться")
