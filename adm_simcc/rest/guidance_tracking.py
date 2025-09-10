from flask import Blueprint, request

from ..dao.dao_guidnace_tracking import (
    create_guidance_config,
    create_guidance_tracking,
    delete_guidance_config,
    delete_guidance_tracking,
    get_all_guidance_configs,
    get_all_guidance_trackings,
    get_guidance_tracking_by_id,
    update_guidance_config,
    update_guidance_tracking,
)

guidance_tracking_bp = Blueprint("guidance_tracking", __name__)


@guidance_tracking_bp.route("/guidance_tracking/", methods=["GET"])
def get_all():
    data = request.args
    return get_all_guidance_trackings(data)


@guidance_tracking_bp.route(
    "/guidance_tracking/<uuid:guidance_id>/", methods=["GET"]
)
def get_one(guidance_id):
    return get_guidance_tracking_by_id(guidance_id)


@guidance_tracking_bp.route("/guidance_tracking/", methods=["POST"])
def create():
    data = request.get_json()
    return create_guidance_tracking(data)


@guidance_tracking_bp.route(
    "/guidance_tracking/<uuid:guidance_id>/", methods=["PUT"]
)
def update(guidance_id):
    data = request.get_json()
    return update_guidance_tracking(guidance_id, data)


@guidance_tracking_bp.route(
    "/guidance_tracking/<uuid:guidance_id>/", methods=["DELETE"]
)
def delete(guidance_id):
    return delete_guidance_tracking(guidance_id)


@guidance_tracking_bp.route("/guidance_config/", methods=["GET"])
def get_all_guidance_configs_():
    data = request.args
    json = get_all_guidance_configs(data)
    return json, 200


@guidance_tracking_bp.route("/guidance_config/", methods=["POST"])
def create_guidance_config_():
    data = request.get_json()
    return create_guidance_config(data)


@guidance_tracking_bp.route("/guidance_config/", methods=["PUT"])
def update_guidance_config_():
    data = request.get_json()
    return update_guidance_config(data)


@guidance_tracking_bp.route(
    "/guidance_config/<uuid:config_id>/", methods=["DELETE"]
)
def delete_guidance_config_(config_id):
    return delete_guidance_config(config_id)
