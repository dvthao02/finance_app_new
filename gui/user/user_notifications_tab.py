from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea, QFrame, QApplication
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect
from PyQt5.QtGui import QFont, QPainter, QColor, QPen, QIcon
import json
from utils.file_helper import load_json
from data_manager.notification_manager import NotificationManager
import os

class ToastNotification(QWidget):
    """Toast notification widget that appears temporarily at bottom-right"""
    
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
        
    def show_notification(self, parent_widget=None):
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            x = screen_geometry.right() - self.width() - 30
            y = screen_geometry.bottom() - self.height() - 30
            self.move(x, y)
        
        self.show()
        self.timer.start(self.duration)
        
    def hide_notification(self):
        self.hide()
        self.deleteLater()

class NotificationCenter(QWidget):
    """Notification center for viewing all notifications"""
    notification_changed = pyqtSignal()
    
    def __init__(self, user_manager, notification_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.notification_manager = notification_manager
        self.init_ui()
        self.load_notifications()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                    stop: 0 #3b82f6, stop: 1 #8b5cf6);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        header = QLabel("Thông báo của bạn")
        header.setFont(QFont('Segoe UI', 24, QFont.Bold))
        header.setStyleSheet("color: white; margin: 0;")
        header_layout.addWidget(header)
        
        subtitle = QLabel("Những thông báo về tài khoản và hoạt động của bạn")
        subtitle.setFont(QFont('Segoe UI', 14))
        subtitle.setStyleSheet("color: rgba(255,255,255,0.9); margin: 0;")
        header_layout.addWidget(subtitle)
        
        layout.addWidget(header_frame)
        
        # Content frame
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 20px;
            }
        """)
        content_layout = QVBoxLayout(content_frame)
        
        # Mark all read button
        action_layout = QHBoxLayout()
        action_layout.setAlignment(Qt.AlignRight)
        
        self.refresh_btn = QPushButton("Làm mới")
        self.refresh_btn.setFont(QFont('Segoe UI', 12))
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1f5f9;
                color: #475569;
                border: 1px solid #cbd5e1;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
                margin-right: 10px;
            }
            QPushButton:hover {
                background-color: #e2e8f0;
            }
        """)
        self.refresh_btn.clicked.connect(self.load_notifications)
        
        mark_all_btn = QPushButton("Đánh dấu tất cả đã đọc")
        mark_all_btn.setFont(QFont('Segoe UI', 12))
        mark_all_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: 500;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        mark_all_btn.clicked.connect(self.mark_all_read)
        
        action_layout.addWidget(self.refresh_btn)
        action_layout.addWidget(mark_all_btn)
        
        content_layout.addLayout(action_layout)
        
        # Scroll area for notifications
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        self.content_widget = QWidget()
        self.content_widget.setStyleSheet("background-color: transparent;")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(12)
        
        scroll.setWidget(self.content_widget)
        content_layout.addWidget(scroll)
        
        layout.addWidget(content_frame)
        
    def load_notifications(self):
        # Clear existing notifications
        for i in reversed(range(self.content_layout.count())):
            widget = self.content_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
            
        try:
            # Lấy user_id từ get_current_user thay vì từ thuộc tính
            current_user = self.user_manager.get_current_user()
            user_id = current_user.get('id') or current_user.get('user_id') if current_user else None
            
            if not user_id:
                no_user_label = QLabel("Không có người dùng đăng nhập. Vui lòng đăng nhập lại.")
                no_user_label.setAlignment(Qt.AlignCenter)
                no_user_label.setFont(QFont('Segoe UI', 14))
                no_user_label.setStyleSheet("""
                    QLabel {
                        color: #ef4444;
                        font-style: italic;
                        padding: 40px;
                    }
                """)
                self.content_layout.addWidget(no_user_label)
                return
            
            # Lấy cả thông báo chung (không có user_id) và thông báo riêng của user
            all_notifications = self.notification_manager.get_all_notifications()
            notifications = []
            
            for notif in all_notifications:
                # Thêm thông báo nếu là thông báo chung hoặc dành cho user hiện tại
                if notif.get('user_id') == user_id or not notif.get('user_id'):
                    notifications.append(notif)
            
            if not notifications:
                no_notif_frame = QFrame()
                no_notif_frame.setStyleSheet("""
                    QFrame {
                        background-color: #f8fafc;
                        border-radius: 8px;
                        padding: 30px;
                    }
                """)
                no_notif_layout = QVBoxLayout(no_notif_frame)
                
                no_notif_label = QLabel("Không có thông báo mới")
                no_notif_label.setAlignment(Qt.AlignCenter)
                no_notif_label.setFont(QFont('Segoe UI', 16, QFont.Bold))
                no_notif_label.setStyleSheet("color: #64748b;")
                
                no_notif_desc = QLabel("Khi có thông báo mới, bạn sẽ thấy chúng ở đây.")
                no_notif_desc.setAlignment(Qt.AlignCenter)
                no_notif_desc.setFont(QFont('Segoe UI', 12))
                no_notif_desc.setStyleSheet("color: #94a3b8; margin-top: 10px;")
                
                no_notif_layout.addWidget(no_notif_label)
                no_notif_layout.addWidget(no_notif_desc)
                
                self.content_layout.addWidget(no_notif_frame)
                return
                
            # Sort by date (newest first)
            notifications.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            for notif in notifications[:20]:  # Show latest 20
                notif_widget = self.create_notification_widget(notif)
                self.content_layout.addWidget(notif_widget)
                
        except Exception as e:
            error_label = QLabel(f"Lỗi tải thông báo: {str(e)}")
            error_label.setFont(QFont('Segoe UI', 12))
            error_label.setStyleSheet("color: #ef4444; padding: 20px;")
            self.content_layout.addWidget(error_label)
            
    def create_notification_widget(self, notification):
        widget = QFrame()
        is_read = notification.get('is_read', False)
        notif_id = notification.get('id')
        
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {'#f8fafc' if is_read else 'white'};
                border: 1px solid {'#e2e8f0' if is_read else '#bfdbfe'};
                border-left: 4px solid {'#94a3b8' if is_read else '#3b82f6'};
                border-radius: 8px;
                padding: 15px;
            }}
            QLabel {{
                border: none;
            }}
            QPushButton {{
                background-color: transparent;
                border: none;
                padding: 5px;
                border-radius: 4px;
            }}
            QPushButton:hover {{
                background-color: #f1f5f9;
            }}
        """)
        
        # Main layout
        main_layout = QVBoxLayout(widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(8)
        
        # Header layout with title and read button
        header_layout = QHBoxLayout()
        
        # Title
        title = QLabel(notification.get('title', 'Thông báo'))
        title.setFont(QFont("Segoe UI", 14, QFont.Bold if not is_read else QFont.Medium))
        title.setStyleSheet(f"color: {'#64748b' if is_read else '#1e293b'};")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Mark as read button
        if not is_read and notif_id:
            mark_read_btn = QPushButton("Đã đọc")
            mark_read_btn.setFont(QFont("Segoe UI", 10))
            mark_read_btn.setCursor(Qt.PointingHandCursor)
            mark_read_btn.setStyleSheet("""
                QPushButton {
                    color: #3b82f6;
                    background-color: #dbeafe;
                    padding: 4px 10px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #bfdbfe;
                }
            """)
            mark_read_btn.clicked.connect(lambda: self.mark_as_read(notif_id))
            header_layout.addWidget(mark_read_btn)
        
        main_layout.addLayout(header_layout)
        
        # Content
        content = QLabel(notification.get('content', notification.get('message', '')))
        content.setWordWrap(True)
        content.setFont(QFont("Segoe UI", 12))
        content.setStyleSheet(f"color: {'#94a3b8' if is_read else '#475569'}; margin-top: 5px;")
        content.setMinimumHeight(content.sizeHint().height())
        main_layout.addWidget(content)
        
        # Date and type
        info_layout = QHBoxLayout()
        
        date_label = QLabel(self.format_date(notification.get('created_at', '')))
        date_label.setFont(QFont("Segoe UI", 10))
        date_label.setStyleSheet("color: #94a3b8; margin-top: 5px;")
        info_layout.addWidget(date_label)
        
        info_layout.addStretch()
        
        # Type label with better visual styling
        type_label = QLabel(notification.get('type', 'Thông báo'))
        type_colors = {
            'Tin tức': ('#dbeafe', '#3b82f6'),  # (bg, text)
            'Cảnh báo': ('#fef3c7', '#d97706'), 
            'Bảo trì': ('#f3e8ff', '#8b5cf6')
        }
        
        notif_type = notification.get('type', 'Thông báo')
        bg_color, text_color = type_colors.get(notif_type, ('#f1f5f9', '#64748b'))
        
        type_label.setFont(QFont("Segoe UI", 10, QFont.Medium))
        type_label.setStyleSheet(f"""
            background-color: {bg_color};
            color: {text_color};
            padding: 3px 10px;
            border-radius: 12px;
        """)
        info_layout.addWidget(type_label)
        
        main_layout.addLayout(info_layout)
        
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
            
    def mark_as_read(self, notification_id):
        """Mark a single notification as read"""
        try:
            if self.notification_manager.update_notification(notification_id, is_read=True):
                show_toast(self, "Đã đánh dấu thông báo là đã đọc", "success")
                self.load_notifications()
                self.notification_changed.emit()
            else:
                show_toast(self, "Không thể đánh dấu thông báo", "error")
        except Exception as e:
            show_toast(self, f"Lỗi: {str(e)}", "error")
            
    def mark_all_read(self):
        """Mark all notifications as read"""
        try:
            current_user = self.user_manager.get_current_user()
            user_id = current_user.get('id') or current_user.get('user_id') if current_user else None
            
            if not user_id:
                show_toast(self, "Không thể xác định người dùng hiện tại", "error")
                return
                
            if self.notification_manager.mark_all_as_read(user_id):
                show_toast(self, "Đã đánh dấu tất cả thông báo là đã đọc", "success")
                self.load_notifications()
                self.notification_changed.emit()
            else:
                show_toast(self, "Không có thông báo nào cần đánh dấu", "info")
        except Exception as e:
            show_toast(self, f"Lỗi: {str(e)}", "error")

def show_toast(parent, message, type="info", duration=3000):
    """Helper function to show toast notification at bottom-right"""
    toast = ToastNotification(message, type, duration, parent)
    toast.show_notification()
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
