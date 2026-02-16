import os
from flask import Flask


def create_app(sync_manager, config_manager):
    app = Flask(__name__, template_folder="templates")
    app.secret_key = os.urandom(24)
    app.config["sync_manager"] = sync_manager
    app.config["config_manager"] = config_manager

    ingress_path = os.environ.get("INGRESS_PATH", "").rstrip("/")
    app.config["INGRESS_PATH"] = ingress_path

    @app.context_processor
    def inject_ingress_path():
        return {"ingress_path": ingress_path}

    from web.routes import bp
    app.register_blueprint(bp)

    return app
