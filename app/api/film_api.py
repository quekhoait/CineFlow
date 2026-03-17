from flask import Blueprint, request, jsonify
from app.services.film_service import FilmServices


film_api=Blueprint('film', __name__, url_prefix='/film')

@film_api.route('/create', methods=['POST'])
def create_films():
    try:
        data=request.get_json()
        f = FilmServices.create(data=data)
        return jsonify({
            "status": "success",
            "data": f
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@film_api.route('/update/<int:id>', methods=['PUT'])
def update_film(id):
    try:
        f = FilmServices.update(id)
        return jsonify({
            "status": "success",
            "data": f
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
#
@film_api.route('/list', methods=['GET'])
def get_films():
    try:
        list_films=FilmServices.list()
        return jsonify({
            "status": "success",
            "data": list_films
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
#
# # Lấy film theo id
@film_api.route('/get/<int:id>', methods=['GET'])
def get_film_by_id(id):
    try:
        film_by_id = FilmServices.get_by_id(id)
        if not film_by_id:
            return jsonify({
                "status": "error",
                "data": "Film not found"
            })
        return jsonify({
            "status": "success",
            "data": film_by_id
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500