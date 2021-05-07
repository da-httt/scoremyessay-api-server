from dependencies import get_db, get_current_account
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
import schemas 
import models 
from typing import Optional, List

router = APIRouter(
    tags=["Admin"],
    responses={404: {"description": "Not found"}},
)

@router.put("/jobs/{job_id}", response_model=schemas.Job)
async def update_job_name(job_id:int,
                        job_name: str,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    db_job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    
    if not db_job:
        raise HTTPException(status_code=404)

    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_job.job_name = job_name
    db.commit()
    db.refresh(db_job)
    return schemas.Job(
        job_id = db_job.job_id,
        job_name = db_job.job_name
    )

@router.post("/jobs", response_model=schemas.Job)
async def create_job(job_name: str,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    db_job = db.query(models.Job).filter(models.Job.job_name == job_name).first()
    
    if db_job:
        raise HTTPException(status_code=409, detail="Job name is already in the database")

    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_job = models.Job(
        job_name = job_name
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return schemas.Job(
        job_id = db_job.job_id,
        job_name = db_job.job_name
    )
    

@router.put("/genders/{gender_id}", response_model=schemas.Gender)
async def update_gender_name(gender_id:int,
                        gender_name: str,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    db_gender = db.query(models.Gender).filter(models.Gender.gender_id == gender_id).first()
    
    if not db_gender:
        raise HTTPException(status_code=404)

    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_gender.gender_name = gender_name
    db.commit()
    db.refresh(db_gender)
    return schemas.Gender(
        gender_id = db_gender.gender_id,
        gender_name = db_gender.gender_name
    )
    

@router.put("/jobs/{job_id}", response_model=schemas.Job)
async def update_job_name(job_id:int,
                        job_name: str,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    db_job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    
    if not db_job:
        raise HTTPException(status_code=404)

    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_job.job_name = job_name
    db.commit()
    db.refresh(db_job)
    return schemas.Job(
        job_id = db_job.job_id,
        job_name = db_job.job_name
    )
    
