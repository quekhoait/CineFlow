from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from app.services import payment_service
from app.dto.payment_dto import PaymentRequest
from app.utils.errors import APIError
from app.utils.json import NewPackage, StatusResponse

payment_api = Blueprint('payment', __name__, url_prefix = '/payments')

@payment_api.route('/create', methods=['POST'])
@jwt_required()
def create():
    try:
        res = payment_service.create(PaymentRequest().load(request.get_json()))
        print(res)
        return NewPackage(status=StatusResponse.SUCCESS, message="Create payment successful",data=res,status_code=201)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid Input", data=e.messages, status_code=404)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        print(e)
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", status_code=500)

@payment_api.route('/<string:method>/callback', methods=['POST'])
def callback(method):
    try:
        payment_service.callback(method, request.get_json())
        return NewPackage(status=StatusResponse.SUCCESS, message="Payment successful",status_code=200)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid Input", data=e.messages, status_code=400)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", status_code=500)


@payment_api.route('/<string:method>/transaction', methods=['POST'])
@jwt_required()
def transaction(method):
    try:
        data = request.get_json()
        result = payment_service.transaction(method, data)
        return NewPackage(status=StatusResponse.SUCCESS, message= "success", data=result,  status_code=200)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        print(e)
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", status_code=500)

@payment_api.route('/refund', methods = ['POST'])
@jwt_required()
def refund():
    try:
        res = payment_service.refund(PaymentRequest().load(request.get_json()))
        return NewPackage(status=StatusResponse.SUCCESS, message="Refund payment successful", data=res, status_code=200)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid Input", data=e.messages, status_code=400)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", status_code=500)