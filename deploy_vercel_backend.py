#!/usr/bin/env python3
"""
Script pour créer un backend enrichi déployable
"""

import os
import json

# Créer la structure pour déploiement Vercel/Netlify
backend_files = {
    "requirements.txt": """
fastapi==0.104.1
uvicorn==0.24.0
httpx==0.25.2
pydantic==2.5.0
python-dotenv==1.0.0
emergentintegrations==1.0.0
python-multipart==0.0.6
""",
    
    "vercel.json": """{
  "functions": {
    "api/index.py": {
      "runtime": "python3.9"
    }
  },
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "/api/index.py"
    }
  ]
}""",

    "api/index.py": """
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
"""
}

print("📦 Création des fichiers de déploiement...")
for filename, content in backend_files.items():
    os.makedirs(os.path.dirname(f"/app/{filename}") if "/" in filename else "/app", exist_ok=True)
    with open(f"/app/{filename}", "w") as f:
        f.write(content.strip())
    print(f"✅ {filename}")

print("🚀 Fichiers prêts pour déploiement!")