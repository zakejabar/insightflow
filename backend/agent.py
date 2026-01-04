from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Dict
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from tools import search_web, search_multiple_queries

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
    """State that flows through the agent"""
    query: str                      # Original user query
    research_plan: List[str]        # Sub-questions to research
    search_results: Dict[str, List[Dict]]  # Results organized by sub-question
    key_findings: List[str]         # Extracted insights
    report: str                     # Final report
    current_step: str               # For progress tracking


def plan_research(state: AgentState) -> AgentState:
    """
    Agent 1: Research Planner
    Breaks down complex query into specific sub-questions
    """
    print("\n🎯 AGENT 1: Planning research...")
    
    prompt = f"""You are a research planner. Your job is to break down complex queries into specific, searchable sub-questions.

User Query: "{state['query']}"

Break this into 3-5 specific sub-questions that would help answer the query comprehensively. Each sub-question should be:
1. Specific and searchable (good for web search)
2. Focused on one aspect
3. Answerable with factual information

Return ONLY a Python list of strings (no explanation, no markdown):
["specific question 1", "specific question 2", "specific question 3"]

Example:
Query: "Compare React vs Vue for enterprise"
Output: ["React enterprise adoption statistics 2024", "Vue.js enterprise use cases", "React vs Vue performance benchmarks", "Enterprise support for React vs Vue"]
"""

    response = llm.invoke(prompt)
    
    # Parse response (expecting a list)
    try:
        # Try to extract list from response
        content = response.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('python'):
                content = content[6:]
            content = content.strip()
        
        # Evaluate as Python list
        research_plan = eval(content)
        
        if not isinstance(research_plan, list):
            raise ValueError("Not a list")
            
    except Exception as e:
        print(f"⚠️ Failed to parse research plan: {e}")
        # Fallback: use original query
        research_plan = [state['query']]
    
    print(f"✓ Created research plan with {len(research_plan)} sub-questions:")
    for i, q in enumerate(research_plan, 1):
        print(f"  {i}. {q}")
    
    return {
        **state,
        "research_plan": research_plan,
        "current_step": "Research plan created"
    }


def gather_information(state: AgentState) -> AgentState:
    """
    Agent 2: Information Gatherer
    Searches the web for each sub-question
    """
    print("\n🔍 AGENT 2: Gathering information...")
    
    # Search for each sub-question
    search_results = search_multiple_queries(state['research_plan'])
    
    # Count total results
    total_results = sum(len(results) for results in search_results.values())
    print(f"✓ Gathered {total_results} sources across {len(search_results)} queries")
    
    return {
        **state,
        "search_results": search_results,
        "current_step": f"Gathered {total_results} sources"
    }


def analyze_information(state: AgentState) -> AgentState:
    """
    Agent 3: Information Analyzer
    Extracts key insights from search results
    """
    print("\n🧠 AGENT 3: Analyzing information...")
    
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
            "key_findings": ["No information found."],
            "current_step": "Analysis complete (no data)"
        }
    
    # Create prompt with all sources
    sources_text = "\n\n".join([
        f"Query: {s['query']}\nTitle: {s['title']}\nURL: {s['url']}\nContent: {s['content'][:500]}..."
        for s in all_sources[:10]  # Limit to top 10 sources to save tokens
    ])
    
    prompt = f"""You are analyzing search results to answer: "{state['query']}"

Search Results:
{sources_text}

Extract 5-7 key findings that directly answer the query. Each finding should:
1. Be specific (include numbers, dates, facts)
2. Cite the source (mention the title)
3. Be relevant to the original query

Format as a Python list of strings:
["Finding 1 (Source: Title)", "Finding 2 (Source: Title)", ...]

Focus on the MOST important and relevant information."""

    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Parse list
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('python'):
                content = content[6:]
            content = content.strip()
        
        key_findings = eval(content)
        
        if not isinstance(key_findings, list):
            raise ValueError("Not a list")
            
    except Exception as e:
        print(f"⚠️ Failed to parse findings: {e}")
        # Fallback: summarize manually
        key_findings = [
            f"Found {len(all_sources)} relevant sources",
            f"Research covered: {', '.join(state['research_plan'][:3])}"
        ]
    
    print(f"✓ Extracted {len(key_findings)} key findings")
    
    return {
        **state,
        "key_findings": key_findings,
        "current_step": "Analysis complete"
    }


def generate_report(state: AgentState) -> AgentState:
    """
    Agent 4: Report Generator
    Creates comprehensive report from findings
    """
    print("\n✍️ AGENT 4: Generating report...")
    
    # Prepare all sources for citation
    all_sources = []
    for query, results in state['search_results'].items():
        all_sources.extend(results)
    
    sources_list = "\n".join([
        f"{i+1}. {s['title']} - {s['url']}"
        for i, s in enumerate(all_sources[:15])  # Top 15 sources
    ])
    
    findings_text = "\n".join([
        f"• {finding}"
        for finding in state['key_findings']
    ])
    
    prompt = f"""You are writing a comprehensive research report.

Original Query: "{state['query']}"

Key Findings:
{findings_text}

Sources:
{sources_list}

Create a well-structured research report with these sections:

# Executive Summary
[2-3 sentence overview of main findings]

# Key Findings
[Detailed explanation of each key finding with specific data]

# Analysis
[Deeper analysis, patterns, implications]

# Conclusion
[Summary and main takeaways]

# Sources
[List all sources used]

Guidelines:
- Be specific (include numbers, percentages, dates)
- Cite sources naturally in text
- Write in clear, professional language
- Focus on answering the original query
- Keep total length around 500-800 words

Write the report now:"""

    response = llm.invoke(prompt)
    report = response.content
    
    print(f"✓ Report generated ({len(report)} characters)")
    
    return {
        **state,
        "report": report,
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
    workflow.set_entry_point("plan")
    workflow.add_edge("plan", "gather")
    workflow.add_edge("gather", "analyze")
    workflow.add_edge("analyze", "report")
    workflow.add_edge("report", END)
    
    return workflow.compile()


# Main function to run the agent
async def run_agent(query: str) -> dict:
    """
    Run the complete research workflow
    
    Args:
        query: User's research query
        
    Returns:
        Dict with report, sources, findings
    """
    print(f"\n{'='*60}")
    print(f"🚀 Starting research for: {query}")
    print(f"{'='*60}")
    
    agent = create_workflow()
    
    initial_state = {
        "query": query,
        "research_plan": [],
        "search_results": {},
        "key_findings": [],
        "report": "",
        "current_step": "Starting"
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