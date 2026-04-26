import os
from flask import Blueprint, render_template, current_app, send_from_directory

from app.utils.middleware import login_required

routes = Blueprint('frontend', __name__, url_prefix='/', template_folder='templates', static_folder='static')

@routes.route('/')
def index():
    return render_template("page/home.html")

@routes.route('/schedule')
def schedule():
    return render_template("page/schedule.html")

@routes.route('/booking')
@login_required
def bookingSeat():
    return render_template("page/booking_seat_page.html")

@routes.route('/profile')
@login_required
def profile():
    return render_template("page/profile.html")

@routes.route('/history')
@login_required
def history():
    return render_template("page/history.html")

@routes.route('/cancel')
@login_required
def cancel():
    return render_template("page/cancel.html")

@routes.route('/google')
def google():
    return render_template("components/user/google.html")

@routes.route('/film')
def film():
    return render_template("page/film.html")

@routes.route('/film/detail')
def filmDetail():
    return render_template("page/film_detail.html")

@routes.route('/templates/<path:filename>')
def templates(filename):
    template_dir = os.path.join(current_app.root_path, 'templates')
    return send_from_directory(template_dir, filename)

@routes.app_errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

@routes.app_errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html'), 500

@routes.app_errorhandler(403)
def forbidden(error):
    return render_template('errors/403.html'), 403

