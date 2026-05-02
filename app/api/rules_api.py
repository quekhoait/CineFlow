import logging

from flask import Blueprint, request
from marshmallow import ValidationError
from app.dto.rule_dto import RulesDTO
from app.services import rules_service
from app.utils.json import NewPackage, StatusResponse
from app.utils.middleware import role_request

rules_api = Blueprint('rules', __name__, url_prefix='/rules')
@rules_api.route('/update', methods=['PATCH'])
@role_request('admin')
def update():
    try:
        data = request.get_json()
        rules_service.update(RulesDTO(many=True).load(data))
        return NewPackage(status=StatusResponse.SUCCESS, message="Update rule successfully",status_code=200)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid data", status_code=400, data=e.messages)
    except Exception as e:
        logging.error("Update rule failed: ", str(e))
        return NewPackage(status=StatusResponse.ERROR, message="Have a problem in update flow" + str(e), status_code=500)

@rules_api.route('', methods=['GET'])
def rules():
    try:
        response = rules_service.rules()
        return NewPackage(status=StatusResponse.SUCCESS, message="Get rule successfully", data=response ,status_code=200)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid data", status_code=400, data=e.messages)
    except Exception as e:
        logging.error("Get rule failed: ", str(e))
        return NewPackage(status=StatusResponse.ERROR, message="Have a problem in update flow" + str(e), status_code=500)