import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.db_file = 'users.json'
        self.data = self.load_data()
        
    def load_data(self):
        """Load data from file"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r') as f:
                    return json.load(f)
            return {'users': [], 'subscribers': []}
        except Exception as e:
            logger.error(f"Error loading database: {e}")
            return {'users': [], 'subscribers': []}
            
    def save_data(self):
        """Save data to file"""
        try:
            with open(self.db_file, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving database: {e}")
            
    def add_user(self, user_id, username, first_name):
        """Add user to database"""
        if user_id not in self.data['users']:
            self.data['users'].append({
                'id': user_id,
                'username': username,
                'first_name': first_name,
                'joined': datetime.now().isoformat()
            })
            self.save_data()
            
    def subscribe_user(self, user_id):
        """Subscribe user to signals"""
        if user_id not in self.data['subscribers']:
            self.data['subscribers'].append(user_id)
            self.save_data()
            
    def unsubscribe_user(self, user_id):
        """Unsubscribe user from signals"""
        if user_id in self.data['subscribers']:
            self.data['subscribers'].remove(user_id)
            self.save_data()
            
    def get_subscribers(self):
        """Get list of subscribers"""
        return self.data['subscribers']
        
    def is_subscribed(self, user_id):
        """Check if user is subscribed"""
        return user_id in self.data['subscribers']
