import os
from utils.file_helper import load_json, save_json, generate_id
import datetime

class TransactionManager:
    def __init__(self, file_path='transactions.json'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        if not os.path.exists(self.file_path):
            save_json(self.file_path, [])

    def get_all_transactions(self):
        return load_json(self.file_path)

    def get_transactions_by_user(self, user_id):
        return [t for t in self.get_all_transactions() if t.get('user_id') == user_id]

    def add_transaction(self, transaction):
        transactions = self.get_all_transactions()
        transaction['id'] = generate_id('trans', transactions)
        transactions.append(transaction)
        save_json(self.file_path, transactions)
        return transaction

    def get_transactions_by_month(self, year, month):
        """Get transactions for a specific month"""
        transactions = self.get_all_transactions()
        month_transactions = []
        
        for t in transactions:
            try:
                # Parse date from ISO format
                tx_date = datetime.datetime.fromisoformat(t['date'].replace('Z', '+00:00'))
                if tx_date.year == year and tx_date.month == month:
                    month_transactions.append(t)
            except Exception:
                continue
                
        return month_transactions
    
    def get_recent_transactions(self, limit=10):
        """Get recent transactions sorted by date"""
        transactions = self.get_all_transactions()
        
        # Sort by date (newest first)
        try:
            sorted_transactions = sorted(transactions, 
                key=lambda t: datetime.datetime.fromisoformat(t['date'].replace('Z', '+00:00')), 
                reverse=True)
        except Exception:
            sorted_transactions = transactions
            
        return sorted_transactions[:limit]
