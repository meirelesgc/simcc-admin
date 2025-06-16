from flask import Blueprint, request

from ..dao.dao_guidnace_tracking import (
    create_guidance_tracking,
    delete_guidance_tracking,
    get_all_guidance_trackings,
    get_guidance_tracking_by_id,
    update_guidance_tracking,
)

guidance_tracking_bp = Blueprint("guidance_tracking", __name__)


@guidance_tracking_bp.route("/guidance_tracking", methods=["GET"])
def get_all():
    return get_all_guidance_trackings()


@guidance_tracking_bp.route(
    "/guidance_tracking/<uuid:guidance_id>", methods=["GET"]
)
def get_one(guidance_id):
    return get_guidance_tracking_by_id(guidance_id)


@guidance_tracking_bp.route("/guidance_tracking", methods=["POST"])
def create():
    data = request.get_json()
    return create_guidance_tracking(data)


@guidance_tracking_bp.route(
    "/guidance_tracking/<uuid:guidance_id>", methods=["PUT"]
)
def update(guidance_id):
    data = request.get_json()
    return update_guidance_tracking(guidance_id, data)


@guidance_tracking_bp.route(
    "/guidance_tracking/<uuid:guidance_id>", methods=["DELETE"]
)
def delete(guidance_id):
    return delete_guidance_tracking(guidance_id)
