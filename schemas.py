from pydantic import BaseModel, EmailStr
import datetime
from typing import Optional, Literal


class UserLogin(BaseModel):
    email: EmailStr
    password: str

# ----------------- Doctors schemas -----------------
class DoctorBase(BaseModel):
    first_name : str
    last_name : str
    email : EmailStr
    phone : str
    specialty : str
    city : str
    street : str
    postal_code : str
    personal_picture : str

class DoctorCreate(DoctorBase):
    password: str

class DoctorOut(DoctorBase):
    id: int

class DoctorUpdate(BaseModel):
    first_name : Optional[str] = None
    last_name : Optional[str] = None
    email : Optional[EmailStr] = None
    phone : Optional[str] = None
    specialty : Optional[str] = None
    city : Optional[str] = None
    street : Optional[str] = None
    postal_code : Optional[str] = None
    personal_picture : Optional[str] = None

# ----------------- Patients schemas -----------------

class PatientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str

class PatientCreate(PatientBase):
    password: str

class PatientOut(PatientBase):
    id: int

class PatientUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

# ----------------- Appointments schemas -----------------


class AppointmentCreate(BaseModel):
    date: datetime.date
    time: datetime.time
    case: str

class AppointmentOut(AppointmentCreate):
    patient_id: int
    doctor_id: int
    id: int
    done: bool
    confirmed: bool
    class Config:
        from_attributes = True

class AppointmentsUpdate(BaseModel):
    date: Optional[datetime.date] = None
    time: Optional[datetime.time] = None
    case: Optional[str] = None


class ConfirmAppointment(BaseModel):
    confirmed: bool
    done: bool

# ------------------ Reschedules ------------------

class Reschedule(BaseModel):
    new_date: datetime.date
    new_time: datetime.time

# ------------------ FeedBack ------------------

class FeedBack(BaseModel):
    rating: Literal[0, 1, 2, 3, 4]
    plain: Optional[str] = None

# ------------------ JWT Tokens ------------------

class Token(BaseModel):
    access_token: str
    token_type: str
    

# what payload data does the token embeds
class TokenData(BaseModel):
    id : Optional[int]