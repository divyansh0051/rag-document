import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from rag_engine import RAGEngine
from evaluator import BenchmarkEvaluator
from auth import DEMO_USERS, create_access_token, verify_token

app = FastAPI(
    title="ApexPolicy AI - Insurance RAG Assistant API",
    description="Intelligent RAG assistant for insurance policy retrieval with page-level citations & evaluation benchmarks.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Engine
DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
rag_engine = RAGEngine(data_dir=DATA_DIR)
evaluator = BenchmarkEvaluator(rag_engine=rag_engine)

class LoginRequest(BaseModel):
    email: str
    password: str

class QueryRequest(BaseModel):
    query: str
    target_document: Optional[str] = None

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        return {"name": "Guest Analyst", "role": "Visitor", "email": "guest@demo.com"}
    token = authorization.replace("Bearer ", "").strip()
    user = verify_token(token)
    if not user:
        return {"name": "Guest Analyst", "role": "Visitor", "email": "guest@demo.com"}
    return user

@app.get("/")
def root():
    return {
        "service": "ApexPolicy AI RAG Assistant",
        "status": "operational",
        "indexed_documents": len(rag_engine.documents_metadata),
        "total_chunks": len(rag_engine.chunks)
    }

@app.post("/api/auth/login")
def login(creds: LoginRequest):
    email = creds.email.lower().strip()
    if email in DEMO_USERS and DEMO_USERS[email]["password"] == creds.password:
        user_info = DEMO_USERS[email]
        token = create_access_token({"email": email, "name": user_info["name"], "role": user_info["role"]})
        return {
            "token": token,
            "user": {
                "email": email,
                "name": user_info["name"],
                "role": user_info["role"],
                "avatar": user_info["avatar"],
                "policy_number": user_info.get("policy_number", None)
            }
        }
    raise HTTPException(status_code=401, detail="Invalid credentials. Use a demo login or password123.")

@app.get("/api/auth/demo-users")
def get_demo_users():
    return [
        {"email": k, "name": v["name"], "role": v["role"], "avatar": v["avatar"]}
        for k, v in DEMO_USERS.items()
    ]

@app.get("/api/documents")
def list_documents():
    return {
        "documents": rag_engine.documents_metadata,
        "total_chunks": len(rag_engine.chunks)
    }

@app.post("/api/upload")
async def upload_document(file: UploadFile = File(...), user: Dict = Depends(get_current_user)):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    os.makedirs(DATA_DIR, exist_ok=True)
    destination = os.path.join(DATA_DIR, file.filename)
    
    with open(destination, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    res = rag_engine.add_uploaded_pdf(destination, file.filename)
    return res

@app.post("/api/query")
def answer_query(body: QueryRequest, user: Dict = Depends(get_current_user)):
    if not body.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    result = rag_engine.generate_answer(body.query, target_doc=body.target_document)
    return {
        **result,
        "user_role": user.get("role", "Visitor"),
        "timestamp": os.environ.get("CURRENT_TIME", "2026-10-14T15:30:00Z")
    }

@app.get("/api/evaluate")
def run_evaluation_benchmark():
    report = evaluator.evaluate_all()
    return report

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
