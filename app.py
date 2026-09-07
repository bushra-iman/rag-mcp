import logging
import os

from flask import Flask, jsonify, request

from config import Config
from routes.mcp_routes import mcp_bp
from routes.rag_routes import rag_bp


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

logger = logging.getLogger(__name__)


# =========================================================
# APP FACTORY
# =========================================================

def create_app():
    app = Flask(__name__)
    app.config["API_KEY"] = os.getenv("API_KEY")

    # -------------------------------------------------
    # SECURITY: optional API key auth
    # (disabled when API_KEY is not set in the environment)
    # -------------------------------------------------

    @app.before_request
    def require_api_key():
        # Allow CORS preflight requests
        if request.method == "OPTIONS":
            return None
        # Public endpoints
        if request.path in ("/", "/health"):
            return None
        # Auth is disabled unless an API key is configured
        api_key = app.config.get("API_KEY")
        if not api_key:
            return None
        provided = request.headers.get("X-API-Key")
        if provided != api_key:
            return jsonify({
                "status": "error",
                "message": "Unauthorized. Missing or invalid X-API-Key header.",
            }), 401

    # -------------------------------------------------
    # BLUEPRINTS
    # -------------------------------------------------
    app.register_blueprint(rag_bp)
    app.register_blueprint(mcp_bp)

    # -------------------------------------------------
    # HOME
    # -------------------------------------------------
    @app.route("/")
    def home():
        return {
            "message": "Welcome to Student Assistant RAG API",
            "version": "1.0",
        }

    return app


app = create_app()


# =========================================================
# START FLASK
# =========================================================

if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "false").lower() == "true"
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=debug,
    )
