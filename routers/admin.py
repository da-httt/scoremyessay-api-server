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

@router.delete("/jobs/{job_id}")
async def delete_job(job_id:int,
                     current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_job = db.query(models.Job).filter(models.Job.job_id == job_id).first()
    if not db_job:
        raise HTTPException(status_code=409, detail="Job not found!")

    try:
        db.delete(db_job)
        db.commit()
    except: 
        raise HTTPException(status_code=500, detail="Can not delete.")
    return {
        "status": "success"
    }

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
    

@router.post("/genders", response_model=schemas.Gender)
async def create_gender(gender_name: str,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_gender = db.query(models.Gender).filter(models.Gender.gender_name == gender_name).first()
    
    if  db_gender:
        raise HTTPException(status_code=409, detail="Gender has already existed!")

    
    
    db_gender = models.Gender(gender_name = gender_name)
    db.add(db_gender) 
    db.commit()
    db.refresh(db_gender)
    return schemas.Gender(
        gender_id = db_gender.gender_id,
        gender_name = db_gender.gender_name
    )
    
@router.delete("/genders/{gender_id}")
async def delete_gender(gender_id:int,
                     current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_gender = db.query(models.Gender).filter(models.Gender.gender_id == gender_id).first()
    if not db_gender:
        raise HTTPException(status_code=409, detail="Gender not found!")

    try:
        db.delete(db_gender)
        db.commit()
    except: 
        raise HTTPException(status_code=500, detail="Can not delete.")
    return {
        "status": "success"
    }



@router.put("/levels/{level_id}", response_model=schemas.Level)
async def update_level_name(level_id:int,
                        level_name: str,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    db_level = db.query(models.EssayLevel).filter(models.EssayLevel.level_id == level_id).first()
    
    if not db_level:
        raise HTTPException(status_code=404)

    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_level.level_name = level_name
    db.commit()
    db.refresh(db_level)
    return schemas.Level(
        level_id = db_level.level_id,
        level_name = db_level.level_name
    )
    

@router.post("/levels", response_model=schemas.Level)
async def create_level(level_name: str,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_level = db.query(models.EssayLevel).filter(models.EssayLevel.level_name == level_name).first()
    
    if  db_level:
        raise HTTPException(status_code=409, detail="Level has already existed!")

    db_level = models.EssayLevel(level_name = level_name)
    db.add(db_level) 
    db.commit()
    db.refresh(db_level)
    return schemas.Level(
        level_id = db_level.level_id,
        level_name = db_level.level_name
    )
    
@router.delete("/levels/{level_id}")
async def delete_level(level_id:int,
                     current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_level = db.query(models.EssayLevel).filter(models.EssayLevel.level_id == level_id).first()
    if not db_level:
        raise HTTPException(status_code=409, detail="Level  not found!")

    try:
        db.delete(db_level)
        db.commit()
    except: 
        raise HTTPException(status_code=500, detail="Can not delete.")
    return {
        "status": "success"
    }


def get_level_id(db_level):
    return db_level.level_id

@router.put("/types/{type_id}", response_model=schemas.Type)
async def update_type_name(type_id:int,
                        type_name: Optional[str] = None, 
                        type_price: Optional[float] = None,
                        level_id: Optional[int] = None,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    db_type = db.query(models.EssayType).filter(models.EssayType.type_id == type_id).first()
    
    if not db_type:
        raise HTTPException(status_code=404)

    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    if type_name:
        db_type.type_name = type_name
    if type_price:
        db_type.type_price = type_price 
    if level_id:
        db_level_list = db.query(models.EssayLevel).all()
        level_list = map(get_level_id, db_level_list)
        if level_id in level_list:
            db_type.level_id = level_id
        else:
            raise HTTPException(status_code=400, detail="Level id not correct")
        
    
    db.commit()
    db.refresh(db_type)
    return schemas.Type(
        type_id = db_type.type_id,
        type_name = db_type.type_name,
        type_price = db_type.type_price,
        level_id = db_type.level_id
    )
    

@router.post("/types", response_model=schemas.Type)
async def create_type( type_name: str,
                        type_price: float, 
                        level_id: int,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_type = db.query(models.EssayType).filter(models.EssayType.type_name == type_name).first()
    
    if  db_type:
        raise HTTPException(status_code=409, detail="Type has already existed!")

    db_type = models.EssayType(type_name = type_name, 
                                type_price = type_price,
                                level_id = level_id)
    db.add(db_type) 
    db.commit()
    db.refresh(db_type)
    return schemas.Type(
        type_id = db_type.type_id,
        type_name = db_type.type_name,
        type_price = db_type.type_price,
        level_id = db_type.level_id
    )
    
@router.delete("/types/{type_id}")
async def delete_type(type_id:int,
                     current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_type = db.query(models.EssayType).filter(models.EssayType.type_id == type_id).first()
    if not db_type:
        raise HTTPException(status_code=409, detail="Level  not found!")

    try:
        db.delete(db_type)
        db.commit()
    except: 
        raise HTTPException(status_code=500, detail="Can not delete.")
    return {
        "status": "success"
    }


@router.put("/options/{option_id}}", response_model=schemas.Option)
async def update_option(option_id:int,
                        option_type: Optional[int] = None, 
                        option_price: Optional[float] = None,
                        option_name: Optional[str] = None,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    pass
    

@router.post("/options", response_model=schemas.Option)
async def create_option( option_name: str,
                        option_price: float, 
                        option_type: int,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    pass 

@router.delete("/options/{option_id}")
async def delet_option(option_id:int,
                     current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    pass