from flask import jsonify
from . import api_blueprint


@api_blueprint.route("/ping")
def ping():
    return jsonify(response="pong"), 200
