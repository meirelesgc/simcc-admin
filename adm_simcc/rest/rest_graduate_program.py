from http import HTTPStatus

import psycopg2
from flask import Blueprint, jsonify, request

from ..dao import dao_graduate_program as dao
from ..models.graduate_program import GraduateProgram, ListGraduateProgram

rest_graduate_program = Blueprint(
    "rest_graduate_program", __name__, url_prefix="/GraduateProgramRest"
)


@rest_graduate_program.route("/Insert", methods=["POST"])
def graduate_program_insert():
    try:
        graduate_program_list = request.get_json()
        list_instance = ListGraduateProgram(
            graduate_program_list=graduate_program_list
        )
        dao.graduate_program_insert(list_instance)
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return (
            jsonify({"message": "programa de pos já cadastrado"}),
            HTTPStatus.CONFLICT,
        )


@rest_graduate_program.route("/Update", methods=["POST"])
def graduate_program_update():
    graduate_program_id = request.args.get("graduate_program_id")
    dao.graduate_program_update(graduate_program_id)
    return jsonify({"message": "ok"}), HTTPStatus.OK


@rest_graduate_program.route("/Fix", methods=["POST"])
def graduate_program_fix():
    graduate_program = request.get_json()
    instance = GraduateProgram(**graduate_program[0])
    dao.graduate_program_fix(instance)
    return jsonify({"message": "ok"}), HTTPStatus.OK


@rest_graduate_program.route("/Delete", methods=["DELETE"])
def graduate_program_delete():
    graduate_program_id = request.args.get("graduate_program_id")
    dao.graduate_program_delete(graduate_program_id)
    return jsonify(), HTTPStatus.NO_CONTENT


@rest_graduate_program.route("/Query", methods=["GET"])
def graduate_program_basic_query():
    institution_id = request.args.get("institution_id")
    graduate_programs = dao.graduate_program_basic_query(institution_id)
    return jsonify(graduate_programs), HTTPStatus.OK


@rest_graduate_program.route("/Query/Count", methods=["GET"])
def graduate_program_count():
    institution_id = request.args.get("institution_id")
    graduate_program_count = dao.graduate_program_count(institution_id)
    return jsonify(graduate_program_count), HTTPStatus.OK
