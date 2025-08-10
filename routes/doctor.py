from fastapi import APIRouter, Depends, status, HTTPException, Response
from sqlalchemy.orm import Session
from schemas import DoctorCreate, DoctorUpdate, DoctorOut, AppointmentOut, AppointmentsUpdate, ConfirmAppointment, PatientOut
from database import get_db
import models
from typing import List
from sqlalchemy import or_
from oauth2 import get_current_user
import utils


router = APIRouter(prefix="/doctors", tags=["Doctors"])

@router.post("/", response_model=DoctorOut)
def create_doctor(doctor: DoctorCreate, db: Session=Depends(get_db)):
    try:
        doctor.password = utils.hash(doctor.password)
        doctor_dict = doctor.model_dump()
        doctor_dict["first_name"] = doctor_dict["first_name"].capitalize()
        doctor_dict["last_name"] = doctor_dict["last_name"].capitalize()
        doctor_dict["specialty"] = doctor_dict["specialty"].capitalize()
        doctor_dict["city"] = doctor_dict["city"].capitalize()

        new_doctor = models.Doctor(**doctor_dict)
        db.add(new_doctor)
        db.commit()
        db.refresh(new_doctor)
        return new_doctor
    except Exception:
        print("Some Error Has Occured, Please Check Your Input Validity")


@router.get("/patients", response_model=List[PatientOut])
def get_doctor_patients(db: Session=Depends(get_db),
                 current_doctor : models.Doctor=Depends(get_current_user)):
    
    if current_doctor.role != "doctor": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns doctors only"
        )

    doctor_appointments = db.query(models.Appointment).filter(models.Appointment.doctor_id == current_doctor.id).all()
    doctor_patients_ids = [appointment.patient_id for appointment in doctor_appointments]

    doctor_patients = db.query(models.Patient).filter(models.Patient.id.in_(doctor_patients_ids)).all()

    if not doctor_patients:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"No Patient Has Been Found!")
    return doctor_patients


@router.get("/appointments", response_model=List[AppointmentOut])
def get_appointments(db: Session=Depends(get_db), current_doctor: models.Doctor=Depends(get_current_user)):
    print (current_doctor.role, type(current_doctor.role))
    if current_doctor.role != "doctor": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns doctors only"
        )

    doctor_appointments = db.query(models.Appointment).filter(models.Appointment.doctor_id == current_doctor.id).all()

    if not doctor_appointments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No Existing Appointments For You !")

    return doctor_appointments


@router.get("/feedbacks")
def get_feedbacks(db: Session=Depends(get_db),
                  current_doctor:models.Doctor=Depends(get_current_user)):
    
    if current_doctor.role != "doctor": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns doctors only"
        )

    doctor_appointments = db.query(models.Appointment).filter(models.Appointment.doctor_id == current_doctor.id).all()

    if not doctor_appointments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No Appointments Found !")

    feedbacks = db.query(models.FeedBack).filter(models.FeedBack.appointment_id.in_(doctor_appointments)).all()

    if not feedbacks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No Feedbacks Found !")
    
    return feedbacks


@router.get("/{id}", response_model=DoctorOut)
def get_doctor(id: int, db: Session=Depends(get_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.id == id).first()
    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Doctor with id: {id} not found!")
    return doctor


@router.delete("/{id}")
def delete_doctor(id: int, db: Session=Depends(get_db),
                  current_doctor: models.Doctor=Depends(get_current_user)):
    
    if current_doctor.role != "doctor": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns doctors only"
        )

    doctor_query = db.query(models.Doctor).filter(models.Doctor.id == id)
    doctor = doctor_query.first()

    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Doctor Not Found !")
    
    if doctor.id != current_doctor.id: # type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You Don't Own this doctor account !")
    
    doctor_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{id}", response_model=DoctorOut)
def update_doctor(id: int, new_doctor: DoctorUpdate, db:Session=Depends(get_db),
                  current_doctor:models.Doctor=Depends(get_current_user)):
    
    if current_doctor.role != "doctor": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns doctors only"
        )

    doctor_query = db.query(models.Doctor).filter(models.Doctor.id == id)
    doctor = doctor_query.first()

    if not doctor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Doctor with id: {id} was not found")
    
    if doctor.id != current_doctor.id: #type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You Don't Own this doctor account !")

    doctor_dict = new_doctor.model_dump(exclude_none=True)
    try:
        doctor_dict["first_name"] = doctor_dict["first_name"].capitalize()
        doctor_dict["last_name"] = doctor_dict["last_name"].capitalize()
        doctor_dict["specialty"] = doctor_dict["specialty"].capitalize()
        doctor_dict["city"] = doctor_dict["city"].capitalize()
    except Exception:
        print ("There we some empty fields.")
    doctor_query.update(doctor_dict, synchronize_session=False) #type: ignore
    db.commit()
    db.refresh(doctor)
    return doctor

