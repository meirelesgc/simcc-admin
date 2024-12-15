from http import HTTPStatus

import psycopg2
from flask import Blueprint, jsonify, request

from ..dao import dao_institution
from ..models.institution import Institution, ListInstitutions

rest_institution = Blueprint(
    "rest_institution", __name__, url_prefix="/InstitutionRest"
)


@rest_institution.route("/Insert", methods=["POST"])
def institution_insert():
    try:
        list_institutions = request.get_json()
        list_instance = ListInstitutions(institution_list=list_institutions)
        dao_institution.institution_insert(list_instance)
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return jsonify(
            {"message": "instituição já cadastrado"}
        ), HTTPStatus.CONFLICT


@rest_institution.route("/Delete", methods=["DELETE"])
def institution_delete():
    institution_id = request.args.get("institution_id")
    dao_institution.delete_institution(institution_id)
    return jsonify({"message": "ok"}), HTTPStatus.OK


@rest_institution.route("/Update", methods=["PUT"])
def institution_update():
    institution = request.get_json()
    institution = Institution(**institution)
    dao_institution.update_institution(institution)
    return jsonify({"message": "ok"}), HTTPStatus.OK


@rest_institution.route("/Query", methods=["GET"])
def institution_basic_query():
    institution_id = request.args.get("institution_id")
    institutions = dao_institution.institution_basic_query(institution_id)
    return jsonify(institutions), HTTPStatus.OK


@rest_institution.route("/Query/Count", methods=["GET"])
def institution_full_query():
    institution_id = request.args.get("institution_id")
    institutions = dao_institution.institution_full_query(institution_id)
    return jsonify(institutions), HTTPStatus.OK
