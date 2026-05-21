# from flask import request, jsonify
# from flask_admin import expose, AdminIndexView
#
# from app import db
# from app.models import Booking
#
#
# # @expose('/checkin', methods=['POST'])
# # def checkin(self):
# #     try:
# #         data = request.get_json() or {}
# #         booking_code = data.get('booking_code')
# #
# #         if not booking_code:
# #             return jsonify({
# #                 "status": "ERROR",
# #                 "message": "Mã đặt vé (booking_code) không được để trống"
# #             }), 400
# #
# #         booking = db.session.query(Booking).filter_by(code=booking_code).first()
# #
# #         if not booking:
# #             return jsonify({
# #                 "status": "ERROR",
# #                 "message": f"Không tìm thấy mã đặt vé '{booking_code}' trên hệ thống"
# #             }), 404
# #
# #         # 3. RÀO LOGIC AN TOÀN (Tùy chọn nhưng nên có):
# #         # Kiểm tra xem vé đã thanh toán chưa mới cho check-in
# #         if booking.payment_status != BookingPaymentStatus.PAID:  # Hãy đổi thành trạng thái PAID tương ứng của bạn
# #             return jsonify({
# #                 "status": "ERROR",
# #                 "message": "Vé này chưa được thanh toán thành công, không thể check-in!"
# #             }), 400
# #
# #         # Kiểm tra xem vé đã từng check-in trước đó chưa để tránh gian lận (Dùng 1 vé vào 2 lần)
# #         if booking.check_in is not None:
# #             return jsonify({
# #                 "status": "ERROR",
# #                 "message": f"Vé này đã được check-in vào lúc {booking.check_in.strftime('%H:%M:%S %d/%m/%Y')}"
# #             }), 400
# #
# #         # 4. THỰC HIỆN CẬP NHẬT THỜI GIAN CHECK-IN
# #         booking.check_in = datetime.now()
# #
# #         # Nếu hệ thống của bạn có trạng thái trạng thái CHECKED_IN, hãy cập nhật luôn
# #         # booking.status = BookingStatus.CHECKED_IN
# #
# #         # Commit thay đổi vào Database
# #         db.session.commit()
# #
# #         # 5. Trả về kết quả thành công cho Client/Máy quét mã QR
# #         return jsonify({
# #             "status": "SUCCESS",
# #             "message": "Check-in thành công!",
# #             "data": {
# #                 "booking_code": booking.code,
# #                 "check_in_time": booking.check_in.strftime('%Y-%m-%d %H:%M:%S'),
# #                 "total_price": booking.total_price,
# #                 "user_id": booking.user_id
# #             }
# #         }), 200
# #
# #     except Exception as e:
# #         # Rollback lại database nếu có lỗi bất ngờ xảy ra (mất kết nối, sập nguồn...)
# #         db.session.rollback()
# #         print(f"Lỗi hệ thống khi checkin: {str(e)}")
# #         return jsonify({
# #             "status": "ERROR",
# #             "message": "Đã xảy ra lỗi hệ thống trong quá trình xử lý check-in"
# #         }), 500
