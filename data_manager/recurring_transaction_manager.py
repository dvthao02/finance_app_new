import os
from utils.file_helper import load_json, save_json, generate_id

class RecurringTransactionManager:
    def __init__(self, file_path='recurring_transactions.json'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        if not os.path.exists(self.file_path):
            save_json(self.file_path, [])

    def get_all_recurring(self):
        return load_json(self.file_path)

    def get_recurring_by_user(self, user_id):
        return [r for r in self.get_all_recurring() if r.get('user_id') == user_id]

    def add_recurring(self, recurring):
        recurrings = self.get_all_recurring()
        recurring['id'] = generate_id('rec', recurrings)
        recurrings.append(recurring)
        save_json(self.file_path, recurrings)
        return recurring
