from http import HTTPStatus

from flask import Flask, jsonify, request
from flask_cors import CORS

from adm_simcc.rest import tag

from .rest.conectee import conectee
from .rest.guidance_tracking import guidance_tracking_bp
from .rest.rest_graduate_program import rest_graduate_program
from .rest.rest_graduate_program_student import rest_graduate_program_student
from .rest.rest_gradute_program_researcher import (
    rest_graduate_program_researcher,
)
from .rest.rest_ind_prod import rest_ind_prod
from .rest.rest_institution import rest_institution
from .rest.rest_newsletter import rest_newsletter
from .rest.rest_researcher import rest_researcher
from .rest.rest_researcher_group import rest_researcher_group
from .rest.rest_system_management import rest_system


def create_app():
    app = Flask(__name__)

    app.register_blueprint(tag.router)
    app.register_blueprint(rest_newsletter)
    app.register_blueprint(rest_researcher_group)
    app.register_blueprint(rest_institution)
    app.register_blueprint(rest_researcher)
    app.register_blueprint(rest_graduate_program)
    app.register_blueprint(rest_graduate_program_researcher)
    app.register_blueprint(rest_graduate_program_student)
    app.register_blueprint(rest_ind_prod)
    app.register_blueprint(rest_system)
    app.register_blueprint(conectee)
    app.register_blueprint(guidance_tracking_bp)

    CORS(app)

    @app.route("/", methods=["GET"])
    def home():
        response_data = {"message": "api em funcionamento"}
        return jsonify(response_data), HTTPStatus.OK

    @app.route("/headers", methods=["GET"])
    def headers():
        all_headers = dict(request.headers)
        return jsonify(all_headers), HTTPStatus.OK

    return app
