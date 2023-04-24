from flask import Blueprint, g, redirect, url_for, abort, render_template, make_response, request, flash
from Genshin_site.FDataBase import FDataBase
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from Genshin_site.UserLogin import UserLogin
from Genshin_site.forms import AuthorisationForm, RegistrationForm, RequestResetForm, ResetPasswordForm, ChangeEmailForm
from werkzeug.security import generate_password_hash, check_password_hash
from Genshin_site.users.utils import send_reset_email, background_maker 
from datetime import datetime

users = Blueprint('users', __name__, template_folder='templates', static_folder='static')
login_manager = LoginManager(users)
login_manager.login_view = 'authorisation'
login_manager.login_message='Авторизуйтесь, чтобы просматривать эту страницу'
login_manager.login_message_category = "success"

dbase = None
@users.before_request
def before_request():
    """соединение с бд перед выполнением запроса"""
    global dbase
    db =  g.get('link_db')
    dbase = FDataBase()

@users.teardown_request
def teardown_request(request):
    global db
    db =  None
    return request

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('mainapp.index'))


@users.route("/profile/<username>?<int:page_num>", methods=["POST", "GET"])
def profile(username, page_num=1):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    user_data = dbase.user_data(username)
    if user_data==None:
        abort(404)
    if user_data["active_background"] != None:
        active_background = background_maker(user_data["active_background"])
    else:
        active_background=None
    try:
        current_user_checker = (user_data['id'] == int(current_user.get_id()))
    except Exception:
        current_user_checker = False
    #if username != current_user.get_id():
    #    abort(401)
    likes = dbase.user_likes(username)
    try:
        guides=dbase.my_guides(username, int(page_num))
        if guides==[]:
            abort(404)
        posts_likes={}
        posts_images={}
        for i in guides:
            posts_likes[i.id] = dbase.how_likes(i.id)
            posts_images[i.id] = dbase.getPostPreview(i.id)
    except Exception:
        abort(404)
    image = dbase.search_character_image(username)
    return render_template("users/profile.html",title = "Profile", likes=likes, image=image, user_data=user_data, current_user_checker = current_user_checker,guides=guides, posts_likes=posts_likes, posts_images=posts_images, userid=user_data["id"], username=user_data["login"],form_reg=form_reg, form_auth=form_auth, active_background=active_background)

@users.route("/profile/profile_settings/<id>", methods=["POST", "GET"])
def profile_settings(id):
    form=ChangeEmailForm()
    if int(current_user.get_id())!=int(id):
        abort(401)
    else:
        backgrounds = dbase.choose_background(id)
        user_data = dbase.user_data(id)
        select_chars = dbase.character_searcher()
        if request.method=="POST":
            dbase.choose_character(request.form["character"], current_user.get_id())
    image = dbase.search_character_image(id)
    return render_template("users/profile_settings.html", title="Настройки", select_chars=select_chars, image=image, user_data=user_data, backgrounds=backgrounds, form=form)

@users.route("/profile/change_email/<id>", methods=["POST", "GET"])
def change_email(id):
    form=ChangeEmailForm()
    if int(current_user.get_id())!=int(id):
        abort(401)
    if request.method=="POST":
        try:
            dbase.change_email(id, form.email.data)
        except Exception:
            print("Ошибка change_email")
    return redirect(url_for('.profile_settings', id=id))
        

@users.route("/profile/select_background/<id>", methods=["POST", "GET"])
def select_background(id):
    if int(current_user.get_id())!=int(id):
        abort(401)
    if request.method=="POST":
        dbase.add_background(id, request.form["backgrounds"])
    return redirect(url_for('.profile_settings', id=id))

@users.route("/profile/admin_request/<username>", methods=["POST", "GET"])
@login_required
def admin_request(username):
    if request.method=="POST":
        username=current_user.getName()
        dbase.add_admin_request(username, request.form['admin_type'], request.form['reason'])
        return redirect(url_for('.profile', username=current_user.get_id(), page_num=1))
    return render_template("users/admin_request.html", title="Admin request")

@users.route('/userava')
@login_required
def userava():
    img=current_user.getAvatar(users)
    if not img:
        return ""
    h=make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h

