import os
import json
import logging
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = """
You are a Commodity Risk Sentinel AI. Your job is to analyze price drops and news to classify market moves.
You will receive a list of de-duplicated news headlines.
You must return only strict JSON. No markdown, no explanations.

Output Schema:
{
  "asset": "string",
  "trigger_level": "L1|L2",
  "news_type": "emotional|structural|unclear",
  "direction": "bullish|bearish|neutral",
  "confidence": "low|medium|high",
  "key_driver": "short explanation",
  "recommended_action": "short actionable advice",
  "supporting_points": ["point 1", "point 2"],
  "news_used": [{"title": "", "source": "", "published_at": ""}]
}

Rules for 'recommended_action':
- If trigger is L2 AND news_type == emotional: "Potential contrarian opportunity (consider DCA)"
- If news_type == structural and bearish: "Do NOT buy against trend"
- If unclear: "Wait and monitor"

LANGUAGE INSTRUCTION:
- Check the 'target_language' provided in the user prompt.
- If 'zh-TW', write 'key_driver', 'recommended_action', and 'supporting_points' in Traditional Chinese (Taiwanese usage/繁體中文 台灣用語).
- Keep 'trigger_level', 'news_type', 'direction', 'confidence' in English (as they are enum keys).
"""

def analyze_risk(asset: str, trigger_level: str, price_data: dict, news_items: list) -> dict:
    """
    Uses LLM to classify the situation.
    """
    target_lang = os.getenv("LANGUAGE", "en")
    news_text = "\n".join([f"- [{n['published_at']}] {n['title']} ({n['source']})" for n in news_items])
    
    user_content = f"""
    ANALYSIS REQUEST
    Target Language: {target_lang}
    Asset: {asset}
    Trigger Level: {trigger_level}
    Price Movement: 1D: {price_data['change_1d']}%, 3D: {price_data['change_3d']}%
    Current Price: {price_data['current_price']}

    Recent News:
    {news_text}

    Task: Classify if this Move is EMOTIONAL (panic) or STRUCTURAL (fundamental).
    """

    try:
        logging.info(f"Sending analysis request for {asset}...")
        response = client.chat.completions.create(
            model="gpt-4o",  # or gpt-3.5-turbo if preferred, assuming gpt-4o for quality
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            response_format={"type": "json_object"},
            temperature=0.3
        )
        
        content = response.choices[0].message.content
        result = json.loads(content)
        
        # Post-Processing: Backfill LINKS to news_used items
        # The AI output might not have the 'link' or might hallucinate it.
        # We match based on title similarity or just assume the AI picked from our list.
        # Simpler approach: Just augment the report with the top provided news items 
        # that match the titles the AI chose.
        
        if result.get('news_used'):
            from .utils import find_best_match_link
            for ai_news in result['news_used']:
                # Find best matching original item to get the link
                link = find_best_match_link(ai_news.get('title', ''), news_items)
                ai_news['link'] = link
        
        # Enforce overrides just in case LLM misses strict specific logic
        # We only override if it matches the specific condition AND we match the language of the output
        # To avoid complexity, we rely on the prompt for language, but if we must override, we check env.
        
        if target_lang == "zh-TW":
            if trigger_level == "L2" and result.get("news_type") == "emotional":
                result["recommended_action"] = "潛在反向操作機會 (考慮分批進場)"
            elif result.get("news_type") == "structural" and result.get("direction") == "bearish":
                result["recommended_action"] = "切勿逆勢承接"
            elif result.get("news_type") == "unclear":
                result["recommended_action"] = "觀望為宜，持續監控"
        else:
            if trigger_level == "L2" and result.get("news_type") == "emotional":
                result["recommended_action"] = "Potential contrarian opportunity (consider DCA)"
            elif result.get("news_type") == "structural" and result.get("direction") == "bearish":
                result["recommended_action"] = "Do NOT buy against trend"
            elif result.get("news_type") == "unclear":
                result["recommended_action"] = "Wait and monitor"
            
        return result

    except Exception as e:
        logging.error(f"AI Analysis failed: {e}")
        return None
