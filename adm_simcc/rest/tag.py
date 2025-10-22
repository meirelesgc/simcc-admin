from flask import Blueprint, request

from adm_simcc.dao import dao_tag

router = Blueprint("tag", __name__)


@router.route("/tag/", methods=["POST"])
def create_tag():
    data = request.args
    return dao_tag.create_tag(data)


@router.route("/tag/", methods=["GET"])
def list_tags():
    return dao_tag.get_tag(None)


@router.route("/tag/<tag_id>", methods=["GET"])
def get_tag(tag_id):
    return dao_tag.get_tag(tag_id)


@router.route("/tag/", methods=["PUT"])
def update_tag():
    data = request.args
    return dao_tag.update_tag(data)


@router.route("/tag/<tag_id>", methods=["DELETE"])
def delete_tag(tag_id):
    return dao_tag.delete_tag(tag_id)
