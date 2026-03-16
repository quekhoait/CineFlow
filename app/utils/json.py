from flask import jsonify

def NewPackage(success: bool, message: str, data=None, status_code=200):
    body = {
        'success': success,
        'message': message,
    }

    if data:
        body.update(data)
    
    return jsonify(body), status_code
