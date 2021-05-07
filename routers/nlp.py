
from dependencies import get_db, get_current_account
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
import schemas 
import models 
from typing import Optional, List
#from dependencies import predictor 
from modules import spelling
import json
 
router = APIRouter(
    tags=["AI Model"],
    responses={404: {"description": "Not found"}},
)


@router.post("/predict_topic")
async def predict_essay_topic(paragraph: str):
    return predictor.predict(paragraph)

    
@router.get("/spelling_errors/{order_id}",
            response_model=schemas.EssayInfoResponse)
async def get_spelling_errors_of_essay(order_id:int,
                                       current_account: schemas.Account = Depends(get_current_account),
                                       db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    
    #If the order not in Database, return error 
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    db_essay = db_order.essay
    
    db_essay_info = db.query(models.EssayInfo).filter(models.EssayInfo.essay_id == db_essay.essay_id).first()
    
    if not db_essay_info:
        num_error, spelling_errors = spelling.spellCheck(db_essay.content)
        data = json.dumps(spelling_errors)
        topic_predicted = predictor.predict(db_essay.title)
        db_essay_info = models.EssayInfo(
            essay_id = db_essay.essay_id,
            predicted_topic = topic_predicted,
            num_errors = num_error,
            spelling_errors = data
        )
        db.add(db_essay_info)
        db.commit()
        db.refresh(db_essay_info)
    
    spelling_errors = json.loads(db_essay_info.spelling_errors)
    list_word_errors = []
    for spell_error in spelling_errors:
        list_word_errors.append(
            schemas.WordError(
                index = spell_error['index'],
                word = spell_error['word'],
                suggested_word = spell_error['suggested_word']
            )
        )
    essay_info_response = schemas.EssayInfoResponse(
        essay_info_id = db_essay_info.info_id,
        essay_id = db_essay_info.essay_id,
        predicted_topic = db_essay_info.predicted_topic,
        num_errors = db_essay_info.num_errors,
        spelling_errors = list_word_errors
    )
    
    return essay_info_response