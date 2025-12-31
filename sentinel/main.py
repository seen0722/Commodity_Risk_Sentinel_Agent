import logging
import os
import yaml
from . import price, news, ai_classifier, notifier

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sentinel.log"),
        logging.StreamHandler()
    ]
)

def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def run():
    logging.info("Starting Commodity Risk Sentinel run...")
    
    config = load_config()
    assets = config.get('assets', {})
    
    for ticker, info in assets.items():
        logging.info(f"Checking {info['name']} ({ticker})...")
        
        # 1. Get Price Data
        market_data = price.get_market_data(ticker)
        if not market_data:
            continue
            
        logging.info(f"Data: {market_data}")

        # 2. Check Triggers
        trigger = price.check_triggers(market_data)
        
        if not trigger:
            logging.info(f"No trigger for {ticker}. Market normal.")
            continue
            
        logging.info(f"⚠️ TRIGGER FIRED: {trigger} for {ticker}")

        # 3. Fetch News
        news_items = news.get_recent_news(info['query'])
        
        # 4. AI Analysis
        analysis = ai_classifier.analyze_risk(
            asset=info['name'],
            trigger_level=trigger,
            price_data=market_data,
            news_items=news_items
        )
        
        if analysis:
            analysis['price_data'] = market_data
            
            # 5. Notify
            logging.info(f"Analysis result: {analysis['news_type']} - {analysis['recommended_action']}")
            notifier.send_line_notification(analysis)
        else:
            logging.error("AI Analysis returned empty result.")

    logging.info("Run complete.")

if __name__ == "__main__":
    run()
