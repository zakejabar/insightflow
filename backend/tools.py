"""
Tools for the InsightFlow agent
Each tool is a function the agent can call
"""

from tavily import TavilyClient
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize Tavily client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using Tavily
    
    Args:
        query: Search query string
        max_results: Max number of results to return
        
    Returns:
        List of search results with title, url, content
    """
    try:
        print(f"🔍 Searching web for: {query}")
        
        # Call Tavily API
        response = tavily_client.search(
            query=query,
            max_results=max_results,
            search_depth="basic",  # "basic" or "advanced"
            include_answer=False,   # We'll generate our own answer
            include_raw_content=False  # Don't need full HTML
        )
        
        # Extract results
        results = []
        for item in response.get('results', []):
            results.append({
                'title': item.get('title', 'No title'),
                'url': item.get('url', ''),
                'content': item.get('content', '')[:1000],  # First 1000 chars
                'score': item.get('score', 0)  # Relevance score
            })
        
        print(f"✓ Found {len(results)} results")
        return results
        
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return []


def search_multiple_queries(queries: list[str]) -> dict[str, list[dict]]:
    """
    Search multiple queries and return results organized by query
    
    Args:
        queries: List of search query strings
        
    Returns:
        Dict mapping query to its results
    """
    results = {}
    for query in queries:
        results[query] = search_web(query, max_results=3)
    return results


def summarize_sources(sources: list[dict], query: str, llm) -> str:
    """
    Use LLM to summarize search results
    
    Args:
        sources: List of search results
        query: Original query for context
        llm: Language model to use
        
    Returns:
        Summary text
    """
    if not sources:
        return "No sources found."
    
    # Combine all source content
    combined_content = "\n\n".join([
        f"Source: {s['title']}\nURL: {s['url']}\nContent: {s['content']}"
        for s in sources
    ])
    
    prompt = f"""Based on these search results, provide a comprehensive summary addressing: "{query}"

Search Results:
{combined_content}

Provide a clear, factual summary with specific details from the sources. Include numbers, dates, and key facts."""

    response = llm.invoke(prompt)
    return response.content