from typing import Any
from flask import jsonify
from enum import Enum

class StatusResponse(Enum):
    SUCCESS = "success",
    ERROR = "error",
    PENDING = "pending",

def NewPackage(status: StatusResponse, message: str, data=None, status_code=200):
    serialized_data = None

    if data is not None:
        if hasattr(data, 'dump'):
            serialized_data = data
        elif hasattr(data, 'to_dict'):
            serialized_data = data.to_dict()
        else:
            serialized_data = data

    body = {
        'status': status.value[0],
        'message': message,
    }

    if serialized_data is not None:
        body['data'] = serialized_data

    return jsonify(body), status_code
