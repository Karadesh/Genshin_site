from flask import Blueprint, request,render_template,flash, url_for, redirect, session, g
import sqlite3

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

def login_admin():
    session['admin_logged'] = 1

def isLogged():
    return True if session.get('admin_logged') else False

def logout_admin():
    session.pop('admin_logged', None)

menu = [{'url': 'index', 'title': 'Главная'},
        {'url': '.logout', 'title': 'Выйти'},
        {'url': '.listposts', 'title': 'Список постов'},
        {'url': '.listusers', 'title': 'Список пользователей'}]

db=None
@admin.before_request
def before_request():
    global db
    db =  g.get('link_db')

@admin.teardown_request
def teardown_request(request):
    global db
    db =  None
    return request

@admin.route('/')
def index():
    if not isLogged():
        return redirect(url_for('.login'))
    return render_template('admin/index.html', menu=menu, title='Admin pannel')

@admin.route('/login', methods=['POST', 'GET'])
def login():
    if isLogged():
        return redirect(url_for('.index'))
    if request.method == "POST":
        if request.form['user'] == "admin" and request.form['password'] == '123':
            login_admin()
            return redirect(url_for('.index'))
        else:
            flash("Неверная пара логин/пароль", "error")
    return render_template('admin/login.html')

@admin.route('/logout', methods=['POST', 'GET'])
def logout():
    if not isLogged():
        return redirect(url_for('.login'))
    else:
        logout_admin()
    return redirect(url_for('.login'))

@admin.route('/list-posts')
def listposts():
    if not isLogged():
        return redirect(url_for('.login'))
    list_posts = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT title, text, url FROM posts")
            list_posts = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей" + str(e))
    return render_template('admin/listposts.html', title="Список постов", menu=menu, list_posts=list_posts)

@admin.route('/list-users')
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))
    list_users = []
    if db:
        try:
            cur = db.cursor()
            cur.execute(f"SELECT login, email FROM users ORDER BY time DESC")
            list_users = cur.fetchall()
        except sqlite3.Error as e:
            print("Ошибка получения статей" + str(e))
    return render_template('admin/listusers.html', title="Список пользователей", menu=menu, list_users=list_users)