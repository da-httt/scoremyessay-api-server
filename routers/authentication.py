from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt

import models 
from dependencies import oauth2_scheme, get_db, pwd_context, get_account, get_current_account, get_current_active_account, verify_password, get_password_hash, create_access_token, authenticate_account
from dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

import schemas 


router = APIRouter(
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)

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

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    account = authenticate_account(db, form_data.username, form_data.password)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": account.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(account_login: schemas.AccountLogin, db: Session = Depends(get_db)):
    account = authenticate_account(db, account_login.username, account_login.password)
    if not account:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": account.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/signup", response_model=schemas.Account)
async def signup_for_new_account(new_account: schemas.SignUp,
                                db: Session = Depends(get_db)):
    
    if get_account(db, new_account.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if not db.query(models.Role).filter(models.Job.job_id == new_account.job_id).first():
        raise HTTPException(status_code=400, detail="role_id not found")
    
    if not db.query(models.Gender).filter(models.Gender.gender_id == new_account.gender_id).first():
        raise HTTPException(status_code=400, detail="gender_id not found")
    
    
    db_account, _ = await create_account(db, new_account)
    return schemas.Account(account_id=db_account.account_id,
                   user_id = db_account.user[0].user_id,
                   email = db_account.email,
                   disabled = db_account.disabled,
                   role_id=db_account.role_id)
    

@router.get("/accounts/me", response_model=schemas.Account)
async def read_account_me(current_account: schemas.Account = Depends(get_current_active_account)):
    return current_account
