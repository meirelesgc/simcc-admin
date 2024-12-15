from http import HTTPStatus

import psycopg2
from flask import Blueprint, jsonify, request

from ..dao import dao_graduate_program_student
from ..models.student import GraduateProgramStudent, ListGraduateProgramStudent

rest_graduate_program_student = Blueprint(
    "rest_graduate_program_student", __name__, url_prefix="/studentRest"
)


@rest_graduate_program_student.route("/insert", methods=["POST"])
def graduate_program_student_insert():
    try:
        student_list = request.get_json()
        list_instance = ListGraduateProgramStudent(student_list=student_list)
        dao_graduate_program_student.student_insert(list_instance)
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return jsonify(
            {"message": "discente já cadastrado"}
        ), HTTPStatus.CONFLICT


@rest_graduate_program_student.route("/update", methods=["PUT"])
def graduate_program_student_update():
    student = request.get_json()
    instance = ListGraduateProgramStudent(student_list=student)
    dao_graduate_program_student.student_update(instance)
    return jsonify({"message": "ok"}), HTTPStatus.OK


@rest_graduate_program_student.route("/delete", methods=["DELETE"])
def graduate_program_student_delete():
    student = request.get_json()
    lattes_id = student[0]["lattes_id"]
    graduate_program_id = student[0]["graduate_program_id"]
    dao_graduate_program_student.student_delete(lattes_id, graduate_program_id)
    return jsonify(), HTTPStatus.NO_CONTENT


@rest_graduate_program_student.route("/query", methods=["GET"])
def graduate_program_student_basic_query():
    institution_id = request.args.get("institution_id")
    graduate_program_id = request.args.get("graduate_program_id")
    students = dao_graduate_program_student.student_basic_query(
        graduate_program_id, institution_id
    )
    return jsonify(students), HTTPStatus.OK
