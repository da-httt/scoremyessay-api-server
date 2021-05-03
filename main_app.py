
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from routers import authentication, user, order, result, nlp
import models 
from dependencies import engine 
from config import custom_openapi 

from fastapi.openapi.utils import get_openapi




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
        description="University Project - 17N10 - Faculty of Information Technology",
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

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}