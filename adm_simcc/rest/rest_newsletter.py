from http import HTTPStatus

from flask import Blueprint, jsonify, request

from ..dao import dao_system

rest_newsletter = Blueprint("rest_newsletter", __name__)


@rest_newsletter.route("/newsletter", methods=["POST"])
def add_email():
    email = request.args.get("email")
    dao_system.add_email(email)
    return jsonify("OK"), HTTPStatus.CREATED


@rest_newsletter.route("/newsletter", methods=["GET"])
def select_email():
    emails = dao_system.select_email()
    return jsonify(emails), HTTPStatus.OK


@rest_newsletter.route("/newsletter", methods=["DELETE"])
def delete_email():
    email = request.args.get("email")
    dao_system.delete_email(email)
    return jsonify("OK"), HTTPStatus.NO_CONTENT
