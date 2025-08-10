from fastapi.routing import APIRouter
import models
from schemas import PatientCreate, PatientOut, PatientUpdate, AppointmentCreate, AppointmentOut, Reschedule, FeedBack
from fastapi import Depends, HTTPException, status, Response
from database import get_db
from sqlalchemy.orm import Session
from typing import List
from oauth2 import get_current_user
from sqlalchemy import or_, and_
import utils
import datetime

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("/", response_model=PatientOut)
def create_patient(patient: PatientCreate, db: Session=Depends(get_db)):
    try:
        patient.password = utils.hash(patient.password)
        patient_dict = patient.model_dump(exclude_none=True)
        patient_dict["first_name"] = patient_dict["first_name"].capitalize()
        patient_dict["last_name"] = patient_dict["last_name"].capitalize()
        new_patient = models.Patient(**patient_dict)
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        return new_patient
    except Exception:
        print("Some Error Has Occured, Please Check Your Input Validity")


@router.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session=Depends(get_db),
                       current_patient=Depends(get_current_user)):
    
    if current_patient.role != "patient": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns patients only"
        )

    appointments_query = db.query(models.Appointment).filter(models.Appointment.id == appointment_id)
    appointment = appointments_query.first()

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Appointment doesn't exist !")

    try:
        if appointment.doctor_id != current_patient.id and appointment.patient_id != current_patient.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You aren't part of this appointment !")
    except Exception:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    appointments_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.delete("/{patient_id}")
def delete_patient(patient_id: int, db: Session=Depends(get_db),
                   current_patient : models.Patient=Depends(get_current_user)):
    
    if current_patient.role != "patient": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns patients only"
        )

    if patient_id != current_patient.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not the owner of this patient profile !")
    
    patient_query = db.query(models.Patient).filter(models.Patient.id == patient_id)
    patient = patient_query.first()


    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No user found !")
 
    patient_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{patient_id}", response_model=PatientOut)
def update_patient(patient_id: int, new_patient: PatientUpdate, db:Session=Depends(get_db),
                   current_patient: models.Patient = Depends(get_current_user)):
    
    if current_patient.role != "patient": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns patients only"
        )

    if patient_id != current_patient.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not the owner of this patient profile !")

    patient_query = db.query(models.Patient).filter(models.Patient.id == patient_id)
    patient = patient_query.first()

    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"patient with id: {patient_id} was not found")

    patient_dict = new_patient.model_dump(exclude_none=True)

    try:
        patient_dict["first_name"] = patient_dict["first_name"].capitalize()
        patient_dict["last_name"] = patient_dict["last_name"].capitalize()
        patient_dict["specialty"] = patient_dict["specialty"].capitalize()
        patient_dict["city"] = patient_dict["city"].capitalize()
    except Exception:
        print ("Some Fields were empty")
    
    patient_query.update(patient_dict, synchronize_session=False) #type: ignore
    db.commit()
    db.refresh(patient)
    return patient


@router.post("/appointments/{doctor_id}", response_model=AppointmentOut)
def create_appointment(doctor_id: int, appointment: AppointmentCreate, db: Session=Depends(get_db),
                       current_patient: models.Patient=Depends(get_current_user)):
        
        if current_patient.role != "patient": #type: ignore
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Method concerns patients only"
            )
        
        doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"Doctor with id: {doctor_id} doesn't exists.")

        similar_appointments = db.query(models.Appointment).filter(and_(
            models.Appointment.date == appointment.date,
            models.Appointment.time == appointment.time,
            or_(
            models.Appointment.doctor_id == doctor_id,
            models.Appointment.patient_id == current_patient.id
            ))).all()

        if similar_appointments:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                detail="Cannot occupy this date and time slot, change it please.")
        
        appointment_dict = appointment.model_dump(exclude_none=True)
        appointment_dict["patient_id"] = current_patient.id
        appointment_dict["doctor_id"] = doctor_id

        new_appointment = models.Appointment(**appointment_dict)
        db.add(new_appointment)
        db.commit()
        db.refresh(new_appointment)
        return new_appointment


@router.get("/appointments", response_model=List[AppointmentOut])
def get_appointments(db: Session=Depends(get_db), current_patient: models.Patient=Depends(get_current_user)):

    if current_patient.role != "patient": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns patients only"
        )

    patient_appointments = db.query(models.Appointment).filter(models.Appointment.patient_id == current_patient.id).all()

    if not patient_appointments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No Existing Appointments For You !")

    return patient_appointments


@router.get("/reschedules")
def get_reschedules(db: Session=Depends(get_db), current_patient: models.Patient=Depends(get_current_user)):

    if current_patient.role != "patient": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns patients only"
        )

    reschedules = []

    appointments = db.query(models.Appointment).filter(models.Appointment.patient_id == current_patient.id).all()

    for app in appointments:
        reschedule = db.query(models.RescheduleRequest).filter(models.RescheduleRequest.appointment_id == app.id).first()
        if reschedule:
            reschedules.append(reschedule)

    if not reschedules:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No Existing Reschedules For You !")

    return reschedules


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(patient_id:int, db: Session=Depends(get_db),
                 current_patient : models.Patient=Depends(get_current_user)):
    
    if current_patient.role != "patient": #type: ignore
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Method concerns patients only"
            )
    
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    
    if not patient:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Patient Not Found !")
    
    if patient_id != current_patient.id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not the owner of this patient profile !")
    return patient

