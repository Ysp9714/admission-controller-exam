from flask import Flask
import ssl

from kind.pod import *
from kind.podgroup import *
from constants import *


def init_app() -> Flask:
    app = Flask(__name__)

    app.register_blueprint(pod)
    app.register_blueprint(podgroup)
    return app


def ssl_ctx() -> ssl.SSLContext:
    context = ssl.SSLContext(ssl.PROTOCOL_TLS)
    context.load_verify_locations(CA_LOCATE)
    context.load_cert_chain(CERT_CHAIN, CERT_KEY)
    return context


app = init_app()
app.run(host="0.0.0.0", debug=DEBUG, ssl_context=ssl_ctx())
