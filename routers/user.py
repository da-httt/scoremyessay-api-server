from dependencies import get_db, get_current_account
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
import schemas 
import models 


router = APIRouter(
    tags=["User"],
    responses={404: {"description": "Not found"}},
)


def get_user_account(db_user: Session):
    return schemas.UserAccount(
            account_id = db_user.account.account_id,
            role_id = db_user.account.role_id,
            email = db_user.account.email,
            disabled = db_user.account.disabled,
            info = schemas.User(user_id = db_user.user_id,
                        name =  db_user.name,
                        date_of_birth =  db_user.date_of_birth,
                        address = db_user.address,
                        gender_id = db_user.gender_id,
                        job_id = db_user.job_id,
                        phone_number = db_user.phone_number)
            
        )
    

@router.get("/jobs", response_model= schemas.JobResponse)
async def read_job_list(db: Session=Depends(get_db)):
    db_job_list = db.query(models.Job).all()
    job_list = []
    for db_job in db_job_list:
        job_list.append(schemas.Job(job_id=db_job.job_id, job_name=db_job.job_name))
    
    job_response = schemas.JobResponse(
        status = "success",
        totalCount = len(job_list),
        data = job_list
    )
    return job_response

@router.get("/genders", response_model= schemas.GenderResponse)
async def read_gender_list(db: Session=Depends(get_db)):
    db_gender_list = db.query(models.Gender).all()
    gender_list = []
    for db_gender in db_gender_list:
        gender_list.append(schemas.Gender(gender_id=db_gender.gender_id, gender_name=db_gender.gender_name))
    
    gender_response = schemas.GenderResponse(
        status = "success",
        totalCount = len(gender_list),
        data = gender_list
    )
    return gender_response


# User route 

@router.get("/users/me", 
         response_model=schemas.UserAccount, 
         description = "Get the user information of current account")
async def read_user_information(current_account: schemas.Account = Depends(get_current_account), db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.account_id == current_account.account_id).first()
    return get_user_account(db_user)
    
@router.get("/users",
         response_model = schemas.UserResponse,
         description = "Get the all user information in database")
async def read_all_users(current_account: schemas.Account = Depends(get_current_account), db: Session = Depends(get_db)):
    if current_account.role_id != 0:
        raise HTTPException(status_code=403, detail="Only Admin can access this api")
    
    db_user_list = db.query(models.User).all()
    user_list = []
    for db_user in db_user_list:
        user_list.append(get_user_account(db_user))
    user_response = schemas.UserResponse(
        status = "success", 
        totalCount = len(user_list),
        perPage = len(user_list),
        data = user_list
    )
    return user_response 
        
        
@router.get("/users/{user_id}")
async def get_user_by_id(user_id:int,
                         current_account: schemas.Account = Depends(get_current_account),
                         db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found") 
    
    if current_account.user_id == user_id or current_account.role_id == 0:
        return get_user_account(db_user)
    else:
        return schemas.UserInfo(
            user_id = db_user.user_id,
            email = db_user.account.email,
                        name =  db_user.name,
                        date_of_birth =  db_user.date_of_birth,
                        address = db_user.address,
                        gender_id = db_user.gender_id,
                        job_id = db_user.job_id,
                        phone_number = db_user.phone_number)
    
    
@router.put("/users/{user_id}",
            response_model=schemas.UserAccount)
async def update_user(user_id: int,
                      new_user_info: schemas.UserInDB,
                      current_account: schemas.Account = Depends(get_current_account),
                      db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404)
    print(db_user.user_id)
    print(current_account.user_id)
    if db_user.user_id != current_account.user_id and current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_user.name = new_user_info.name 
    db_user.address = new_user_info.address
    db_user.date_of_birth = new_user_info.date_of_birth
    db_user.gender_id = new_user_info.gender_id
    db_user.job_id = new_user_info.job_id
    db_user.phone_number = new_user_info.phone_number
    db.commit()
    db.refresh(db_user)
    
    return get_user_account(db_user)
    

@router.delete("/users/{user_id}")
async def delete_user(user_id:int,
                      current_account: schemas.Account = Depends(get_current_account),
                      db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.user_id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404)

    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_user.account.disabled = not db_user.account.disabled
    db.commit()
    db.refresh(db_user)
    
    return get_user_account(db_user)

    