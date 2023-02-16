from flask import Blueprint, request,render_template,flash, abort, url_for, redirect, g
from Genshin_site.FDataBase import FDataBase
from flask_login import login_required, current_user

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')

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
    if not current_user.is_authenticated:
        return redirect(url_for('users.authorisation'))
    elif current_user.getAdmin() == "user":
        abort(401)
    return render_template('admin/index.html', title='Admin pannel')

@admin.route('/list-posts')
def listposts():
    if not current_user.is_authenticated:
        return redirect(url_for('users.authorisation'))
    if current_user.getAdmin() == "moderator" or current_user.getAdmin() == "god":
        list_posts = []
        try:
            list_posts = dbase.get_admin_posts()
        except:
            print("Ошибка получения статей listposts")
    else:
        abort(401)
    return render_template('admin/listposts.html', title="Список постов", list_posts=list_posts)

@admin.route('/post/<alias>')
def admin_showpost(alias):
    if not current_user.is_authenticated:
        return redirect(url_for('users.authorisation'))
    if current_user.getAdmin() == "moderator" or current_user.getAdmin() == "god":
        get_post = dbase.get_post(alias)
        title = get_post['title'] 
        post = get_post['text']
        url = get_post['url']
        userid = get_post['userid']
        isactive = get_post['isactive']
        islocked = get_post['islocked']
    else:
        abort(401)
    return render_template("admin/post.html", title = title, post=post, isactive=isactive, userid=str(userid), url=url, comments=dbase.getAdminCommentsAnonce(url), islocked=islocked)

@admin.route("/lock_post/<alias>")
def lock_post(alias):
    if not current_user.is_authenticated:
        return redirect(url_for('users.authorisation'))
    if current_user.getAdmin() == "moderator" or current_user.getAdmin() == "god":
        try:
            dbase.lockpost(alias)
        except:
            print("Ошибка закрытия поста lock_post")
    else:
        abort(401)
    return(redirect(url_for('.admin_showpost', alias=alias)))

@admin.route('/changepoststatus/<alias>', methods=['POST', 'GET'])
def admin_changepoststatus(alias):
    if not current_user.is_authenticated:
        return redirect(url_for('users.authorisation'))
    if current_user.getAdmin() == "moderator" or current_user.getAdmin() == "god":
        get_post=dbase.get_post(alias)
        if request.method == "POST":
            try:
                dbase.admin_post_change_active(alias, request.form['reason'])
                return redirect(url_for('.listposts'))
            except:
                print("Ошибка изменения статуса postchangeactive")
                return False
    else:
        abort(401)
    return render_template("admin/postdelete.html", post=get_post)

@admin.route('/deletecomment/<id>?<postname>')
def deletecomment(id, postname):
    if not current_user.is_authenticated:
        return redirect(url_for('users.authorisation'))
    else:
        if current_user.getAdmin() == "moderator" or current_user.getAdmin() == "god":
            dbase.delete_comment(id, 'deleted by admin')
        else:
            abort(401)
    return redirect(url_for('.admin_showpost', alias=postname))

@admin.route('/list-users')
def listusers():
    if not current_user.is_authenticated:
        return redirect(url_for('users.authorisation'))
    if current_user.getAdmin() == "moderator" or current_user.getAdmin() == "god":
        list_users = []
        try:
            list_users = dbase.admin_users()
        except:
            print("Ошибка получения статей listusers")
    else:
        abort(401)
    return render_template('admin/listusers.html', title="Список пользователей", list_users=list_users)

@admin.route('/user_changestatus/<id>')
def user_changestatus(id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.authorisation'))
    if current_user.getAdmin() == "moderator" or current_user.getAdmin() == "god":
        try:
            dbase.admin_user_change_active(id)
            return redirect(url_for('.listusers'))
        except:
            print("Ошибка Изменения статуса user_changestatus")
    else:
        abort(401)
@admin.route('/feedbacks')
def listfeedbacks():
    if not current_user.is_authenticated:
        return redirect(url_for('users.authorisation'))
    if current_user.getAdmin() == "feedback" or current_user.getAdmin() == "god":
        list_feedbacks = []
        try:
            list_feedbacks = dbase.admin_feedback()
        except:
            print("Ошибка получения статей listposts")
    else:
        abort(401)
    return render_template('admin/feedbacks.html', title="Фидбек", list_feedbacks=list_feedbacks)

@admin.route("/feedback/<int:id>", methods=['POST', 'GET'])
def feedbackanswer(id):
    if not current_user.is_authenticated:
        return redirect(url_for('users.authorisation'))
    if current_user.getAdmin() == "feedback" or current_user.getAdmin() == "god":
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
    else:
        abort(401)
    return render_template('admin/feedback.html', title="Фидбек", feedback=get_feedback_list, id=feedback_id)