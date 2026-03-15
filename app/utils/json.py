from flask import jsonify

def NewPackage(success: bool, message: str, data=None, status_code=200):
    body = {
        'success': success,
        'message': message,
        'data': data,
    }
    
    return jsonify(body), status_code
