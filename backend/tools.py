"""
Tools for the InsightFlow agent
Each tool is a function the agent can call
"""

from tavily import TavilyClient
import os
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import time

load_dotenv()

# Initialize Tavily client
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))



def search_academic(query: str, min_citations: int = 0, open_access: bool = False, year_start: int = 2020, logs: list = None) -> list[dict]:
    """
    Search for academic papers using Semantic Scholar API
    """
    try:
        print(f"🎓 Academic Search: {query} (Citations > {min_citations}, OpenAccess={open_access})")
        
        url = "https://api.semanticscholar.org/graph/v1/paper/search"
        params = {
            "query": query,
            "limit": 5,
            "fields": "title,url,abstract,year,citationCount,isOpenAccess,venue",
            "year": f"{year_start}-"
        }
        
        if open_access:
            params["openAccessPdf"] = "" # Filters for papers with public PDFs
            
        if logs is not None:
             logs.append(f"GET https://api.semanticscholar.org/graph/v1/paper/search?query={query}&year={year_start}-")
            
        # Be a good citizen
        headers = {'User-Agent': 'InsightFlow/1.0 (Educational Research Agent)'}
        
        # Retry logic for Rate Limiting
        for attempt in range(3):
            time.sleep(2.0 * (attempt + 1))  # Backoff: 2s, 4s, 6s
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                if logs is not None: logs.append(f"<- 200 OK")
                break
            elif response.status_code == 429:
                if logs is not None: logs.append(f"<- 429 Too Many Requests. Retrying in {2.0 * (attempt + 1)}s...")
                print(f"⚠️ Rate limit hit (Attempt {attempt+1}/3). Sleeping...")
                time.sleep(5)
                continue
            else:
                print(f"❌ Semantic Scholar Error: {response.text}")
                return []
        
        if response.status_code != 200:
             return []
            
        data = response.json()
        results = []
        
        for item in data.get('data', []):
            citation_count = item.get('citationCount', 0)
            
            # Client-side filtering for min citations (API doesn't always support it nicely)
            if citation_count < min_citations:
                continue
                
            results.append({
                'title': f"{item.get('title')} ({item.get('year')})",
                'url': item.get('url') or f"https://www.semanticscholar.org/paper/{item.get('paperId')}",
                'content': f"Abstract: {item.get('abstract')}\nCitations: {citation_count}\nVenue: {item.get('venue')}",
                'score': citation_count  # Use citations as score
            })
            
        print(f"✓ Found {len(results)} papers")
        return results
        
    except Exception as e:
        print(f"❌ Academic Search failed: {e}")
        return []


def search_web(query: str, max_results: int = 5, logs: list = None) -> list[dict]:
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
        if logs is not None: logs.append(f"POST https://api.tavily.com/search (query='{query}')")
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


def search_multiple_queries(queries: list[str], logs: list = None) -> dict[str, list[dict]]:
    """
    Search multiple queries and return results organized by query
    
    Args:
        queries: List of search query strings
        
    Returns:
        Dict mapping query to its results
    """
    results = {}
    results = {}
    for query in queries:
        results[query] = search_web(query, max_results=3, logs=logs)
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


def scrape_url(url: str, logs: list = None) -> str:
    """
    Scrape text content from a URL
    
    Args:
        url: URL to scrape
        
    Returns:
        Extracted text content
    """
    try:
        print(f"📖 Scraping: {url}")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        if logs is not None: logs.append(f"GET {url}")
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if logs is not None: logs.append(f"<- {response.status_code} {response.reason}")
        
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
            
        # Get text
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        # Truncate to avoid token limits (approx 10k chars)
        return text[:10000]
        
    except Exception as e:
        print(f"❌ Scraping failed for {url}: {e}")
        return ""