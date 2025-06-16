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

    def get_logs_by_date_range(self, start_date, end_date):
        """
        Lọc logs theo khoảng thời gian
        
        Args:
            start_date (str): Ngày bắt đầu định dạng YYYY-MM-DD
            end_date (str): Ngày kết thúc định dạng YYYY-MM-DD
            
        Returns:
            list: Danh sách logs trong khoảng thời gian
        """
        logs = self.get_all_logs()
        filtered = []
        
        # Đảm bảo end_date kết thúc vào cuối ngày
        if end_date and len(end_date) == 10:  # Chỉ có ngày (YYYY-MM-DD)
            end_date = f"{end_date}T23:59:59"
            
        for log in logs:
            timestamp = log.get('timestamp', '')
            
            # Bỏ qua nếu không có timestamp
            if not timestamp:
                continue
                
            # Lọc theo ngày bắt đầu
            if start_date and timestamp < start_date:
                continue
                
            # Lọc theo ngày kết thúc
            if end_date and timestamp > end_date:
                continue
                
            filtered.append(log)
            
        return filtered

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
