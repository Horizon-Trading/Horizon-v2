from datetime import datetime, timezone
import json
import logging


class JsonFormatter(logging.Formatter):
    def format(self, record):
        return json.dumps(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }
        )


def configure_logging(level):
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def record_status(component, status, error=None):
    from news.repository import supabase

    try:
        supabase.table("worker_status").upsert(
            {
                "component": component,
                "status": status,
                "error": error,
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        ).execute()
    except Exception as exc:
        logging.getLogger(__name__).warning(
            "Status write failed error=%s", type(exc).__name__
        )
