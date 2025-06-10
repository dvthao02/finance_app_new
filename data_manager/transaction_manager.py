import os
from utils.file_helper import load_json, save_json, generate_id

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
