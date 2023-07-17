__all__ = ["deployment"]

import copy
from typing import Dict, Tuple

from jsonpatch import JsonPatch
from flask import jsonify, Blueprint, request
from constants import *
from utils import validating_admission_review, mutating_admission_review


deployment: Blueprint = Blueprint("podgroup", __name__, url_prefix="/deployment")


@deployment.route("/", methods=["POST"])
def validate_webhook():
    request_info = dict()
    if isinstance(request.json, Dict):
        request_info = request.json
    if request_info["request"]["operation"] == CREATE:
        deployment.logger.debug(request_info)
        allowed, status = create_validate(request_info["request"]["object"])
    elif request_info["request"]["operation"] == UPDATE:
        deployment.logger.debug(request_info)
        allowed, status = update_validate(request_info["request"]["object"])
    else:
        allowed = False
        status = "invalid operation"
    return validating_admission_review(request_info["request"]["uid"], allowed, status)


@deployment.route("/mutate", methods=["POST"])
def mutate_webhook():
    allowed = True
    request_info = dict()
    if isinstance(request.json, Dict):
        request_info = request.json
    request_info_object = request_info["request"]["object"]
    if request_info["request"]["operation"] == CREATE:
        patch = create_mutate(request_info_object)
    elif request_info["request"]["operation"] == UPDATE:
        patch = update_mutate(request_info_object)
    else:
        patch = ""
    admissionReview = mutating_admission_review(
        request_info["request"]["uid"], allowed=allowed, patch=patch
    )
    return jsonify(admissionReview)


def create_validate(request_object: Dict) -> Tuple[bool, str]:
    deployment.logger.debug("create_validate")
    status = ""
    allowed = True
    try:
        if request_object["spec"].get("schedulerName") != SCHEDULER_NAME:
            allowed = False
    except Exception as e:
        deployment.logger.debug(e)
        allowed = False

    return allowed, status


def update_validate(request_object: Dict) -> Tuple[bool, str]:
    deployment.logger.debug("update_validate")
    status = ""
    allowed = True

    if request_object["spec"].get("schedulerName"):
        if request_object["spec"].get("schedulerName") != SCHEDULER_NAME:
            allowed = False
            status = SCHEDULER_FAIL

    return allowed, status


def create_mutate(request_object):
    deployment.logger.debug("create_mutate")
    modified_info_object = copy.deepcopy(request_object)
    modified_info_object["spec"]["schedulerName"] = SCHEDULER_NAME
    patch = JsonPatch.from_diff(request_object, modified_info_object)
    return patch


def update_mutate(request_object):
    deployment.logger.debug("update_mutate")
    deployment.logger.debug(request_object)
    modified_info_object = request_object

    if request_object["spec"].get("schedulerName"):
        modified_info_object = copy.deepcopy(request_object)
        modified_info_object["spec"]["schedulerName"] = SCHEDULER_NAME

    patch = JsonPatch.from_diff(request_object, modified_info_object)
    deployment.logger.debug(patch)
    return patch