# --------------- Appointments for doctors ---------------

@router.patch("/appointments/{appointment_id}", response_model=AppointmentOut)
def update_appointment(appointment_id: int, new_appointment: AppointmentsUpdate, db:Session=Depends(get_db), 
                       current_doctor:models.Doctor=Depends(get_current_user)):
        
    if current_doctor.role != "doctor": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns doctors only"
        )    
    
    target_appointment_query = db.query(models.Appointment).filter(models.Appointment.id == appointment_id)
    target_appointment = target_appointment_query.first()
    if not target_appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Appointment has not been found !")
    
    if bool(target_appointment.doctor_id != current_doctor.id):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You aren't part of this appointment !")
        
    all_appointments = db.query(models.Appointment).filter(or_(models.Appointment.doctor_id == current_doctor.id,
                                                               models.Appointment.patient_id == target_appointment.patient_id)).all()
    
    new_appointment_dict = new_appointment.model_dump(exclude_none=True)

    for appointment in all_appointments:

        if (appointment.date == new_appointment_dict.get("date") and
            appointment.time == new_appointment_dict.get("time")):
            raise HTTPException(status_code=status.HTTP_304_NOT_MODIFIED,
                                detail="Can not use update appointment to this time and date, please change.")
    print("here")
    target_appointment_query.update(new_appointment_dict) # type: ignore
    db.commit()
    db.refresh(target_appointment)
    return target_appointment


@router.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session=Depends(get_db),
                       current_doctor=Depends(get_current_user)):
    
    if current_doctor.role != "doctor": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns doctors only"
        )

    appointments_query = db.query(models.Appointment).filter(models.Appointment.id == appointment_id)
    appointment = appointments_query.first()

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Appointment doesn't exist !")

    try:
        if appointment.doctor_id != current_doctor.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You aren't part of this appointment !")
    except Exception:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)

    appointments_query.delete(appointment)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/appointments/{appointment_id}")
def confirm_or_done_appointment(appointment_id: int, confirm_or_done: ConfirmAppointment, db:Session=Depends(get_db),
                     current_doctor: models.Doctor=Depends(get_current_user)):
    
    if current_doctor.role != "doctor": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns doctors only"
        )
    
    appointment_query = db.query(models.Appointment).filter(models.Appointment.id == appointment_id)
    appointment = appointment_query.first()

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Appointment not found !")
    
    if appointment.doctor_id != current_doctor.id: #type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You aren't part of this appointment !")

    confirmation_dict = confirm_or_done.model_dump(exclude_none=True)
    if confirmation_dict["done"] and not confirmation_dict["confirmed"]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Appointment has to be Confirmed before set to Done.")
    appointment_query.update(confirmation_dict, synchronize_session=False) # type: ignore
    db.commit()

    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post("/reschedules/{appointment_id}")
def confirm_reschedule(appointment_id: int, db:Session=Depends(get_db),
                     current_doctor: models.Doctor=Depends(get_current_user)):
    
    if current_doctor.role != "doctor": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns doctors only"
        )
    
    appointment_query = db.query(models.Appointment).filter(models.Appointment.id == appointment_id)
    appointment = appointment_query.first()

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Appointment not found !")
    
    if appointment.doctor_id != current_doctor.id: #type: ignore
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You aren't part of this appointment !")
    
    reschedule_query = db.query(models.RescheduleRequest).filter(models.RescheduleRequest.appointment_id == appointment_id)
    reschedule = reschedule_query.first()

    if not reschedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Reschedule not found !")
    
    appointment.date = reschedule.new_date
    appointment.time = reschedule.new_time
    reschedule_query.delete(synchronize_session=False)
    
    db.commit()

    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.delete("/reschedules/{appointment_id}")
def reject_reschedule(appointment_id: int, db: Session=Depends(get_db),
                       current_doctor=Depends(get_current_user)):
    
    if current_doctor.role != "doctor": #type: ignore
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Method concerns doctors only"
        )

    appointments_query = db.query(models.Appointment).filter(models.Appointment.id == appointment_id)
    appointment = appointments_query.first()

    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Appointment doesn't exist !")

    try:
        if appointment.doctor_id != current_doctor.id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="You aren't part of this appointment !")
    except Exception:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    
    reschedule_query = db.query(models.RescheduleRequest).filter(models.RescheduleRequest.appointment_id == appointment_id)
    reschedule = reschedule_query.first()

    if not reschedule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Reschdule not found !")

    reschedule_query.delete(synchronize_session=False)

    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)