import requests
import json
import logging
from datetime import datetime
import random

logger = logging.getLogger(__name__)

class ForexAPI:
    def __init__(self):
        self.cache = {}
        self.last_update = {}
        
    def get_live_price(self, pair):
        """Get live price for a currency pair"""
        try:
            # Using free API - you can replace with your preferred API
            # Demo: Using simulated data for testing
            # In production, use a real API like: https://api.exchangerate.host/latest
            
            # Simulate API call (replace with actual API)
            base_price = self.get_base_price(pair)
            if base_price:
                # Add some volatility
                variation = random.uniform(-0.002, 0.002)
                price = base_price * (1 + variation)
                return round(price, 5)
            
            # Fallback to simulated data
            return self.simulate_price(pair)
            
        except Exception as e:
            logger.error(f"Error fetching price for {pair}: {e}")
            return None
            
    def get_base_price(self, pair):
        """Get base price from API"""
        try:
            # Example with exchangerate.host API
            base = pair[:3]
            target = pair[3:]
            
            url = f"https://api.exchangerate.host/convert?from={base}&to={target}&amount=1"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    return data.get('result')
            return None
            
        except Exception as e:
            logger.error(f"API error for {pair}: {e}")
            return None
            
    def simulate_price(self, pair):
        """Simulate price for demo purposes"""
        # Base prices for common pairs
        base_prices = {
            'EURUSD': 1.0920,
            'GBPUSD': 1.2650,
            'USDJPY': 148.50,
            'AUDUSD': 0.6550,
            'USDCAD': 1.3450,
            'USDCHF': 0.8750,
            'NZDUSD': 0.6100,
            'EURGBP': 0.8620
        }
        
        if pair in base_prices:
            # Add random variation
            variation = random.uniform(-0.0015, 0.0015)
            return round(base_prices[pair] * (1 + variation), 5)
        return 1.0000
        
    def get_market_summary(self):
        """Get summary of all market prices"""
        summary = {}
        for pair in ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF']:
            price = self.get_live_price(pair)
            if price:
                # Calculate change (simulated)
                change = random.uniform(-0.5, 0.5)
                summary[pair] = {
                    'price': price,
                    'change': round(change, 2)
                }
        return summary
