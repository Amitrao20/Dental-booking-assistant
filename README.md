# 🦷 Bright Smile Dental Clinic — AI Appointment Assistant

> An AI-powered dental appointment booking system built with **FastAPI**, **SQLite**, and **Ollama (gpt-oss:120b-cloud)**.  
> Patients can chat with **Denta**, the AI assistant, to get service recommendations, check availability, and book appointments — all stored in a real database.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🤖 AI Chat (Denta) | Powered by Ollama `gpt-oss:120b-cloud` |
| 📅 Appointment Booking | Real-time slot picker, stored in SQLite |
| 💡 Service Recommendations | AI recommends based on symptoms |
| 🔍 Appointment Lookup | Search bookings by phone number |
| 🗄️ Full Database | 4 tables: Services, Dentists, TimeSlots, Appointments |
| 🌐 Simple Chat UI | HTML + CSS + Vanilla JS, no framework needed |

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.11 + FastAPI |
| Database | SQLite + SQLAlchemy ORM |
| AI Model | Ollama `gpt-oss:120b-cloud` |
| Frontend | HTML5 + CSS3 + Vanilla JavaScript |
| Server | Uvicorn (ASGI) |

---

## 📁 Project Structure

```
dental-booking-assistant/
├── app/
│   ├── __init__.py           # Empty init file
│   ├── database.py           # DB engine, session, seed data
│   ├── models.py             # SQLAlchemy table models
│   ├── schemas.py            # Pydantic request/response schemas
│   ├── ai_assistant.py       # Ollama chat integration
│   └── routers/
│       ├── __init__.py       # Empty init file
│       ├── services.py       # GET /services, GET /dentists
│       ├── appointments.py   # GET /availability, POST /appointments, GET /lookup
│       └── chat.py           # POST /chat (AI + action parser)
├── static/
│   ├── index.html            # Main chat UI
│   ├── style.css             # All styles
│   └── app.js                # Chat logic, slot picker, booking form
├── main.py                   # FastAPI app entry point
├── run.py                    # One-command start script
├── db_setup.py               # DB utility: create, seed, view, reset
├── requirements.txt          # All Python dependencies
├── .env                      # Environment config (not committed to git)
├── .gitignore                # Excludes .env, venv, *.db
└── README.md                 # This file
```

---

## 🗄️ Database Structure

The app uses **SQLite** — a file-based database (`dental_clinic.db`) that is automatically created when you first run the app. No separate database server is needed.

### Tables Overview

```
dental_clinic.db
│
├── services          → 8 dental services (name, price, duration)
├── dentists          → 3 dentists (name, specialization)
├── time_slots        → Available appointment slots (auto-generated for 14 days)
└── appointments      → Booked appointments (created when Denta confirms a booking)
```

### Table: `services`

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment primary key |
| name | TEXT | Service name (e.g. "General Checkup") |
| description | TEXT | What the service involves |
| duration_minutes | INTEGER | How long it takes |
| price | REAL | Price in ₹ INR |

### Table: `dentists`

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment primary key |
| name | TEXT | Doctor's full name |
| specialization | TEXT | e.g. "General Dentist", "Orthodontist" |

### Table: `time_slots`

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment primary key |
| dentist_id | INTEGER (FK) | Links to `dentists.id` |
| slot_date | TEXT | Date in `YYYY-MM-DD` format |
| slot_time | TEXT | Time in `HH:MM` format |
| is_available | BOOLEAN | `True` = open, `False` = booked |

### Table: `appointments`

| Column | Type | Description |
|---|---|---|
| id | INTEGER (PK) | Auto-increment primary key (Booking ID) |
| patient_name | TEXT | Patient's full name |
| patient_phone | TEXT | Patient's phone number |
| patient_email | TEXT | Patient's email (optional) |
| service_id | INTEGER (FK) | Links to `services.id` |
| dentist_id | INTEGER (FK) | Links to `dentists.id` |
| slot_id | INTEGER (FK) | Links to `time_slots.id` |
| status | TEXT | `"confirmed"` by default |
| notes | TEXT | Any special requests |
| created_at | DATETIME | Timestamp of booking |

### How a Booking Works (End-to-End)

```
Patient chats with Denta
        ↓
AI recommends a service + asks for preferred date
        ↓
Backend queries time_slots WHERE is_available = TRUE
        ↓
Slot picker shown in UI
        ↓
Patient picks a slot → fills name + phone → clicks Confirm
        ↓
POST /api/appointments
  → Creates a new row in `appointments`
  → Sets time_slots.is_available = FALSE
  → Returns booking ID
        ↓
Success card shown with Booking ID #N
```

---

## 📦 Prerequisites

Before running, make sure all of these are installed:

| Tool | Required Version | Check Command |
|---|---|---|
| Python | **3.11.x** (not 3.13 or 3.14) | `py -3.11 --version` |
| pip | Latest | `pip --version` |
| Ollama | Any recent version | `ollama --version` |

> ⚠️ **Python 3.11 is required.** Python 3.13 and 3.14 break `pydantic-core` because pre-built wheels are not available yet. Download Python 3.11 from: https://www.python.org/downloads/release/python-3119/

---

## 🚀 Quick Start (Step-by-Step)

### Step 1 — Pull the Ollama Cloud Model (do once)

Open Command Prompt and run:

```cmd
ollama pull gpt-oss:120b-cloud
```

If prompted to log in, run `ollama login` first and create a free account at ollama.com.

---

### Step 2 — Clone or Download the Project

```cmd
git clone https://github.com/YOUR_USERNAME/dental-booking-assistant.git
cd dental-booking-assistant
```

