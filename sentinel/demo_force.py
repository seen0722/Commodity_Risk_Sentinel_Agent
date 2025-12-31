import logging
import time
import os
import yaml
from . import price, news, ai_classifier, notifier

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def mock_get_market_data(ticker):
    """Mocks a 6% crash"""
    return {
        "symbol": ticker,
        "current_price": 180.50,
        "change_1d": -6.5,
        "change_3d": -8.2
    }

def run_demo():
    print("\n>>> STARTING DEMO MODE via sentinel.demo_force <<<")
    print(">>> Simulating a CRASH in Gold prices (-6.5%) to trigger AI Analysis <<<\n")
    
    config = load_config()
    # For demo, just check Gold if present, or first asset
    assets = config.get('assets', {})
    if "IAU" in assets:
        target_assets = {"IAU": assets["IAU"]}
    else:
        target_assets = {list(assets.keys())[0]: list(assets.values())[0]}
    
    for ticker, info in target_assets.items():
        logging.info(f"Checking {info['name']} ({ticker})...")
        
        # 1. Get MOCKED Price Data
        market_data = mock_get_market_data(ticker)
        logging.info(f"Data: {market_data}")

        # 2. Check Triggers (Using real trigger logic from config)
        trigger = price.check_triggers(market_data)
        
        if not trigger:
            logging.info(f"No trigger for {ticker}. Market normal.")
            continue
            
        logging.info(f"⚠️ TRIGGER FIRED: {trigger} for {ticker}")

        # 3. Fetch News (Real News)
        news_items = news.get_recent_news(info['query'])
        print(f"\n[News Fetched]: Found {len(news_items)} articles.")
        
        # 4. AI Analysis
        analysis = ai_classifier.analyze_risk(
            asset=info['name'],
            trigger_level=trigger,
            price_data=market_data,
            news_items=news_items
        )
        
        if analysis:
            analysis['price_data'] = market_data
            
            print("\n" + "="*40)
            print(" AI ANALYSIS RESULT ")
            print("="*40)
            print(f"Type: {analysis.get('news_type')}")
            print(f"Confidence: {analysis.get('confidence')}")
            print(f"Direction: {analysis.get('direction')}")
            print(f"Key Driver: {analysis.get('key_driver')}")
            print(f"Recommendation: {analysis.get('recommended_action')}")
            print(f"Supporting Points: {analysis.get('supporting_points')}")
            print("="*40 + "\n")
            
            # 5. Notify
            notifier.send_line_notification(analysis)
        else:
            logging.error("AI Analysis returned empty result.")

    logging.info("Demo run complete.")

if __name__ == "__main__":
    run_demo()
