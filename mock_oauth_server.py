from flask import Flask, request, jsonify
import secrets

from config import Config


app = Flask(__name__)


# =========================================================
# FAKE OAUTH CREDENTIALS
# =========================================================

CLIENT_ID = "1234"

CLIENT_SECRET = "client-secret"


# =========================================================
# TOKEN ENDPOINT
# =========================================================

@app.route(
    "/oauth/token",
    methods=["POST"]
)
def token():

    grant_type = request.form.get(
        "grant_type"
    )

    client_id = request.form.get(
        "client_id"
    )

    client_secret = request.form.get(
        "client_secret"
    )

    # -----------------------------------------------------
    # VALIDATE GRANT TYPE
    # -----------------------------------------------------

    if grant_type != "client_credentials":

        return jsonify({
            "error":
                "unsupported_grant_type"
        }), 400

    # -----------------------------------------------------
    # VALIDATE CLIENT
    # -----------------------------------------------------

    if (
        client_id != CLIENT_ID
        or
        client_secret != CLIENT_SECRET
    ):

        return jsonify({
            "error":
                "invalid_client"
        }), 401

    # -----------------------------------------------------
    # CREATE FAKE ACCESS TOKEN
    # -----------------------------------------------------

    access_token = (
        "mock_"
        +
        secrets.token_urlsafe(32)
    )

    return jsonify({

        "access_token":
            access_token,

        "token_type":
            "Bearer",

        "expires_in":
            3600

    }), 200


# =========================================================
# HEALTH CHECK
# =========================================================

@app.route(
    "/",
    methods=["GET"]
)
def health():

    return jsonify({

        "status":
            "success",

        "message":
            "Mock OAuth server is running."

    }), 200


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        host=Config.OAUTH_HOST,
        port=Config.OAUTH_PORT,
        debug=True
    )
