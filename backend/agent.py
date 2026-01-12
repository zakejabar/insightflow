from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from tools import search_web, search_multiple_queries, scrape_url, search_academic
from pydantic import BaseModel, Field

load_dotenv()

# OpenRouter setup
llm = ChatOpenAI(
    model="moonshotai/kimi-k2-instruct-0905",  # or "meta-llama/llama-3.1-70b-instruct"
    openai_api_key=os.getenv("GROQ_API_KEY"),
    openai_api_base="https://api.groq.com/openai/v1",
    temperature=0.7,
    max_tokens=4000
)

# --- Pydantic Models for Structured Output ---

class ResearchPlan(BaseModel):
    items: List[str] = Field(
        description="List of 3-5 specific, actionable search queries. Each query should be focused on retrieving factual information.",
        min_items=3, 
        max_items=5
    )

class KeyFinding(BaseModel):
    topic: str = Field(description="The main topic this finding addresses")
    details: str = Field(description="Specific facts, numbers, or details found")
    source_title: str = Field(description="Title of the source")
    source_url: str = Field(description="URL of the source")

class ResearchInsights(BaseModel):
    findings: List[KeyFinding] = Field(description="List of key findings extracted from search results")
    further_research_needed: bool = Field(description="True if the current findings are insufficient to answer the query comprehensively", default=False)
    missing_information: List[str] = Field(description="List of specific questions that still need to be answered", default_factory=list)

# ----------------------------------------------


class AgentState(TypedDict):
    """State that flows through the agent"""
    query: str                      # Original user query
    research_plan: List[str]        # Sub-questions to research
    search_results: Dict[str, List[Dict]]  # Results organized by sub-question
    key_findings: List[KeyFinding]  # Extracted insights (structured)
    report: str                     # Final report
    current_step: str               # For progress tracking
    logs: List[str]                 # Stream of thought logs
    loop_count: int                 # To prevent infinite loops
    
    # --- Phase 3: Academic Filters ---
    search_mode: str                # 'web' or 'academic'
    min_citations: int              # Filter for academic papers
    open_access: bool               # Filter for open access



def plan_research(state: AgentState) -> AgentState:
    """
    Agent 1: Research Planner
    Breaks down complex query into specific sub-questions
    """
    print("\n🎯 AGENT 1: Planning research...")
    
    # Initialize logs if not present
    logs = state.get('logs', [])
    logs.append(f"🤖 Planner: Analyzing query '{state['query']}'...")
    
    # Use structured output to guarantee a list of strings
    planner = llm.with_structured_output(ResearchPlan)
    
    mode = state.get('search_mode', 'web')
    
    if mode == 'academic':
        # --- Academic Prompt (Keywords) ---
        prompt = f"""You are an expert academic research planner.
User Query: "{state['query']}"

Your goal is to generate 3-5 specific **keyword-based search queries** for the Semantic Scholar API.
Academic search engines require precise keywords, NOT natural language questions.

Rules:
1. Remove "stop words" (what is, how to, etc.).
2. Focus on concepts and terminology.
3. Keep queries under 6-8 words.

Example:
Query: "How does AI impact student grades?"
Output: ["AI impact student academic performance", "artificial intelligence grade point average higher education", "machine learning student learning outcomes"]

Generate the plan."""
    else:
        # --- Web Prompt (Questions) ---
        prompt = f"""You are a research planner. Your job is to break down complex queries into specific, searchable sub-questions.

User Query: "{state['query']}"

Break this into 3-5 specific sub-questions that would help answer the query comprehensively. Each sub-question should be:
1. Specific and searchable (good for web search)
2. Focused on one aspect
3. Answerable with factual information

Example:
Query: "Compare React vs Vue for enterprise"
Output: ["React enterprise adoption statistics 2024", "Vue.js enterprise use cases", "React vs Vue performance benchmarks", "Enterprise support for React vs Vue"]
"""

    try:
        plan_result = planner.invoke(prompt)
        research_plan = plan_result.items
    except Exception as e:
        print(f"⚠️ Failed to generate plan gracefully: {e}")
        # Fallback
        research_plan = [
            f"{state['query']} overview",
            f"{state['query']} statistics",
            f"{state['query']} latest news"
        ]
    
    print(f"✓ Created research plan with {len(research_plan)} sub-questions:")
    for i, q in enumerate(research_plan, 1):
        print(f"  {i}. {q}")
    
    return {
        **state,
        "research_plan": research_plan,
        "current_step": "Research plan created",
        "logs": logs + [f"📋 Plan created with {len(research_plan)} steps."]
    }


