from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import Service, Dentist
from app.schemas import ServiceOut, DentistOut

router = APIRouter()


@router.get("/services", response_model=List[ServiceOut])
def get_services(db: Session = Depends(get_db)):
    return db.query(Service).all()


@router.get("/dentists", response_model=List[DentistOut])
def get_dentists(db: Session = Depends(get_db)):
    return db.query(Dentist).all()