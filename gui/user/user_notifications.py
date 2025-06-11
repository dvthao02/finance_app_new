from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QFrame
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QPainter, QColor, QPen
import json
from utils.file_helper import load_json

class ToastNotification(QWidget):
    """Toast notification widget that appears temporarily"""
    
    def __init__(self, message, type="info", duration=3000, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.message = message
        self.type = type
        self.duration = duration
        
        self.setup_ui()
        self.setup_animation()
        
    def setup_ui(self):
        self.setFixedSize(300, 60)
        
        # Color scheme based on type
        colors = {
            "success": "#4CAF50",
            "error": "#F44336", 
            "warning": "#FF9800",
            "info": "#2196F3"
        }
        
        bg_color = colors.get(self.type, colors["info"])
        
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {bg_color};
                border-radius: 8px;
                color: white;
            }}
            QLabel {{
                padding: 10px;
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        label = QLabel(self.message)
        label.setWordWrap(True)
        layout.addWidget(label)
        
    def setup_animation(self):
        # Auto-hide timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.hide_notification)
        self.timer.setSingleShot(True)
        
    def show_notification(self, parent_widget):
        if parent_widget:
            # Position at top-right of parent
            parent_rect = parent_widget.geometry()
            x = parent_rect.x() + parent_rect.width() - self.width() - 20
            y = parent_rect.y() + 80
            self.move(x, y)
        
        self.show()
        self.timer.start(self.duration)
        
    def hide_notification(self):
        self.hide()
        self.deleteLater()

class NotificationCenter(QWidget):
    """Notification center for viewing all notifications"""
    
    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.init_ui()
        self.load_notifications()
        
    def init_ui(self):
        self.setWindowTitle("Thông báo")
        self.setFixedSize(400, 500)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("Thông báo của bạn")
        header.setFont(QFont("Segoe UI", 16, QFont.Bold))
        header.setStyleSheet("""
            QLabel {
                padding: 15px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header)
        
        # Scroll area for notifications
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f8fafc;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.content_widget)
        layout.addWidget(scroll)
        
        # Mark all read button
        mark_all_btn = QPushButton("Đánh dấu tất cả đã đọc")
        mark_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
        """)
        mark_all_btn.clicked.connect(self.mark_all_read)
        layout.addWidget(mark_all_btn)
        
    def load_notifications(self):
        # Clear existing notifications
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().setParent(None)
            
        try:
            notifications = load_json('data/notifications.json')
            user_id = getattr(self.user_manager, 'current_user', {}).get('user_id')
            
            # Filter notifications for current user
            user_notifications = []
            for notif in notifications:
                if not notif.get('user_id') or notif.get('user_id') == user_id:
                    user_notifications.append(notif)
                    
            if not user_notifications:
                no_notif_label = QLabel("Không có thông báo nào")
                no_notif_label.setAlignment(Qt.AlignCenter)
                no_notif_label.setStyleSheet("""
                    QLabel {
                        color: #666;
                        font-style: italic;
                        padding: 20px;
                    }
                """)
                self.content_layout.addWidget(no_notif_label)
                return
                
            # Sort by date (newest first)
            user_notifications.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            for notif in user_notifications[:20]:  # Show latest 20
                notif_widget = self.create_notification_widget(notif)
                self.content_layout.addWidget(notif_widget)
                
        except Exception as e:
            error_label = QLabel(f"Lỗi tải thông báo: {str(e)}")
            error_label.setStyleSheet("color: red; padding: 10px;")
            self.content_layout.addWidget(error_label)
            
    def create_notification_widget(self, notification):
        widget = QFrame()
        is_read = notification.get('is_read', False)
        
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {'#f0f0f0' if is_read else 'white'};
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                margin: 5px;
                padding: 10px;
            }}
            QLabel {{
                border: none;
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title = QLabel(notification.get('title', 'Thông báo'))
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet(f"color: {'#666' if is_read else '#333'};")
        layout.addWidget(title)
        
        # Content
        content = QLabel(notification.get('content', ''))
        content.setWordWrap(True)
        content.setStyleSheet(f"color: {'#888' if is_read else '#555'}; font-size: 11px;")
        layout.addWidget(content)
        
        # Date and type
        info_layout = QHBoxLayout()
        
        date_label = QLabel(self.format_date(notification.get('created_at', '')))
        date_label.setStyleSheet("color: #999; font-size: 10px;")
        info_layout.addWidget(date_label)
        
        info_layout.addStretch()
        
        type_label = QLabel(notification.get('type', 'Thông báo'))
        type_colors = {
            'Tin tức': '#2196F3',
            'Cảnh báo': '#FF9800', 
            'Bảo trì': '#9C27B0'
        }
        type_color = type_colors.get(notification.get('type'), '#666')
        type_label.setStyleSheet(f"""
            background-color: {type_color};
            color: white;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 9px;
            font-weight: bold;
        """)
        info_layout.addWidget(type_label)
        
        layout.addLayout(info_layout)
        
        return widget
        
    def format_date(self, date_str):
        try:
            from datetime import datetime
            if not date_str:
                return ""
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.strftime("%d/%m/%Y %H:%M")
        except:
            return date_str
            
    def mark_all_read(self):
        try:
            notifications = load_json('data/notifications.json')
            user_id = getattr(self.user_manager, 'current_user', {}).get('user_id')
            
            # Mark user notifications as read
            for notif in notifications:
                if not notif.get('user_id') or notif.get('user_id') == user_id:
                    notif['is_read'] = True
                    
            # Save back to file
            with open('data/notifications.json', 'w', encoding='utf-8') as f:
                json.dump(notifications, f, ensure_ascii=False, indent=2)
                
            # Reload display
            self.load_notifications()
            
            # Show toast
            toast = ToastNotification("Đã đánh dấu tất cả thông báo là đã đọc", "success", parent=self)
            toast.show_notification(self)
            
        except Exception as e:
            toast = ToastNotification(f"Lỗi: {str(e)}", "error", parent=self)
            toast.show_notification(self)

def show_toast(parent, message, type="info", duration=3000):
    """Helper function to show toast notification"""
    toast = ToastNotification(message, type, duration, parent)
    toast.show_notification(parent)
    return toast

def show_welcome_message(user, parent=None):
    """Show welcome message for user login"""
    name = user.get('full_name', user.get('username', 'Người dùng'))
    from datetime import datetime
    current_hour = datetime.now().hour
    
    if 5 <= current_hour < 12:
        greeting = "Chào buổi sáng"
    elif 12 <= current_hour < 18:
        greeting = "Chào buổi chiều"
    else:
        greeting = "Chào buổi tối"
        
    message = f"{greeting}, {name}! Chào mừng bạn quay trở lại."
    return show_toast(parent, message, "success", 4000)
