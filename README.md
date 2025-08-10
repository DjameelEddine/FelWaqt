# 🏥 FEL WAQT - Medical Appointment Management Backend

A **FastAPI** backend for managing patient–doctor interactions.  
Patients can search for doctors, book and reschedule appointments, leave feedback, and manage their profile.  
Doctors can confirm/reschedule appointments, view feedback, and see their upcoming schedule.

---

## 🚀 Features

### **For Patients**
- Search doctors by name, specialty, or location.
- Book appointments with doctors.
- Request appointment reschedules.
- View and manage upcoming and past appointments.
- Submit feedback for doctors.

### **For Doctors**
- View and confirm/cancel appointments.
- Accept or reject patient reschedule requests.
- View received feedback.
- Manage patient information.

### **Common**
- Secure authentication with JWT tokens.
- Role-based access control (patient/doctor).
- Database migrations with Alembic.

---

## 🛠️ Tech Stack
- **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Migrations:** Alembic
- **Auth:** JWT (JSON Web Tokens)
- **Validation:** Pydantic

---

## ⚙️ Setup & Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/DjameelEddine/FelWaqt.git
cd FelWaqt
```

### 2️⃣ Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate         # Windows
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure environment variables
Create a `.env` file in the project root:
```
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 5️⃣ Apply migrations
```bash
alembic upgrade head
```

### 6️⃣ Run the server
```bash
uvicorn app.main:app --reload
```

---

## 📌 API Documentation
Once running, open:
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🧪 Testing
Run tests with:
```bash
pytest
```

---

## ✨ Author
**Achour Djamel** — [GitHub](https://github.com/DjameelEddine) | [LinkedIn](https://www.linkedin.com/in/djamel-achour-407a4028a/)