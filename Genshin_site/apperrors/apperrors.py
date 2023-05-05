from flask import Blueprint, render_template
from Genshin_site.forms import RegistrationForm, AuthorisationForm

apperrors = Blueprint('apperrors', __name__, template_folder='templates', static_folder='static')

@apperrors.app_errorhandler(404)
def pageNotFound(error):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    return render_template("apperrors/page404.html",title = "Страница не найдена", form_auth=form_auth, form_reg=form_reg), 404

@apperrors.app_errorhandler(401)
def pageAbort(error):
    form_auth = AuthorisationForm()
    form_reg = RegistrationForm()
    return render_template("apperrors/page401.html",title = "Не авторизован", form_auth=form_auth, form_reg=form_reg), 401