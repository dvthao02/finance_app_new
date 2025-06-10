import os
from utils.file_helper import load_json, save_json, generate_id

class BudgetManager:
    def __init__(self, file_path='budgets.json'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        if not os.path.exists(self.file_path):
            save_json(self.file_path, [])

    def get_all_budgets(self):
        return load_json(self.file_path)

    def get_budgets_by_user(self, user_id):
        return [b for b in self.get_all_budgets() if b.get('user_id') == user_id]

    def add_budget(self, budget):
        budgets = self.get_all_budgets()
        budget['id'] = generate_id('budget', budgets)
        budgets.append(budget)
        save_json(self.file_path, budgets)
        return budget
