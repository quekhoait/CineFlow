from flask import Blueprint, request, jsonify, render_template
from app.services import film_service
from app.utils.json import NewPackage, StatusResponse
from marshmallow import ValidationError
from app.dto.film_dto import CreateFilm

film_api=Blueprint('film', __name__, url_prefix='/films')


@film_api.route('/<int:id>/update', methods=['PUT'])
def update(id):
    try:
        data=request.get_json()
        data=CreateFilm(partial=True).load(data)
        film = film_service.update(data, id)
        return NewPackage(status=StatusResponse.SUCCESS, message="update film success", data=film, status_code=200)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)

@film_api.route('', methods=['GET'])
def films():
    try:
        query = request.args.get("strategy") # future, showing, all
        list_films=film_service.list(query)
        return NewPackage(status=StatusResponse.SUCCESS, message="get list film success", data=list_films, status_code=200)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)

@film_api.route('/<int:id>', methods=['GET'])
def film(id):
    try:
        film = film_service.get_by_id(id)
        return NewPackage(status=StatusResponse.SUCCESS, message="get film success", data=film, status_code=200)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)

@film_api.route('/search', methods=['GET'])
def search():
    try:
        title = request.args.get("title")
        if not title:
            raise ValueError("Title is required")
        film=film_service.get_by_title(title)
        return NewPackage(status=StatusResponse.SUCCESS, message="Search film success", data=film, status_code=200)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)



