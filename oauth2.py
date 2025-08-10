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
        role = payload.get("role")

        if not id:
            raise credentials_exception
        
        if not role:
            raise credentials_exception
        
        # pydantic model to validate token data (payload)
        token_data = schemas.TokenData(id=id, role=role)

    except JWTError:
        raise credentials_exception
    
    return token_data
    

# dependency function to get the currently logged in user
# it automatically extracts the token from the authorization header
# "WWW-Authenticate": "Bearer" informs the client to send a bearer token
def get_current_user(token: str=Depends(oauth2_scheme), db:Session=Depends(get_db)):
    cred_exc = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    token_data = verify_access_token(token, cred_exc)

    if token_data.role == "doctor":
        user = db.query(models.Doctor).filter_by(id=token_data.id).first()
    elif token_data.role == "patient":
        user = db.query(models.Patient).filter_by(id=token_data.id).first()
    else:
        raise cred_exc

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
