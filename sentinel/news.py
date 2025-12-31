import feedparser
import urllib.parse
import logging
from difflib import SequenceMatcher

def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_recent_news(query: str, max_items: int = 15) -> list:
    """
    Fetches news from Google News RSS.
    Applies de-duplication to filter out very similar headlines.
    """
    try:
        logging.info(f"Fetching news for query: {query}")
        encoded_query = urllib.parse.quote(query)
        rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        
        feed = feedparser.parse(rss_url)
        raw_items = []
        
        # 1. Parse Raw Items
        for entry in feed.entries[:max_items]:
            item = {
                "title": entry.title,
                "source": entry.source.title if hasattr(entry, 'source') else "Unknown",
                "published_at": entry.get('published', ''),
                "summary": entry.summary if hasattr(entry, 'summary') else "",
                "link": entry.link
            }
            raw_items.append(item)
            
        # 2. De-duplication / Clustering
        # We reject an item if it is > 60% similar to any item already accepted
        unique_items = []
        
        for item in raw_items:
            is_duplicate = False
            for unique in unique_items:
                # Compare Titles
                similarity = similar(item['title'].lower(), unique['title'].lower())
                if similarity > 0.6:  # 60% similarity threshold
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_items.append(item)
                
        # Return top N unique items (e.g. top 8) to avoid overwhelming context
        return unique_items[:8]

    except Exception as e:
        logging.error(f"Error fetching news for {query}: {e}")
        return []
