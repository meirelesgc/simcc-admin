import psycopg2
from http import HTTPStatus
from flask import Blueprint, jsonify, request

from ..dao import dao_teacher
from ..models.teachers import ListTeachers

rest_teacher = Blueprint("rest_teacher", __name__)


@rest_teacher.route("/docentes", methods=["POST"])
def teacher_insert():
    try:
        teachers = request.get_json()
        teachers = ListTeachers(list_teachers=teachers)
        dao_teacher.ufmg_researcher_insert(teachers)
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return jsonify({"message": "Docente já cadastrado"}), HTTPStatus.CONFLICT


@rest_teacher.route("/docentes", methods=["GET"])
def teacher_query():
    year = request.args.get("year")
    semester = request.args.get("semester")
    teachers = dao_teacher.reacher_basic_query(year, semester)
    return jsonify(teachers), HTTPStatus.OK


@rest_teacher.route("/docentes/semestres", methods=["GET"])
def teacher_query_semester():
    semesters = dao_teacher.teacher_query_semester()
    return jsonify(semesters), HTTPStatus.OK
