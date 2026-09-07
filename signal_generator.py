import random
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class SignalGenerator:
    def __init__(self):
        self.analysis_cache = {}
        
    def generate_signal(self, pair, price):
        """Generate a trading signal"""
        try:
            # Get technical indicators
            indicators = self.get_indicators(pair, price)
            
            # Determine action based on indicators
            action = self.determine_action(indicators)
            
            # Calculate SL and TP
            sl, tp = self.calculate_sl_tp(price, action)
            
            # Calculate confidence
            confidence = self.calculate_confidence(indicators)
            
            # Generate analysis
            analysis = self.generate_analysis(indicators, action)
            
            return {
                'pair': pair,
                'action': action,
                'entry': round(price, 5),
                'sl': round(sl, 5),
                'tp': round(tp, 5),
                'risk_reward': self.calculate_risk_reward(price, sl, tp, action),
                'confidence': confidence,
                'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error generating signal: {e}")
            return self.get_fallback_signal(pair, price)
            
    def get_indicators(self, pair, price):
        """Get technical indicators (simulated)"""
        # Simulate indicators - in production, calculate from real data
        return {
            'rsi': random.randint(25, 75),
            'ma_trend': random.choice(['Bullish', 'Bearish', 'Neutral']),
            'support': round(price * 0.995, 5),
            'resistance': round(price * 1.005, 5),
            'momentum': random.uniform(-1, 1)
        }
        
    def determine_action(self, indicators):
        """Determine action based on indicators"""
        rsi = indicators['rsi']
        trend = indicators['ma_trend']
        momentum = indicators['momentum']
        
        # Buy signals
        if rsi < 30 and trend == 'Bullish' and momentum > 0:
            return 'BUY'
        elif rsi < 35 and trend == 'Bullish':
            return 'BUY'
            
        # Sell signals
        if rsi > 70 and trend == 'Bearish' and momentum < 0:
            return 'SELL'
        elif rsi > 65 and trend == 'Bearish':
            return 'SELL'
            
        # Neutral
        return random.choice(['BUY', 'SELL'])  # In production, be more conservative
        
    def calculate_sl_tp(self, price, action):
        """Calculate Stop Loss and Take Profit"""
        pip_value = 0.0001  # Standard pip for most pairs
        
        if action == 'BUY':
            sl = price - (30 * pip_value)  # 30 pips SL
            tp = price + (60 * pip_value)  # 60 pips TP
        else:  # SELL
            sl = price + (30 * pip_value)
            tp = price - (60 * pip_value)
            
        return round(sl, 5), round(tp, 5)
        
    def calculate_risk_reward(self, price, sl, tp, action):
        """Calculate risk/reward ratio"""
        if action == 'BUY':
            risk = price - sl
            reward = tp - price
        else:
            risk = sl - price
            reward = price - tp
            
        if risk <= 0:
            return "1:1"
            
        ratio = reward / risk
        return f"1:{ratio:.1f}"
        
    def calculate_confidence(self, indicators):
        """Calculate signal confidence"""
        confidence = 60  # Base confidence
        
        # Adjust based on indicators
        rsi = indicators['rsi']
        if rsi < 25 or rsi > 75:
            confidence += 15
        elif rsi < 35 or rsi > 65:
            confidence += 10
            
        if indicators['ma_trend'] != 'Neutral':
            confidence += 10
            
        confidence = min(95, confidence)  # Cap at 95%
        return f"{confidence}%"
        
    def generate_analysis(self, indicators, action):
        """Generate analysis text"""
        rsi = indicators['rsi']
        trend = indicators['ma_trend']
        
        analysis = f"RSI at {rsi} indicates "
        if rsi < 30:
            analysis += "oversold conditions. "
        elif rsi > 70:
            analysis += "overbought conditions. "
        else:
            analysis += "neutral conditions. "
            
        analysis += f"Moving averages show {trend} trend. "
        
        if action == 'BUY':
            analysis += "Bullish momentum detected with good entry opportunity."
        else:
            analysis += "Bearish pressure building, suitable for short position."
            
        return analysis
        
    def get_fallback_signal(self, pair, price):
        """Get fallback signal if generation fails"""
        action = random.choice(['BUY', 'SELL'])
        sl, tp = self.calculate_sl_tp(price, action)
        
        return {
            'pair': pair,
            'action': action,
            'entry': round(price, 5),
            'sl': round(sl, 5),
            'tp': round(tp, 5),
            'risk_reward': "1:2",
            'confidence': "50%",
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'analysis': "Basic signal generated. Use with caution."
        }
        
    def get_technical_analysis(self, pair):
        """Get detailed technical analysis"""
        price = 1.0920  # Simulated price
        indicators = self.get_indicators(pair, price)
        
        return {
            'trend': indicators['ma_trend'],
            'support': indicators['support'],
            'resistance': indicators['resistance'],
            'rsi': indicators['rsi'],
            'ma': indicators['ma_trend'],
            'summary': f"Overall {indicators['ma_trend'].lower()} trend with RSI at {indicators['rsi']}",
            'recommendation': 'BUY' if indicators['rsi'] < 40 else 'SELL' if indicators['rsi'] > 60 else 'HOLD'
        }
