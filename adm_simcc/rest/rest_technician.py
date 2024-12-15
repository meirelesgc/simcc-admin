import psycopg2
from http import HTTPStatus
from flask import Blueprint, jsonify, request

from ..dao import dao_technician
from ..models.technician import ListTechnician, ListTechnicianDepartament

rest_technician = Blueprint("rest_technician", __name__)


@rest_technician.route("/tecnicos", methods=["POST"])
def technician_insert():
    try:
        technician = request.get_json()
        technician = ListTechnician(list_technician=technician)
        dao_technician.technician_insert(technician)
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return jsonify(
            {"message": "Tecnico já cadastrado"}
        ), HTTPStatus.CONFLICT


@rest_technician.route("/tecnicos", methods=["GET"])
def technician_basic_query():
    year = request.args.get("year")
    semester = request.args.get("semester")
    departament = request.args.get("departament")
    technicians = dao_technician.technician_basic_query(
        year, semester, departament
    )
    return jsonify(technicians), HTTPStatus.OK


@rest_technician.route("/tecnicos/semestres", methods=["GET"])
def technician_query_semester():
    semesters = dao_technician.technician_query_semester()
    return jsonify(semesters), HTTPStatus.OK


@rest_technician.route("/tecnicos/departament", methods=["POST"])
def departament_technician_insert():
    technician = request.get_json()
    technician = ListTechnicianDepartament(technician_departament=technician)
    dao_technician.departament_technician_insert(technician)
    return jsonify({"message": "ok"}), HTTPStatus.CREATED


@rest_technician.route("/tecnicos/departament", methods=["DELETE"])
def departament_technician_delete():
    technician = request.get_json()
    dao_technician.departament_technician_delete(technician)
    return jsonify({"message": "ok"}), HTTPStatus.NO_CONTENT


@rest_technician.route("/tecnicos/departament", methods=["GET"])
def technician_departament_basic_query():
    dep_id = request.args.get("dep_id")
    technician_id = request.args.get("technician_id")
    technician = dao_technician.technician_departament_basic_query(
        technician_id, dep_id
    )
    return jsonify(technician), HTTPStatus.OK
