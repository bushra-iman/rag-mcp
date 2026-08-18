import os
from dotenv import load_dotenv
# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================
load_dotenv()
class Config:
    OPENAI_API_KEY = os.getenv(
        "OPENAI_API_KEY"
    )
    VECTOR_DB_PATH = os.getenv(
        "VECTOR_DB_PATH",
        "vector_store"
    )
    FLASK_ENV = os.getenv(
        "FLASK_ENV",
        "development"
    )