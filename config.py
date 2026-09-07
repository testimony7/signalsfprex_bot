import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))

# Forex pairs
FOREX_PAIRS = [
    'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 
    'USDCAD', 'USDCHF', 'NZDUSD', 'EURGBP'
]

# Default signal settings
DEFAULT_SL = 30  # pips
DEFAULT_TP = 60  # pips

# Update intervals (in seconds)
MARKET_UPDATE_INTERVAL = 300  # 5 minutes
