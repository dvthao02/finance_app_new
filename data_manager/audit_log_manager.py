import os
from utils.file_helper import load_json, save_json, generate_id, get_current_datetime

class AuditLogManager:
    def __init__(self, file_path='login_history.json'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        if not os.path.exists(self.file_path):
            save_json(self.file_path, [])

    def get_all_logs(self):
        return load_json(self.file_path)

    def add_log(self, user_id, action):
        logs = self.get_all_logs()
        log = {
            'user_id': user_id,
            'action': action,
            'timestamp': get_current_datetime()
        }
        logs.append(log)
        save_json(self.file_path, logs)
        return log
