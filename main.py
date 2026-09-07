import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    ContextTypes, MessageHandler, filters
)
from config import BOT_TOKEN, ADMIN_ID, FOREX_PAIRS, DEFAULT_SL, DEFAULT_TP
from forex_api import ForexAPI
from signal_generator import SignalGenerator
from database import Database
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import pytz

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize components
forex_api = ForexAPI()
signal_gen = SignalGenerator()
db = Database()
scheduler = AsyncIOScheduler(timezone=pytz.UTC)

# Store user subscriptions
user_subscriptions = {}

class SignalsForexBot:
    def __init__(self):
        self.application = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start command handler"""
        user = update.effective_user
        await update.message.reply_text(
            f"🚀 *Welcome to SignalsForexBot!*\n\n"
            f"Hello {user.first_name}! 👋\n\n"
            f"I'm your smart Forex signals assistant. Here's what I can do:\n\n"
            f"📊 *Live Signals* - Get real-time trading signals\n"
            f"📈 *Market Analysis* - Technical & fundamental analysis\n"
            f"🎯 *SL & TP Targets* - Precise stop-loss and take-profit levels\n"
            f"💹 *Live Updates* - Current market prices and trends\n\n"
            f"Use /help to see all available commands.",
            parse_mode='Markdown'
        )
        db.add_user(user.id, user.username, user.first_name)
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Help command handler"""
        help_text = """
📚 *Available Commands:*

/start - Start the bot
/help - Show this help message
/signal <pair> - Get signal for specific pair (e.g., /signal EURUSD)
/signals - Get signals for all pairs
/analysis <pair> - Get technical analysis
/market - Get live market updates
/subscribe - Subscribe to daily signals
/unsubscribe - Unsubscribe from signals
/pairs - Show all available forex pairs
/about - About this bot

*Examples:*
/signal EURUSD
/analysis GBPUSD
/market

*Support:*
Contact @support for any issues
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')
        
    async def signal_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get signal for specific pair"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Please specify a currency pair.\n"
                    "Example: /signal EURUSD\n"
                    "Use /pairs to see available pairs."
                )
                return
                
            pair = context.args[0].upper()
            if pair not in FOREX_PAIRS:
                await update.message.reply_text(
                    f"❌ Pair '{pair}' not supported.\n"
                    f"Use /pairs to see available pairs."
                )
                return
                
            # Get current price
            price = forex_api.get_live_price(pair)
            if not price:
                await update.message.reply_text(
                    f"❌ Could not fetch price for {pair}. Please try again later."
                )
                return
                
            # Generate signal
            signal = signal_gen.generate_signal(pair, price)
            
            # Format signal message
            signal_text = self.format_signal_message(signal)
            await update.message.reply_text(signal_text, parse_mode='Markdown')
            
            # Log the signal
            logger.info(f"Signal generated for {pair} by user {update.effective_user.id}")
            
        except Exception as e:
            logger.error(f"Error in signal_command: {e}")
            await update.message.reply_text(
                "❌ An error occurred. Please try again later."
            )
            
    async def signals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get signals for all pairs"""
        try:
            await update.message.reply_text(
                "📊 *Generating signals for all pairs...*\n"
                "Please wait a moment. ⏳",
                parse_mode='Markdown'
            )
            
            signals = []
            for pair in FOREX_PAIRS:
                price = forex_api.get_live_price(pair)
                if price:
                    signal = signal_gen.generate_signal(pair, price)
                    signals.append(signal)
                    
            if not signals:
                await update.message.reply_text(
                    "❌ Could not fetch signals. Please try again later."
                )
                return
                
            # Format and send all signals
            message = "📊 *Live Signals for All Pairs*\n\n"
            for signal in signals:
                message += f"*{signal['pair']}*: {signal['action']} @ {signal['entry']}\n"
                message += f"📈 SL: {signal['sl']} | TP: {signal['tp']}\n"
                message += f"📊 Confidence: {signal['confidence']}\n\n"
                
            # Split message if too long
            if len(message) > 4000:
                parts = [message[i:i+4000] for i in range(0, len(message), 4000)]
                for part in parts:
                    await update.message.reply_text(part, parse_mode='Markdown')
            else:
                await update.message.reply_text(message, parse_mode='Markdown')
                
        except Exception as e:
            logger.error(f"Error in signals_command: {e}")
            await update.message.reply_text(
                "❌ An error occurred. Please try again later."
            )
            
    async def analysis_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get technical analysis for a pair"""
        try:
            if not context.args:
                await update.message.reply_text(
                    "❌ Please specify a currency pair.\n"
                    "Example: /analysis EURUSD"
                )
                return
                
            pair = context.args[0].upper()
            if pair not in FOREX_PAIRS:
                await update.message.reply_text(
                    f"❌ Pair '{pair}' not supported."
                )
                return
                
            # Get analysis
            analysis = signal_gen.get_technical_analysis(pair)
            if not analysis:
                await update.message.reply_text(
                    f"❌ Could not fetch analysis for {pair}."
                )
                return
                
            message = f"""
📊 *Technical Analysis - {pair}*

📈 *Trend:* {analysis['trend']}
🎯 *Support:* {analysis['support']}
🎯 *Resistance:* {analysis['resistance']}
📊 *RSI:* {analysis['rsi']}
📉 *Moving Averages:* {analysis['ma']}
⭐ *Overall:* {analysis['summary']}

