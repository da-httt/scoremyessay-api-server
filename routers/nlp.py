
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
from modules import paragraph
import json
from modules.yake_model.YAKE import YAKE
from nltk.corpus import stopwords

router = APIRouter(
    tags=["AI Model"],
    responses={404: {"description": "Not found"}},
)

window = 2
use_stems = False # use stems instead of words for weighting
stoplist = stopwords.words('english')
threshold = 0.8

"""@router.post("/predict_topic")
async def predict_essay_topic(paragraph: str):
    return {}  # predictor.predict(paragraph)
"""

async def extract_keywords(text):
    extractor = YAKE()
    extractor.load_document(input=text, language='en',normalization=None)
    extractor.candidate_selection(n=1, stoplist=stoplist)
    extractor.candidate_weighting(window=window,
                            stoplist=stoplist,
                            use_stems=use_stems)
    keyphrases = extractor.get_n_best(n=3, threshold=threshold)
    keyphrases = [k[0] for k in keyphrases]
    if keyphrases == []:
        keyphrases = ["keywords","not","found"]
    return keyphrases


@router.post("/extract_keywords")
async def extract_keywords_from_text(paragraph: str):
    return {"keywords list": extract_keywords(paragraph)}  


@router.get("/spelling_errors/{order_id}",
            response_model=schemas.EssayInfoResponse)
async def get_spelling_errors_of_essay(order_id: int,
                                       current_account: schemas.Account = Depends(
                                           get_current_account),
                                       db: Session = Depends(get_db)):
    db_order = db.query(models.Order).filter(
        models.Order.order_id == order_id).first()

    # If the order not in Database, return error
    if not db_order:
        raise HTTPException(status_code=404, detail="Order not found")

    db_essay = db_order.essay

    db_essay_info = db.query(models.EssayInfo).filter(
        models.EssayInfo.essay_id == db_essay.essay_id).first()

    if not db_essay_info:
        num_error, spelling_errors = spelling.spellCheckAdvance(db_essay.content)
        data = json.dumps(spelling_errors)
        keywords = "keyword-from-essay"  # predictor.predict(db_essay.title)
        db_essay_info = models.EssayInfo(
            essay_id=db_essay.essay_id,
            keywords=keywords,
            num_errors=num_error,
            spelling_errors=data
        )
        db.add(db_essay_info)
        db.commit()
        db.refresh(db_essay_info)

    spelling_errors = json.loads(db_essay_info.spelling_errors)
    list_word_errors = []
    for spell_error in spelling_errors:
        list_word_errors.append(
            schemas.WordError(
                index=spell_error['index'],
                word=spell_error['word'],
                sentence=spell_error['sentence'],
                sentence_index=spell_error['sentence_index'],
                suggested_word=spell_error['suggested_word']
            )
        )
    essay_info_response = schemas.EssayInfoResponse(
        essay_info_id=db_essay_info.info_id,
        essay_id=db_essay_info.essay_id,
        keywords=db_essay_info.keywords.split("-"),
        num_errors=db_essay_info.num_errors,
        number_of_sentences=paragraph.getSentenceCount(db_essay.content),
        average_sentence_length=paragraph.getAvgSentenceLength(
            db_essay.content),
        number_of_words=paragraph.getWordCount(db_essay.content),
        spelling_errors=list_word_errors
    )

    return essay_info_response

@router.get("/demo_check")
async def demo_check(input_text: str):
    numMistakes, data = spelling.spellCheckAdvance(input_text)
    return {
        "number of mytakes": numMistakes,
        "corrections": data
    }
    