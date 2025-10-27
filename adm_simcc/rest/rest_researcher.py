import json
from http import HTTPStatus

import psycopg2
from flask import Blueprint, jsonify, request

from ..dao import dao_researcher
from ..models.researcher import (
    ListResearcherDepartament,
    ListResearchers,
)

rest_researcher = Blueprint(
    "rest_researcher", __name__, url_prefix="/ResearcherRest"
)


@rest_researcher.route("/Insert", methods=["POST"])
def researcher_insert():
    try:
        researcher_list = request.get_json()
        if not isinstance(researcher_list, list):
            researcher_list = [researcher_list]
        list_instance = ListResearchers(researcher_list=researcher_list)
        dao_researcher.researcher_insert(list_instance)
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return jsonify(
            {"message": "pesquisador já cadastrado"}
        ), HTTPStatus.CONFLICT
    except Exception as e:
        print(e)
        return jsonify(
            {"message": f"Erro inesperado: {str(e)}"}
        ), HTTPStatus.INTERNAL_SERVER_ERROR


@rest_researcher.route("/Update", methods=["PUT"])
def researcher_update():
    researcher_data = request.get_json()

    if (
        not researcher_data
        or not isinstance(researcher_data, list)
        or not researcher_data[0]
    ):
        return jsonify(
            {"message": "Dados de entrada inválidos."}
        ), HTTPStatus.BAD_REQUEST

    researcher = researcher_data[0]

    try:
        dao_researcher.researcher_update(researcher)

        return jsonify(
            {"message": "Registro atualizado com sucesso."}
        ), HTTPStatus.OK

    except dao_researcher.ConflictError as e:
        return jsonify(
            {"message": f"Erro de Conflito: {e}"}
        ), HTTPStatus.CONFLICT

    except json.JSONDecodeError:
        return jsonify(
            {
                "message": "Erro na formatação JSON de algum campo no corpo da requisição."
            }
        ), HTTPStatus.BAD_REQUEST

    except Exception as e:
        print(f"Erro inesperado durante a atualização do pesquisador: {e}")
        return jsonify(
            {"message": "Erro interno do servidor ao atualizar o registro."}
        ), HTTPStatus.INTERNAL_SERVER_ERROR


@rest_researcher.route("/Delete", methods=["DELETE"])
def researcher_delete():
    researcher_id = request.args.get("researcher_id")
    dao_researcher.researcher_delete(researcher_id)
    return jsonify(""), HTTPStatus.NO_CONTENT


@rest_researcher.route("/Query", methods=["GET"])
def researcher_basic_query():
    institution_id = request.args.get("institution_id")
    researcher_name = request.args.get("name")
    rows = request.args.get("count")
    lattes_id = request.args.get("lattes_id")
    researcher_id = request.args.get("researcher_id")

    researchers = dao_researcher.researcher_basic_query(
        institution_id=institution_id,
        researcher_name=researcher_name,
        rows=rows,
        lattes_id=lattes_id,
        researcher_id=researcher_id,
    )
    return jsonify(researchers), HTTPStatus.OK


@rest_researcher.route("/Query/Count", methods=["GET"])
def researcher_count():
    institution_id = request.args.get("institution_id")
    researchers_count = dao_researcher.researcher_count(institution_id)
    return jsonify(researchers_count)


@rest_researcher.route("/departament", methods=["POST"])
def researcher_departament_insert():
    try:
        researchers = request.get_json()
        researchers = ListResearcherDepartament(
            researcher_departament=researchers
        )
        dao_researcher.researcher_departament_insert(researchers)
        return jsonify({"message": "ok"}), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return (
            jsonify(
                {"message": "pesquisador ja cadastrado neste departamento"}
            ),
            HTTPStatus.CONFLICT,
        )


@rest_researcher.route("/departament", methods=["DELETE"])
def researcher_departament_delete():
    researcher = request.get_json()
    dao_researcher.researcher_departament_delete(researcher)
    return jsonify({"message": "ok"}), HTTPStatus.NO_CONTENT


@rest_researcher.route("/departament", methods=["GET"])
def researcher_departament_basic_query():
    researcher_id = request.args.get("researcher_id")

    researchers = dao_researcher.researcher_departament_basic_query(
        researcher_id
    )
    return jsonify(researchers), HTTPStatus.OK
