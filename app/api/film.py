from flask import Blueprint, request, jsonify
from ..services import film

film_api=Blueprint('film', __name__, url_prefix='/film')

#Lấy danh sách film
@film_api_router('/create', methods=['POST'])
def create_films():
    try:
        data=request.get_json()
        f = film.FilmServices.create_film(data=data)
        return jsonify({
            "status": "success",
            "data": f
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@film_api_router('/update/<int:id>', methods=['PUT'])
def update_film(id):
    try:
        f = film.FilmServices.update_film(id)
        return jsonify({
            "status": "success",
            "data": f
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@film_api_router('/list', methods=['GET'])
def get_films():
    try:
        list_films=film.FilmServices.get_all_film()
        return jsonify({
            "status": "success",
            "data": list_films
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Lấy film theo id
@film_api_router('/get/<int:id>', methods=['GET'])
def get_film_by_id(id):
    try:
        film_by_id = film.FilmServices.get_film_by_id(id)
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