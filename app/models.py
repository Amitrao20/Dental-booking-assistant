from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Service(Base):
    __tablename__ = "services"

    id                = Column(Integer, primary_key=True, index=True)
    name              = Column(String,  nullable=False)
    description       = Column(String)
    duration_minutes  = Column(Integer)
    price             = Column(Float)

    appointments = relationship("Appointment", back_populates="service")


class Dentist(Base):
    __tablename__ = "dentists"

    id             = Column(Integer, primary_key=True, index=True)
    name           = Column(String, nullable=False)
    specialization = Column(String)

    time_slots   = relationship("TimeSlot",   back_populates="dentist")
    appointments = relationship("Appointment", back_populates="dentist")


class TimeSlot(Base):
    __tablename__ = "time_slots"

    id           = Column(Integer, primary_key=True, index=True)
    dentist_id   = Column(Integer, ForeignKey("dentists.id"))
    slot_date    = Column(String,  nullable=False)   # "YYYY-MM-DD"
    slot_time    = Column(String,  nullable=False)   # "HH:MM"
    is_available = Column(Boolean, default=True)

    dentist     = relationship("Dentist",      back_populates="time_slots")
    appointment = relationship("Appointment",  back_populates="slot", uselist=False)


class Appointment(Base):
    __tablename__ = "appointments"

    id            = Column(Integer,  primary_key=True, index=True)
    patient_name  = Column(String,   nullable=False)
    patient_phone = Column(String,   nullable=False)
    patient_email = Column(String)
    service_id    = Column(Integer,  ForeignKey("services.id"))
    dentist_id    = Column(Integer,  ForeignKey("dentists.id"))
    slot_id       = Column(Integer,  ForeignKey("time_slots.id"))
    status        = Column(String,   default="confirmed")
    notes         = Column(String)
    created_at    = Column(DateTime, default=datetime.utcnow)

    service = relationship("Service",  back_populates="appointments")
    dentist = relationship("Dentist",  back_populates="appointments")
    slot    = relationship("TimeSlot", back_populates="appointment")