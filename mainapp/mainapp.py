from flask import Blueprint, render_template, g, request, flash
from FDataBase import FDataBase

mainapp = Blueprint('mainapp', __name__, template_folder='templates', static_folder='static')

dbase = None
@mainapp.before_request
def before_request():
    """соединение с бд перед выполнением запроса"""
    global dbase
    db =  g.get('link_db')
    dbase = FDataBase(db)

@mainapp.teardown_request
def teardown_request(request):
    global db
    db =  None
    return request

@mainapp.route("/index")
@mainapp.route("/")
def index():
    return render_template("mainapp/index.html", off_menu=dbase.getOffmenu())

@mainapp.route("/guides")
def guides():
    return render_template("mainapp/guides.html",title = "Guides", off_menu=dbase.getOffmenu())

@mainapp.route("/characters")
def characters():
    return render_template("mainapp/characters.html",title = "Characters", off_menu=dbase.getOffmenu())

@mainapp.route("/feedback", methods=["POST", "GET"])
def feedback():
    if request.method == 'POST':
        if request.form['message'] == '':
            flash('Пожалуйста, напишите ваше сообщение', category='error')
        else:
            flash('Сообщение отправлено', category='success')
            print(request.form['message'])
    return render_template("mainapp/feedback.html",title = "Feedback", off_menu=dbase.getOffmenu())