def gather_information(state: AgentState) -> AgentState:
    """
    Agent 2: Information Gatherer
    Searches the web AND scrapes deep content for top results
    """
    print("\n🔍 AGENT 2: Gathering information...")
    logs = state.get('logs', [])
    logs.append("🕵️‍♀️ Gatherer: Starting information retrieval...")
    
    # 1. Choose Search Strategy
    mode = state.get('search_mode', 'web')
    print(f"  🚦 Search Mode: {mode}")
    
    research_plan = state['research_plan']
    search_results = {}
    
    if mode == 'academic':
        # --- Academic Mode (Semantic Scholar) ---
        print("  🎓 Running Academic Search...")
        logs.append(f"🎓 Mode: Academic. Querying Semantic Scholar...")
        for query in research_plan:
            logs.append(f"🔎 Citing: {query}...")
            results = search_academic(
                query, 
                min_citations=state.get('min_citations', 0),
                open_access=state.get('open_access', False),
                logs=logs
            )
            if results:
                search_results[query] = results
                
    else:
        # --- Web Mode (Tavily) ---
        logs.append(f"🌍 Mode: Web. Searching Tavily...")
        search_results = search_multiple_queries(research_plan, logs=logs)
        
        # 2. Deep Scrape (Top 1 result per query) - ONLY for Web Mode (Academic abstracts are usually enough)
        print("  📖 Deep scraping top results...")
        for query, results in search_results.items():
            if results:
                top_result = results[0]  # Take the best one
                print(f"  - Scraping: {top_result['title']}")
                content = scrape_url(top_result['url'], logs=logs)
                if content:
                    top_result['content'] = f"[FULL CONTENT] {content}"
                else:
                    top_result['content'] = f"[Snippey] {top_result['content']}"
    
    # Count total results
    total_results = sum(len(results) for results in search_results.values())
    print(f"✓ Gathered {total_results} sources across {len(search_results)} queries")
    
    return {
        **state,
        "search_results": search_results,
        "current_step": f"Gathered {total_results} sources",
        "logs": logs + [f"✅ Found {total_results} sources."]
    }


def analyze_information(state: AgentState) -> AgentState:
    """
    Agent 3: Information Analyzer
    Extracts key insights from search results
    """
    print("\n🧠 AGENT 3: Analyzing information...")
    logs = state.get('logs', [])
    logs.append("🧠 Analyst: Reading and extracting insights...")
    
    # Combine all search results
    all_sources = []
    for query, results in state['search_results'].items():
        for result in results:
            all_sources.append({
                'query': query,
                'title': result['title'],
                'url': result['url'],
                'content': result['content']
            })
    
    if not all_sources:
        return {
            **state,
            "key_findings": [
                KeyFinding(
                    topic="No Info", 
                    details="No relevant sources found to analyze.", 
                    source_title="System", 
                    source_url="#"
                )
            ],
            "current_step": "Analysis complete (no data)"
        }
    
    # Create prompt with all sources
    sources_text = "\n\n".join([
        f"Query: {s['query']}\nTitle: {s['title']}\nURL: {s['url']}\nContent: {s['content'][:500]}..."
        for s in all_sources[:10]  # Limit to top 10 sources to save tokens
    ])
    
    # Use structured output
    analyzer = llm.with_structured_output(ResearchInsights)
    
    prompt = f"""You are analyzing search results to answer: "{state['query']}"
    
    Search Results:
    {sources_text}
    
    Current Loop Count: {state.get('loop_count', 0)} (Max 3)
    Search Mode: {state.get('search_mode', 'web')}
    
    Analyze the results. 
    1. Extract key findings.
    2. CRITICAL: If the results are insufficient or unclear, set 'further_research_needed' to True.
    3. If requesting more info:
       - Mode 'web': Generate specific QUESTIONS.
       - Mode 'academic': Generate specific KEYWORDS (3-5 words max).
    4. If you have enough info, or if Loop Count is >= 3, set 'further_research_needed' to False.
    """

    try:
        result = analyzer.invoke(prompt)
        key_findings = result.findings
        
        # Handle looping
        if result.further_research_needed and state.get('loop_count', 0) < 3:
            print(f"🤔 Analyzer requests more research: {result.missing_information}")
            # Update plan with new questions
            return {
                **state,
                "key_findings": key_findings,
                "research_plan": result.missing_information,  # New questions
                "loop_count": state.get("loop_count", 0) + 1,
                "current_step": "Looping back for more info"
            }
        else:
            return {
                **state,
                "key_findings": key_findings,
                "loop_count": state.get("loop_count", 0),  # Keep same
                "current_step": "Analysis complete",
                "logs": logs + [f"💡 Analysis complete. Found {len(key_findings)} insights."]
            }
            
    except Exception as e:
        print(f"⚠️ Failed to analyze using structured output: {e}")
        # Fallback
        key_findings = [
            KeyFinding(
                topic="Analysis Error", 
                details=f"Could not analyze results due to error: {str(e)}", 
                source_title="System", 
                source_url="#"
            )
        ]
    
    print(f"✓ Extracted {len(key_findings)} key findings")
    
    return {
        **state,
        "key_findings": key_findings,
        "current_step": "Analysis complete"
    }


