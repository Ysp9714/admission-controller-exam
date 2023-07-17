def admission_review(uid, allowed, status=""):
    return {
        "kind": "AdmissionReview",
        "apiVersion": "admission.k8s.io/v1",
        "response": {
            "allowed": allowed,
            "uid": uid,
            "status": {"reason": status},
        },
    }
