from flask import Blueprint, g, jsonify, request, make_response
from Genshin_site.FDataBase import FDataBase

api = Blueprint('api', __name__, template_folder='templates', static_folder='static')

dbase = None
'''соединение с бд перед выполнением запроса'''
@api.before_request
def before_request():
    global dbase
    db =  g.get('link_db')
    dbase = FDataBase()

'''Отключение от бд после выполнения запроса'''
@api.teardown_request
def teardown_request(request):
    global db
    db =  None
    return request

@api.route('/posts', methods=['GET'])
def api_posts():
    validated_posts=dbase.api_validated_posts()
    return jsonify(validated_posts)

@api.route('/posts', methods=['POST'])
def api_create_post():
    post_creation = request.json
    post_creator = dbase.api_create_post(post_creation)
    if post_creator == True:
        return 'created', 200
    else:
        return 'post with that name was already made', 400
    
@api.route('/posts/<int:postid>', methods=['DELETE'])
def api_delete_post(postid):
    post_deleter = dbase.api_delete_post(postid)
    if post_deleter == True:
        return 'deleted', 204
    else:
        return 'cannot delete', 400