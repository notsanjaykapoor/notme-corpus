import os


def qdrant_dashboard_url() -> str:
    return f"{qdrant_root_url()}/dashboard"


def qdrant_root_url() -> str:
    return os.environ.get("QDRANT_URL")