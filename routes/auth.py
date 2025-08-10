from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from database import get_db
from schemas import Token
from sqlalchemy.orm import Session
import models
import utils
import oauth2

router = APIRouter(prefix="/login", tags=["Authentification"])

@router.post("/", response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(),
           db:Session=Depends(get_db)):

    patient = db.query(models.Patient).filter(models.Patient.email == user_credentials.username).first()

    if not patient:

        doctor = db.query(models.Doctor).filter(models.Doctor.email == user_credentials.username).first()

        if not doctor:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Invalid Credentials")
        
        is_verified = utils.verify(user_credentials.password, doctor.password)
    
        if not is_verified:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Invalid Credentials")
    
        access_token = oauth2.create_access_token(payload={"user_id": doctor.id})

        return {"access_token": access_token, "token_type": "bearer"}
    
    # Verify user's password
    is_verified = utils.verify(user_credentials.password, patient.password)
    
    if not is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Invalid Credentials")
    
    access_token = oauth2.create_access_token(payload={"user_id": patient.id})
    
    return {"access_token": access_token, "token_type": "bearer"}