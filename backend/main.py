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
    try:
        from agent import run_agent
        
        # We'll monkey-patch the agent to report progress
        # Import the original functions
        from agent import plan_research, gather_information, analyze_information, generate_report
        
        # Wrap each function to update progress
        original_plan = plan_research
        original_gather = gather_information
        original_analyze = analyze_information
        original_report = generate_report
        
        def plan_with_progress(state):
            research_jobs[job_id]["progress"] = "Planning research strategy..."
            return original_plan(state)
        
        def gather_with_progress(state):
            research_jobs[job_id]["progress"] = "Searching the web for sources..."
            return original_gather(state)
        
        def analyze_with_progress(state):
            research_jobs[job_id]["progress"] = "Analyzing information and extracting insights..."
            return original_analyze(state)
        
        def report_with_progress(state):
            research_jobs[job_id]["progress"] = "Generating comprehensive report..."
            return original_report(state)
        
        # Monkey-patch (temporary override)
        import agent
        agent.plan_research = plan_with_progress
        agent.gather_information = gather_with_progress
        agent.analyze_information = analyze_with_progress
        agent.generate_report = report_with_progress
        
        # Run agent
        result = await run_agent(query)
        
        # Restore original functions
        agent.plan_research = original_plan
        agent.gather_information = original_gather
        agent.analyze_information = original_analyze
        agent.generate_report = original_report
        
        # Mark complete
        research_jobs[job_id]["status"] = "completed"
        research_jobs[job_id]["result"] = result
        research_jobs[job_id]["progress"] = "Complete!"
        
        print(f"✅ Job {job_id[:8]}... completed successfully")
        
    except Exception as e:
        research_jobs[job_id]["status"] = "error"
        research_jobs[job_id]["error"] = str(e)
        print(f"❌ Job {job_id[:8]}... failed: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Add this near the top with other functions
def update_progress(job_id: str, message: str):
    """Update job progress message"""
    if job_id in research_jobs:
        research_jobs[job_id]["progress"] = message
        print(f"📊 Progress update [{job_id[:8]}...]: {message}")       