import json
from pathlib import Path
from fastapi import Depends
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.utils.jwt_required import token_required

router = APIRouter()

LOG_DIR = Path("app/logs")

@router.get("")
def get_logs(
    date: str | None = None,
    user = Depends(token_required([0, 1, 2]))
):
    if not LOG_DIR.exists():
        raise HTTPException(status_code=404, detail="Log directory not found")

    if not date:
        date = datetime.now().strftime("%Y-%m-%d")

    log_file = LOG_DIR / f"{date}.json"

    if not log_file.exists():
        raise HTTPException(status_code=404, detail=f"No logs found for {date}")

    logs = []
    with open(log_file, "r", encoding="utf-8") as f:
        for line in f:
            try:
                logs.append(json.loads(line.strip()))
            except json.JSONDecodeError:
                continue

    return {"status_code": 200, "date": date, "count": len(logs), "logs": logs}