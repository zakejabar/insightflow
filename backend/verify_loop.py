
import asyncio
import os
from agent import run_agent

async def main():
    # Test query that needs up-to-date info or specifics
    query = "What are the latest updates in LangGraph as of 2024?"
    
    print(f"🧪 Testing Query: {query}")
    
    try:
        result = await run_agent(query)
        
        print("\n✅ Verification Complete!")
        print(f"• Report Length: {len(result['report'])} chars")
        print(f"• Sources: {len(result['sources'])}")
        print(f"• Insights: {len(result['insights'])}")
        
        # Check if we looped
        # (We can't easily check internal state loop_count from here, 
        # but we can check if content looks scraped)
        
        for source in result['sources'][:3]:
            print(f"  - Source: {source['title']}")
            if "[FULL CONTENT]" in source.get('content', ''):
                print(f"    ✅ Deep Scraped ({len(source['content'])} chars)")
            else:
                print(f"    ⚠️ Snippet only")
                
    except Exception as e:
        print(f"❌ Verification Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
