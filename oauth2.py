# FILE TO CREATE AND VERIFY JWT TOKENS
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import schemas
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, status, Depends
from database import get_db
from sqlalchemy.orm import Session
import models
from config import settings

# to extract the bearer token automatically from the header
# and to define where clients should get tokens (/login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


SECRET_KEY = "7348WUEIFJKSDIU9QDJWKS4UFEWNDQ09PWJOKNLFADVKGVFHBKCUFWOIEJPQW032984UIJEKDS4UI3J"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

def create_access_token(payload: dict):
    payload_to_encode = payload.copy()

    # add expiry date to payload's items
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload_to_encode.update({"exp": expire})

    # create a token
    token = jwt.encode(payload_to_encode, SECRET_KEY, ALGORITHM)

    return token

def verify_access_token(token: str, credentials_exception):

    try:
        # checks the signature validity and expiration and returns the payload dict
        payload = jwt.decode(token, SECRET_KEY, [ALGORITHM])

        # retrieve id since it's the only component of the token
        id = payload.get("user_id")

        if not id:
            raise credentials_exception
        
        # pydantic model to validate token data (payload)
        token_data = schemas.TokenData(id=id)

    except JWTError:
        raise credentials_exception
    
    return token_data
    

# dependency function to get the currently logged in user
# it automatically extracts the token from the authorization header
# "WWW-Authenticate": "Bearer" informs the client to send a bearer token
def get_current_user(token: str=Depends(oauth2_scheme), db:Session=Depends(get_db)):
    credential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                         detail="Could not validate credentials",
                                         headers={"WWW-Authenticate": "Bearer"})
    
    token_data = verify_access_token(token, credential_exception)


    # extract logged in user for more DB operations
    doctor = db.query(models.Doctor).filter(models.Doctor.id == token_data.id).first()
  
    if not doctor:
        patient = db.query(models.Patient).filter(models.Patient.id == token_data.id).first()
        
        if not patient:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User With Received Credentials Doesn't Exist !")
        return patient

    return doctor