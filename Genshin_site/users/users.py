from flask import Blueprint, g, redirect, url_for, abort, render_template, make_response, request, flash, json
from Genshin_site.FDataBase import FDataBase
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from Genshin_site.UserLogin import UserLogin
from Genshin_site.forms import AuthorisationForm, RegistrationForm, RequestResetForm, ResetPasswordForm, ChangeEmailForm, AddSocialSitesForm
from werkzeug.security import generate_password_hash, check_password_hash
from Genshin_site.users.utils import send_reset_email, background_maker, save_avatar
from datetime import datetime
import os

users = Blueprint('users', __name__, template_folder='templates', static_folder='static')
login_manager = LoginManager(users)
login_manager.login_view = 'authorisation'
login_manager.login_message='Авторизуйтесь, чтобы просматривать эту страницу'
login_manager.login_message_category = "success"

dbase = None
'''соединение с бд перед выполнением запроса'''
@users.before_request
def before_request():
    global dbase
    db =  g.get('link_db')
    dbase = FDataBase()

'''Отключение от бд после выполнения запроса'''
@users.teardown_request
def teardown_request(request):
    global db
    db =  None
    return request

'''Выход из аккаунта'''
@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('mainapp.index'))

'''Страница профиля'''
@users.route("/profile/<username>?<int:page_num>", methods=["POST", "GET"])
def profile(username, page_num=1):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    user_data = dbase.user_data(username) #Поиск данных пользователя из бд
    if user_data==None:
        abort(404)
    if user_data["active_background"] != None:
        active_background = background_maker(user_data["active_background"]) #Генерация имени изображения бэкграунда пользователя
    else:
        active_background=None
    try:
        current_user_checker = (user_data['id'] == int(current_user.get_id()))
    except Exception:
        current_user_checker = False
    likes = dbase.user_likes(username) #Поиск количества лайков всех постов пользователя в бд
    try:
        guides=dbase.my_guides(username, int(page_num)) #Список постов пользователя
        if guides==[]:
            abort(404)
        posts_likes={}
        posts_images={}
        comments_num={}
        for i in guides:
            posts_likes[i.id] = dbase.how_likes(i.id) #Поиск количества лайков постов в бд
            posts_images[i.id] = dbase.getPostPreviews(i.id) #Поиск изображения-превью постов в бд
            comments_num[i.url] = dbase.how_comments(i.url) #Поиск количества комментариев к постам в бд
    except Exception:
        abort(404)
    how_posts=dbase.how_posts(username)  #Поиск количества всех постов пользователя в бд
    image = dbase.search_character_image(username) #Поиск изображений любимых персонажей пользователя в бд
    char_names = dbase.search_character_names(username) #Поиск имен любимых персонажей пользователя в бд
    recommended_authors=dbase.recommended_authors(username) #Поиск рекомендованных пользователем авторов в бд
    socialsites=dbase.user_social_sites(username) #Поиск ссылок на социальные сети пользователя в бд
    best_post = dbase.user_best_post(username) #Поиск самого оцененного поста пользователя в бд
    if best_post!=[]:
        best_post["comments"]=dbase.how_comments(best_post.get("url")) #Поиск количества комментариев к самому оцененному посту пользователя в бд
    return render_template("users/profile.html", likes=likes, comments_num=comments_num, image=image, user_data=user_data, current_user_checker = current_user_checker,guides=guides, posts_likes=posts_likes, posts_images=posts_images, userid=user_data["id"], username=user_data["login"],form_reg=form_reg, form_auth=form_auth, active_background=active_background, recommended_authors=recommended_authors, best_post=best_post, title=f"Страница пользователя {user_data['login']}", char_names=char_names, how_posts=how_posts, socialsites=socialsites)

'''Страница настроек профиля'''
@users.route("/profile/profile_settings/<id>", methods=["POST", "GET"])
def profile_settings(id):
    form=ChangeEmailForm()
    social_form = AddSocialSitesForm()
    if current_user.get_id()==None:
        abort(404)
    if int(current_user.get_id())!=int(id):
        abort(401)
    else:
        backgrounds = dbase.choose_background(id) #Список изображений-бэкграундов на страницу профиля
        user_data = dbase.user_data(id) #Поиск данных пользователя из бд
        select_chars = dbase.character_searcher() #Поиск списка персонажей из бд
        if request.method=="POST":
            dbase.choose_character(request.form["character"], current_user.get_id()) #Добавить выбранного любимого персонажа в бд
    image = dbase.search_character_image(id) #словарь имен изображений любимых персонажей пользователя в бд
    return render_template("users/profile_settings.html", title="Настройки", select_chars=select_chars, image=image, user_data=user_data, backgrounds=backgrounds, form=form, social_form=social_form)

