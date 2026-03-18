from flask import Blueprint, request, jsonify
from app.services import film_service
from app.utils.json import NewPackage, StatusResponse
from marshmallow import ValidationError
from app.dto.film_dto import CreateFilm

film_api=Blueprint('film', __name__, url_prefix='/film')

@film_api.route('/create', methods=['POST'])
def create_films():
    try:
        data=request.get_json()
        data=CreateFilm().load(data)
        f = film_service.create(data=data)
        return NewPackage(status=StatusResponse.SUCCESS, message="created film success", data=f, status_code=200)
    except ValidationError as e:
        return NewPackage(status=StatusResponse.ERROR, message="Invalid", data=e.messages,status_code=400)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data= str(e), status_code=500)

@film_api.route('/update/<int:id>', methods=['PUT'])
def update_film(id):
    try:
        data=request.get_json()
        data=CreateFilm(partial=True).load(data)
        f = film_service.update(data, id)
        return NewPackage(status=StatusResponse.SUCCESS, message="update film success", data=f, status_code=200)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)

@film_api.route('/list', methods=['GET'])
def get_films():
    try:
        list_films=film_service.list()
        return NewPackage(status=StatusResponse.SUCCESS, message="update film success", data=list_films, status_code=200)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)

# # Lấy film theo id
@film_api.route('/get/<int:id>', methods=['GET'])
def get_film_by_id(id):
    try:
        film_by_id = film_service.get_by_id(id)
        return NewPackage(status=StatusResponse.SUCCESS, message="update film success", data=film_by_id, status_code=200)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)

#Lấy theo tên film
@film_api.route('/get', methods=['GET'])
def get_by_title():
    try:
        title = request.args.get("title")
        if not title:
            raise ValueError("Title is required")
        film=film_service.get_by_title(title)
        return NewPackage(status=StatusResponse.SUCCESS, message="get film by title success", data=film, status_code=200)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)

@film_api.route('/list/now-showing', methods=['GET'])
def get_now_showing():
    try:
        film=film_service.get_now_showing()
        return NewPackage(status=StatusResponse.SUCCESS, message="get film by title success", data=film, status_code=200)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)