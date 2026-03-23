from flask import Blueprint

show_api = Blueprint('show', __name__, url_prefix='/shows')

@show_api.route('/')
def shows():
    pass

@show_api.route('/<int:id>/seats/')
def seats(id):
    pass