'''Обработчик опции "добавить социальную сеть"'''
@users.route("/profile/profile_settings/add_socials/<userid>", methods=['POST'])
def add_socials(userid):
    if userid != current_user.get_id():
        abort(403)
    social_form = AddSocialSitesForm()
    if request.method == "POST":
        dbase.add_socials(userid=userid, site=social_form.site.data)
    return redirect(url_for('.profile_settings', id=userid))

'''Обработчик опции "Удалить социальную сеть'''
@users.route("/profile/profile_settings/del/<site>")
def del_socials(site):
    try:
        dbase.del_social(site, current_user.get_id())
    except Exception as e:
        print(str(e))
        abort(404)
    return redirect(url_for('.profile_settings', id=current_user.get_id()))

'''Обработчик опции "показывать/не показывать любимых персонажей в профиле"'''
@users.route("/profile/profile_settings/show_characters/")
def show_characters():
    dbase.show_characters() #Добавить/убрать в бд отметку "показать любимых персонажей"
    return redirect(url_for('.profile_settings', id=current_user.get_id()))

'''Обработчик опции "показывать/не показывать социальные сети в профиле'''
@users.route("/profile/profile_settings/show_socials/")
def show_socials():
    dbase.show_socials() #Добавить/убрать в бд отметку "показать социальные сети"
    return redirect(url_for('.profile_settings', id=current_user.get_id()))

'''Обработчик опции "показывать/не показывать рекомендованных пользователем авторов в профиле"'''
@users.route("/profile/profile_settings/show_authors/")
def show_authors():
    dbase.show_authors() #Добавить/убрать в бд отметку "показать авторов"
    return redirect(url_for('.profile_settings', id=current_user.get_id()))

'''Обработчик опции "показывать/не показывать самый оцененный пост пользователя"'''
@users.route("/profile/profile_settings/show_best_post/")
def show_best_post():
    dbase.show_best_post() #Добавить/убрать в бд отметку "показать любимый пост"
    return redirect(url_for('.profile_settings', id=current_user.get_id()))

'''Обработчик опции "изменить одного из трех любимых персонажей пользователя"'''
@users.route("/profile/profile_settings/change_char/<char_num>", methods=["POST", "GET"])
def change_character(char_num):
    if request.method=="POST":
            dbase.choose_character(request.form["character"], char_num) #Добавить отметку в бд о новом любимом персонаже
    return redirect(url_for('.profile_settings', id=current_user.get_id()))

'''Обработчик опции "удалить одного из трех любимых персонажей пользователя"'''
@users.route("/profile/profile_settings/delete_char/<char_num>")
def delete_char(char_num):
    dbase.delete_character(char_num) #Добавить отметку в бд об удалении любимого персонаже
    return redirect(url_for('.profile_settings', id=current_user.get_id()))

'''Рекомендовать автора'''
@users.route("/profile/recommend/<id>")
def user_recommend(id):
    dbase.user_recommend(id) #добавление в бд информации о новом рекомендуемом пользователем авторе
    return redirect(url_for('.profile', username=id, page_num=1))

'''Изменить e-mail'''
@users.route("/profile/change_email/<id>", methods=["POST", "GET"])
def change_email(id):
    form=ChangeEmailForm()
    if int(current_user.get_id())!=int(id):
        abort(401)
    if request.method=="POST":
        try:
            dbase.change_email(id, form.email.data) #Добавить новый e-mail в бд
        except Exception:
            print("Ошибка change_email")
    return redirect(url_for('.profile_settings', id=id))
        
'''Выбор изображения бэкграунда профиля пользователя'''
@users.route("/profile/select_background/<id>", methods=["POST", "GET"])
def select_background(id):
    if int(current_user.get_id())!=int(id):
        abort(401)
    if request.method=="POST":
        dbase.add_background(id, request.form["backgrounds"]) #Добавление информации о новом активном бэкграунде в бд
    return redirect(url_for('.profile_settings', id=id))

