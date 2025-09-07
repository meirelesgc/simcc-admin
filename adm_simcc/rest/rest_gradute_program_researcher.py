from http import HTTPStatus

from flask import Blueprint, jsonify, request

from ..dao import dao_graduate_program_researcher as dao

rest_graduate_program_researcher = Blueprint(
    "rest_graduate_program_researcher",
    __name__,
    url_prefix="/GraduateProgramResearcherRest",
)


@rest_graduate_program_researcher.route("/Insert", methods=["POST"])
def graduate_program_researcher_insert():
    gpr = request.get_json()
    if not isinstance(gpr, list):
        gpr = [gpr]
    if dao.gpr_insert(gpr):
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    return jsonify({"message": "error"}), HTTPStatus.INTERNAL_SERVER_ERROR


@rest_graduate_program_researcher.route("/Insert/Lattes", methods=["POST"])
def graduate_program_researcher_insert_lattes():
    gpr = request.get_json()
    if not isinstance(gpr, list):
        gpr = [gpr]
    if dao.graduate_program_researcher_insert_lattes(gpr):
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    return jsonify({"message": "error"}), HTTPStatus.INTERNAL_SERVER_ERROR


@rest_graduate_program_researcher.route("/Delete", methods=["DELETE"])
def gpr_delete():
    gpr = request.get_json()
    if not isinstance(gpr, list):
        gpr = [gpr]
    dao.gpr_delete(gpr)
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
