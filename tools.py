from langchain.tools import tool
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os 
from dotenv import load_dotenv
load_dotenv()


tavily = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

@tool
def web_search(query: str):
    """Search the web for recent and reliable information."""
    results = tavily.search(query=query, max_results=5)
    #return results
#print(web_search.invoke("What are the recent news of war?"))

    out=[]
    for r in results['results']:
        out.append(
            f"Title: {r['title']}\n"
            f"URL: {r['url']}\n"
            f"Snippet: {r['content'][:300]}\n"
)
    return "\n--------\n".join(out)

    """ I have used the out list for returning the  results in the proper way as initial results was so messy """

print(web_search.invoke("what is the recent news of war? "))