import psycopg2

from flask import Blueprint, jsonify, request
from http import HTTPStatus

from ..dao import dao_institution
from ..dao import dao_researcher_group
from ..models.researcher_group import ListResearcherGroup


rest_researcher_group = Blueprint(
    "rest_researcher_group", __name__, url_prefix="/researchGroupRest"
)


@rest_researcher_group.route("/Insert", methods=["POST"])
def research_group_insert():
    try:
        researcher_groups_list = request.get_json()
        instance = ListResearcherGroup(researcher_groups_list=researcher_groups_list)
        dao_researcher_group.research_group_insert(instance)
        return jsonify(), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return (
            jsonify({"message": "grupo de pesquisa duplicado"}),
            HTTPStatus.CONFLICT,
        )


@rest_researcher_group.route("/Query", methods=["GET"])
def research_group_basic_query():
    institution_id = request.args.get("institution_id")
    research_group_id = request.args.get("research_group_id")
    researcher_id = request.args.get("researcher_id")
    research_groups = dao_researcher_group.research_group_basic_query(
        institution_id, research_group_id, researcher_id
    )
    return jsonify(research_groups), HTTPStatus.OK


@rest_researcher_group.route("/Delete", methods=["DELETE"])
def research_group_delete():
    research_group_id = request.args.get("research_group_id")
    institution_id = request.args.get("institution_id")
    dao_researcher_group.research_group_delete(research_group_id, institution_id)
    return jsonify(), HTTPStatus.NO_CONTENT


@rest_researcher_group.route("/Update", methods=["POST"])
def research_group_update():
    researcher_groups_list = request.get_json()
    instance = ListResearcherGroup(researcher_groups_list=researcher_groups_list)
    institution_name = instance.researcher_groups_list[0].instituicao
    institution_id = dao_institution.institution_query_name(institution_name)
    dao_researcher_group.research_group_delete(institution_id)
    dao_researcher_group.research_group_insert(instance)
    return jsonify("Dados atualizados com sucesso!"), HTTPStatus.OK
