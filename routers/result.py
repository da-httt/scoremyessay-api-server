
from dependencies import get_db, get_current_account
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
import schemas 
import models 
from typing import Optional, List
from modules import paragraph

router = APIRouter(
    tags=["Result"],
    responses={404: {"description": "Not found"}},
)



@router.get("/results/{order_id}",
         response_model = schemas.ResultResponse)
async def get_order_result(order_id: int,
                            current_account: schemas.Account = Depends(get_current_account),
                            db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    
    isCriteria = False 
    isExtra = False 
    
    
    #If the order not in Database, return error 
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    #check if the order is paid 
    if db_order.status_id == 0:
        raise HTTPException(status_code=405, detail="Order hasn't been paid yet!")
    
    if db_order.status_id == 1:
        raise HTTPException(status_code=405, detail="The order hasn't been taken by any teacher!")
    
    #Check permission 
    if current_account.role_id != 0 and current_account.user_id not in [db_order.student_id, db_order.teacher_id]:
        raise HTTPException(status_code=403)
    
    if current_account == 1 and db_order.status_id != 3:
        raise HTTPException(status_code=403, detail="The essay has been not graded yet!")
    
    db_result = db.query(models.Result).filter(models.Result.order_id == order_id).first()
    
    db_option_list = db.query(models.Option).order_by(models.Option.option_id).all()
    option_list = [int(item) for item in db_order.option_list.split("-") if db_option_list[int(item)].option_type == 0]
    option_list.sort()
    extra_option_list = [option_id for option_id in option_list if option_id not in [0,1,2]]

    if 3 in option_list:
        isCriteria = True 
    if len(extra_option_list) > 0:
        isExtra = True 

    db_criteria_list = db.query(models.Criteria).all()
    if not db_result:
        db_result = models.Result(
            order_id = order_id,
            isCriteria = isCriteria,
            isExtra = isExtra
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        if isExtra:
            for extra_option_id in extra_option_list:
                db_extra = models.ExtraResult(
                    result_id = db_result.result_id,
                    option_id = extra_option_id
                )
                db.add(db_extra)
                db.commit()
                db.refresh(db_extra)
                
        if isCriteria:
            for db_criteria in db_criteria_list:
                db_result_criteria = models.ResultCriteria(
                    result_id = db_result.result_id, 
                    criteria_id = db_criteria.criteria_id
                )
                db.add(db_result_criteria)
                db.commit()
                db.refresh(db_result_criteria)
    
    
    result_response = schemas.ResultResponse(
        order_status_id = db_order.status_id,
        result_id = db_result.result_id,
        isCriteria = isCriteria,
        isExtra = isExtra,
        grade = db_result.grade,
        grade_comment = db_result.grade_comment,
        review = db_result.review,
        comment = db_result.comment, 
    )
    
    criteria_results = [] 
    extra_results = [] 
    
    if isCriteria:
        for db_criteria_result in db.query(models.ResultCriteria).filter(models.ResultCriteria.result_id == db_result.result_id).all():
            criteria_results.append(schemas.CriteriaResponse(
                result_id = db_result.result_id,
                criteria_id = db_criteria_result.criteria_id,
                criteria_name = db_criteria_result.criteria.criteria_name,
                criteria_comment = db_criteria_result.criteria_comment,
                criteria_score = db_criteria_result.criteria_score
            ))
        print(criteria_results)
        result_response.criteria_results = criteria_results
    
    if isExtra:
        for db_extra in db.query(models.ExtraResult).filter(models.ExtraResult.result_id == db_result.result_id).all():
            extra_results.append(schemas.ExtraResponse(
                result_id = db_result.result_id,
                option_id = db_extra.option_id,
                option_name = db_extra.option.option_name,
                content = db_extra.content
            ))
        print(extra_results)
        result_response.extra_results = extra_results
    
    
    return result_response



@router.put("/results/{order_id}",
         response_model=schemas.ResultResponse)
async def update_result(order_id: int,
                        status_id: Optional[int],
                        new_result: schemas.ResultInDB,
                        current_account: schemas.Account = Depends(get_current_account),
                        db: Session = Depends(get_db)
                        ):
    
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    
    isCriteria = False 
    isExtra = False 
    
    
    #If the order not in Database, return error 
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    #check if the order is paid 
    if db_order.status_id in [0,1]:
        raise HTTPException(status_code=405, detail="Order has been paid yet!")
    
    #Check permission 
    if current_account.role_id != 0 and current_account.user_id not in [db_order.student_id, db_order.teacher_id]:
        raise HTTPException(status_code=403)
    
    db_result = db.query(models.Result).filter(models.Result.order_id == order_id).first()
    
    db_option_list = db.query(models.Option).order_by(models.Option.option_id).all()
    option_list = [int(item) for item in db_order.option_list.split("-") if db_option_list[int(item)].option_type == 0]
    option_list.sort()
    extra_option_list = [option_id for option_id in option_list if option_id not in [0,1,2]]

    if 3 in option_list:
        isCriteria = True 
    if len(extra_option_list) > 0:
        isExtra = True 
    db_criteria_list = db.query(models.Criteria).all()
    if not db_result:
        db_result = models.Result(
            order_id = order_id,
            isCriteria = isCriteria,
            isExtra = isExtra
        )
        db.add(db_result)
        db.commit()
        db.refresh(db_result)
        if isExtra:
            for extra_option_id in extra_option_list:
                db_extra = models.ExtraResult(
                    result_id = db_result.result_id,
                    option_id = extra_option_id
                )
                db.add(db_extra)
                db.commit()
                db.refresh(db_extra)
                
        if isCriteria:
            for db_criteria in db_criteria_list:
                db_result_criteria = models.ResultCriteria(
                    result_id = db_result.result_id, 
                    criteria_id = db_criteria.criteria_id
                )
                db.add(db_result_criteria)
                db.commit()
                db.refresh(db_result_criteria)
                
    db_criteria_result_list = db.query(models.ResultCriteria).filter(models.ResultCriteria.result_id == db_result.result_id).all()
    if len(db_criteria_result_list) != len(new_result.criteria_results):
        raise HTTPException(status_code=400, detail="Not enough criteria input")
    db_extra_result_list = db.query(models.ExtraResult).filter(models.ExtraResult.result_id == db_result.result_id).all()
    if len(db_extra_result_list) != len(new_result.extra_results):
        raise HTTPException(status_code=400, detail="Not enough extra input")

    db_result.grade = new_result.grade 
    db_result.grade_comment = new_result.grade_comment
    db_result.review = new_result.review 
    db_result.comment = new_result.comment
    db.commit()
    db.refresh(db_result)
    
    if status_id and status_id in [3,4]:
        db_order.status_id = status_id
        db.commit()
        db.refresh(db_order)
        
    
    result_response = schemas.ResultResponse(
        order_status_id = db_order.status_id,
        result_id = db_result.result_id,
        isCriteria = isCriteria,
        isExtra = isExtra,
        grade = db_result.grade,
        grade_comment = db_result.grade_comment,
        review = db_result.review,
        comment = db_result.comment, 
    )
    
    criteria_results = [] 
    extra_results = [] 
    
    if isCriteria:
        for index, db_criteria_result in enumerate(db_criteria_result_list):
            db_criteria_result.criteria_comment = new_result.criteria_results[index].criteria_comment
            db_criteria_result.criteria_score = new_result.criteria_results[index].criteria_score
            db.commit()
            db.refresh(db_criteria_result)
            criteria_results.append(schemas.CriteriaResponse(
                result_id = db_result.result_id,
                criteria_id = db_criteria_result.criteria_id,
                criteria_name = db_criteria_result.criteria.criteria_name,
                criteria_comment = db_criteria_result.criteria_comment,
                criteria_score = db_criteria_result.criteria_score
            ))
        result_response.criteria_results = criteria_results
    
    if isExtra:
        for index, db_extra in enumerate(db_extra_result_list):
            db_extra.content = new_result.extra_results[index].content
            db.commit()
            db.refresh(db_extra)
            extra_results.append(schemas.ExtraResponse(
                result_id = db_result.result_id,
                option_id = db_extra.option_id,
                option_name = db_extra.option.option_name,
                content = db_extra.content
            ))
        result_response.extra_results = extra_results
    
    return result_response



@router.get("/essay_comments/{order_id}",
         response_model= schemas.EssayCommentResponse)
async def get_essay_comment(order_id:int,
                            current_account: schemas.Account = Depends(get_current_account),
                            db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    #If the order not in Database, return error 
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    #check if the order is paid 
    if db_order.status_id in [0,1]:
        raise HTTPException(status_code=405, detail="Order has been paid yet!")
    
    #Check permission 
    if current_account.role_id != 0 and current_account.user_id not in [db_order.student_id, db_order.teacher_id]:
        raise HTTPException(status_code=403)
        
    db_essay = db_order.essay 
    
    db_essay_comment_list = db.query(models.EssayComment).filter(models.EssayComment.essay_id == db_essay.essay_id).order_by(models.EssayComment.sentence_index).all()
    essay = db_essay.content.replace("\n"," ")
    sentences = paragraph.paragraph_to_sentences(essay)
    print(sentences)

    if len(db_essay_comment_list) == 0:
        for index, sentence in enumerate(sentences):
            db_essay_comment = models.EssayComment(
                essay_id = db_essay.essay_id,
                sentence_index = index,
            )
            db.add(db_essay_comment)
            db.commit()
            db.refresh(db_essay_comment)
            
    db_essay_comment_list = db.query(models.EssayComment).filter(models.EssayComment.essay_id == db_essay.essay_id).order_by(models.EssayComment.sentence_index).all()
     
    essay_comments = []
    for index, db_essay_comment in enumerate(db_essay_comment_list):
        essay_comments.append(schemas.EssayComment(
            sentence_index = db_essay_comment.sentence_index,
            sentence = sentences[index],
            comment = db_essay_comment.comment
        ))
    
    
    
    essay_comment_response = schemas.EssayCommentResponse(
        essay_id = db_essay.essay_id,
        title = db_essay.title,
        content = db_essay.content,
        type_id = db_essay.type_id,
        essay_comments = essay_comments
    )
    
    return essay_comment_response

    
                            


@router.put("/essay_comments/{order_id}",
         response_model= schemas.EssayCommentResponse)
async def update_essay_comment(order_id:int,
                            new_essay_comment: List[schemas.EssayCommentInDB],
                            current_account: schemas.Account = Depends(get_current_account),
                            db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    #If the order not in Database, return error 
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    #check if the order is paid 
    if db_order.status_id in [0,1]:
        raise HTTPException(status_code=405, detail="Order has been paid yet!")
    
    #Check permission 
    if current_account.role_id != 0 and current_account.user_id not in [db_order.student_id, db_order.teacher_id]:
        raise HTTPException(status_code=403)
        
    db_essay = db_order.essay 
    
    db_essay_comment_list = db.query(models.EssayComment).filter(models.EssayComment.essay_id == db_essay.essay_id).order_by(models.EssayComment.sentence_index).all()
    essay = db_essay.content.replace("\n"," ")
    sentences = paragraph.paragraph_to_sentences(essay)
    print(sentences)

    if len(db_essay_comment_list) == 0:
        for index, sentence in enumerate(sentences):
            db_essay_comment = models.EssayComment(
                essay_id = db_essay.essay_id,
                sentence_index = index,
            )
            db.add(db_essay_comment)
            db.commit()
            db.refresh(db_essay_comment)
    
    db_essay_comment_list = db.query(models.EssayComment).filter(models.EssayComment.essay_id == db_essay.essay_id).order_by(models.EssayComment.sentence_index).all()
    
    
    for index, essay_comment in enumerate(new_essay_comment):
        sentence_index = essay_comment.sentence_index 
        if sentence_index > len(db_essay_comment_list):
            raise HTTPException(status_code=400, detail="Sentence index out of range")
        db_essay_comment = db_essay_comment_list[sentence_index]
        db_essay_comment.comment = essay_comment.comment
        db.commit()
        db.refresh(db_essay_comment)
        
    essay_comments = []
    for index, db_essay_comment in enumerate(db_essay_comment_list):
        essay_comments.append(schemas.EssayComment(
            sentence_index = db_essay_comment.sentence_index,
            sentence = sentences[index],
            comment = db_essay_comment.comment
        ))
    
    essay_comment_response = schemas.EssayCommentResponse(
        essay_id = db_essay.essay_id,
        title = db_essay.title,
        content = db_essay.content,
        type_id = db_essay.type_id,
        essay_comments = essay_comments
    )
    
    return essay_comment_response

    
                            