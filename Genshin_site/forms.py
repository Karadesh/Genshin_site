from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, BooleanField, PasswordField, SelectField, TextAreaField, MultipleFileField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf.file import FileAllowed

chars_list = [("Дехья", "Дехья"), ("Мика", "Мика"), ("Аль-Хайтам", "Аль-Хайтам"), ("Яо Яо","Яо Яо"), ("Странник", "Странник"), ("Фарузан","Фарузан"), 
              ("Лайла","Лайла"), ("Нахида", "Нахида"), ("Нилу","Нилу"), ("Сайно","Сайно"), ("Кандакия","Кандакия"), ("Дори","Дори"), ("Тигнари","Тигнари")] 
            #  "Коллеи", "Хэйдзо", "Куки Синобу", "Е Лань", "Камисато Аято", "Яэ Мико", 
            #  "Шэнь Хэ", "Юнь Цзинь", "Аратаки Итто", "Горо", "Тома", "Кокоми", "Райдэн", 
            #  "Элой", "Кудзё Сара", "Ёимия", "Саю", "Камисато Аяка", "Каэдэхара Кадзуха", 
            #  "Эола", "Янь Фэй", "Розария", "Ху Тао", "Сяо", "Гань Юй", "Альбедо", "Чжун Ли", 
            #  "Синь Янь", "Тарталья", "Диона", "Кли", "Венти", "Ци Ци", "Мона", "Кэ Цин", 
            #  "Дилюк", "Джинн", "Эмбер", "Чун Юнь", "Фишль", "Сян Лин", "Син Цю", "Сахароза", 
            #  "Рэйзор", "Ноэлль", "Нин Гуан", "Лиза", "Кэйа", "Бэй Доу", "Беннет", "Барбара", 
            #  "Путешественник"]

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

class PostForm(FlaskForm):
    title = StringField("Название статьи:", validators=[DataRequired(), Length(min=1, max=100)])
    character = SelectField("Персонаж:", choices=chars_list)
    text = TextAreaField("Текст статьи:", validators=[DataRequired(), Length(min=10)])
    image = MultipleFileField("Изображение (png, jpg, jpeg)", render_kw={'multiple':True})
    submit = SubmitField("Опубликовать")