from flask import Blueprint, render_template

routes = Blueprint('frontend', __name__, url_prefix='/', template_folder='templates', static_folder='static')

@routes.route('/')
def index():
    return render_template("user/index.html")