from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import asyncio
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="InsightFlow API")

# CORS for Next.js
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job storage (will use Redis later)
research_jobs: Dict[str, dict] = {}

class ResearchRequest(BaseModel):
    query: str

class StatusResponse(BaseModel):
    job_id: str
    status: str  # 'processing', 'completed', 'error'
    progress: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None

@app.post("/api/research")
async def create_research(request: ResearchRequest):
    """Start a new research job"""
    job_id = str(uuid.uuid4())
    
    research_jobs[job_id] = {
        "status": "processing",
        "query": request.query,
        "progress": "Initializing agent...",
        "result": None,
        "error": None
    }
    
    # Start agent in background
    asyncio.create_task(run_research_agent(job_id, request.query))
    
    return {"job_id": job_id, "status": "processing"}

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Check job status"""
    if job_id not in research_jobs:
        return {"error": "Job not found"}
    
    return research_jobs[job_id]

@app.get("/api/result/{job_id}")
async def get_result(job_id: str):
    """Get final result"""
    if job_id not in research_jobs:
        return {"error": "Job not found"}
    
    job = research_jobs[job_id]
    if job["status"] != "completed":
        return {"error": "Job not completed yet"}
    
    return job["result"]

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Handle PDF uploads"""
    # TODO: Implement PDF parsing
    return {"filename": file.filename, "status": "uploaded"}

@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "openrouter_key_set": bool(os.getenv("OPENROUTER_API_KEY"))
    }

async def run_research_agent(job_id: str, query: str):
    """Run the LangGraph agent"""
    try:
        # Import agent here to avoid circular imports
        from agent import run_agent
        
        # Update progress
        research_jobs[job_id]["progress"] = "Planning research..."
        
        # Run the agent
        result = await run_agent(query)
        
        # Update with result
        research_jobs[job_id]["status"] = "completed"
        research_jobs[job_id]["result"] = result
        research_jobs[job_id]["progress"] = "Complete!"
        
    except Exception as e:
        research_jobs[job_id]["status"] = "error"
        research_jobs[job_id]["error"] = str(e)
        print(f"Error in research agent: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Add this near the top with other functions
def update_progress(job_id: str, message: str):
    """Update job progress message"""
    if job_id in research_jobs:
        research_jobs[job_id]["progress"] = message
        print(f"📊 Progress update [{job_id[:8]}...]: {message}")       