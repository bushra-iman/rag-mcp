import sqlite3

from langgraph.checkpoint.sqlite import (
    SqliteSaver
)


# =========================================================
# DATABASE
# =========================================================

DATABASE_PATH = (
    "checkpoints.sqlite"
)


# =========================================================
# CONNECTION
# =========================================================

conn = sqlite3.connect(
    DATABASE_PATH,
    check_same_thread=False
)


# =========================================================
# CHECKPOINTER
# =========================================================

memory = SqliteSaver(
    conn
)


# =========================================================
# BUILD TENANT THREAD ID
# =========================================================

def build_thread_id(
    tenant_id,
    thread_id
):

    return (
        f"{tenant_id}:{thread_id}"
    )


# =========================================================
# LIST THREADS
# =========================================================

def list_threads(
    tenant_id=None
):

    threads = set()

    for checkpoint in (
        memory.list(None)
    ):

        config = (
            checkpoint.config
        )

        configurable = (
            config.get(
                "configurable",
                {}
            )
        )

        saved_thread_id = (
            configurable.get(
                "thread_id"
            )
        )

        if not saved_thread_id:

            continue

        if tenant_id:

            prefix = (
                f"{tenant_id}:"
            )

            if not saved_thread_id.startswith(
                prefix
            ):

                continue

            original_thread_id = (
                saved_thread_id[
                    len(prefix):
                ]
            )

            threads.add(
                original_thread_id
            )

        else:

            threads.add(
                saved_thread_id
            )

    return sorted(
        threads
    )


# =========================================================
# TOP CONVERSATIONS
# =========================================================

def get_top_conversations(
    tenant_id,
    limit=5
):

    latest_threads = {}

    prefix = (
        f"{tenant_id}:"
    )

    for checkpoint in (
        memory.list(None)
    ):

        config = (
            checkpoint.config
        )

        configurable = (
            config.get(
                "configurable",
                {}
            )
        )

        saved_thread_id = (
            configurable.get(
                "thread_id"
            )
        )

        if not saved_thread_id:

            continue

        if not saved_thread_id.startswith(
            prefix
        ):

            continue

        thread_id = (
            saved_thread_id[
                len(prefix):
            ]
        )

        checkpoint_data = (
            checkpoint.checkpoint
        )

        timestamp = (
            checkpoint_data.get(
                "ts",
                ""
            )
        )

        channel_values = (
            checkpoint_data.get(
                "channel_values",
                {}
            )
        )

        messages = (
            channel_values.get(
                "messages",
                []
            )
        )

        last_message = ""

        for message in reversed(
            messages
        ):

            if hasattr(
                message,
                "type"
            ):

                if message.type == "human":

                    last_message = getattr(
                        message,
                        "content",
                        ""
                    )

                    break

            elif isinstance(
                message,
                dict
            ):

                if (
                    message.get(
                        "role"
                    )
                    == "user"
                ):

                    last_message = (
                        message.get(
                            "content",
                            ""
                        )
                    )

                    break

        conversation = {

            "tenant_id":
                tenant_id,

            "thread_id":
                thread_id,

            "last_message":
                last_message,

            "updated_at":
                timestamp
        }

        if (
            thread_id
            not in latest_threads
            or timestamp
            > latest_threads[
                thread_id
            ][
                "updated_at"
            ]
        ):

            latest_threads[
                thread_id
            ] = conversation

    conversations = list(
        latest_threads.values()
    )

    conversations.sort(
        key=lambda item:
            item["updated_at"],
        reverse=True
    )

    return conversations[
        :limit
    ]