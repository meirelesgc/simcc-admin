from http import HTTPStatus

import psycopg2
from flask import Blueprint, jsonify, request

from ..dao import dao_graduate_program_researcher as dao
from ..models.graduate_program_resarcher import ListResearcher

rest_graduate_program_researcher = Blueprint(
    "rest_graduate_program_researcher",
    __name__,
    url_prefix="/GraduateProgramResearcherRest",
)


@rest_graduate_program_researcher.route("/Insert", methods=["POST"])
def graduate_program_researcher_insert():
    try:
        list_instance = request.get_json()
        researcher_instance = ListResearcher(researcher_list=list_instance)
        dao.graduate_program_researcher_insert(researcher_instance)
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return (
            jsonify({"message": "pesquisador já cadastrado no programa"}),
            HTTPStatus.CONFLICT,
        )


@rest_graduate_program_researcher.route("/Insert/Lattes", methods=["POST"])
def graduate_program_researcher_insert_lattes():
    try:
        list_instance = request.get_json()
        researcher_instance = ListResearcher(researcher_list=list_instance)
        dao.graduate_program_researcher_insert_lattes(researcher_instance)
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return (
            jsonify({"message": "pesquisador já cadastrado no programa"}),
            HTTPStatus.CONFLICT,
        )


@rest_graduate_program_researcher.route("/Update", methods=["PUT"])
def graduate_program_researcher_update():
    try:
        list_instance = request.get_json()
        researcher_instance = ListResearcher(researcher_list=list_instance)
        dao.graduate_program_researcher_update(researcher_instance)
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return (
            jsonify({"message": "pesquisador já cadastrado no programa"}),
            HTTPStatus.CONFLICT,
        )


@rest_graduate_program_researcher.route("/Delete", methods=["DELETE"])
def graduate_program_researcher_delete():
    researcher = request.get_json()
    lattes_id = researcher[0]["lattes_id"]
    graduate_program_id = researcher[0]["graduate_program_id"]
    dao.graduate_program_researcher_delete(lattes_id, graduate_program_id)
    return jsonify(), HTTPStatus.NO_CONTENT


@rest_graduate_program_researcher.route("/Query", methods=["GET"])
def graduate_program_researcher_basic_query():
    graduate_program_id = request.args.get("graduate_program_id")
    type_ = request.args.get("type")
    researchers = dao.graduate_program_researcher_basic_query(
        graduate_program_id, type_
    )
    return jsonify(researchers), HTTPStatus.OK


@rest_graduate_program_researcher.route("/Query/Count", methods=["GET"])
def graduate_program_researcher_count():
    institution_id = request.args.get("institution_id")
    graduate_program_id = request.args.get("graduate_program_id")
    researchers_count = dao.graduate_program_researcher_count(
        institution_id, graduate_program_id
    )
    return jsonify(researchers_count), HTTPStatus.OK
