from http import HTTPStatus

import pandas as pd
import psycopg2
from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename

from ..dao import dao_conectee, dao_technician
from ..models.departament import ListDiscipline
from ..models.teachers import ListTeachers
from ..models.technician import ListTechnician, ListTechnicianDepartament

conectee = Blueprint("conectee", __name__)


@conectee.route("/departamentos", methods=["POST"])
def departament_insert():
    departaments = request.form.to_dict()
    departaments_file = request.files
    dao_conectee.departament_insert(departaments, departaments_file)
    return jsonify("OK"), HTTPStatus.CREATED


@conectee.route("/departamentos", methods=["GET"])
def departament_basic_query():
    dep_id = request.args.get("dep_id")
    departaments = dao_conectee.departament_basic_query(dep_id)
    return jsonify(departaments), HTTPStatus.OK


@conectee.route("/departamentos", methods=["DELETE"])
def departament_delete():
    dep_id = request.args.get("dep_id")
    dao_conectee.departament_delete(dep_id)
    return jsonify("OK"), HTTPStatus.NO_CONTENT


@conectee.route("/departamentos/update", methods=["POST"])
def departament_update():
    departament = request.form.to_dict()
    departaments_file = request.files
    dao_conectee.departament_update(departament, departaments_file)
    return jsonify("OK"), HTTPStatus.OK


@conectee.route("/departamentos/researcher", methods=["GET"])
def departament_researcher_query():
    dep_id = request.args.get("dep_id")
    researchers = dao_conectee.departament_researcher_query(dep_id)
    return jsonify(researchers), HTTPStatus.OK


@conectee.route("/departamentos/disciplinas", methods=["POST"])
def departament_insert_discipline():
    disciplines = request.get_json()
    disciplines = ListDiscipline(list_discipline=disciplines)
    dao_conectee.departament_insert_discipline(disciplines)
    return jsonify("OK"), HTTPStatus.CREATED


@conectee.route("/departamentos/disciplinas", methods=["GET"])
def departament_query_discipline():
    dep_id = request.args.get("dep_id")
    disciplines = dao_conectee.departament_query_discipline(dep_id)
    return jsonify(disciplines), HTTPStatus.OK


@conectee.route("/departamentos/disciplinas/semestres", methods=["GET"])
def departament_query_discipline_semester():
    dep_id = request.args.get("dep_id")
    semesters = dao_conectee.departament_query_discipline_semester(dep_id)
    return jsonify(semesters), HTTPStatus.OK


@conectee.route("/docentes", methods=["POST"])
def teacher_insert():
    try:
        teachers = request.get_json()
        teachers = ListTeachers(list_teachers=teachers)
        dao_conectee.ufmg_researcher_insert(teachers)
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return jsonify(
            {"message": "Docente já cadastrado"}
        ), HTTPStatus.CONFLICT


@conectee.route("/v2/ufmg/researcher", methods=["POST"])
def post_ufmg_researcher():
    researcher = request.get_json()
    result = dao_conectee.post_ufmg_researcher(researcher)
    return jsonify(result), HTTPStatus.CREATED


@conectee.route("/v2/ufmg/researcher/upload", methods=["POST"])
def post_ufmg_researcher_upload():
    file = request.files.get("file")

    if file is None or file.filename == str():
        return {"error": "Nenhum arquivo enviado"}, 400

    filename = secure_filename(file.filename)

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(file)
        elif filename.endswith(".xls") or filename.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            return {"error": "Formato de arquivo não suportado"}, 400
    except Exception as e:
        return {"error": f"Erro ao ler o arquivo: {str(e)}"}, 400

    data = df.to_dict(orient="records")
    result = dao_conectee.post_ufmg_researcher(data)
    return jsonify(result), HTTPStatus.CREATED


@conectee.route("/docentes", methods=["GET"])
def teacher_query():
    year = request.args.get("year")
    semester = request.args.get("semester")
    teachers = dao_conectee.reacher_basic_query(year, semester)
    return jsonify(teachers), HTTPStatus.OK


@conectee.route("/docentes/semestres", methods=["GET"])
def teacher_query_semester():
    semesters = dao_conectee.teacher_query_semester()
    return jsonify(semesters), HTTPStatus.OK


@conectee.route("/tecnicos", methods=["POST"])
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


@conectee.route("/tecnicos", methods=["GET"])
def technician_basic_query():
    year = request.args.get("year")
    semester = request.args.get("semester")
    departament = request.args.get("departament")
    technicians = dao_technician.technician_basic_query(
        year, semester, departament
    )
    return jsonify(technicians), HTTPStatus.OK


@conectee.route("/tecnicos/semestres", methods=["GET"])
def technician_query_semester():
    semesters = dao_technician.technician_query_semester()
    return jsonify(semesters), HTTPStatus.OK


@conectee.route("/tecnicos/departament", methods=["POST"])
def departament_technician_insert():
    technician = request.get_json()
    technician = ListTechnicianDepartament(technician_departament=technician)
    dao_technician.departament_technician_insert(technician)
    return jsonify({"message": "ok"}), HTTPStatus.CREATED


@conectee.route("/tecnicos/departament", methods=["DELETE"])
def departament_technician_delete():
    technician = request.get_json()
    dao_technician.departament_technician_delete(technician)
    return jsonify({"message": "ok"}), HTTPStatus.NO_CONTENT


@conectee.route("/tecnicos/departament", methods=["GET"])
def technician_departament_basic_query():
    dep_id = request.args.get("dep_id")
    technician_id = request.args.get("technician_id")
    technician = dao_technician.technician_departament_basic_query(
        technician_id, dep_id
    )
    return jsonify(technician), HTTPStatus.OK


# @conectee.route('/v2/')
