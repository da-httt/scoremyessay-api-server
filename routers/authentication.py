from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi_mail import FastMail, MessageSchema,ConnectionConfig
from starlette.requests import Request
from starlette.responses import JSONResponse
from routers.teacher_promo import create_teacher_status
import models
from dependencies import oauth2_scheme, get_db, pwd_context, get_account, get_current_account, get_current_active_account, verify_password, get_password_hash, create_access_token, authenticate_account
from dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, conf

import schemas


router = APIRouter(
    tags=["Authentication"],
    responses={404: {"description": "Not found"}},
)


async def create_account(db: Session, new_account, role_id=1, default_password=None):

    if not default_password:
        hashed_password = get_password_hash(new_account.password)
    else:
        hashed_password = get_password_hash(default_password)
    db_account = models.Account(email=new_account.email,
                                hashed_password=hashed_password,
                                disabled=False,
                                role_id=role_id)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)

    db_user = models.User(account_id=db_account.account_id,
                          name=new_account.name,
                          address=new_account.address,
                          gender_id=new_account.gender_id,
                          job_id=new_account.job_id,
                          phone_number=new_account.phone_number,
                          date_of_birth=new_account.date_of_birth
                          )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    if db_user:
        if role_id == 2:
            create_teacher_status(db, db_user.user_id, level_id=0)
    
    if new_account.avatar:
        db_avatar = models.Avatar(user_id=db_user.user_id, img=new_account.avatar)
        db.add(db_avatar)
        db.commit()
        db.refresh(db_avatar)
        

    return db_account, db_user


async def change_password(db: Session, db_account: models.Account, new_password: str):
    hashed_password = get_password_hash(new_password)
    
    db_account.hashed_password = hashed_password
    db.commit()
    db.refresh(db_account)
    return db_account


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
    account = authenticate_account(
        db, account_login.username, account_login.password)
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
                           user_id=db_account.user[0].user_id,
                           email=db_account.email,
                           disabled=db_account.disabled,
                           role_id=db_account.role_id)


@router.get("/accounts/me", response_model=schemas.Account)
async def read_account_me(current_account: schemas.Account = Depends(get_current_active_account)):
    return current_account 

"""@router.post("/signup/admin/teacher", response_model=schemas.Account)
async def signup_for_new_account(new_account: schemas.SignUp,
                                current_account: schemas.Account = Depends(get_current_account),
                                 db: Session = Depends(get_db)):

    if get_account(db, new_account.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    if not db.query(models.Role).filter(models.Job.job_id == new_account.job_id).first():
        raise HTTPException(status_code=400, detail="role_id not found")

    if not db.query(models.Gender).filter(models.Gender.gender_id == new_account.gender_id).first():
        raise HTTPException(status_code=400, detail="gender_id not found")

    db_account, _ = await create_account(db, new_account,role_id=2)
    return schemas.Account(account_id=db_account.account_id,
                           user_id=db_account.user[0].user_id,
                           email=db_account.email,
                           disabled=db_account.disabled,
                           role_id=db_account.role_id)
"""

@router.get("/accounts/me", response_model=schemas.Account)
async def read_account_me(current_account: schemas.Account = Depends(get_current_active_account)):
    return current_account



@router.put("/change_password/me", response_model=schemas.Account)
async def change_current_password(new_password: str,
                          current_account: schemas.Account = Depends(
                              get_current_active_account),
                          db: Session = Depends(get_db)):
    db_account = db.query(models.Account).filter(
        models.Account.account_id == current_account.account_id).first()
    print(db_account.hashed_password)
    db_account = await change_password(db, db_account, new_password)
    print(db_account.hashed_password)

    return current_account


@router.put("/change_password/{account_id}", response_model=schemas.Account)
async def change_password_by_account_id(account_id: int,
                          new_password: str,
                          current_account: schemas.Account = Depends(
                              get_current_active_account),
                          db: Session = Depends(get_db)):
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    db_account = db.query(models.Account).filter(
        models.Account.account_id == account_id).first()
    db_account = await change_password(db, db_account, new_password)
    return current_account



@router.post("/signup/teacher")
async def sign_up_for_teacher(teacher_form: schemas.TeacherForm,
                              db: Session = Depends(get_db)):
    
    if get_account(db, teacher_form.email):
        raise HTTPException(status_code=409, detail="Email already registered")

    if not db.query(models.Role).filter(models.Job.job_id == teacher_form.job_id).first():
        raise HTTPException(status_code=400, detail="role_id not found")

    if not db.query(models.Gender).filter(models.Gender.gender_id == teacher_form.gender_id).first():
        raise HTTPException(status_code=400, detail="gender_id not found")

    db_account, db_user = await create_account(db, teacher_form,role_id=2,default_password="123456")

    if db_account:
        template = f"""
            <html>
            <body>
            
    <p>From ScoreMyEssay, !!!
            <br>Congratulation, your application has been approved.!!</p>
            <p>You can access ScoreMyEssay with account below:</p>
            <br>Name: {db_user.name}
            <br>Email: {db_account.email}
            <br>Password: {123456}
            </body>
            </html>
            """
    message = MessageSchema(
        subject="ScoreMyEssay - Teacher Application Result",
        recipients=[db_account.email],  # List of recipients, as many as you can pass 
        body=template,
        subtype="html"
        )
  
    fm = FastMail(conf)
    await fm.send_message(message)
    print(message)
  
    
    return JSONResponse(status_code=200, content={"message": "Application has been sent!"})
