from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import date, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dental_clinic.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def seed_data():
    # Local imports to avoid circular dependency
    from app.models import Service, Dentist, TimeSlot

    db = SessionLocal()

    # Skip if already seeded
    if db.query(Service).count() > 0:
        db.close()
        print("ℹ️  Database already seeded, skipping.")
        return

    # ── Services ──────────────────────────────────────────
    services = [
        Service(name="General Checkup",       description="Routine dental exam & professional cleaning",         duration_minutes=30, price=500.0),
        Service(name="Teeth Whitening",        description="Professional in-clinic teeth whitening treatment",    duration_minutes=60, price=2500.0),
        Service(name="Root Canal",             description="Root canal treatment for infected or damaged teeth",  duration_minutes=90, price=5000.0),
        Service(name="Dental Filling",         description="Tooth-coloured composite resin cavity filling",       duration_minutes=45, price=1500.0),
        Service(name="Tooth Extraction",       description="Safe and painless tooth removal",                     duration_minutes=30, price=800.0),
        Service(name="Braces Consultation",    description="Orthodontic consultation and treatment planning",      duration_minutes=60, price=1000.0),
        Service(name="Dental Crown",           description="Porcelain or metal crown placement",                  duration_minutes=90, price=8000.0),
        Service(name="Gum Treatment",          description="Periodontal deep-cleaning and gum disease treatment", duration_minutes=60, price=3000.0),
    ]
    db.add_all(services)

    # ── Dentists ──────────────────────────────────────────
    dentists = [
        Dentist(name="Dr. Priya Sharma",  specialization="General Dentist"),
        Dentist(name="Dr. Rahul Mehta",   specialization="Orthodontist"),
        Dentist(name="Dr. Anita Patel",   specialization="Endodontist"),
    ]
    db.add_all(dentists)
    db.commit()

    # ── Time slots: next 14 days, Mon–Sat ─────────────────
    time_slots = [
        "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
        "14:00", "14:30", "15:00", "15:30", "16:00", "16:30", "17:00",
    ]

    all_dentists = db.query(Dentist).all()
    for day_offset in range(1, 15):
        slot_date = date.today() + timedelta(days=day_offset)
        if slot_date.weekday() < 6:   # 0=Mon … 5=Sat
            for dentist in all_dentists:
                for t in time_slots:
                    db.add(TimeSlot(
                        dentist_id=dentist.id,
                        slot_date=slot_date.isoformat(),
                        slot_time=t,
                        is_available=True,
                    ))

    db.commit()
    db.close()
    print("✅ Database seeded — services, dentists & time-slots created!")