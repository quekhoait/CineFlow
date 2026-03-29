from flask import Blueprint

film_api = Blueprint('film', __name__, url_prefix='/films')

@film_api.route('/')
def films():
    pass

@film_api.route('/<int:id>/shows/')
def shows(id):
    pass