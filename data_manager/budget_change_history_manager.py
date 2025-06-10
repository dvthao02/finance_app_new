import os
from utils.file_helper import load_json, save_json, generate_id

class BudgetChangeHistoryManager:
    def __init__(self, file_path='budget_change_history.json'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        if not os.path.exists(self.file_path):
            save_json(self.file_path, [])

    def get_all_changes(self):
        return load_json(self.file_path)

    def get_changes_by_user(self, user_id):
        return [c for c in self.get_all_changes() if c.get('user_id') == user_id]

    def add_change(self, change):
        changes = self.get_all_changes()
        change['id'] = generate_id('chg', changes)
        changes.append(change)
        save_json(self.file_path, changes)
        return change
