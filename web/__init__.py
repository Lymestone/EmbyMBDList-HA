import os
from flask import Flask, request


def create_app(sync_manager, config_manager):
    app = Flask(__name__, template_folder="templates")
    app.secret_key = os.urandom(24)
    app.config["sync_manager"] = sync_manager
    app.config["config_manager"] = config_manager

    @app.context_processor
    def inject_ingress_path():
        # HA sends the ingress path via X-Ingress-Path header on each request
        ingress_path = request.headers.get("X-Ingress-Path", "").rstrip("/")
        return {"ingress_path": ingress_path}

    from web.routes import bp
    app.register_blueprint(bp)

    return app
