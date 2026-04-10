import os
from flask import Blueprint, render_template, current_app, send_from_directory

routes = Blueprint('frontend', __name__, url_prefix='/', template_folder='templates', static_folder='static')

@routes.route('/')
def index():
    return render_template("page/home.html")

@routes.route('/schedule')
def schedule():
    return render_template("page/schedule.html")

@routes.route('/booking')
def bookingSeat():
    return render_template("page/booking_seat_page.html")

@routes.route('/profile')
def profile():
    return render_template("page/profile.html")

@routes.route('/history')
def history():
    return render_template("page/history.html")

@routes.route('/cancel')
def cancel():
    return render_template("page/cancel.html")

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