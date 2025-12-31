# Commodity Risk Sentinel Agent

A Python-based AI agent that monitors Gold (IAU), Silver (SLV), and Copper (COPX) for abnormal price movements using Yahoo Finance. When a significant drop triggers an alert, it fetches recent news and uses GPT-4 to classify the move as either "Emotional" (profit-taking/panic) or "Structural" (trend change), sending actionable insights via LINE Notify.

## Features

- **Automated Price Monitoring**: Checks 1-day and 3-day % changes.
- **Smart Triggers**: Only activates AI analysis on significant drops (L1: -3%, L2: -5%/-8%).
- **AI Analysis**: Uses OpenAI (GPT-4) to correlate price drops with news sentiment.
- **Notifications**: Sends concise summaries to LINE Notify.
- **Demo Mode**: Includes a simulation script to test AI responses during calm markets.

## Setup

### 1. Configure Environment
LINE Notify was discontinued in 2025. This project uses **LINE Messaging API**.

1.  Go to [LINE Developers Console](https://developers.line.biz/).
2.  Create a "Messaging API" Channel.
3.  Issue a **Channel Access Token** (long string).
4.  Find your **User ID** (at the bottom of the "Basic Settings" tab).
5.  Update `.env`:

```ini
OPENAI_API_KEY=sk-...
LINE_CHANNEL_ACCESS_TOKEN=your_token_here
LINE_USER_ID=your_user_id_here
```

### 2. Install Dependencies
The project uses a virtual environment to manage dependencies.

```bash
# Create and activate virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

## Usage

### Run Real-Time Monitor
This checks current market data. If markets are calm, it may finish without outputting alerts.

```bash
# using the virtual environment python
venv/bin/python -m sentinel.main
```

### Run Demo (Simulation)
Simulates a **6.5% crash in Gold** to force the triggers to fire and demonstrate the AI analysis + Notification flow.

```bash
venv/bin/python -m sentinel.demo_force
```

## Scheduling (Cron)
To run this automatically every hour:

1.  Open crontab:
    ```bash
    crontab -e
    ```
2.  Add the following line (adjust path to match your actual project path):
    ```bash
    0 * * * * cd /Users/chenzeming/dev/Commodity_Risk_Sentinel_Agent && /Users/chenzeming/dev/Commodity_Risk_Sentinel_Agent/venv/bin/python -m sentinel.main >> sentinel.log 2>&1
    ```
