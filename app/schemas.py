from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ServiceOut(BaseModel):
    id: int
    name: str
    description: str
    duration_minutes: int
    price: float

    model_config = {"from_attributes": True}


class DentistOut(BaseModel):
    id: int
    name: str
    specialization: str

    model_config = {"from_attributes": True}


class TimeSlotOut(BaseModel):
    id: int
    dentist_id: int
    dentist_name: str
    slot_date: str
    slot_time: str
    is_available: bool

    model_config = {"from_attributes": True}


class AppointmentCreate(BaseModel):
    patient_name: str
    patient_phone: str
    patient_email: Optional[str] = None
    service_id: int
    slot_id: int
    notes: Optional[str] = None


class AppointmentOut(BaseModel):
    id: int
    patient_name: str
    patient_phone: str
    service_id: int
    dentist_id: int
    slot_id: int
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: str
    history: List[ChatMessage] = []