'''Отправка заявки на администрирование'''
@users.route("/profile/admin_request/<username>", methods=["POST", "GET"])
@login_required
def admin_request(username):
    if request.method=="POST":
        username=current_user.getName() #Поиск имени пользователя
        dbase.add_admin_request(username, request.form['admin_type'], request.form['reason']) #Добавить заявку в бд
        return redirect(url_for('.profile', username=current_user.get_id(), page_num=1))
    return render_template("users/admin_request.html", title="Admin request")

'''Загрузка аватара пользователя'''
@users.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                image_name=str(current_user.get_id())
                _, f_ext = os.path.splitext(file.filename)
                image_name=image_name+f_ext
                save_avatar(file,image_name)
                res = dbase.updateUserAvatar(image_name, current_user.get_id()) #Добавление названия аватара+формат
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error"+str(e))
        else:
            flash("Ошибка обновления аватара", "error")
    return redirect(url_for('.profile_settings', id=current_user.get_id()))

'''Авторизация пользователя'''
@users.route("/authorisation", methods=['POST', 'GET'])
def authorisation():
    #session.permanent = True #для запоминания сессии. потом включить
    if current_user.is_authenticated:
        return redirect(request.args.get("next") or url_for(".profile", username=current_user.get_id(), page_num=1))
    form = AuthorisationForm()
    if form.validate_on_submit():
        user = dbase.getUserByLogin(form.name.data) #Поиск пользователя по логину
        '''Проверка имени и пароля пользователя'''
        if user and check_password_hash(user.password, form.password.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            dbase.ach_newbie(form.name.data) #Проверка достижения "Я еще новенький"
            return redirect(request.args.get("next") or url_for("mainapp.index"))
        flash("Неверный логин или пароль", "error")
    return render_template("users/authorisation.html", title="Authorisation", form=form) 

'''Регистрация'''
@users.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.password.data)
        try:
            dbase.add_user(form.name.data, hash, form.email.data) #Добавление пользователя в бд(логин, хэш пароля и e-mail)
            flash("Вы успешно зарегистрированы!", "success")
            '''Добавление достижений пользователя из json файла'''
            with users.open_resource(users.root_path + url_for('static', filename='achievments.json')) as json_file:
                data = json.load(json_file)
                dbase.add_achievments(form.email.data, data)
            dbase.user_week_likes(form.email.data) #Тестовая таблица
            return redirect(url_for('.authorisation'))
        except:
            flash("Ошибка при добавлении в БД", "error")
    else:
        flash("Проверьте поле 'e-mail'. Также пароль должен быть не менее одного символа", "error")
    return render_template("users/register.html", title="Registration", form=form)

'''Обработчик авторизации+ регистрации для базового шаблона'''
@users.route("/auth_reg", methods=["POST", "GET"])
def auth_reg():
    if current_user.is_authenticated:
        return redirect(request.args.get("next") or url_for(".profile", username=current_user.get_id(), page_num=1))
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    '''Авторизация(такой же обработчик, как и authorisation)'''
    if form_auth.validate_on_submit():
        user = dbase.getUserByLogin(form_auth.name.data) 
        if user and check_password_hash(user.password, form_auth.password.data):
            userlogin = UserLogin().create(user)
            rm = form_auth.remember.data
            login_user(userlogin, remember=rm)
            dbase.ach_newbie(form_auth.name.data)
            return redirect(request.args.get("next") or url_for("mainapp.index"))
        flash("Неверный логин или пароль", "error")
    '''Регистрация(такой же обработчик, как и register)'''
    if form_reg.validate_on_submit():
        hash = generate_password_hash(form_reg.password.data)
        try:
            dbase.add_user(form_reg.name.data, hash, form_reg.email.data)
            with users.open_resource(users.root_path + url_for('static', filename='achievments.json')) as json_file:
                data = json.load(json_file)
                dbase.add_achievments(form_reg.email.data, data)
            dbase.user_week_likes(form_reg.email.data)
            flash("Вы успешно зарегистрированы!", "success")
            return redirect(url_for('.authorisation'))
        except:
            flash("Ошибка при добавлении в БД", "error")
    else:
        flash("Проверьте поле 'e-mail'. Также пароль должен быть не менее одного символа", "error")
    return render_template("/base.html", form_auth=form_auth, form_reg=form_reg)

