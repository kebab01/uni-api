from http.client import HTTPException
from fastapi import FastAPI, Path, Header, HTTPException
from pydantic import BaseModel
from typing import Optional
import calendarEvents
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI()

AUTH_TOKEN = os.getenv('AUTH_TOKEN')

@app.get("/")
async def root(Authorization: Optional[str] = Header(None)):

    if Authorization != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Not authenticated" )
    
    return {}

@app.get('/events')
async def getEvents(Authorization: Optional[str] = Header(None)):
    
    if Authorization != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Not authenticated" )
    
    r = calendarEvents.get_all()
    return r

@app.get('/events/{subject_code}')
async def getEvents(subject_code:str, Authorization: Optional[str] = Header(None)):
    
    if Authorization != AUTH_TOKEN:
        raise HTTPException(status_code=403, detail="Not authenticated" )

    r = calendarEvents.get_subject(subject_code)
    return r