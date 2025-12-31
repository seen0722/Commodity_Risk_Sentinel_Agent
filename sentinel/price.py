import yfinance as yf
import logging
import yaml
import os

# Load Config
def load_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

CONFIG = load_config()

def get_market_data(ticker_symbol: str) -> dict:
    """
    Fetches market data for a given ticker.
    Returns calculated changes or None if failed.
    """
    try:
        logging.info(f"Fetching price data for {ticker_symbol}...")
        ticker = yf.Ticker(ticker_symbol)
        # Fetch 1 month to ensure enough data points
        hist = ticker.history(period="1mo")
        
        if len(hist) < 4:
            logging.warning(f"Not enough data for {ticker_symbol}")
            return None
            
        current_price = hist['Close'].iloc[-1]
        price_1d_ago = hist['Close'].iloc[-2]
        price_3d_ago = hist['Close'].iloc[-4]
        
        change_1d = ((current_price - price_1d_ago) / price_1d_ago) * 100
        change_3d = ((current_price - price_3d_ago) / price_3d_ago) * 100
        
        return {
            "symbol": ticker_symbol,
            "current_price": round(current_price, 2),
            "change_1d": round(change_1d, 2),
            "change_3d": round(change_3d, 2)
        }
    except Exception as e:
        logging.error(f"Error fetching data for {ticker_symbol}: {e}")
        return None

def check_triggers(data: dict) -> str:
    """
    Checks if price movement triggers alerts based on config.yaml.
    """
    if not data:
        return None
        
    c1 = data['change_1d']
    c3 = data['change_3d']
    
    triggers = CONFIG.get('triggers', {})
    l1 = triggers.get('level_1', {})
    l2 = triggers.get('level_2', {})
    
    # Check Level 2 (Severe)
    if c1 <= l2.get('change_1d', -99) or c3 <= l2.get('change_3d', -99):
        return 'L2'
        
    # Check Level 1 (Warning)
    elif c1 <= l1.get('change_1d', -99):
        return 'L1'
        
    return None
