import os
from utils.file_helper import load_json, save_json, generate_id, get_current_datetime

class NotificationManager:
    def __init__(self, file_path='notifications.json'):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        if not os.path.exists(self.file_path):
            save_json(self.file_path, [])

    def get_all_notifications(self):
        return load_json(self.file_path)

    def add_notification(self, title, content, notify_type):
        notifications = self.get_all_notifications()
        notification = {
            'id': generate_id('notify', notifications),
            'title': title,
            'content': content,
            'type': notify_type,
            'created_at': get_current_datetime()
        }
        notifications.append(notification)
        save_json(self.file_path, notifications)
        return notification

    def update_notification(self, notification_id, **kwargs):
        notifications = self.get_all_notifications()
        updated = False
        for n in notifications:
            if n.get('notification_id') == notification_id or n.get('id') == notification_id:
                for k, v in kwargs.items():
                    n[k] = v
                updated = True
                break
        if updated:
            save_json(self.file_path, notifications)
        return updated

    def delete_notification(self, notification_id):
        notifications = self.get_all_notifications()
        new_list = [n for n in notifications if n.get('notification_id') != notification_id and n.get('id') != notification_id]
        save_json(self.file_path, new_list)
        return len(new_list) < len(notifications)
