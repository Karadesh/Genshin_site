from flask import Blueprint, render_template

apperrors = Blueprint('apperrors', __name__, template_folder='templates', static_folder='static')

@apperrors.app_errorhandler(404)
def pageNotFound(error):
    return render_template("apperrors/page404.html",title = "Страница не найдена"), 404

@apperrors.app_errorhandler(401)
def pageAbort(error):
    return render_template("apperrors/page401.html",title = "Не авторизован"), 401