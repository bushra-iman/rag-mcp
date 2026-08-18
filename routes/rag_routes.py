from flask import (
    Blueprint,
    request,
    jsonify
)
from services.rag_engine import (
    ask_question,
    create_vector_store_from_files,
    get_memory_threads,
    get_top_5_conversations
)
rag_bp = Blueprint(
    "rag",
    __name__
)
# =========================================================
# HEALTH CHECK
# =========================================================
@rag_bp.route(
    "/health",
    methods=["GET"]
)
def health():
    return jsonify({
        "status":
            "success",
        "message":
            "Student Assistant API is running."
    }), 200
# =========================================================
# QUERY API
# =========================================================
@rag_bp.route(
    "/query",
    methods=["POST"]
)
def query():
    data = request.get_json(
        silent=True
    )
    if not data:
        return jsonify({
            "error":
                "Request body is required."
        }), 400
    if "question" not in data:
        return jsonify({
            "error":
                "Question is required."
        }), 400
    tenant_id = data.get(
        "tenant_id"
    )
    if not tenant_id:
        return jsonify({
            "error":
                "Tenant ID is required."
        }), 400
    thread_id = data.get(
        "thread_id",
        "default"
    )
    question = data[
        "question"
    ]
    try:
        result = ask_question(
            question=question,
            thread_id=thread_id,
            tenant_id=tenant_id
        )
        return jsonify({
            "answer":
                result["answer"],
            "sources":
                result["sources"],
            "tenant_id":
                tenant_id,
            "thread_id":
                thread_id
        }), 200
    except Exception as exc:

        import traceback

        traceback.print_exc()

        return jsonify({

            "error": str(exc),

            "error_type": type(exc).__name__,

            "traceback": traceback.format_exc()

        }), 500
# =========================================================
# LIST MEMORY THREADS
# =========================================================
@rag_bp.route(
    "/threads",
    methods=["GET"]
)
def get_threads():
    tenant_id = request.args.get(
        "tenant_id"
    )
    if not tenant_id:
        return jsonify({
            "error":
                "Tenant ID is required."
        }), 400
    try:
        thread_list = (
            get_memory_threads(
                tenant_id
            )
        )
        return jsonify({
            "status":
                "success",
            "tenant_id":
                tenant_id,
            "total_threads":
                len(thread_list),
            "threads":
                thread_list
        }), 200
    except Exception as exc:
        return jsonify({
            "error":
                str(exc)
        }), 500
# =========================================================
# TOP 5
# =========================================================
@rag_bp.route(
    "/top5",
    methods=["GET"]
)
def top5():
    tenant_id = request.args.get(
        "tenant_id"
    )
    if not tenant_id:
        return jsonify({
            "error":
                "Tenant ID is required."
        }), 400
    try:
        conversations = (
            get_top_5_conversations(
                tenant_id
            )
        )
        return jsonify({
            "status":
                "success",
            "tenant_id":
                tenant_id,
            "total":
                len(conversations),
            "conversations":
                conversations
        }), 200
    except Exception as exc:
        return jsonify({
            "error":
                str(exc)
        }), 500
# =========================================================
# FILE INGEST
# =========================================================
@rag_bp.route(
    "/ingest",
    methods=["POST"]
)
def ingest():
    if "files" not in request.files:
        return jsonify({
            "error":
                "No files were uploaded."
        }), 400
    files = request.files.getlist(
        "files"
    )
    files = [
        file
        for file in files
        if file and file.filename
    ]
    if not files:
        return jsonify({
            "error":
                "Please upload at least one file."
        }), 400
    try:
        result = (
            create_vector_store_from_files(
                files
            )
        )
        return jsonify(
            result
        ), 200
    except ValueError as exc:
        return jsonify({
            "error":
                str(exc)
        }), 400
    except Exception as exc:
        return jsonify({
            "error":
                str(exc)
        }), 500