'''Сброс пароля - отправка токена'''
@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('mainapp.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = dbase.search_user_by_email(form.email.data) #Поиск пользователя в бд по e-mail
        send_reset_email(user)
        flash('На почту отправлено письмо с''инструкциями по сбросу пароля', 'success')
        return redirect(url_for('.authorisation'))
    return render_template('users/reset_request.html', title='Сброс пароля', form=form)

'''Сброс пароля - сброс по токену'''
@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('mainapp.index'))
    user = dbase.verify_reset_tokens(token) #Проверка токена в бд
    if user is None:
        flash('Это недействительный или просроченный токен', 'error')
        return redirect(url_for('.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.password.data)
        dbase.change_password(user, hash) #Изменение пароля в бд
        flash('Ваш пароль был обновлен!''Теперь вы можете авторизоваться', 'success')
        return redirect(url_for('.authorisation'))
    return render_template('users/reset_token.html', title='Сброс пароля', form=form)

'''Достижения пользователя'''
@users.route("/achievments/<id>")
def achievments(id):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    try: 
        user_data = dbase.user_data(id) #Поиск информации о пользователе в бд
        if user_data==None:
            abort(404)
        how_posts=dbase.how_posts(id) #Количество постов пользователя (для сверки достижения)
        dbase.achievments_posts_checker(id, how_posts) #Проверка количества постов пользователя с требуемым в достижении
        likes = dbase.user_likes(id) #Количество лайков пользователя (для сверки достижения)
        user_time = dbase.user_time(id) #Дата с момента регистрации пользователя до текущего (для сверки достижения)
        if len(user_time)>1 and (user_time[1] == "days," or user_time[1] == "day,"):
            how_days=int(user_time[0])
            how_months = int((str(int(how_days)/30)).split(".")[0])
            ach_date=dbase.ach_date(id, user_time) #Сверка времени с момента регистрации пользователя с временем, требуемым в достижении
        else:
            how_days=0
            how_months=0
        ready_achievments=dbase.ready_ach_searcher(id)
        date_earned_achievments=dbase.list_achievments(id, "date", True) #Список словарей заработанных достижений, связанных с временем в качестве пользователя из бд
        date_notearned_achievments=dbase.list_achievments(id, "date", False) #Список словарей не заработанных достижений, связанных с временем в качестве пользователя из бд
        likes_earned_achievments=dbase.list_achievments(id, "likes", True) #Список словарей заработанных достижений, связанных с лайками из бд
        likes_notearned_achievments=dbase.list_achievments(id, "likes", False) #Список словарей не заработанных достижений, связанных с лайками из бд
        posts_earned_achievments=dbase.list_achievments(id, "posts", True) #Список словарей заработанных достижений, связанных с постами из бд
        posts_notearned_achievments=dbase.list_achievments(id, "posts", False) #Список словарей не заработанных достижений, связанных с постами из бд
    except Exception as e:
        print("achievments error" + str(e))
        abort(404)
    return render_template('users/achievments.html', title=f'Достижения пользователя {user_data["login"]}', form_reg=form_reg, form_auth=form_auth, ready_achievments=ready_achievments, date_earned_achievments=date_earned_achievments, date_notearned_achievments=date_notearned_achievments, likes_earned_achievments=likes_earned_achievments, likes_notearned_achievments=likes_notearned_achievments, posts_earned_achievments=posts_earned_achievments, posts_notearned_achievments=posts_notearned_achievments, how_days=how_days, how_months=how_months, likes=likes, how_posts=how_posts, userid=id)

'''Получение заработанного достижения'''
@users.route("/achievments/earn/<userid>?<achievment_name>")
def earn_achievment(userid, achievment_name):
    if int(userid)==int(current_user.get_id()):
        dbase.earn_ready_achievment(userid, achievment_name) #Изменение в бд статуса достижения с ready на earned
    else:
        abort(404)
    return redirect(request.args.get("next") or url_for(".achievments", id=current_user.get_id()))