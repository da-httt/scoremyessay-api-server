
from db import SessionLocal
from sqlalchemy.orm.session import Session
from sqlalchemy.util.langhelpers import dependencies
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from routers import authentication, statistics, user, order, result, nlp, admin, teacher_promo
from routers.teacher_promo import get_free_qualified_teacher
import models
import schemas
from dependencies import engine, get_db
from config import custom_openapi 
from fastapi.responses import HTMLResponse
from fastapi.openapi.utils import get_openapi
import global_var


global_var.init()

models.Base.metadata.create_all(bind=engine)

    

app = FastAPI(
    title="ScoreMyEssay API"
)
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="ScoreMyEssay API",
        version="2.0.0",
        description='''
        University Project - 17N10 - Faculty of Information Technology
        For testing:
        1. admin@scoremyessay.com / admin 
        2. teacher@gmail.com / teacher 
        3. student@gmail.com / student 
        
        ''',
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://i.imgur.com/94xK65e.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(order.router)
app.include_router(result.router)
app.include_router(nlp.router)
app.include_router(statistics.router)
app.include_router(admin.router)
app.include_router(teacher_promo.router)

@app.on_event("startup")
async def startup_event():
    db= SessionLocal()
    global_var.total_level0 = get_free_qualified_teacher(db, level_id=0)
    global_var.total_level1 = get_free_qualified_teacher(db, level_id=1)
    db.close()
    
with open('./template/index.html', 'r') as f:
    html_string = f.read()
    
@app.get("/", response_class=HTMLResponse)
async def root():   
    return html_string

