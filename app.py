from flask import Flask

from routes.rag_routes import rag_bp
from routes.mcp_routes import mcp_bp


app = Flask(__name__)


# =========================================================
# EXISTING RAG ROUTES
# =========================================================

app.register_blueprint(
    rag_bp
)


# =========================================================
# MCP ROUTES
# =========================================================

app.register_blueprint(
    mcp_bp
)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return {
        "message": "Welcome to Student Assistant RAG API",
        "version": "1.0"
    }


# =========================================================
# START FLASK
# =========================================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )