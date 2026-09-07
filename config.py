import os

from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()


class Config:
    # -------------------------------------------------
    # OpenAI
    # -------------------------------------------------
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # -------------------------------------------------
    # App
    # -------------------------------------------------
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    API_KEY = os.getenv("API_KEY")

    # -------------------------------------------------
    # Storage
    # -------------------------------------------------
    VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "vector_store")

    # -------------------------------------------------
    # Servers / ports
    # (change PORT in .env if 5000 is already in use)
    # -------------------------------------------------
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))

    MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
    MCP_PORT = int(os.getenv("MCP_PORT", "8000"))

    OAUTH_HOST = os.getenv("OAUTH_HOST", "127.0.0.1")
    OAUTH_PORT = int(os.getenv("OAUTH_PORT", "7000"))
