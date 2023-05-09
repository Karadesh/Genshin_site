from flask import Blueprint, request,render_template,flash, abort, url_for, redirect, g
from Genshin_site.FDataBase import FDataBase
from flask_login import login_required, current_user
from Genshin_site.forms import AddCharForm, AddImageForm, AddStoryForm, PostForm, AddElementForm
from Genshin_site.all_posts.utils import save_picture
from transliterate import translit
from Genshin_site.admin.utils import send_feedback_answer, save_character_image
import os
import secrets


admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')
dbase = None



def user_checker():
    if current_user.getAdmin() == "user":
       return True

def authentificator():
    if not current_user.is_authenticated:
        return False
    else:
        return True
    
def moderator_checker():
    if current_user.getAdmin() == "moderator" or current_user.getAdmin() == "god":
        return True
    
def feedback_checker():
    if current_user.getAdmin() == "feedback" or current_user.getAdmin() == "god":
        return True

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
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    posts_preview={}
    posts =dbase.make_daypost()
    for i in posts:
        posts_preview[i.id] = dbase.getPostPreview(i.id)
    return render_template('admin/index.html', title='Admin pannel',posts = posts, posts_preview=posts_preview)

@admin.route('/list-posts')
def listposts():
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if moderator_checker():
        list_posts = []
        posts_preview={}
        try:
            list_posts = dbase.get_admin_posts()
            for i in list_posts:
                posts_preview[i["id"]] = dbase.getPostPreview(i["id"])
        except:
            print("Ошибка получения статей listposts")
    else:
        abort(401)
    return render_template('admin/listposts.html', title="Список постов", list_posts=list_posts, posts_preview=posts_preview)

@admin.route('/post/<alias>')
def admin_showpost(alias):
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if moderator_checker():
        get_post = dbase.get_post(alias)
        if get_post==None:
            abort(404)
        title = get_post['title'] 
        post = get_post['text']
        url = get_post['url']
        userid = get_post['userid']
        isactive = get_post['isactive']
        islocked = get_post['islocked']
        images=get_post['images']
    else:
        abort(401)
    return render_template("admin/post.html", title = title, post=post, isactive=isactive, userid=str(userid), url=url, comments=dbase.getAdminCommentsAnonce(url), islocked=islocked, images=images)

@admin.route("/lock_post/<alias>")
def lock_post(alias):
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if moderator_checker():
        try:
            locker=dbase.lockpost(alias)
            if locker==None:
                abort(404)
        except:
            print("Ошибка закрытия поста lock_post")
    else:
        abort(401)
    return(redirect(url_for('.admin_showpost', alias=alias)))

@admin.route('/changepoststatus/<alias>', methods=['POST', 'GET'])
def admin_changepoststatus(alias):
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if moderator_checker():
        get_post=dbase.get_post(alias)
        if get_post==None:
            abort(404)
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
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    else:
        if moderator_checker():
            deleter = dbase.delete_comment(id, 'deleted by admin')
            if deleter==None:
                abort(404)
        else:
            abort(401)
    return redirect(url_for('.admin_showpost', alias=postname))

@admin.route('/list-users')
def listusers():
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if moderator_checker():
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
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if moderator_checker():
        try:
            status_changer=dbase.admin_user_change_active(id)
            if status_changer==None:
                abort(404)
            return redirect(url_for('.listusers'))
        except:
            print("Ошибка Изменения статуса user_changestatus")
    else:
        abort(401)
@admin.route('/feedbacks')
def listfeedbacks():
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if feedback_checker():
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
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if feedback_checker():
        get_feedback = dbase.get_feedback(id)
        if get_feedback==None:
            abort(404)
        feedback_id = id
        username = get_feedback['username']
        email = get_feedback['email']
        message = get_feedback['message']
        get_feedback_list = [get_feedback]

        if request.method == "POST":
            try:
                dbase.create_answer(feedback_id, username, email, message, request.form['username'], request.form['message'])
                feedback=dbase.find_answer(feedback_id)
                send_feedback_answer(feedback)
                return(redirect(url_for('.listfeedbacks' )))
            except:
                print('Ошибка создания ответа на фидбек')
    else:
        abort(401)
    return render_template('admin/feedback.html', title="Фидбек", feedback=get_feedback_list, id=feedback_id)

