from flask import Blueprint, request, jsonify, render_template
from app.services import payment_services
from app.utils.json import NewPackage, StatusResponse
from marshmallow import ValidationError
from app.Momo import momo


payment_api=Blueprint('payment', __name__, url_prefix='/payment')

@payment_api.route('/create/<int:booking_id>', methods=['POST'])
def create_payment(booking_id):
    try:
        data = request.get_json()
        payment_req = momo.created_pay(booking_id=booking_id, amount=data.get('amount'))
        payment_db = ""
        if payment_req.get('resultCode') == 0:
            payment_db = payment_services.create_payment(payment_req, booking_id)
        return NewPackage(status=StatusResponse.SUCCESS, message="created film success", data=payment_db, status_code=200)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid", data=e.messages,status_code=400)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data= str(e), status_code=500)

