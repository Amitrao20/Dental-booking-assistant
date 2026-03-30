from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.models import Appointment, TimeSlot, Service
from app.schemas import AppointmentCreate, AppointmentOut, TimeSlotOut

router = APIRouter()


@router.get("/availability", response_model=List[TimeSlotOut])
def get_availability(
    date: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(TimeSlot).filter(TimeSlot.is_available == True)

    if date:
        query = query.filter(TimeSlot.slot_date == date)

    slots = query.order_by(TimeSlot.slot_date, TimeSlot.slot_time).limit(60).all()

    return [
        TimeSlotOut(
            id=s.id,
            dentist_id=s.dentist_id,
            dentist_name=s.dentist.name,
            slot_date=s.slot_date,
            slot_time=s.slot_time,
            is_available=s.is_available,
        )
        for s in slots
    ]


@router.post("/appointments", response_model=AppointmentOut)
def book_appointment(data: AppointmentCreate, db: Session = Depends(get_db)):
    slot = (
        db.query(TimeSlot)
        .filter(TimeSlot.id == data.slot_id, TimeSlot.is_available == True)
        .first()
    )
    if not slot:
        raise HTTPException(status_code=400, detail="Time slot is no longer available.")

    service = db.query(Service).filter(Service.id == data.service_id).first()
    if not service:
        raise HTTPException(status_code=404, detail="Service not found.")

    appt = Appointment(
        patient_name=data.patient_name,
        patient_phone=data.patient_phone,
        patient_email=data.patient_email,
        service_id=data.service_id,
        dentist_id=slot.dentist_id,
        slot_id=data.slot_id,
        notes=data.notes,
        status="confirmed",
    )
    slot.is_available = False
    db.add(appt)
    db.commit()
    db.refresh(appt)
    return appt


@router.get("/appointments/lookup")
def lookup_appointments(phone: str, db: Session = Depends(get_db)):
    appointments = (
        db.query(Appointment)
        .filter(Appointment.patient_phone == phone)
        .all()
    )
    if not appointments:
        return {"found": False, "appointments": []}

    return {
        "found": True,
        "appointments": [
            {
                "id": a.id,
                "patient_name": a.patient_name,
                "service": a.service.name,
                "dentist": a.dentist.name,
                "date": a.slot.slot_date,
                "time": a.slot.slot_time,
                "status": a.status,
            }
            for a in appointments
        ],
    }