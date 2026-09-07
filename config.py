 import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

# Validate required variables
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN is not set in environment variables")

if not ADMIN_ID:
    raise ValueError("ADMIN_ID is not set in environment variables")

try:
    ADMIN_ID = int(ADMIN_ID)
except ValueError:
    raise ValueError(f"ADMIN_ID must be a number, got: {ADMIN_ID}")

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