def should_continue(state: AgentState) -> str:
    """
    Decide whether to loop back or continue to report
    """
    if state['current_step'] == "Looping back for more info":
        return "gather"
    return "report"


def generate_report(state: AgentState) -> AgentState:
    """
    Agent 4: Report Generator
    Creates comprehensive report from findings
    """
    print("\n✍️ AGENT 4: Generating report...")
    logs = state.get('logs', [])
    logs.append("✍️ Writer: Compiling final report...")
    
    # Prepare all sources for citation
    all_sources = []
    for query, results in state['search_results'].items():
        all_sources.extend(results)
    
    sources_list = "\n".join([
        f"{i+1}. {s['title']} - {s['url']}"
        for i, s in enumerate(all_sources[:15])  # Top 15 sources
    ])
    
    findings_text = "\n".join([
        f"• {f.topic}: {f.details} (Source: {f.source_title})"
        for f in state['key_findings']
    ])
    
    prompt = f"""You are an academic research assistant. 
    Query: "{state['query']}"
    
    Here are the key findings from the research:
    {findings_text}
    
    Write a comprehensive research report.
    Structure:
    1. Executive Summary
    2. Key Findings (Cite sources using [Title])
    3. Analysis
    4. Conclusion
    
    CRITICAL RULES:
    - ONLY use the information provided in the findings above.
    - Do NOT hallucinate papers or citations that are not listed above.
    - If there is no information on a specific aspect, state "No direct evidence found".
    - Do NOT make up a "Sources" list at the end. The system will handle that.

    Guidelines:
    - Be specific (include numbers, percentages, dates)
    - Cite sources naturally in text
    - Write in clear, professional language
    - Keep total length around 500-800 words
    - Use Markdown formatting (# for headings, ** for bold, - for lists, etc.)
    - DO NOT wrap the entire report in a code block (no ``` at the beginning or end)
    Write ONLY the report content, starting directly with # Executive Summary:"""

    response = llm.invoke(prompt)
    raw_report = response.content.strip()
    
    # Extra safety: strip any outer code blocks if the model ignores instructions
    if raw_report.startswith('```'):
        lines = raw_report.split('\n')
        # Skip the opening ```
        lines = lines[1:]
        # Remove closing ``` if present
        if lines and lines[-1].strip() == '```':
            lines = lines[:-1]
        # If it specified ```markdown or ```python, skip that line too
        if lines and lines[0].strip().startswith('markdown') or lines[0].strip().startswith('python'):
            lines = lines[1:]
        raw_report = '\n'.join(lines).strip()
    
    print(f"✓ Report generated ({len(raw_report)} characters)")
    return {
        **state,
        "report": raw_report,
        "current_step": "Report complete"
    }


# Build the workflow
def create_workflow():
    """Create the LangGraph workflow"""
    workflow = StateGraph(AgentState)
    
    # Add nodes (agents)
    workflow.add_node("plan", plan_research)
    workflow.add_node("gather", gather_information)
    workflow.add_node("analyze", analyze_information)
    workflow.add_node("report", generate_report)
    
    # Define edges (flow)
    # Define edges (flow)
    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "gather")
    workflow.add_edge("gather", "analyze")
    
    # Conditional edge
    workflow.add_conditional_edges(
        "analyze", 
        should_continue,
        {
            "gather": "gather",
            "report": "report"
        }
    )
    
    workflow.add_edge("report", END)
    
    return workflow.compile()


# Main function to run the agent
async def run_agent(query: str, search_mode: str = "web", min_citations: int = 0, open_access: bool = False) -> dict:
    """
    Run the complete research workflow
    """
    print(f"\n{'='*60}")
    print(f"🚀 Starting research for: {query} [Mode: {search_mode}]")
    print(f"{'='*60}")
    
    agent = create_workflow()
    
    initial_state = {
        "query": query,
        "research_plan": [],
        "search_results": {},
        "key_findings": [],
        "report": "",
        "current_step": "Starting",
        "logs": ["🚀 System initialized."],
        "loop_count": 0,
        "search_mode": search_mode,
        "min_citations": min_citations,
        "open_access": open_access
    }
    
    # Run the workflow
    result = await agent.ainvoke(initial_state)
    
    # Prepare sources for frontend
    all_sources = []
    for query_text, results in result['search_results'].items():
        all_sources.extend(results)
    
    print(f"\n{'='*60}")
    print(f"✅ Research complete!")
    print(f"{'='*60}\n")
    
    return {
        "query": query,
        "report": result['report'],
        "sources": all_sources[:10],  # Top 10 sources
        "insights": result['key_findings']
    }