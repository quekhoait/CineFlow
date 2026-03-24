from flask import Blueprint

from app.utils.json import NewPackage, StatusResponse

payment_api = Blueprint('payment', __name__, url_prefix = '/payments')

@payment_api.route('/<int:id>/refund', methods = ['POST'])
def refund(id):
    return NewPackage(StatusResponse.SUCCESS, message="Refund successful", status_code=200)
