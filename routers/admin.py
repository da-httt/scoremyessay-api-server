from sqlalchemy.sql.operators import op
from dependencies import get_db, get_current_account
from fastapi import APIRouter, Depends, HTTPException, status, Body 
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
import schemas 
import models 
from typing import Optional, List
import json 
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
                        option_in_db: schemas.OptionInDB,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    
    if current_account.role_id != 0 :
        raise HTTPException(status_code=403)

    option_name = option_in_db.option_name
    option_price = option_in_db.option_price 
    option_type = option_in_db.option_type
    
    db_option = db.query(models.Option).filter(models.Option.option_id == option_id).first()
    if not db_option:
        raise HTTPException(status_code=404)
    
    if option_type not in [0,1] or option_price < 0:
        raise HTTPException(status_code=400, detail="option data not allowed")    
    
    if len(db.query(models.Option).filter(models.Option.option_name == option_name).all()) > 1:
        raise HTTPException(status_code=409, detail="option name has already existed")
    
    if db_option.option_id not in [0,1]:
        db_option.option_type = option_type
    
    db_option.option_name = option_name
    db_option.option_price = option_price
    db.commit()
    db.refresh(db_option)

    
    return schemas.Option(
        option_id = db_option.option_id,
        option_name = db_option.option_name,
        option_type = db_option.option_type,
        option_price = db_option.option_price 
    )
    
@router.post("/options", response_model=schemas.Option)
async def create_option( option_in_db: schemas.OptionInDB,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    if current_account.role_id != 0 :
        raise HTTPException(status_code=403)

    option_name = option_in_db.option_name
    option_price = option_in_db.option_price 
    option_type = option_in_db.option_type
    db_option = db.query(models.Option).filter(models.Option.option_name == option_name).first()
    if  db_option:
        raise HTTPException(status_code=409, detail="Option has already existed")

    if option_type not in [0,1] or option_price < 0:
        raise HTTPException(status_code=400, detail="option data not allowed")    
    
    db_option = models.Option(
        option_name =option_name,
        option_type = option_type,
        option_price = option_price
    )
    db.add(db_option)
    db.commit()
    db.refresh(db_option)
    
    return schemas.Option(
        option_id = db_option.option_id,
        option_name = db_option.option_name,
        option_type = db_option.option_type,
        option_price = db_option.option_price 
    )

@router.delete("/options/{option_id}")
async def delete_option(option_id:int,
                     current_account: schemas.Account = Depends(get_current_account),
                        db: Session=Depends(get_db)):
    if current_account.role_id != 0 :
        raise HTTPException(status_code=403)

    
    db_option = db.query(models.Option).filter(models.Option.option_id == option_id).first()
    if not db_option:
        raise HTTPException(status_code=404)
    
    
    if db_option.option_id not in [0,1]:
        try:
            db.delete(db_option)
            db.commit()
            return {
                "status": "success"
            }
        except: 
            raise HTTPException(status_code=500)
    
    else: 
        raise HTTPException(status_code=403, detail="This option can not be deleted!")
    
def get_topic(db_essay:models.Essay, db:Session):
    db_essay_info = db_essay.essay_info
    return db_essay_info[0]

def get_time_left(db_order: models.Order):
    time_left = 0
    if db_order.status_id != 0:
        current_time_left =  db_order.deadline - datetime.today() + timedelta(hours=1)
        if current_time_left.days >= 0 :
            time_left = current_time_left.days*24 + (current_time_left.seconds // 3600)
    return time_left 

def get_order_response(db_order: models.Order, db: Session):
    db_essay = db_order.essay
    deadline = None 
    if db_order.deadline:
        deadline = db_order.deadline.strftime("%m/%d/%Y, %H:%M:%S")
    db_essay_info = get_topic(db_essay, db)
    return schemas.OrderResponse(
            status_id = db_order.status_id,
            order_id = db_order.order_id,
            student_id = db_order.student_id,
            teacher_id = db_order.teacher_id,
            sent_date = db_order.sent_date.strftime("%m/%d/%Y, %H:%M:%S"),
            updated_date = db_order.updated_date.strftime("%m/%d/%Y, %H:%M:%S"),
            updated_by = db_order.updated_by,
            essay = schemas.EssayResponse(
                essay_id = db_essay.essay_id,
                title = db_essay.title,
                content = db_essay.content,
                type_id = db_essay.type_id
            ),
            option_list = [int(item) for item in db_order.option_list.split("-")],
            total_price = db_order.total_price,
            is_disabled = db_order.is_disabled,
            deadline = deadline,
            time_left = get_time_left(db_order),
            topic_name = db_essay_info.predicted_topic
        )


@router.put("/orders/reset/{order_id}")
async def reset_deadline(order_id: int, 
                        current_account: schemas.Account = Depends(get_current_account),
                         db: Session = Depends(get_db)):
    if current_account.role_id != 0:
        raise HTTPException(status_code=403)
    
    db_optionlist = db.query(models.Option).order_by(models.Option.option_id).all()

    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
        
    if not db_order or db_order.is_disabled:
        raise HTTPException(status_code=404)
    
    
    option_list = [int(item) for item in db_order.option_list.split("-")]
    updated_date = datetime.today()

    deadline = 0
    for option_id in option_list:
        for db_option in db_optionlist:
            if db_option.option_id == option_id:
                if db_option.option_type == 1:
                    deadline_hour = int(db_option.option_name) 
    deadline = datetime.today() + timedelta(hours=deadline_hour)
    
    db_order.deadline = deadline
    if db_order.status_id == 4:
        db_order.status_id = 2
    db.commit()
    db.refresh(db_order)
    
    return get_order_response(db_order, db)
