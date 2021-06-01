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
from datetime import datetime, timedelta

from fastapi_mail import FastMail, MessageSchema,ConnectionConfig

#from modules.topic_classification import inference 
import json 
#Define secret key and algorithm
SECRET_KEY = "b8f93afd6ae4f16427e475cb090a23671e6e9f00dc5fbd603c1469355f575854"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1000

conf = ConnectionConfig(
   MAIL_USERNAME="scoremyessay.dut@gmail.com",
   MAIL_PASSWORD="123456Ll",
   MAIL_FROM = "scoremyessay.dut@gmail.com",
   MAIL_PORT=587,
   MAIL_SERVER="smtp.gmail.com",
   MAIL_TLS=True,
   MAIL_SSL=False)


#Load model
"""def load_model():
    predictor = inference.Predictor()
    return predictor 
"""
#predictor = load_model()

def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
'''
Get Free Qualified Teacher
'''
"""
def get_list_teacher_status(db: Session):
    return db.query(models.TeacherStatus).all()

def get_free_qualified_teacher(db: Session, db_list_teacher_status, level_id: int ):
    db.refresh(db_list_teacher_status)
    db_free_teacher = [db_teacher for db_teacher in db_list_teacher_status if (db_teacher.active_essay < 5 and db_teacher.level_id == level_id)]
    return len(db_free_teacher)
def change_total(db_teacher_status: models.TeacherStatus):
    level = db_teacher_status
    
def update_last_active(db: Session, db_teacher_status: models.TeacherStatus):
    current_time = datetime.today()
    try:
        db_teacher_status.lastTimeActive = current_time
        db.commit()
        db.refresh(db_teacher_status)
    except: 
        raise HTTPException(status_code=500, detail="Can not read teacher status")
def if_level_qualified(db: Session, db_user: models.User, db_essay: models.Essay):
    try:
        level_id = db_user.teacher_status[0].level_id 
        if level_id == db_essay.level_id:
            return True 
        else:
            raise HTTPException(status_code=403, detail="Teacher Level doesn't match the Essay Level.")
    except:
        raise HTTPException(status_code=500, detail="Cant not read the Teacher information.")
    
    
def if_any_teacher_left(db: Session, db_essay: models.Essay):
    level_id = db_essay.level_id 
    return 1
    
    
def change_current_scoring_essay(db: Session, db_teacher_status: models.TeacherStatus, increase=True):
    try:
        if increase:
            if db_teacher_status.active_essays == 5:
                raise HTTPException(status_code=405, detail="The teacher has reached maximum essays")
            db_teacher_status.active_essays += 1
        else:
            if db_teacher_status.active_essays == 0:
                raise HTTPException(status_code=405)
            if db_teacher_status.active_essays == 5:
                db_teacher_status.active_essays -= 1
        db.commit()
        db.refresh(db_teacher_status)
    except:
        raise HTTPException(status_code=500, detail="Can not change teacher current active essay.")
    
def if_max_essays(db_teacher_status: models.TeacherStatus):
    try:
        if db_teacher_status.active_essays == 5:
            return True
        else:
            return False 
    except:
        raise HTTPException(status_code=500, detail="Can not read the teacher's current active essay")
    
#Level 0 Teacher 
db_list_teacher_status = get_list_teacher_status(get_db())
total_level0 = get_free_qualified_teacher(get_db(), db_list_teacher_status, level_id=0)
total_level1 = get_free_qualified_teacher(get_db(), db_list_teacher_status, level_id=1)


"""
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
