from typing import Optional
from fastapi import FastAPI 

app = FastAPI()

@app.get("/")
async def read_root():
    return {"Hello": "This is the root of api"}


