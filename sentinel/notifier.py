import os
import requests
import logging
import json
from dotenv import load_dotenv

load_dotenv()

def create_flex_message(report: dict, lang: str):
    """
    Creates a LINE Flex Message JSON object.
    """
    # Localization Labels
    if lang == "zh-TW":
        lbl_risk = "風險警報"
        lbl_price = "當前價格"
        lbl_type = "市場類型"
        lbl_driver = "主要原因"
        lbl_rec = "建議行動"
        lbl_news = "焦點新聞"
    else:
        lbl_risk = "RISK ALERT"
        lbl_price = "Current Price"
        lbl_type = "Market Type"
        lbl_driver = "Key Driver"
        lbl_rec = "Action"
        lbl_news = "Top News"

    # Colors
    color_header = "#D32F2F" # Red for Alert
    color_bg = "#FFFFFF"
    
    asset = report.get('asset', 'Unknown')
    trigger = report.get('trigger_level', '')
    price = str(report.get('price_data', {}).get('current_price'))
    chg1 = report.get('price_data', {}).get('change_1d')
    chg3 = report.get('price_data', {}).get('change_3d')
    news_type = report.get('news_type', '').upper()
    driver = report.get('key_driver', '')
    rec = report.get('recommended_action', '')
    
    # Format Price Change String
    price_change_str = f"1D: {chg1}% | 3D: {chg3}%"
    
    # News Section - Show up to 3 items
    news_components = []
    if report.get('news_used'):
        news_components.append({
            "type": "text",
            "text": lbl_news,
            "weight": "bold",
            "size": "sm",
            "margin": "lg",
            "color": "#555555"
        })
        
        # Limit to top 3 news items
        for news in report['news_used'][:3]:
            # Fallback URL if 'link' is missing, though news.py provides it
            url = news.get('link', 'https://news.google.com')
            source = news.get('source', '')
            
            news_components.append({
                "type": "text",
                "text": f"• {news['title']} ({source})",
                "size": "xs",
                "color": "#0066cc", # Blue to indicate link
                "wrap": True,
                "margin": "sm",
                "action": {
                    "type": "uri",
                    "label": "Read",
                    "uri": url
                }
            })

    flex_json = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"{asset} {lbl_risk} ({trigger})",
                    "weight": "bold",
                    "color": "#FFFFFF",
                    "size": "lg"
                }
            ],
            "backgroundColor": color_header
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                # Price Section
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": lbl_price,
                            "size": "xs",
                            "color": "#aaaaaa"
                        },
                        {
                            "type": "text",
                            "text": f"{price} ({price_change_str})",
                            "weight": "bold",
                            "size": "md"
                        }
                    ]
                },
                {
                    "type": "separator",
                    "margin": "lg"
                },
                # Type & Driver
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"{lbl_type}: {news_type}",
                            "size": "sm",
                            "weight": "bold",
                            "color": "#333333"
                        },
                        {
                            "type": "text",
                            "text": driver,
                            "size": "xs",
                            "color": "#666666",
                            "wrap": True,
                            "margin": "xs"
                        }
                    ]
                },
                # Recommendation (Highlighted)
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "lg",
                    "backgroundColor": "#F5F5F5",
                    "cornerRadius": "md",
                    "paddingAll": "md",
                    "contents": [
                        {
                            "type": "text",
                            "text": lbl_rec,
                            "size": "xs",
                            "color": "#aaaaaa"
                        },
                        {
                            "type": "text",
                            "text": rec,
                            "size": "sm",
                            "weight": "bold",
                            "color": "#009688",
                            "wrap": True
                        }
                    ]
                },
                # News Section
                *news_components
            ]
        }
    }
    return flex_json

def send_line_notification(report: dict):
    """
    Sends a formatted Flex Message to LINE.
    """
    channel_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
    user_id = os.getenv("LINE_USER_ID")
    lang = os.getenv("LANGUAGE", "en")
    
    if not channel_token or channel_token.startswith("your_") or not user_id or user_id.startswith("your_"):
        logging.warning("LINE Messaging API Credentials not set. Notification skipped.")
        return

    api_url = "https://api.line.me/v2/bot/message/push"
    
    flex_content = create_flex_message(report, lang)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_token}"
    }
    
    payload = {
        "to": user_id,
        "messages": [
            {
                "type": "flex",
                "altText": f"🚨 {report.get('asset')} Risk Alert",
                "contents": flex_content
            }
        ]
    }

    try:
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            logging.info("LINE Notification sent successfully (Flex Message).")
        else:
            logging.error(f"Failed to send LINE notification: {response.status_code} {response.text}")
    except Exception as e:
        logging.error(f"Error sending notification: {e}")
