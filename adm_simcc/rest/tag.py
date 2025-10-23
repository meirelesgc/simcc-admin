from flask import Blueprint, jsonify, request

from adm_simcc.dao import dao_tag

router = Blueprint("tag", __name__)


@router.route("/tag/", methods=["POST"])
def create_tag():
    data = request.get_json()
    response = dao_tag.create_tag(data)
    return jsonify(response)


@router.route("/tag/", methods=["GET"])
def list_tags():
    response = dao_tag.get_tag(None)
    return jsonify(response)


@router.route("/tag/<tag_id>", methods=["GET"])
def get_tag(tag_id):
    response = dao_tag.get_tag(tag_id)
    return jsonify(response)


@router.route("/tag/", methods=["PUT"])
def update_tag():
    data = request.get_json()
    response = dao_tag.update_tag(data)
    return jsonify(response)


@router.route("/tag/<tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    response = dao_tag.delete_tag(tag_id)
    return jsonify(response)
