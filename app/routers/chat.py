import json
import re
from datetime import date as dt, timedelta
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Service, TimeSlot
from app.schemas import ChatRequest
from app.ai_assistant import chat_with_assistant

router = APIRouter()


def _parse_action(response: str):
    """Extract ACTION:{...} from AI response. Returns (clean_message, action_dict)."""
    match = re.search(r"ACTION:(\{.*?\})", response, re.DOTALL)
    if match:
        try:
            action = json.loads(match.group(1))
            clean = response.replace(f"ACTION:{match.group(1)}", "").strip()
            return clean, action
        except json.JSONDecodeError:
            pass
    return response, None


def _resolve_slots(preferred_date: Optional[str], db: Session):
    """Return available TimeSlot objects for a date or the next 7 days."""
    if preferred_date:
        slots = (
            db.query(TimeSlot)
            .filter(TimeSlot.is_available == True, TimeSlot.slot_date == preferred_date)
            .order_by(TimeSlot.slot_time)
            .all()
        )
        # fallback: next 7 days if nothing found for that date
        if not slots:
            preferred_date = None

    if not preferred_date:
        today = dt.today()
        dates = [(today + timedelta(days=i)).isoformat() for i in range(1, 8)]
        slots = (
            db.query(TimeSlot)
            .filter(TimeSlot.is_available == True, TimeSlot.slot_date.in_(dates))
            .order_by(TimeSlot.slot_date, TimeSlot.slot_time)
            .limit(42)
            .all()
        )

    return slots


@router.post("/chat")
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    raw = chat_with_assistant(
        request.message,
        [m.model_dump() for m in request.history],
    )

    message, action = _parse_action(raw)
    extra_data = None

    if action and action.get("type") == "show_availability":
        preferred_date = action.get("preferred_date")
        service_name = action.get("service_name", "")

        slots = _resolve_slots(preferred_date, db)

        # Match service name → service_id
        service_id = 1
        for svc in db.query(Service).all():
            if service_name.lower() in svc.name.lower() or svc.name.lower() in service_name.lower():
                service_id = svc.id
                break

        extra_data = {
            "type": "availability",
            "service_id": service_id,
            "service_name": service_name or "Your Appointment",
            "slots": [
                {
                    "id": s.id,
                    "dentist_name": s.dentist.name,
                    "date": s.slot_date,
                    "time": s.slot_time,
                }
                for s in slots[:30]
            ],
        }

    return {"message": message, "action": action, "extra_data": extra_data}