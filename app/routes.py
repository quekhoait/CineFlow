from flask import Blueprint, render_template

routes = Blueprint('frontend', __name__, url_prefix='/', template_folder='templates', static_folder='static')

@routes.route('/')
def index():
    return render_template("page/home.html")

@routes.route('/booking')
def booking():
    return render_template("page/booking.html")

@routes.route('/booking-seat')
def bookingSeat():
    return render_template("page/booking_seat_page.html")

@routes.route('/profile')
def profile():
    return render_template("page/profile.html")

@routes.route('/history')
def history():
    return render_template("page/history.html")