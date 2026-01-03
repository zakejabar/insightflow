from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# OpenRouter setup
llm = ChatOpenAI(
    model="moonshotai/kimi-k2-instruct-0905",  # or "meta-llama/llama-3.1-70b-instruct"
    openai_api_key=os.getenv("GROQ_API_KEY"),
    openai_api_base="https://api.groq.com/openai/v1",
    temperature=0.7,
    max_tokens=4000
)

class AgentState(TypedDict):
    query: str
    research_plan: List[str]
    sources: List[Dict]
    insights: List[str]
    report: str
    current_step: str

def plan_research(state: AgentState) -> AgentState:
    """Agent 1: Break query into sub-questions"""
    print("🎯 Planning research...")
    
    prompt = f"""You are a research planner. Given this query: "{state['query']}"

Break it down into 3-5 specific sub-questions that would help answer it comprehensively.

Return ONLY a Python list of strings, like:
["question 1", "question 2", "question 3"]

No explanation, just the list."""

    response = llm.invoke(prompt)
    
    # Simple parsing (you can improve this)
    plan = ["Sub-question 1", "Sub-question 2", "Sub-question 3"]  # Placeholder
    
    return {
        **state,
        "research_plan": plan,
        "current_step": "Planning complete"
    }

def gather_sources(state: AgentState) -> AgentState:
    """Agent 2: Search for sources"""
    print("🔍 Gathering sources...")
    
    # For now, mock sources (we'll add real web search later)
    sources = [
        {
            "title": "Source 1",
            "url": "https://example.com",
            "content": "Sample content about the topic..."
        },
        {
            "title": "Source 2",
            "url": "https://example2.com",
            "content": "More information about the research query..."
        }
    ]
    
    return {
        **state,
        "sources": sources,
        "current_step": "Sources gathered"
    }

def analyze_sources(state: AgentState) -> AgentState:
    """Agent 3: Extract insights"""
    print("🧠 Analyzing sources...")
    
    # Combine all source content
    all_content = "\n\n".join([s["content"] for s in state["sources"]])
    
    prompt = f"""Analyze these sources and extract 5 key insights for: "{state['query']}"

Sources:
{all_content}

Return insights as a numbered list."""

    response = llm.invoke(prompt)
    
    insights = response.content.split("\n")
    
    return {
        **state,
        "insights": insights,
        "current_step": "Analysis complete"
    }

def generate_report(state: AgentState) -> AgentState:
    """Agent 4: Create final report"""
    print("✍️ Generating report...")
    
    prompt = f"""Create a comprehensive research report:

Query: {state['query']}

Research Plan:
{state['research_plan']}

Key Insights:
{state['insights']}

Sources:
{[s['title'] for s in state['sources']]}

Generate a well-structured report with:
1. Executive Summary
2. Key Findings (with citations)
3. Detailed Analysis
4. Sources

Use markdown formatting."""

    response = llm.invoke(prompt)
    
    return {
        **state,
        "report": response.content,
        "current_step": "Report complete"
    }

# Build the workflow
def create_workflow():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("plan", plan_research)
    workflow.add_node("gather", gather_sources)
    workflow.add_node("analyze", analyze_sources)
    workflow.add_node("report", generate_report)
    
    # Define flow
    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "gather")
    workflow.add_edge("gather", "analyze")
    workflow.add_edge("analyze", "report")
    workflow.add_edge("report", END)
    
    return workflow.compile()

# Main function to run agent
async def run_agent(query: str) -> dict:
    """Run the research agent"""
    agent = create_workflow()
    
    initial_state = {
        "query": query,
        "research_plan": [],
        "sources": [],
        "insights": [],
        "report": "",
        "current_step": "Starting"
    }
    
    # Run the workflow
    result = await agent.ainvoke(initial_state)
    
    return {
        "query": query,
        "report": result["report"],
        "sources": result["sources"],
        "insights": result["insights"]
    }