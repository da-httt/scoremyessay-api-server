from typing import Optional, List
from fastapi import FastAPI, Query, Depends, Path, Body, Header, Form, File, UploadFile, HTTPException, status
from pydantic import BaseModel, Field 
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from db import SessionLocal, engine 
from passlib.context import CryptContext
import schemas 
import models
from jose import JWTError, jwt
from modules.topic_classification import inference 

#Define secret key and algorithm
SECRET_KEY = "b8f93afd6ae4f16427e475cb090a23671e6e9f00dc5fbd603c1469355f575854"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1000


#Load model
def load_model():
    predictor = inference.Predictor()
    return predictor 

predictor = load_model()

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


#Define CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Define authenticate function
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_account(db: Session, email: str):
    print("checking email with " + email)
    return db.query(models.Account).filter(models.Account.email == email).first()


def authenticate_account(db: Session, email: str, password: str):
    account = get_account(db, email)
    if not account:
        print("Account not found!")
        return False 
    if not verify_password(password, account.hashed_password):
        print("Wrong password")
        return False 
    return account

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    return encoded_jwt 


    

async def get_current_account(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try: 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub") 
        if email is None:
            raise credentials_exception
        token_data = schemas.TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    account = get_account(db, email=token_data.email)
    if account is None:
        raise credentials_exception
    
    print("see role: " + account.role.role_name)
    schema_account = schemas.Account(
        user_id = account.user[0].user_id,
        account_id=account.account_id,
        email=account.email,
        role_id=account.role_id,
        disabled=account.disabled)
    return schema_account 

#Authentication Route 
async def get_current_active_account(account: schemas.Account = Depends(get_current_account)):
    print("Getting info..")
    if account.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    print(account)
    return account