*Recommendation:* {analysis['recommendation']}
"""
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in analysis_command: {e}")
            await update.message.reply_text(
                "❌ An error occurred. Please try again later."
            )
            
    async def market_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get live market updates"""
        try:
            await update.message.reply_text(
                "💹 *Fetching live market data...*\n"
                "Please wait. ⏳",
                parse_mode='Markdown'
            )
            
            market_data = forex_api.get_market_summary()
            message = "💹 *Live Market Update*\n\n"
            
            for pair, data in market_data.items():
                change = data['change']
                emoji = "🟢" if change > 0 else "🔴" if change < 0 else "⚪"
                message += f"{emoji} *{pair}*: {data['price']} ({change:+.2f}%)\n"
                
            message += f"\n🕐 *Last Updated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC"
            
            await update.message.reply_text(message, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in market_command: {e}")
            await update.message.reply_text(
                "❌ Could not fetch market data. Please try again later."
            )
            
    async def subscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Subscribe to daily signals"""
        user_id = update.effective_user.id
        db.subscribe_user(user_id)
        user_subscriptions[user_id] = True
        
        await update.message.reply_text(
            "✅ *Subscription Successful!*\n\n"
            "You will now receive daily forex signals.\n"
            "Use /unsubscribe to stop receiving signals.",
            parse_mode='Markdown'
        )
        
    async def unsubscribe_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Unsubscribe from daily signals"""
        user_id = update.effective_user.id
        db.unsubscribe_user(user_id)
        if user_id in user_subscriptions:
            del user_subscriptions[user_id]
            
        await update.message.reply_text(
            "✅ *Unsubscribed Successfully!*\n\n"
            "You will no longer receive daily signals.",
            parse_mode='Markdown'
        )
        
    async def pairs_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all available pairs"""
        pairs_list = "\n".join([f"• {pair}" for pair in FOREX_PAIRS])
        await update.message.reply_text(
            f"📊 *Available Forex Pairs:*\n\n{pairs_list}\n\n"
            f"Total: {len(FOREX_PAIRS)} pairs",
            parse_mode='Markdown'
        )
        
    async def about_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """About the bot"""
        await update.message.reply_text(
            "🤖 *About SignalsForexBot*\n\n"
            "Version: 1.0.0\n\n"
            "This bot provides smart forex signals with:\n"
            "• Entry points\n"
            "• Stop Loss (SL)\n"
            "• Take Profit (TP)\n"
            "• Technical analysis\n"
            "• Live market updates\n\n"
            "Data sources: Live market data\n"
            "Support: @support",
            parse_mode='Markdown'
        )
        
    def format_signal_message(self, signal):
        """Format signal message with emojis"""
        emoji = "📈" if signal['action'] == "BUY" else "📉" if signal['action'] == "SELL" else "⏳"
        
        message = f"""
{emoji} *SIGNAL ALERT* {emoji}

*Pair:* {signal['pair']}
*Action:* {signal['action']}
*Entry:* {signal['entry']}
*Stop Loss:* {signal['sl']}
*Take Profit:* {signal['tp']}

*Risk/Reward:* {signal['risk_reward']}
*Confidence:* {signal['confidence']}
*Time:* {signal['time']}

*Analysis:*
{signal['analysis']}
"""
        return message
        
    async def send_daily_signals(self):
        """Send daily signals to subscribed users"""
        try:
            subscribers = db.get_subscribers()
            if not subscribers:
                return
                
            # Generate signals
            signals = []
            for pair in FOREX_PAIRS[:5]:  # Send signals for top 5 pairs
                price = forex_api.get_live_price(pair)
                if price:
                    signal = signal_gen.generate_signal(pair, price)
                    signals.append(signal)
                    
            if not signals:
                return
                
            # Format message
            message = "📊 *Daily Signal Update*\n\n"
            for signal in signals:
                message += f"*{signal['pair']}*: {signal['action']} @ {signal['entry']}\n"
                message += f"SL: {signal['sl']} | TP: {signal['tp']}\n"
                message += f"Confidence: {signal['confidence']}\n\n"
                
            # Send to all subscribers
            for user_id in subscribers:
                try:
                    await self.application.bot.send_message(
                        chat_id=user_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    await asyncio.sleep(0.1)  # Rate limiting
                except Exception as e:
                    logger.error(f"Failed to send to {user_id}: {e}")
                    
        except Exception as e:
            logger.error(f"Error in send_daily_signals: {e}")
            
    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred. Please try again later."
            )
            
    def run(self):
        """Run the bot"""
        try:
            # Create application
            self.application = Application.builder().token(BOT_TOKEN).build()
            
            # Add command handlers
            self.application.add_handler(CommandHandler("start", self.start))
            self.application.add_handler(CommandHandler("help", self.help_command))
            self.application.add_handler(CommandHandler("signal", self.signal_command))
            self.application.add_handler(CommandHandler("signals", self.signals_command))
            self.application.add_handler(CommandHandler("analysis", self.analysis_command))
            self.application.add_handler(CommandHandler("market", self.market_command))
            self.application.add_handler(CommandHandler("subscribe", self.subscribe_command))
            self.application.add_handler(CommandHandler("unsubscribe", self.unsubscribe_command))
            self.application.add_handler(CommandHandler("pairs", self.pairs_command))
            self.application.add_handler(CommandHandler("about", self.about_command))
            
            # Add error handler
            self.application.add_error_handler(self.error_handler)
            
            # Start scheduler for daily signals
            scheduler.add_job(self.send_daily_signals, 'interval', hours=24)
            scheduler.start()
            
            # Run the bot
            logger.info("Bot started successfully!")
            self.application.run_polling(allowed_updates=Update.ALL_TYPES)
            
        except Exception as e:
            logger.error(f"Error running bot: {e}")
            raise

if __name__ == "__main__":
    bot = SignalsForexBot()
    bot.run()
