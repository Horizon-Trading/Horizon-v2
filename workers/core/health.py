from datetime import datetime, timezone
from news.repository import supabase


def healthy():
    try:
        rows = {
            row["component"]: row
            for row in supabase.table("worker_status").select("*").execute().data
        }
        now = datetime.now(timezone.utc)
        for component in ("recovery", "paper_trader"):
            row = rows.get(component)
            if (
                not row
                or row["status"] == "error"
                or (now - datetime.fromisoformat(row["updated_at"])).total_seconds()
                > 180
            ):
                return False
        return rows.get("news_stream", {}).get("status") == "connected"
    except Exception:
        return False


if __name__ == "__main__":
    raise SystemExit(0 if healthy() else 1)
