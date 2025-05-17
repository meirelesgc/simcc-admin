import json
import os
from http import HTTPStatus

import psycopg2
from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from ..dao import dao_system
from ..models import FeedbackSchema, UserModel

rest_system = Blueprint("rest_system_management", __name__)
HOP_LOCK_FILE_PATH = os.getenv("HOP_LOCK_FILE_PATH", "/tmp/hop_execution.lock")
HOP_LOG_FILE_PATH = os.getenv("HOP_LOG_FILE_PATH")
HOP_ROUTINE_PATH = os.getenv("HOP_ROUTINE_PATH")


@rest_system.route("/s/user", methods=["POST"])
def create_user():
    try:
        user = request.get_json()
        user = UserModel(**user[0])
        dao_system.create_user(user)
        return jsonify("OK"), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return jsonify(
            {"message": "discente já cadastrado"}
        ), HTTPStatus.CONFLICT


@rest_system.route("/s/user", methods=["GET"])
def select_user():
    uid = request.args.get("uid")
    user = dao_system.select_user(uid)
    return jsonify(user), HTTPStatus.OK


@rest_system.route("/s/user/all", methods=["GET"])
def list_users():
    user = dao_system.list_users()
    return jsonify(user), HTTPStatus.OK


@rest_system.route("/s/user/entrys", methods=["GET"])
def list_all_users():
    user = dao_system.list_all_users()
    return jsonify(user), HTTPStatus.OK


@rest_system.route("/s/user", methods=["PUT"])
def update_user():
    user = request.get_json()
    dao_system.update_user(user[0])
    return jsonify(), HTTPStatus.OK


@rest_system.route("/s/save-directory", methods=["POST"])
def save_directory():
    data = request.json
    directory = data.get("directory")

    if not directory:
        return jsonify({"error": "No directory provided"}), 400

    try:
        with open("files/directory.json", "w", encoding="utf-8") as file:
            json.dump({"directory": directory}, file)
        return jsonify({"message": "Directory saved successfully"}), 200
    except Exception as e:
        print("Error saving directory:", e)
        return jsonify({"error": "Failed to save directory"}), 500


@rest_system.route("/s/directory", methods=["GET"])
def get_directory():
    try:
        with open("files/directory.json", "r", encoding="utf-8") as file:
            data = json.load(file)
            directory_path = data.get("directory")
        if not directory_path:
            return jsonify({"error": "Directory path not found"}), 404

        directory_list = os.listdir(directory_path)
        return jsonify(directory_list)
    except FileNotFoundError:
        return jsonify({"error": "Directory file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@rest_system.route("/s/role", methods=["POST"])
def create_new_role():
    role = request.get_json()
    dao_system.create_new_role(role)
    return jsonify("OK"), HTTPStatus.CREATED


@rest_system.route("/s/role", methods=["GET"])
def view_roles():
    roles = dao_system.view_roles()
    return jsonify(roles), HTTPStatus.OK


@rest_system.route("/s/role", methods=["PUT"])
def update_role():
    role = request.get_json()
    dao_system.update_role(role)
    return jsonify("OK"), HTTPStatus.CREATED


@rest_system.route("/s/role", methods=["DELETE"])
def delete_role():
    role = request.get_json()
    dao_system.delete_role(role)
    return jsonify(), HTTPStatus.OK


@rest_system.route("/s/permission", methods=["POST"])
def create_new_permission():
    permission = request.get_json()
    dao_system.create_new_permission(permission)
    return jsonify("OK"), HTTPStatus.CREATED


@rest_system.route("/s/permission", methods=["GET"])
def permissions_view():
    role_id = request.args.get("role_id")
    roles = dao_system.permissions_view(role_id)
    return jsonify(roles), HTTPStatus.OK


@rest_system.route("/s/permission", methods=["PUT"])
def update_permission():
    permission = request.get_json()
    dao_system.update_permission(permission)
    return jsonify("OK"), HTTPStatus.CREATED


@rest_system.route("/s/permission", methods=["DELETE"])
def delete_permission():
    permission = request.get_json()
    dao_system.delete_permission(permission)
    return jsonify("OK"), HTTPStatus.NO_CONTENT


@rest_system.route("/s/user/role", methods=["POST"])
def assign_user():
    try:
        user = request.get_json()
        dao_system.assign_user(user)
        return jsonify("OK"), HTTPStatus.CREATED
    except psycopg2.errors.UniqueViolation:
        return jsonify(
            {"message": "discente já cadastrado"}
        ), HTTPStatus.CONFLICT


@rest_system.route("/s/user/permissions", methods=["GET"])
def view_user_roles():
    uid = request.args.get("uid")
    role_id = request.args.get("role_id")
    permissions = dao_system.view_user_roles(uid, role_id)
    return jsonify(permissions), HTTPStatus.OK


@rest_system.route("/s/user/role", methods=["DELETE"])
def unassign_user():
    technician = request.get_json()
    dao_system.unassign_user(technician)
    return jsonify("OK"), HTTPStatus.NO_CONTENT


@rest_system.route("/s/feedback", methods=["POST"])
def feedback():
    try:
        feedback_data = FeedbackSchema(**request.json)
        dao_system.add_feedback(feedback_data)
        response = {
            "message": "Feedback recebido com sucesso!",
            "data": feedback_data.model_dump(),
        }
        return jsonify(response), 200
    except ValidationError as e:
        response = {"message": "Validation error", "errors": e.errors()}
        return jsonify(response), 400


@rest_system.route("/s/feedback", methods=["GET"])
def list_feedback():
    response = dao_system.list_feedback()
    return response


@rest_system.route("/s/feedback", methods=["DELETE"])
def delete_feedback():
    feedback_id = request.args.get("feedback_id")
    dao_system.delete_feedback(feedback_id)
    return jsonify({"message": "Feedback deleted"}), 204
