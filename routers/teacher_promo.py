
from db import SessionLocal
import global_var
from sqlalchemy.sql.expression import update
from dependencies import get_db, get_current_account
from fastapi import APIRouter, Depends, HTTPException, status, Query 
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import schemas 
import models 
from typing import Optional, List
from sqlalchemy import desc, schema
from modules import paragraph
#from dependencies import predictor 
from modules import spelling
import json





router = APIRouter(
    tags=["Teacher Management"],
    responses={404: {"description": "Not found"}}
)

'''
Get Free Qualified Teacher
'''
def get_list_teacher_status(db: Session):
    db_list_teacher_status = db.query(models.TeacherStatus).all()
    list_teacher_status = []
    for db_teacher_status in db_list_teacher_status:
        list_teacher_status.append(convert_db_to_schemas(db_teacher_status))
    return list_teacher_status

def get_free_qualified_teacher(db: Session, level_id: int ):
    db_list_teacher_status = db.query(models.TeacherStatus).all()
    db_free_teacher = [db_teacher for db_teacher in db_list_teacher_status if (db_teacher.active_essays < global_var.maximum_essays and db_teacher.level_id == level_id)]
    if db_free_teacher is None:
        return 0
    return len(db_free_teacher)

def change_total(level_id:int, increase=False):
    if level_id == 0:
        if increase:
            global_var.total_level0 += 1
        else:
            global_var.total_level0 -= 1
    else:
        if increase:
            global_var.total_level1 += 1
        else:
            global_var.total_level1 -= 1
    
def update_last_active(db: Session, db_teacher_status: models.TeacherStatus):
    current_time = datetime.today()
    try:
        db_teacher_status.lastTimeActive = current_time
        db.commit()
        db.refresh(db_teacher_status)
        return db_teacher_status, convert_db_to_schemas(db_teacher_status)
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
    
    
def if_any_teacher_left(level_id: int):
    if level_id == 0:
        print("Total Level 0 " + str(global_var.total_level0))
        if  global_var.total_level0 > 0:
            return True 
        else:
            return False 
    if level_id == 1:
        print("Total Level 1 " + str(global_var.total_level1))
        if global_var.total_level1 > 0:
            return True 
        else:
            return False 
    
    
def change_current_scoring_essay(db: Session, db_teacher_status: models.TeacherStatus, increase=True):
    try:
        if increase:
            if db_teacher_status.active_essays == global_var.maximum_essays:
                raise HTTPException(status_code=405, detail="The teacher has reached maximum essays")
            if db_teacher_status.active_essays == global_var.maximum_essays-1:
                change_total(db_teacher_status.level_id)
            db_teacher_status.active_essays += 1
        else:
            if db_teacher_status.active_essays == 0:
                raise HTTPException(status_code=405)
            if db_teacher_status.active_essays == global_var.maximum_essays:
                change_total(db_teacher_status.level_id, increase=True)
            db_teacher_status.active_essays -= 1
        db.commit()
        db.refresh(db_teacher_status)
        update_last_active(db, db_teacher_status)
        return db_teacher_status, convert_db_to_schemas(db_teacher_status)
    except:
        raise HTTPException(status_code=500, detail="Can not change teacher current active essay.")
    
def if_max_essays(db_teacher_status: models.TeacherStatus):
    try:
        if db_teacher_status.active_essays == global_var.maximum_essays:
            return True
        else:
            return False 
    except:
        raise HTTPException(status_code=500, detail="Can not read the teacher's current active essay")

async def create_teacher_status(db: Session, teacher_id:int, level_id:int = 0):
    db_teacher_status = db.query(models.TeacherStatus).filter(models.TeacherStatus.teacher_id == teacher_id).first()
    if not db_teacher_status:
        db_teacher_status = models.TeacherStatus(
            teacher_id = teacher_id,
            level_id = level_id,
            active_essays = 0
        ) 
        db.add(db_teacher_status)
        db.commit()
        db.refresh(db_teacher_status)
        update_last_active(db, db_teacher_status)
        return db_teacher_status, convert_db_to_schemas(db_teacher_status)
    
    else:
        raise HTTPException(status_code=409, detail="teacher status has already existed")
    
def convert_db_to_schemas(db_teacher_status: models.TeacherStatus):
    return  schemas.TeacherStatus(
            teacher_id = db_teacher_status.teacher_id, 
            level_id = db_teacher_status.level_id,
            active_essays = db_teacher_status.active_essays,
            lastTimeActive = db_teacher_status.lastTimeActive
        )
    


@router.get("/teacher_status")
async def get_teacher_status(db: Session = Depends(get_db)):
    list_teacher_status = get_list_teacher_status(db)
    return list_teacher_status


@router.get("/teacher_status/me")
async def get_current_teacher_status(current_account: schemas.Account = Depends(get_current_account),
                                     db: Session = Depends(get_db)):
    
    if current_account.role_id != 2: 
        raise HTTPException(status_code=403)
    db_teacher_status = db.query(models.TeacherStatus).filter(models.TeacherStatus.teacher_id == current_account.user_id).first()
    if not db_teacher_status:
        db_teacher_status= await create_teacher_status(db, current_account.user_id, level_id=0)
    teacher_status = convert_db_to_schemas(db_teacher_status)
    update_last_active(db, db_teacher_status)
    return teacher_status

@router.get("/teacher_status/isanyfree")
async def check_if_any_teacher_free(level_id: int, db: Session = Depends(get_db), ):
    if level_id not in [0,1]:
        raise HTTPException(status_code=404)
    return {
        "isAnyFree": if_any_teacher_left(level_id=0)}    