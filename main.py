from fastapi import FastAPI
# import models
from database import engine
from routes import doctor, patient, auth, home

# models.Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(doctor.router)
app.include_router(patient.router)
app.include_router(auth.router)
app.include_router(home.router)