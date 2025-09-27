from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Import notre backend enrichi
import sys
sys.path.append('..')
from server import *

@app.get("/")
def root():
    return {"message": "Backend enrichi déployé", "status": "ok"}