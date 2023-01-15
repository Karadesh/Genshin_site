from flask import Blueprint, request,render_template,flash, url_for, redirect, session, g
import sqlite3
from Genshin_site.FDataBase import FDataBase

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

def login_admin():
    session['admin_logged'] = 1

def isLogged():
    return True if session.get('admin_logged') else False

def logout_admin():
    session.pop('admin_logged', None)

menu = [{'url': '.index', 'title': 'Главная'},
        {'url': '.logout', 'title': 'Выйти'},
        {'url': '.listposts', 'title': 'Список постов'},
        {'url': '.listusers', 'title': 'Список пользователей'},
        {'url': '.listfeedbacks', 'title': 'Фидбек'}]

dbase = None
@admin.before_request
def before_request():
    """соединение с бд перед выполнением запроса"""
    global dbase
    db =  g.get('link_db')
    dbase = FDataBase()

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
        if request.form['user'] == "admin" and request.form['password'] == '123': #сделать полноценную проверку с бд
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
    try:
        list_posts = dbase.get_admin_posts()
    except:
        print("Ошибка получения статей listposts")
    return render_template('admin/listposts.html', title="Список постов", menu=menu, list_posts=list_posts)

@admin.route('/post/<alias>')
def admin_showpost(alias):
    if not isLogged():
        return redirect(url_for('.login'))
    else:
        get_post = dbase.get_post(alias)
        title = get_post['title'] 
        post = get_post['text']
        url = get_post['url']
        userid = get_post['userid']
        isactive = get_post['isactive']
        islocked = get_post['islocked']
    return render_template("admin/post.html", title = title, post=post, isactive=isactive, userid=str(userid), url=url, comments=dbase.getAdminCommentsAnonce(url), islocked=islocked)

@admin.route("/lock_post/<alias>")
def lock_post(alias):
    try:
        dbase.lockpost(alias)
    except:
        print("Ошибка закрытия поста lock_post")
    return(redirect(url_for('.admin_showpost', alias=alias)))

@admin.route('/changepoststatus/<alias>', methods=['POST', 'GET'])
def admin_changepoststatus(alias):
    if not isLogged():
        return redirect(url_for('.login'))
    else:
        get_post=dbase.get_post(alias)
        if request.method == "POST":
            try:
                dbase.admin_post_change_active(alias, request.form['reason'])
                return redirect(url_for('.listposts'))
            except:
                print("Ошибка изменения статуса postchangeactive")
                return False
    return render_template("admin/postdelete.html", post=get_post)

@admin.route('/deletecomment/<id>?<postname>')
def deletecomment(id, postname):
    if not isLogged():
        return redirect(url_for('.login'))
    else:
        dbase.delete_comment(id, 'deleted by admin')
        return redirect(url_for('.admin_showpost', alias=postname))

@admin.route('/list-users')
def listusers():
    if not isLogged():
        return redirect(url_for('.login'))
    list_users = []
    try:
        list_users = dbase.admin_users()
    except:
            print("Ошибка получения статей listusers")
    return render_template('admin/listusers.html', title="Список пользователей", menu=menu, list_users=list_users)

@admin.route('/feedbacks')
def listfeedbacks():
    if not isLogged():
        return redirect(url_for('.login'))
    list_feedbacks = []
    try:
        list_feedbacks = dbase.admin_feedback()
    except:
        print("Ошибка получения статей listposts")
    return render_template('admin/feedbacks.html', title="Фидбек", menu=menu, list_feedbacks=list_feedbacks)

@admin.route("/feedback/<int:id>", methods=['POST', 'GET'])
def feedbackanswer(id):
    if not isLogged():
        return redirect(url_for('.login'))
    get_feedback = dbase.get_feedback(id)
    print(id)
    feedback_id = id
    username = get_feedback['username']
    email = get_feedback['email']
    message = get_feedback['message']
    get_feedback_list = [get_feedback]

    if request.method == "POST":
        try:
            dbase.create_answer(feedback_id, username, email, message, request.form['username'], request.form['message'])
            return(redirect(url_for('.listfeedbacks' )))
        except:
            print('Ошибка создания ответа на фидбек')
    return render_template('admin/feedback.html', title="Фидбек", menu=menu, feedback=get_feedback_list, id=feedback_id)