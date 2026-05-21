from flask import redirect, url_for
from flask_admin import expose, AdminIndexView
from flask_jwt_extended import verify_jwt_in_request, get_jwt
import datetime

from flask import request, jsonify
from flask_admin import expose, AdminIndexView

from app import db
from app.models import Booking, BookingPaymentStatus

class AdminView(AdminIndexView):
    def is_accessible(self):
        try:
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims["roles"]
            return user_role == "admin"
        except Exception:
            return False

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('frontend.index', error='forbidden'))

    @expose('/')
    def index(self):
        return self.render('layout/admin.html')

    @expose('/settings')
    def settings(self):
        return self.render('page/settings.html')

    @expose('/checkin', methods=['POST'])
    def checkin(self):
        try:
            data = request.get_json() or {}
            booking_code = data.get('booking_code')

            if not booking_code:
                return jsonify({
                    "status": "ERROR",
                    "message": "Mã đặt vé (booking_code) không được để trống"
                }), 400

            booking = db.session.query(Booking).filter_by(code=booking_code).first()

            if not booking:
                return jsonify({
                    "status": "ERROR",
                    "message": f"Không tìm thấy mã đặt vé '{booking_code}' trên hệ thống"
                }), 404

            if booking.payment_status != BookingPaymentStatus.PAID:
                return jsonify({
                    "status": "ERROR",
                    "message": "Vé này chưa được thanh toán thành công, không thể check-in!"
                }), 400
            if booking.check_in is not None:
                return jsonify({
                    "status": "ERROR",
                    "message": f"Vé này đã được check-in vào lúc {booking.check_in.strftime('%H:%M:%S %d/%m/%Y')}"
                }), 400
            booking.check_in = datetime.now()
            db.session.commit()
            return jsonify({
                "status": "SUCCESS",
                "message": "Check-in thành công!",
                "data": {
                    "booking_code": booking.code,
                    "check_in_time": booking.check_in.strftime('%Y-%m-%d %H:%M:%S'),
                    "total_price": booking.total_price,
                    "user_id": booking.user_id
                }
            }), 200

        except Exception as e:
            db.session.rollback()
            print(f"Lỗi hệ thống khi checkin: {str(e)}")
            return jsonify({
                "status": "ERROR",
                "message": "Đã xảy ra lỗi hệ thống trong quá trình xử lý check-in"
            }), 500
