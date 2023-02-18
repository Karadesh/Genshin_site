from flask import Blueprint, g, redirect, url_for, abort, render_template, make_response, request, flash
from Genshin_site.FDataBase import FDataBase
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from Genshin_site.UserLogin import UserLogin
from Genshin_site.forms import AuthorisationForm, RegistrationForm
from werkzeug.security import generate_password_hash, check_password_hash

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


@users.route("/profile/<username>", methods=["POST", "GET"])
@login_required
def profile(username):
    if username != current_user.get_id():
        abort(401)
    return render_template("users/profile.html",title = "Profile")

@users.route("/profile/admin_request/<username>", methods=["POST", "GET"])
@login_required
def admin_request(username):
    if request.method=="POST":
        dbase.add_admin_request(username, request.form['admin_type'], request.form['reason'])
        return redirect(url_for('.profile', username=current_user.get_id()))
    return render_template("users/admin_request.html", title="Admin request")

@users.route("/my_posts")
def my_posts():
    return render_template("users/my_posts.html",title = "My Posts", off_menu=dbase.getOffmenu())

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
    return redirect(url_for('.profile', username=current_user.get_id()))

@users.route("/authorisation", methods=['POST', 'GET'])
def authorisation():
    #session.permanent = True #для запоминания сессии. потом включить
    if current_user.is_authenticated:
        return redirect(request.args.get("next") or url_for(".profile", username=current_user.get_id()))
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