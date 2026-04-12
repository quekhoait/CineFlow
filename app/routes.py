import os
from flask import Blueprint, render_template, current_app, send_from_directory, redirect, url_for
from flask_jwt_extended import jwt_required

from app import jwt

routes = Blueprint('frontend', __name__, url_prefix='/', template_folder='templates', static_folder='static')

@routes.route('/')
def index():
    return render_template("page/home.html")

@routes.route('/schedule')
def schedule():
    return render_template("page/schedule.html")

@routes.route('/booking')
@jwt_required()
def bookingSeat():
    return render_template("page/booking_seat_page.html")

@routes.route('/profile')
@jwt_required()
def profile():
    return render_template("page/profile.html")

@routes.route('/history')
@jwt_required()
def history():
    return render_template("page/history.html")

@routes.route('/cancel')
@jwt_required()
def cancel():
    return render_template("page/cancel.html")

@routes.route('/templates/<path:filename>')
def templates(filename):
    template_dir = os.path.join(current_app.root_path, 'templates')
    return send_from_directory(template_dir, filename)

@jwt.unauthorized_loader
def unauthorized_callback(callback):
    return redirect(url_for('frontend.index', error='unauthorized'))

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return redirect(url_for('frontend.index', error='expired'))