from flask import Blueprint, request, jsonify, render_template
from app.services import cinema_service
from app.utils.json import NewPackage, StatusResponse
from marshmallow import ValidationError


cinema_api=Blueprint('cinema', __name__, url_prefix='/cinema')

@cinema_api.route('/list', methods=['GET'])
def get_cinemas():
    try:
        list = cinema_service.list()
        return NewPackage(status=StatusResponse.SUCCESS,message="get lits cinema success", data=list, status_code=200 )
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)
      
@cinema_api.route('/films/<int:cinema_id>', methods=['GET'])
def get_films_schedule_by_cinemaId(cinema_id):
    try:
        date = request.args.get("date")
        film = cinema_service.get_films_schedule_by_cinemaId(cinema_id, date)
        return NewPackage(status=StatusResponse.SUCCESS, message="get film success", data=film, status_code=200)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)

@cinema_api.route('/get/<int:cinema_id>', methods=['GET'])
def get_cinema_by_id(cinema_id):
    try:
        film = cinema_service.get_by_id(cinema_id)
        return NewPackage(status=StatusResponse.SUCCESS, message="get cinema success", data=film, status_code=200)
    except Exception as e:
        return NewPackage(status=StatusResponse.ERROR, message="Internal Server Error", data=str(e), status_code=500)