---

### Step 3 — Create a Virtual Environment with Python 3.11

```cmd
py -3.11 -m venv venv
venv\Scripts\activate
```

You should see `(venv)` at the start of your prompt.

Verify:
```cmd
python --version
```
Must show `Python 3.11.x`.

---

### Step 4 — Install Dependencies

```cmd
pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 5 — Set Up the Database

The database is created **automatically** when you first run the app. But you can also set it up manually and inspect it:

```cmd
python db_setup.py
```

This will:
- ✅ Create `dental_clinic.db`
- ✅ Create all 4 tables
- ✅ Seed 8 services, 3 dentists
- ✅ Generate ~500+ time slots for the next 14 days
- ✅ Print a summary of what was created

---

### Step 6 — Start the Application

You need **two** terminal windows open at the same time.

**Terminal 1 — Start Ollama:**
```cmd
ollama serve
```

**Terminal 2 — Start the App:**
```cmd
cd dental-booking-assistant
venv\Scripts\activate
python run.py
```

You will see:
```
✅ Database seeded — services, dentists & time-slots created!
🦷 Starting Bright Smile Dental Clinic AI Assistant...
🌐 Open your browser at: http://127.0.0.1:8000
📚 API docs at: http://127.0.0.1:8000/docs
```

---

### Step 7 — Open in Browser

```
http://127.0.0.1:8000
```

---

## 🧪 How to Test the App (UI Flow)

### Test 1 — Book an Appointment via AI Chat
1. Click **"📅 Book Appointment"** quick button
2. Denta will ask what service you need
3. Type: *"I have tooth pain"* → Denta recommends General Checkup
4. Type: *"Yes, let's book that for tomorrow"*
5. A **slot picker** appears — click any available time
6. A **booking form** appears — fill in name and phone
7. Click **"🎉 Confirm Booking"**
8. A green **success card** appears with your Booking ID

### Test 2 — Look Up an Appointment
1. Click **"🔍 My Appointments"**
2. Enter the phone number you used when booking
3. Your appointment details will appear

### Test 3 — Browse Services
1. Click any service card on the left panel (e.g. "Teeth Whitening")
2. Denta explains the service, price, and duration

### Test 4 — View API Documentation
Go to: `http://127.0.0.1:8000/docs`  
You can test every API endpoint directly from the browser.

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/services` | List all 8 dental services |
| `GET` | `/api/dentists` | List all 3 dentists |
| `GET` | `/api/availability?date=YYYY-MM-DD` | Available time slots (optional date filter) |
| `POST` | `/api/appointments` | Book an appointment (saves to DB) |
| `GET` | `/api/appointments/lookup?phone=NUMBER` | Look up appointments by phone |
| `POST` | `/api/chat` | Chat with AI assistant (Denta) |
| `GET` | `/docs` | Interactive API documentation |
| `GET` | `/health` | Health check |

### Example: Book an Appointment (POST /api/appointments)

**Request body:**
```json
{
  "patient_name": "Rahul Sharma",
  "patient_phone": "9876543210",
  "patient_email": "rahul@example.com",
  "service_id": 1,
  "slot_id": 42,
  "notes": "Sensitive to cold water"
}
```

**Response:**
```json
{
  "id": 1,
  "patient_name": "Rahul Sharma",
  "patient_phone": "9876543210",
  "service_id": 1,
  "dentist_id": 1,
  "slot_id": 42,
  "status": "confirmed",
  "created_at": "2026-03-29T10:30:00"
}
```

---

## ⚙️ Configuration (`.env` file)

```env
OLLAMA_MODEL=gpt-oss:120b-cloud
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_URL=sqlite:///./dental_clinic.db
```

### Alternative Ollama Models

| Model | Speed | Quality | Local/Cloud |
|---|---|---|---|
| `gpt-oss:120b-cloud` | Fast | ⭐⭐⭐⭐⭐ | ☁️ Cloud |
| `llama3.2` | Fast | ⭐⭐⭐ | 💻 Local (2GB) |
| `llama3.1` | Medium | ⭐⭐⭐⭐ | 💻 Local (4GB) |
| `mistral` | Fast | ⭐⭐⭐ | 💻 Local (4GB) |

---

## 🚀 Deploy to GitHub

```cmd
cd dental-booking-assistant

git init
git add .
git commit -m "AI dental booking assistant with Ollama model"

git remote add origin https://github.com/YOUR_USERNAME/dental-booking-assistant.git
git branch -M main
git push -u origin main
```

> ✅ The `.gitignore` already excludes `.env`, `venv/`, and `*.db` so no secrets or patient data are pushed.

### For teammates cloning the repo:
```cmd
git clone https://github.com/YOUR_USERNAME/dental-booking-assistant.git
cd dental-booking-assistant
py -3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
# Create their own .env file
python run.py
```

---

## 🔧 Troubleshooting

| Error | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: No module named 'uvicorn'` | Packages not installed in venv | Run `pip install -r requirements.txt` inside activated venv |
| `pydantic-core` Rust build error | Using Python 3.13 or 3.14 | Switch to Python 3.11 (`py -3.11 -m venv venv`) |
| `Model gpt-oss:120b-cloud not found` | Model not pulled | Run `ollama pull gpt-oss:120b-cloud` |
| `Connection refused` on Ollama | Ollama not running | Open a new terminal and run `ollama serve` |
| Slots not showing in chat | DB not seeded | Run `python db_setup.py` |
| App starts but DB is empty | First run issue | Stop app, run `python db_setup.py --reset`, restart |

---

Thank you ❤️