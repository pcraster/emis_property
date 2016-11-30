from flask import Blueprint
from flask_restful import Api


api_blueprint = Blueprint("api", __name__)
api_restful = Api(api_blueprint)


from . import property, ping
