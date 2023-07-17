import base64


def admission_review(uid, allowed, patch):
    return {
        "kind": "AdmissionReview",
        "apiVersion": "admission.k8s.io/v1",
        "response": {
            "allowed": allowed,
            "uid": uid,
            "status": {"reason": "Add Scheduler"},
            "patch": base64.b64encode(str(patch).encode()).decode(),
            "patchType": "JSONPatch",
        },
    }
