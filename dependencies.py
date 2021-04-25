from typing import Optional, List
from fastapi import FastAPI, Query, Depends, Path, Body, Header, Form, File, UploadFile, HTTPException
from pydantic import BaseModel, Field 
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


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
        account_id=account.account_id,
        email=account.email,
        role_id=account.role_id,
        disabled=account.disabled)
    return schema_account 

async def create_account(db: Session, new_account: schemas.SignUp):
    
    hashed_password = get_password_hash(new_account.password)
    db_account = models.Account(email=new_account.email, 
                                hashed_password=hashed_password, 
                                disabled=False, 
                                role_id=1)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    
    db_user = models.User(account_id=db_account.account_id,
                          name = new_account.name,
                          address = new_account.address,
                          gender_id = new_account.gender_id,
                          job_id = new_account.job_id,
                          phone_number = new_account.phone_number,
                          date_of_birth = new_account.date_of_birth
                         )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_account, db_user