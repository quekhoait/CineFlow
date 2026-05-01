from flask import Blueprint, request
from app.services import film_service
from app.utils.json import NewPackage, StatusResponse
from app.utils.errors import APIError

film_api=Blueprint('film', __name__, url_prefix='/films')


@film_api.route('', methods=['GET'])
def films():
    try:
        query = request.args.get("strategy") # future, showing
        list_films=film_service.list(query)
        return NewPackage(status=StatusResponse.SUCCESS, message="get list film success", data=list_films, status_code=200)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)

@film_api.route('/<int:id>', methods=['GET'])
def film(id):
    try:
        film = film_service.get_by_id(id)
        return NewPackage(status=StatusResponse.SUCCESS, message="get film success", data=film, status_code=200)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)

@film_api.route('/search', methods=['GET'])
def search():
    try:
        title = request.args.get('title', '')
        film=film_service.get_by_title(title)
        return NewPackage(status=StatusResponse.SUCCESS, message="Search film success", data=film, status_code=200)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, data="", status_code=e.status_code)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)

@film_api.route('/<int:film_id>/cinemas', methods=['GET'])
def cinemas(film_id):
    try:
        date = request.args.get("date")
        cinema = film_service.get_schedule_by_film_and_date(film_id, date)
        return NewPackage(status=StatusResponse.SUCCESS, message="get cinema  success", data=cinema, status_code=200)
    except APIError as e:
        return NewPackage(status=StatusResponse.ERROR, message=e.message, status_code=e.status_code)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)
