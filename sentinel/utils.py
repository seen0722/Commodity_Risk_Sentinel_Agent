from difflib import SequenceMatcher

def find_best_match_link(ai_title: str, original_items: list) -> str:
    """
    Finds the link of the most similar title in the original list.
    """
    best_ratio = 0.0
    best_link = None
    
    for item in original_items:
        ratio = SequenceMatcher(None, ai_title.lower(), item['title'].lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best_link = item.get('link')
            
    # If the match is too poor (e.g. < 40%), maybe just return None or search result page?
    # But usually AI uses the provided title almost exactly.
    if best_ratio > 0.4:
        return best_link
    return "https://news.google.com"
