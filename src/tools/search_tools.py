import sys
try:
    import duckduckgo_search
    # Shim ddgs for compatibility with langchain_community search tools
    if "ddgs" not in sys.modules:
        sys.modules["ddgs"] = duckduckgo_search
except ImportError:
    pass

from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchResults

@tool
def search_news(query: str) -> str:
    """
    Searches for news about a company using the Yahoo Finance API.
    
    Args:
        query (str): A stock ticker symbol (e.g., 'TSM', 'NVDA', 'AAPL').
        
    Returns:
        str: A string containing titles, links, and summaries of recent news.
    """
    # Set User-Agent to prevent 403 Forbidden errors when scraping Yahoo Finance
    import os
    import yfinance as yf
    os.environ["USER_AGENT"] = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    try:
        print(f"DEBUG: Searching Yahoo Finance for '{query}'")
        ticker = yf.Ticker(query)
        news = ticker.news
        
        # Format news data for the LLM Analyst agents
        formatted_results = ""
        if news:
            for item in news:
                if not item:
                    continue
                
                # Yahoo Finance news items can have varying dictionary structures
                try:
                    content = item.get('content', item)
                except AttributeError:
                    print(f"DEBUG: Item is not a dict: {item}")
                    continue
                    
                if content is None:
                    content = item
                
                title = content.get('title', 'No Title')
                
                # Attempt to extract the URL from nested fields
                link = content.get('link')
                if not link and 'clickThroughUrl' in content:
                    click_through = content['clickThroughUrl']
                    if click_through:
                        link = click_through.get('url')
                
                if not link:
                    link = 'No Link'
                    
                summary = content.get('summary', 'No Summary')
                
                formatted_results += f"Title: {title}\nLink: {link}\nSummary: {summary}\n---\n"
        else:
            formatted_results = "No news found."
            
        print(f"DEBUG: Found {len(formatted_results)} characters of results.")
        return formatted_results
    except Exception as e:
        print(f"DEBUG: Error in search_news: {e}")
        return f"Error searching news for {query}: {str(e)}"

@tool
def web_search(query: str) -> str:
    """
    Performs a general web search using the DuckDuckGo engine.
    
    Use this for qualitative research, competitive analysis, and identifying market
    sentiments or specific macro risks not found in ticker-specific news.
    
    Args:
        query (str): The search query string.
        
    Returns:
        str: Aggregated web search results.
    """
    try:
        print(f"DEBUG: Performing web search for '{query}'")
        # Utilize the 'news' backend to ensure high relevancy for investment analysis
        search = DuckDuckGoSearchResults(backend="news")
        results = search.run(query)
        return results
    except Exception as e:
        print(f"DEBUG: Error in web_search: {e}")
        return f"Error performing web search for {query}: {str(e)}"