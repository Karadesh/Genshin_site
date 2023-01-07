from flask import Blueprint, request,render_template,flash, url_for, redirect, g, abort
from flask_login import login_required, current_user
from Genshin_site.FDataBase import FDataBase
import base64

all_posts = Blueprint('all_posts', __name__, template_folder='templates', static_folder='static')

dbase = None
@all_posts.before_request
def before_request():
    """соединение с бд перед выполнением запроса"""
    global dbase
    db =  g.get('link_db')
    dbase = FDataBase()

@all_posts.teardown_request
def teardown_request(request):
    global db
    db =  None
    return request

def get_avatars_dict(url, app=all_posts):
    try:
        usernames = dbase.getCommentatorsNames(url)
        avas_dict = {}
        for i in dbase.getCommentatorsAvas(usernames):
            for j, k in i.items():
                if k == None:
                    with app.open_resource(app.root_path + url_for('.static', filename= 'images/default.jpeg'), "rb") as f:
                        base64_string=base64.b64encode(f.read()).decode('utf-8')
                else:
                    base64_string = base64.b64encode(k).decode('utf-8')
                img_url=f'data:image/png;base64,{base64_string}'
                avas_dict[j] = img_url
    except:
        pass
    return avas_dict

@all_posts.route("/posts")
def posts():
    return render_template("all_posts/posts.html",title = "Список постов", off_menu=dbase.getOffmenu(), posts=dbase.getPostsAnonce())

@all_posts.route("/post/<alias>", methods=['POST', 'GET'])
def show_post(alias):
    get_post = dbase.get_post(alias)
    title = get_post['title'] 
    post = get_post['text']
    url = get_post['url']
    userid = get_post['userid']
    if not title:
        abort(404)
    if request.method == "POST":
        if len(request.form['comment'])> 1:
            c = dbase.create_comment(request.form['comment'], alias)
            if not c:
                flash('Ошибка добавления комментария', category = 'error')
            else:
                return(redirect(url_for('.show_post', alias=url)))
        else:
            flash('Ошибка добавления комментария', category = 'error')
    return render_template("all_posts/post.html", title = title, post=post, userid=str(userid), off_menu=dbase.getOffmenu(), comments=dbase.getCommentsAnonce(url), url=[url], avatars=get_avatars_dict(url))

@all_posts.route("/confirm_delete/<alias>")
@login_required
def confirm_delete(alias):
    return render_template("all_posts/confirm_delete.html", alias=alias)

@all_posts.route("/delete_post/<alias>", methods=['GET','DELETE'])
@login_required
def delete_post(alias):
        dbase.delete_post(alias)
        return(redirect(url_for('.posts')))

@all_posts.route("/delete_comment/<alias>?<id>", methods=['GET', 'DELETE'])
@login_required
def delete_comment(alias, id):
    dbase.delete_comment(id)
    return(redirect(url_for('.show_post', alias=alias)))

@all_posts.route("/create_post", methods=['POST', 'GET'])
@login_required
def create_post():
    if request.method == "POST":
        if len(request.form['name']) > 4 and len(request.form['post'])>1: #проверку на свой вкус
            userid = int(current_user.get_id())
            try:
                res = dbase.create_post(request.form['name'], request.form['post'], userid)
                return redirect(url_for('.posts'))
            except:
                flash('Ошибка добавления статьи', category = 'error')
        else:
            flash('Ошибка добавления статьи', category = 'error')
    return render_template("all_posts/create_post.html",title = "Create Post", off_menu=dbase.getOffmenu())


