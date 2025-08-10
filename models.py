from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.sql.sqltypes import Date, Time
from sqlalchemy.sql.expression import text


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String(15), nullable=False, unique=True) # frontend phone validation
    password = Column(String, nullable=False)


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String(15), nullable=False, unique=True)
    specialty = Column(String, nullable=False)
    city = Column(String(50), nullable=False)
    street = Column(String(50), nullable=False)
    postal_code = Column(String(10), nullable=False)
    personal_picture = Column(String(200), unique=True) # href to the image
    password = Column(String, nullable=False)


class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, nullable=False)

    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"))
    
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))

    date = Column(Date, nullable=False)
    
    time = Column(Time(timezone=True), nullable=False)

    case = Column(String(20), nullable=False, )
    
    done = Column(Boolean, nullable=False, server_default=text("False"))

    confirmed = Column(Boolean, nullable=False, server_default=text('False'))


class RescheduleRequest(Base):
    __tablename__ = "reschedules"

    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"),
                            primary_key=True, nullable=False)
    
    old_date = Column(Date, nullable=False)
    old_time = Column(Time, nullable=False)
    new_date = Column(Date, nullable=False)
    new_time = Column(Time, nullable=False)


class FeedBack(Base):
    __tablename__ = "feedbacks"

    appointment_id = Column(Integer, 
                            ForeignKey("appointments.id", ondelete="CASCADE"),
                            primary_key=True)
    
    rating = Column(Integer)
    
    plain = Column(String(200), nullable=False)