@admin.route("/adminrequests")
def admin_requests():
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if feedback_checker():
        try:
            list_requests = dbase.admin_list_requests()
        except:
            print("Ошибка admin_requests")
    return render_template('admin/requests.html', title="Запросы на администрирование", list_requests=list_requests)

@admin.route("/aprove_request/<username>?<type>")
def aprove_admin(username,type):
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if feedback_checker():
        try:
            new_admin=dbase.add_new_admin(username,type)
            if new_admin==None:
                abort(404)
        except:
            print("ошибка добавления администратора")
    return redirect(url_for('.admin_requests'))

@admin.route("/cancel_request/<username>")
def cancel_admin(username):
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if feedback_checker():
        try:
            delete_request=dbase.admin_delete_request(username)
            if delete_request==None:
                abort(404)
        except:
            print("ошибка удаления реквеста cancel_admin")
    return redirect(url_for('.admin_requests'))

@admin.route("/add_character", methods=['POST', 'GET'])
def add_character():
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if feedback_checker():
        form_addchar = AddCharForm()
        form_addimage = AddImageForm()
        form_addstory = AddStoryForm()
        form_addelement = AddElementForm()
        select_chars = dbase.character_searcher()
        if request.method == "POST" and form_addchar.validate_on_submit():
            try:
                image = form_addchar.image.data
                url = translit(form_addchar.name.data, language_code='ru', reversed=True)
                image_name=url+".jpg"
                save_character_image(image, image_name)
                dbase.admin_add_character(form_addchar.name.data, url, url, form_addchar.story.data)
                return redirect(url_for('.add_character'))
            except:
                print("Ошибка добавления полной формы add_character")
        if request.method == "POST" and form_addimage.validate_on_submit():
            try:
                image = form_addimage.image.data
                url = translit(request.form['character'], language_code='ru', reversed=True)
                image_name=url+".jpg"
                save_character_image(image, image_name)
                dbase.admin_add_character(name = request.form['character'], url = url, image=url)
                return redirect(url_for('.add_character'))
            except:
                print("Ошибка добавления картинки add_character")
        if request.method == "POST" and form_addstory.validate_on_submit():
            try:
                url = translit(request.form['character'], language_code='ru', reversed=True)
                dbase.admin_add_character(name = request.form['character'], url = url, story = form_addstory.story.data)
                return redirect(url_for('.add_character'))
            except:
                print("Ошибка добавления истории add_character")
        if request.method == "POST" and form_addelement.validate_on_submit():
            try:
                url = translit(request.form['character'], language_code='ru', reversed=True)
                dbase.admin_add_character(name = request.form['character'], url = url, element = form_addelement.element.data)
            except:
                print("Ошибка добавления элемента add_character")
    return render_template('admin/addchar.html', title="Добавление/изменение персонажа", form_addchar=form_addchar, form_addimage=form_addimage, form_addstory=form_addstory, select_chars=select_chars, form_addelement=form_addelement)

@admin.route("/make_post", methods=["POST", "GET"])
def admin_make_post():
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if feedback_checker():
        form = PostForm()
        select_chars = dbase.character_searcher()
        if request.method=="POST":
            if form.validate_on_submit():
                userid = int(current_user.get_id())
                try:
                    dbase.create_post(form.title.data, form.text.data, userid, request.form['character'])
                    for i in form.image.data:
                        null_checker=i.filename
                    if null_checker != '':
                        post_id = dbase.get_post_id(form.title.data)
                    for i in form.image.data:
                        image_name = secrets.token_hex(16)
                        _, f_ext = os.path.splitext(i.filename)
                        image_name=image_name+f_ext
                        save_picture(i, image_name)
                        dbase.add_images(image_name, post_id)
                    return redirect(url_for('.admin_make_post'))
                except:
                    flash('Ошибка добавления статьи', category = 'error')
    return render_template('admin/makepost.html', title="Создать пост", form=form, select_chars=select_chars)

@admin.route("/makepostofday/<id>")
def make_post_of_day(id):
    if not authentificator():
        return redirect(url_for('users.authorisation'))
    if user_checker():
       return abort(401)
    if feedback_checker():
        try:
            postofday=dbase.choose_daypost(id)
            if postofday==None:
                abort(404)
            return redirect(url_for(".index"))
        except:
            print("Не получилось выбрать пост дня")