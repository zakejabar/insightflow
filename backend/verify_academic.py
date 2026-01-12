
import asyncio
import os
import sys
# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)
from agent import run_agent

async def main():
    # Test query for Academic Mode
    query = "research about impact of trading to people psychology in long term"
    
    print(f"🎓 Testing Academic Mode: {query}")
    print("  - Min Citations: 50")
    print("  - Open Access: True")
    
    try:
        result = await run_agent(
            query, 
            search_mode="academic", 
            min_citations=50, 
            open_access=True
        )
        
        print("\n✅ Verification Complete!")
        print(f"• Report Length: {len(result['report'])} chars")
        print(f"• Sources: {len(result['sources'])}")
        
        for source in result['sources'][:5]:
            print(f"  - Paper: {source['title']}")
            print(f"    URL: {source['url']}")
            # Check content for Citation count info which we put in the content string
            if "Citations:" in source.get('content', ''):
                 print(f"    ✓ Has Citation Data")
            if "Abstract:" in source.get('content', ''):
                 print(f"    ✓ Has Abstract")
                
    except Exception as e:
        print(f"❌ Verification Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
