from typing import Any
from flask import jsonify

def auto_serialize(obj: Any) -> Any:
    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    elif hasattr(obj, '__dict__'):
        return obj.__dict__
    return obj

def NewPackage(success: bool, message: str, data=None, status_code=200):
    body = {
        'success': success,
        'message': message,
    }

    if data is not None:
        if isinstance(data, list):
            body['data'] = [auto_serialize(item) for item in data]
        else:
            body['data'] = auto_serialize(data)
    
    return jsonify(body), status_code
