from flask import Flask, render_template, url_for, request, flash, session, redirect, abort, g, make_response
import sqlite3
import os
from config import Config
from FDataBase import FDataBase
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from UserLogin import UserLogin
import base64
from forms import AuthorisationForm, RegistrationForm


app = Flask(__name__)
app.config.from_object(Config)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'gensh.db')))
#app.permanent_session_lifetime = datetime.timedelta(days=10) #для запоминания сессии. Потом включить
login_manager = LoginManager(app)
login_manager.login_view = 'authorisation'
login_manager.login_message='Авторизуйтесь, чтобы просматривать эту страницу'
login_manager.login_message_category = "success"



def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
        db.commit()
        db.close()

def get_db():
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
        return g.link_db

def get_avatars_dict(url, app=app):
    username = dbase.getCommentatorsNames(url)
    usernames = []
    try:
        for i in username:
            usernames.append(i[0])
        avas_dict = {}
        for j, k in dbase.getCommentatorsAvas(usernames):
            if k == None:
                with app.open_resource(app.root_path + url_for('static', filename= 'images/default.jpeg'), "rb") as f:
                    base64_string=base64.b64encode(f.read()).decode('utf-8')
            else:
                base64_string = base64.b64encode(k).decode('utf-8')
            img_url=f'data:image/png;base64,{base64_string}'
            avas_dict[j] = img_url
    except:
        pass
    return avas_dict

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'link_db'):
        g.link_db.close()

dbase = None
@app.before_request
def before_request():
    """соединение с бд перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase=FDataBase(db)

@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id, dbase)


@app.route("/index")
@app.route("/")
def index():
    return render_template("index.html", off_menu=dbase.getOffmenu())

@app.route("/posts")
def posts():
    return render_template("posts.html",title = "Список постов", off_menu=dbase.getOffmenu(), posts=dbase.getPostsAnonce())

@app.route("/post/<alias>", methods=['POST', 'GET'])
def show_post(alias):
    title, post, url, userid = dbase.get_post(alias)
    if not title:
        abort(404)
    if request.method == "POST":
        if len(request.form['comment'])> 1:
            res = dbase.create_comment(request.form['comment'], alias)
            if not res:
                flash('Ошибка добавления комментария', category = 'error')
            else:
                return(redirect(url_for('show_post', alias=url)))
        else:
            flash('Ошибка добавления комментария', category = 'error')
    return render_template("post.html", title = title, post=post, userid=str(userid), off_menu=dbase.getOffmenu(), comments=dbase.getCommentsAnonce(url), url=[url], avatars=get_avatars_dict(url))

@app.route("/confirm_delete/<alias>")
@login_required
def confirm_delete(alias):
    return render_template("confirm_delete.html", alias=alias)

@app.route("/delete_post/<alias>", methods=['GET','DELETE'])
@login_required
def delete_post(alias):
        dbase.delete_post(alias)
        return(redirect(url_for('posts')))

@app.route("/delete_comment/<alias>?<id>", methods=['GET', 'DELETE'])
@login_required
def delete_comment(alias, id):
    dbase.delete_comment(id)
    return(redirect(url_for('show_post', alias=alias)))

@app.route("/my_posts")
def my_posts():
    return render_template("my_posts.html",title = "My Posts", off_menu=dbase.getOffmenu())

@app.route("/create_post", methods=['POST', 'GET'])
@login_required
def create_post():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post'])>1: #проверку на свой вкус
            userid = int(current_user.get_id())
            res = dbase.create_post(request.form['name'], request.form['post'], userid)
            if not  res:
                flash('Ошибка добавления статьи', category = 'error')
            else:
                return redirect(url_for('posts'))
        else:
            flash('Ошибка добавления статьи', category = 'error')
    return render_template("create_post.html",title = "Create Post", off_menu=dbase.getOffmenu())

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route("/profile/<username>")
@login_required
def profile(username):
    if username != current_user.get_id():
        abort(401)
    return render_template("profile.html",title = "Profile")

@app.route('/userava')
@login_required
def userava():
    img=current_user.getAvatar(app)
    if not img:
        return ""
    h=make_response(img)
    h.headers['Content-Type'] = 'image/png'
    return h

@app.route('/upload', methods=["POST", "GET"])
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
    return redirect(url_for('profile', username=current_user.get_id()))

@app.route("/authorisation", methods=['POST', 'GET'])
def authorisation():
    #session.permanent = True #для запоминания сессии. потом включить
    if current_user.is_authenticated:
        return redirect(request.args.get("next") or url_for("profile", username=current_user.get_id()))
    form = AuthorisationForm()
    if form.validate_on_submit():
        user = dbase.getUserByLogin(form.name.data)
        if user and check_password_hash(user['password'], form.password.data):
            userlogin = UserLogin().create(user)
            rm = form.remember.data
            login_user(userlogin, remember=rm)
            return redirect(request.args.get("next") or url_for("index"))
        flash("Неверный логин или пароль", "error")
    return render_template("authorisation.html", title="Authorisation", form=form) 

@app.route("/register", methods=["POST", "GET"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hash = generate_password_hash(form.password.data)
        res = dbase.add_user(form.name.data, hash, form.email.data)
        if res:
            flash("Вы успешно зарегистрированы!", "success")
            return redirect(url_for('authorisation'))
        else:
            flash("Ошибка при добавлении в БД", "error")
    else:
        flash("Проверьте поле 'e-mail'. Также пароль должен быть не менее одного символа", "error")
    return render_template("register.html", title="Registration", form=form)

@app.route("/guides")
def guides():
    return render_template("guides.html",title = "Guides", off_menu=dbase.getOffmenu())

@app.route("/characters")
def characters():
    return render_template("characters.html",title = "Characters", off_menu=dbase.getOffmenu())

@app.route("/feedback", methods=["POST", "GET"])
def feedback():
    if request.method == 'POST':
        if request.form['message'] == '':
            flash('Пожалуйста, напишите ваше сообщение', category='error')
        else:
            flash('Сообщение отправлено', category='success')
            print(request.form['message'])
    return render_template("feedback.html",title = "Feedback", off_menu=dbase.getOffmenu())

@app.errorhandler(404)
def pageNotFound(error):
    return render_template("page404.html",title = "Страница не найдена", off_menu=dbase.getOffmenu()), 404

@app.errorhandler(401)
def pageAbort(error):
    return render_template("page401.html",title = "Не авторизован", off_menu=dbase.getOffmenu()), 401



#create_db()

if __name__ == "__main__":
    app.run(debug=True)
