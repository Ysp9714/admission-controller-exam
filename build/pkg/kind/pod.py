__all__ = ["pod"]

from typing import Dict, Tuple
import copy

from jsonpatch import JsonPatch
from flask import jsonify, Blueprint, request, current_app

from constants import *
from utils import validating_admission_review, mutating_admission_review

pod: Blueprint = Blueprint("pod_route", __name__, url_prefix="/pod")


@pod.route("/", methods=["POST"])
def validate_webhook():
    """ValidatingWebhook 함수의 진입점
    operation에 따라 다른 로직 적용
    """
    request_info = dict()
    if isinstance(request.json, Dict):
        request_info = request.json
    if request_info["request"]["operation"] == CREATE:
        current_app.logger.debug(request_info)
        allowed, status = create_validate(request_info["request"]["object"])
    elif request_info["request"]["operation"] == UPDATE:
        current_app.logger.debug(request_info)
        allowed, status = update_validate(request_info["request"]["object"])
    else:
        allowed = False
        status = "invalid operation"
    return validating_admission_review(request_info["request"]["uid"], allowed, status)


@pod.route("/mutate", methods=["POST"])
def mutate_webhook():
    """Mutating Webhook의 진입점
    operation에 따라 다른 로직 적용
    """
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
    """Create Validating Webhook이 하는 일

    Args:
        request_object (Dict): client가 요청한 내용

    Returns:
        Tuple[bool, str]: 승인여부, 관련 메시지
    """
    current_app.logger.debug("create_validate")
    status = ""
    allowed = True
    try:
        if request_object["spec"].get("schedulerName") != SCHEDULER_NAME:
            allowed = False
    except Exception as e:
        current_app.logger.debug(e)
        allowed = False

    return allowed, status


def update_validate(request_object: Dict) -> Tuple[bool, str]:
    """Update Validating Webhook이 하는 일

    Args:
        request_object (Dict): Client가 요청한 내용

    Returns:
        Tuple[bool, str]: 승인여부, 관련 메시지
    """
    current_app.logger.debug("update_validate")
    status = ""
    allowed = True

    if request_object["spec"].get("schedulerName"):
        if request_object["spec"].get("schedulerName") != SCHEDULER_NAME:
            allowed = False
            status = SCHEDULER_FAIL

    return allowed, status


def create_mutate(request_object):
    """Create Mutating Webhook이 하는 일

    Args:
        request_object (Dict): Client가 요청한 내용

    Returns:
        Tuple[bool, str]: 승인여부, 관련 메시지
    """
    current_app.logger.debug("create_mutate")
    modified_info_object = copy.deepcopy(request_object)
    modified_info_object["spec"]["schedulerName"] = SCHEDULER_NAME
    patch = JsonPatch.from_diff(request_object, modified_info_object)
    return patch


def update_mutate(request_object):
    """Update Mutating Webhook이 하는 일

    Args:
        request_object (Dict): Client가 요청한 내용

    Returns:
        Tuple[bool, str]: 승인여부, 관련 메시지
    """
    current_app.logger.debug("update_mutate")
    current_app.logger.debug(request_object)
    modified_info_object = request_object

    if request_object["spec"].get("schedulerName"):
        modified_info_object = copy.deepcopy(request_object)
        modified_info_object["spec"]["schedulerName"] = SCHEDULER_NAME

    patch = JsonPatch.from_diff(request_object, modified_info_object)
    current_app.logger.debug(patch)
    return patch