@users.route('/upload', methods=["POST", "GET"])
@login_required
def upload():
    if request.method == 'POST':
        file = request.files['file']
        if file and current_user.verifyExt(file.filename):
            try:
                img = file.read()
                res = dbase.updateUserAvatar(img, current_user.get_id())
                if not res:
                    flash("Ошибка обновления аватара", "error")
                flash("Аватар обновлен", "success")
            except FileNotFoundError as e:
                flash("Ошибка чтения файла", "error")
        else:
            flash("Ошибка обновления аватара", "error")
    return redirect(url_for('.profile_settings', id=current_user.get_id()))

@users.route("/authorisation", methods=['POST', 'GET'])
def authorisation():
    #session.permanent = True #для запоминания сессии. потом включить
    if current_user.is_authenticated:
        return redirect(request.args.get("next") or url_for(".profile", username=current_user.get_id(), page_num=1))
    form = AuthorisationForm()
    if form.validate_on_submit():
        user = dbase.getUserByLogin(form.name.data)
        if user and check_password_hash(user.password, form.password.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("mainapp.index"))
        flash("Неверный логин или пароль", "error")
    return render_template("users/authorisation.html", title="Authorisation", form=form) 

@users.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.password.data)
        try:
            dbase.add_user(form.name.data, hash, form.email.data)
            flash("Вы успешно зарегистрированы!", "success")
            return redirect(url_for('.authorisation'))
        except:
            flash("Ошибка при добавлении в БД", "error")
    else:
        flash("Проверьте поле 'e-mail'. Также пароль должен быть не менее одного символа", "error")
    return render_template("users/register.html", title="Registration", form=form)

@users.route("/auth_reg", methods=["POST", "GET"])
def auth_reg():
    if current_user.is_authenticated:
        return redirect(request.args.get("next") or url_for(".profile", username=current_user.get_id(), page_num=1))
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    if form_auth.validate_on_submit():
        user = dbase.getUserByLogin(form_auth.name.data)
        if user and check_password_hash(user.password, form_auth.password.data):
            userlogin = UserLogin().create(user)
            rm = form_auth.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("mainapp.index"))
        flash("Неверный логин или пароль", "error")
    if form_reg.validate_on_submit():
        hash = generate_password_hash(form_reg.password.data)
        try:
            dbase.add_user(form_reg.name.data, hash, form_reg.email.data)
            dbase.user_week_likes(form_reg.email.data)
            flash("Вы успешно зарегистрированы!", "success")
            return redirect(url_for('.authorisation'))
        except:
            flash("Ошибка при добавлении в БД", "error")
    else:
        flash("Проверьте поле 'e-mail'. Также пароль должен быть не менее одного символа", "error")
    return render_template("/base.html", form_auth=form_auth, form_reg=form_reg)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('mainapp.index'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = dbase.search_user_by_email(form.email.data)
        send_reset_email(user)
        flash('На почту отправлено письмо с''инструкциями по сбросу пароля', 'success')
        return redirect(url_for('.authorisation'))
    return render_template('users/reset_request.html', title='Сброс пароля', form=form)

@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('mainapp.index'))
    user = dbase.verify_reset_tokens(token)
    if user is None:
        flash('Это недействительный или просроченный токен', 'error')
        return redirect(url_for('.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.password.data)
        dbase.change_password(user, hash)
        flash('Ваш пароль был обновлен!''Теперь вы можете авторизоваться', 'success')
        return redirect(url_for('.authorisation'))
    return render_template('users/reset_token.html', title='Сброс пароля', form=form)

@users.route("/userguides/<id>?<int:page_num>")
def my_guides(id, page_num):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    try:
        user_data = dbase.user_data(id)
        if user_data==None:
            abort(404)
        guides=dbase.my_guides(id, page_num)
        if guides==[]:
            abort(404)
        likes={}
        images={}
        for i in guides:
            likes[i.id] = dbase.how_likes(i.id)
            images[i.id] = dbase.getPostPreview(i.id)
    except Exception:
        abort(404)
    return render_template('users/my_guides.html', title=f'Гайды пользователя {user_data["login"]}', guides=guides, likes=likes, images=images, userid=user_data["id"], username=user_data["login"], form_reg=form_reg, form_auth=form_auth)


@users.route("/achievments/<id>")
def achievments(id):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    try: 
        user_data = dbase.user_data(id)
        if user_data==None:
            abort(404)
    except Exception:
        print("achievments error")
        abort(404)
    return render_template('users/achievments.html', title=f'Достижения пользователя {user_data["login"]}', form_reg=form_reg, form_auth=form_auth)
