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
    search_mode: str = "web"  # 'web' or 'academic'
    min_citations: int = 0
    open_access: bool = False

class StatusResponse(BaseModel):
    job_id: str
    status: str  # 'processing', 'completed', 'error'
    progress: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    result: Optional[dict] = None
    error: Optional[str] = None
    current_step: Optional[str] = None
    logs: Optional[list[str]] = []

@app.post("/api/research")
async def create_research(request: ResearchRequest):
    """Start a new research job"""
    job_id = str(uuid.uuid4())
    
    research_jobs[job_id] = {
        "status": "processing",
        "query": request.query,
        "mode": request.search_mode,
        "progress": "Initializing agent...",
        "current_step": "Planning",
        "logs": ["🚀 System initialized."],
        "result": None,
        "error": None
    }
    
    # Start agent in background
    asyncio.create_task(run_research_agent(
        job_id, 
        request.query, 
        request.search_mode, 
        request.min_citations, 
        request.open_access
    ))
    
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

# @app.post("/api/upload")
# async def upload_file(file: UploadFile = File(...)):
#     """Handle PDF uploads"""
#     # TODO: Implement PDF parsing
#     return {"filename": file.filename, "status": "uploaded"}

@app.get("/api/health")
async def health():
    """Health check"""
    return {
        "status": "healthy",
        "openrouter_key_set": bool(os.getenv("OPENROUTER_API_KEY"))
    }

async def run_research_agent(job_id: str, query: str, search_mode: str = "web", min_citations: int = 0, open_access: bool = False):
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
            research_jobs[job_id]["current_step"] = "Planning"
            research_jobs[job_id]["current_step_index"] = 0  # ← ADD THIS
            research_jobs[job_id]["progress"] = "Breaking down your query..."
            result = original_plan(state)
            if "logs" in result: research_jobs[job_id]["logs"] = result["logs"]
            research_jobs[job_id]["progress"] = f"Created {len(result['research_plan'])} research questions"
            return result

        def gather_with_progress(state):
            research_jobs[job_id]["current_step"] = "Gathering"
            research_jobs[job_id]["current_step_index"] = 1  # ← ADD THIS
            research_jobs[job_id]["progress"] = "Searching the web..."
            result = original_gather(state)
            if "logs" in result: research_jobs[job_id]["logs"] = result["logs"]
            total = sum(len(r) for r in result['search_results'].values())
            research_jobs[job_id]["progress"] = f"Found {total} sources"
            return result

        def analyze_with_progress(state):
            research_jobs[job_id]["current_step"] = "Analyzing"
            research_jobs[job_id]["current_step_index"] = 2  # ← ADD THIS
            research_jobs[job_id]["progress"] = "Extracting key insights..."
            result = original_analyze(state)
            if "logs" in result: research_jobs[job_id]["logs"] = result["logs"]
            research_jobs[job_id]["progress"] = f"Extracted {len(result['key_findings'])} findings"
            return result

        def report_with_progress(state):
            research_jobs[job_id]["current_step"] = "Reporting"
            research_jobs[job_id]["current_step_index"] = 3  # ← ADD THIS
            research_jobs[job_id]["progress"] = "Generating report..."
            result = original_report(state)
            if "logs" in result: research_jobs[job_id]["logs"] = result["logs"]
            research_jobs[job_id]["progress"] = "Report complete!"
            return result
        
        # Monkey-patch (temporary override)
        import agent
        agent.plan_research = plan_with_progress
        agent.gather_information = gather_with_progress
        agent.analyze_information = analyze_with_progress
        agent.generate_report = report_with_progress
        
        # Run agent
        result = await run_agent(query, search_mode, min_citations, open_access)
        
        # Restore original functions
        agent.plan_research = original_plan
        agent.gather_information = original_gather
        agent.analyze_information = original_analyze
        agent.generate_report = original_report
        
        # Mark complete
        research_jobs[job_id]["status"] = "completed"
        research_jobs[job_id]["result"] = result
        if "logs" in result: research_jobs[job_id]["logs"] = result["logs"]
        research_jobs[job_id]["progress"] = "Complete!"
        research_jobs[job_id]["current_step"] = "Complete"
        
        print(f"✅ Job {job_id[:8]}... completed successfully")
        
    except Exception as e:
        research_jobs[job_id]["status"] = "error"
        research_jobs[job_id]["error"] = str(e)
        research_jobs[job_id]["current_step"] = "Error"
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