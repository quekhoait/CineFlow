from flask import Blueprint, request, jsonify, render_template
from app.services import payment_services
from app.utils.json import NewPackage, StatusResponse
from marshmallow import ValidationError
from app.Momo import momo
from app.utils.errors import APIError


payment_api=Blueprint('payment', __name__, url_prefix='/payment')

@payment_api.route('/create/<int:booking_id>', methods=['POST'])
def create_payment(booking_id):
    try:
        data = request.get_json()
        payment_db = payment_services.create_payment(data, booking_id)
        return NewPackage(status=StatusResponse.SUCCESS, message="created film success", data=payment_db, status_code=200)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid", data=e.messages,status_code=400)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data= str(e), status_code=500)


@payment_api.route('/momo/ipn', methods=['POST'])
def call_ipn():
    return momo.momo_ipn()


@payment_api.route('/refund/<int:payment_id>', methods=['POST'])
def refund_payment(payment_id):
    try:
        payment = payment_services.process_refund(payment_id)
        return NewPackage(status=StatusResponse.SUCCESS, message="refund success", data=payment,
                          status_code=200)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message,data="",status_code=e.status_code)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid", data=e.messages, status_code=400)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)