# ----------------- Reschedules for Patients -----------------

@router.post("/reschedules/{appointment_id}")
def reschedule_appointment(appointment_id: int, reschedule:Reschedule,
                           db:Session=Depends(get_db),
                           current_patient: models.Patient=Depends(get_current_user)):
    
    if current_patient.role != "patient": #type: ignore
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Method concerns patients only"
            )
    
    if reschedule.new_date < datetime.datetime.utcnow().date():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New date must be in the future.")

    if reschedule.new_date == datetime.datetime.utcnow().date() and reschedule.new_time <= datetime.datetime.utcnow().time():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="New time must be in the future.")
    
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Appointment Not Found !")

    if appointment.patient_id != current_patient.id: #type:ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You aren't part of this appointment !")
    
    reschedule_query = db.query(models.RescheduleRequest).filter(models.RescheduleRequest.appointment_id == appointment_id)
    existing_reschedule = reschedule_query.first()

    reschedule_dict = reschedule.model_dump(exclude_none=True)

    similar_appointments = db.query(models.Appointment).filter(and_(
            models.Appointment.date == reschedule_dict["new_date"],
            models.Appointment.time == reschedule_dict["new_time"],
            or_(
            models.Appointment.doctor_id == appointment.doctor_id,
            models.Appointment.patient_id == current_patient.id
            ))).all()
    
    if similar_appointments:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Cannot occupy this date and time slot, change it please.")

    if existing_reschedule:
        reschedule_dict["old_date"] = existing_reschedule.old_date
        reschedule_dict["old_time"] = existing_reschedule.old_time
        reschedule_query.update(reschedule_dict, synchronize_session=False) #type: ignore
        db.commit()
        db.refresh(existing_reschedule)
        return existing_reschedule
    
    reschedule_dict["appointment_id"] = appointment_id
    reschedule_dict["old_date"] = appointment.date
    reschedule_dict["old_time"] = appointment.time

    new_reschedule = models.RescheduleRequest(**reschedule_dict)

    try:
        db.add(new_reschedule)
        db.commit()
        db.refresh(new_reschedule)
    except Exception:
        return Response(status_code=status.HTTP_417_EXPECTATION_FAILED)
    
    return new_reschedule


@router.delete("/reschedules/{appointment_id}")
def delete_reschedule(appointment_id: int, db:Session=Depends(get_db),
                      current_patient: models.Patient=Depends(get_current_user)):
    
    if current_patient.role != "patient": #type: ignore
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Method concerns patients only"
            )
    
    reschedule_query = db.query(models.RescheduleRequest).filter(models.RescheduleRequest.appointment_id == appointment_id)
    reschedule = reschedule_query.first()

    if not reschedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                           detail="Reschedule doesn't exists !")
    
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Appoitment doesn't exists !")
    
    if appointment.patient_id != current_patient.id:   #type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You aren't part of the appointment !")
    
    reschedule_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ------------- Patient FeedBack -------------

@router.post("/feedbacks/{appointment_id}")
def add_feedback(appointment_id: int, feedback: FeedBack, db:Session=Depends(get_db),
                 current_patient:models.Patient=Depends(get_current_user)):
    
    if current_patient.role != "patient": #type: ignore
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Method concerns patients only"
            )
    
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Appointment Not Found !")
    
    if appointment.patient_id != current_patient.id: # type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You aren't part of this appointment !")
    
    feedback_dict = feedback.model_dump(exclude_none=True)
    feedback_dict["appointment_id"] = appointment_id
    new_feedback = models.FeedBack(**feedback_dict)
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback


@router.delete("/feedbacks/{appointment_id}")
def remove_feedback(appointment_id: int, db:Session=Depends(get_db),
                 current_patient:models.Patient=Depends(get_current_user)):
    
    if current_patient.role != "patient": #type: ignore
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Method concerns patients only"
            )
    
    appointment = db.query(models.Appointment).filter(models.Appointment.id == appointment_id).first()

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Appointment Not Found !")
    
    if appointment.patient_id != current_patient.id: # type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You aren't part of this appointment !")
    
    feedback_query = db.query(models.FeedBack).filter(models.FeedBack.appointment_id == appointment_id)
    feedback = feedback_query.first()

    if not feedback:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="FeedBack Not Found !")
    
    feedback_query.delete(feedback, synchronize_session=False) # type:ignore
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/feedbacks", response_model=List[FeedBack])
def get_feedbacks(db: Session=Depends(get_db), current_patient: models.Patient=Depends(get_current_user)):

    if current_patient.role != "patient": #type: ignore
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Method concerns patients only"
            )

    feedbacks = []
    appointments = get_appointments(db, current_patient)
    for app in appointments:
        feedback = db.query(models.FeedBack).filter(models.FeedBack.appointment_id == app.id).first()
        if feedback:
            feedbacks.append(feedback)

    if not feedbacks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No Existing Reschedules For You !")

    return feedbacks