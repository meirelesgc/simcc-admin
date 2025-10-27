from flask import Blueprint, jsonify, request

from adm_simcc.dao import dao_area

router = Blueprint("area", __name__)


@router.route("/area/", methods=["POST"])
def create_area():
    data = request.get_json()
    response = dao_area.create_area(data)
    return jsonify(response)


@router.route("/area/", methods=["GET"])
def list_areas():
    response = dao_area.get_area(None)
    return jsonify(response)


@router.route("/area/<area_id>", methods=["GET"])
def get_area(area_id):
    response = dao_area.get_area(area_id)
    return jsonify(response)


@router.route("/area/", methods=["PUT"])
def update_area():
    data = request.get_json()
    response = dao_area.update_area(data)
    return jsonify(response)


@router.route("/area/<area_id>", methods=["DELETE"])
def delete_area(area_id):
    response = dao_area.delete_area(area_id)
    return jsonify(response)
