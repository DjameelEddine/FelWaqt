from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
import models
from sqlalchemy.orm import Session
from database import get_db
from sqlalchemy import or_
from schemas import DoctorOut

router = APIRouter(tags=["Home"])

@router.get("/", response_model=List[DoctorOut])
def get_doctors(search: str = "", db: Session = Depends(get_db)):
    search = search.capitalize()

    doctors = db.query(models.Doctor).filter(
        or_(
        models.Doctor.first_name.contains(search),
        models.Doctor.last_name.contains(search),
        models.Doctor.city.contains(search),
        models.Doctor.specialty.contains(search),
        models.Doctor.postal_code == search,
        )
        ).all()
    if not doctors:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="No Doctor Has Been Found!")
    return doctors