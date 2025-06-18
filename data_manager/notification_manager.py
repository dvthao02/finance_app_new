import os
from utils.file_helper import load_json, save_json, generate_id, get_current_datetime
from PyQt5.QtCore import pyqtSignal, QObject # Add QObject and pyqtSignal

class NotificationManager(QObject): # Inherit from QObject
    notification_added = pyqtSignal(dict) # Signal that emits the new notification

    def __init__(self, file_path='notifications.json'):
        super().__init__() # Call QObject constructor
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        self.file_path = os.path.join(data_dir, file_path)
        if not os.path.exists(self.file_path):
            save_json(self.file_path, [])

    def get_all_notifications(self):
        return load_json(self.file_path)

    def add_notification(self, title, content, notify_type, user_id=None):
        notifications = self.get_all_notifications()
        notification = {
            'id': generate_id('notify', notifications),
            'title': title,
            'content': content,
            'type': notify_type,
            'created_at': get_current_datetime(),
            'user_id': user_id,
            'is_read': False  # Luôn thêm trường is_read khi tạo mới
        }
        notifications.append(notification)
        save_json(self.file_path, notifications)
        self.notification_added.emit(notification) # Emit signal with the new notification
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

    def get_user_notifications(self, user_id):
        """Lấy tất cả thông báo của user"""
        return [n for n in self.get_all_notifications() if n.get('user_id') == user_id]

    def get_unread_count(self, user_id):
        """Đếm số lượng thông báo chưa đọc của user"""
        return sum(1 for n in self.get_user_notifications(user_id) if not n.get('is_read', False))

    def mark_all_as_read(self, user_id):
        """Đánh dấu tất cả thông báo của user là đã đọc"""
        notifications = self.get_all_notifications()
        changed = False
        for n in notifications:
            if n.get('user_id') == user_id and not n.get('is_read', False):
                n['is_read'] = True
                changed = True
        if changed:
            save_json(self.file_path, notifications)
        return changed
