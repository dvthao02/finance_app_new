from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QComboBox, QSizePolicy, QStackedWidget, QLineEdit
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
import os


class BaseDashboard(QWidget):
    logout_signal = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_user = None
        self.sidebar_buttons = []
        self.content_stack = None
        self.current_tab_index = 0
        self.init_ui()
    
    def init_ui(self):
        """Khởi tạo cấu trúc UI cơ sở""" # Đã dịch
        self.setWindowTitle(self.get_dashboard_title())
        self.setMinimumSize(1350, 850)
          # Đặt style mặc định toàn diện để hài hòa hơn
        self.setStyleSheet("""
            /* Kiểu mặc định toàn cục - Tăng kích thước font */
            QWidget { 
                background-color: #f8fafc; 
                font-family: 'Segoe UI', sans-serif;
                font-size: 16px;
                color: #1e293b;
            }
            
            /* Kiểu Label */
            QLabel {
                color: #334155;
                font-size: 16px;
            }
            
            /* Kiểu Button */
            QPushButton {
                font-size: 16px;
                font-weight: 500;
                padding: 10px 18px;
                border-radius: 6px;
                border: 1px solid #e2e8f0;
                background: white;
                color: #374151;
                min-height: 22px;
            }
            QPushButton:hover {
                background: #f9fafb;
                border-color: #d1d5db;
            }
            QPushButton:pressed {
                background: #f3f4f6;
            }
            
            /* Kiểu Input */
            QLineEdit, QComboBox {
                font-size: 16px;
                padding: 10px 14px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
                color: #374151;
                min-height: 18px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3b82f6;
            }
            
            /* Kiểu Table */
            QTableWidget {
                font-size: 16px;
                gridline-color: #f1f5f9;
                background: white;
                selection-background-color: #eff6ff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 12px 14px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 14px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: 600;
                font-size: 14px;
                color: #6b7280;
            }
            
            /* Kiểu Frame */
            QFrame {
                border-radius: 8px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Tiêu đề
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Phần thân với sidebar và nội dung
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Thanh bên
        sidebar = self.create_sidebar()
        body_layout.addWidget(sidebar)

        # Khu vực nội dung chính
        self.content_stack = QStackedWidget()
        self.content_stack.setMinimumWidth(800)
        self.content_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
          # Thêm content_stack vào body_layout
        body_layout.addWidget(self.content_stack)
        main_layout.addLayout(body_layout)

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(70)
        
        # ÉP BUỘC NỀN MÀU XANH - đảm bảo chắc chắn có màu xanh
        header.setAutoFillBackground(True)
        header.setStyleSheet("""
            QFrame {
                background-color: #3b82f6 !important;
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                    stop: 0 #1e40af, stop: 0.5 #3b82f6, stop: 1 #06b6d4) !important;
                border: none !important;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(20)
        
        # Logo và tên ứng dụng
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(12)
        
        logo = QLabel()
        logo.setStyleSheet("color: white !important; background: transparent;")
        try:
            logo_path = self.get_asset_path('app_icon.png')
            if os.path.exists(logo_path):
                logo.setPixmap(QPixmap(logo_path).scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            else:
                logo.setText('💼')
                logo.setFont(QFont('Segoe UI', 20))
                logo.setStyleSheet("color: white !important; background: transparent;")
        except:
            logo.setText('💼')
            logo.setFont(QFont('Segoe UI', 20))
            logo.setStyleSheet("color: white !important; background: transparent;")
        logo_layout.addWidget(logo)
        
        app_name = QLabel(self.get_dashboard_title())
        app_name.setFont(QFont('Segoe UI', 18, QFont.Bold))
        app_name.setStyleSheet('color: white !important; font-weight: 600; background: transparent;')
        logo_layout.addWidget(app_name)
        
        layout.addLayout(logo_layout)
        layout.addStretch()
        
        layout.addStretch()
        
        # Chuông thông báo
        self.notification_btn = QPushButton('🔔')
        self.notification_btn.setFont(QFont('Segoe UI', 16))
        self.notification_btn.setFixedSize(44, 44)
        self.notification_btn.setStyleSheet("""
            QPushButton {
                color: white !important;
                background: rgba(255,255,255,0.15) !important;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 22px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.25) !important;
                border-color: rgba(255,255,255,0.3);
                color: white !important;
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.1) !important;
                color: white !important;
            }
        """)
        layout.addWidget(self.notification_btn)
        
        # Thông tin người dùng (có thể nhấp chuột)
        user_name = self.current_user.get('full_name', self.current_user.get('name', 'User')) if self.current_user else 'User'
        # Lấy avatar qua UserManager để đảm bảo đúng logic
        from data_manager.user_manager import UserManager
        user_manager = UserManager()
        user_avatar = user_manager.get_user_avatar(self.current_user.get('username')) if self.current_user else 'assets/avatar_user_001.jpg'
        self.user_button = QPushButton(f'  {user_name}')
        self.user_button.setFont(QFont('Segoe UI', 13, QFont.Medium))
        self.user_button.setStyleSheet("""
            QPushButton {
                padding: 6px 16px;
                border-radius: 18px;
                background: #e0f2fe;
                color: #0f172a;
                font-weight: 500;
                text-align: left;
            }
        """)
        # Set avatar icon (bo tròn)
        from PyQt5.QtGui import QIcon, QPixmap, QPainterPath, QPainter
        def get_rounded_avatar(path, size=32):
            pixmap = QPixmap(path).scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
            rounded = QPixmap(size, size)
            rounded.fill(Qt.transparent)
            painter = QPainter(rounded)
            painter.setRenderHint(QPainter.Antialiasing)
            path = QPainterPath()
            path.addEllipse(0, 0, size, size)
            painter.setClipPath(path)
            painter.drawPixmap(0, 0, pixmap)
            painter.end()
            return rounded
        avatar_icon = QIcon(get_rounded_avatar(user_avatar, 32))
        self.user_button.setIcon(avatar_icon)
        self.user_button.setIconSize(QSize(32, 32))
        self.user_button.clicked.connect(self.show_profile)
        layout.addWidget(self.user_button)
        
        return header

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(260)  # Tăng width một chút để phù hợp với font lớn hơn
        sidebar.setStyleSheet("""
            QFrame {
                background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
                border-right: 1px solid #e2e8f0;
                border-radius: 0px;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 24, 0, 24)
        layout.setSpacing(6)
        
        # Mục menu
        self.sidebar_buttons = []
        nav_items = self.get_navigation_items()
        
        for i, (text, icon_name) in enumerate(nav_items):
            btn = QPushButton(f"  {text}")
            btn.setFont(QFont('Segoe UI', 15, QFont.Medium))  # Tăng font size lên 15
            btn.setFixedHeight(52)  # Tăng height để phù hợp
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            
            if i == 0:  # Mục đầu tiên được chọn mặc định
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding-left: 22px;
                        border: none;
                        border-radius: 10px;
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                            stop: 0 #3b82f6, stop: 1 #06b6d4);
                        color: white;
                        margin: 3px 12px;
                        font-weight: 600;
                        font-size: 15px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                            stop: 0 #2563eb, stop: 1 #0891b2);
                    }
                """)
                btn.setChecked(True)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding-left: 22px;
                        border: none;
                        border-radius: 10px;
                        background: transparent;
                        color: #64748b;
                        margin: 3px 12px;
                        font-weight: 500;
                        font-size: 15px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                            stop: 0 #f0f9ff, stop: 1 #e0f2fe);
                        color: #0369a1;
                        border-left: 4px solid #3b82f6;
                    }
                """)
            btn.clicked.connect(lambda checked, idx=i: self.switch_tab(idx))
            layout.addWidget(btn)
            self.sidebar_buttons.append(btn)
        
        layout.addStretch()
        
        # Nút đăng xuất ở dưới cùng
        logout_btn = QPushButton('🚪  Đăng xuất')
        logout_btn.setFont(QFont('Segoe UI', 15, QFont.Medium))
        logout_btn.setFixedHeight(50)
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding-left: 22px;
                border: none;
                border-radius: 10px;
                background: transparent;
                color: #dc2626;
                margin: 3px 12px;
                font-weight: 500;
                font-size: 15px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                    stop: 0 #fef2f2, stop: 1 #fee2e2);
                color: #b91c1c;
                border-left: 4px solid #dc2626;
            }
        """)
        logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(logout_btn)
        
        return sidebar

    def switch_tab(self, index):
        """Chuyển đổi sang tab khác với hiệu ứng mượt mà"""
        print(f"DEBUG: Switching to tab index {index}")
          # Cập nhật trạng thái nút với phản hồi hình ảnh
        for i, btn in enumerate(self.sidebar_buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding-left: 22px;
                        border: none;
                        border-radius: 10px;
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                            stop: 0 #3b82f6, stop: 1 #06b6d4);
                        color: white;
                        margin: 3px 12px;
                        font-weight: 600;
                        font-size: 15px;
                    }
                """)
                btn.setChecked(True)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding-left: 22px;
                        border: none;
                        border-radius: 10px;
                        background: transparent;
                        color: #64748b;
                        margin: 3px 12px;
                        font-weight: 500;
                        font-size: 15px;
                    }
                    QPushButton:hover {
                        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                            stop: 0 #f0f9ff, stop: 1 #e0f2fe);
                        color: #0369a1;
                        border-left: 4px solid #3b82f6;
                    }
                """)
                btn.setChecked(False)
        
        # Chuyển đổi nội dung với kiểm tra lỗi
                # Switch content with error checking
        if self.content_stack and 0 <= index < self.content_stack.count():
            self.content_stack.setCurrentIndex(index)
            self.current_tab_index = index
            
            # Ensure the current widget is visible
            current_widget = self.content_stack.currentWidget()
            if current_widget:
                current_widget.setVisible(True)
                current_widget.show()
                print(f"DEBUG: Switched to tab {index}, widget: {current_widget}")
                print(f"DEBUG: Widget visible: {current_widget.isVisible()}")
            
            self.on_tab_changed(index)
        else:
            print(f"DEBUG: Cannot switch to tab {index} - stack count: {self.content_stack.count() if self.content_stack else 'None'}")
    
    def get_asset_path(self, filename):
        """Lấy đường dẫn đầy đủ tới tệp tin tài sản"""
        # Lấy thư mục nơi kịch bản đang được thực thi
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(current_dir, 'assets', filename)
    
    def add_content_widget(self, widget):
        """Thêm một widget vào ngăn xếp nội dung"""
        print(f"DEBUG: add_content_widget called, content_stack: {self.content_stack}")
        print(f"DEBUG: content_stack type: {type(self.content_stack)}")
        print(f"DEBUG: content_stack is not None: {self.content_stack is not None}")
        if self.content_stack is not None:
            self.content_stack.addWidget(widget)
            print(f"DEBUG: Widget added, stack count now: {self.content_stack.count()}")
        else:
            print("ERROR: content_stack is None in add_content_widget!")
    
    def set_current_user(self, user):
        """Đặt người dùng hiện tại và cập nhật UI"""
        self.current_user = user
        self.update_user_info()
        # Cập nhật tiêu đề để hiển thị thông tin người dùng
        self.update_header()
        # Hiển thị thông báo chào mừng sau một khoảng thời gian ngắn
        QTimer.singleShot(1500, self.show_welcome_toast)
    
    def update_header(self):
        """Cập nhật tiêu đề với thông tin người dùng hiện tại"""
        # Tìm và cập nhật tiêu đề
        main_layout = self.layout()
        if main_layout and main_layout.count() > 0:
            # Xóa tiêu đề cũ
            old_header = main_layout.itemAt(0).widget()
            if old_header:
                old_header.setParent(None)
            
            # Tạo tiêu đề mới với thông tin người dùng
            new_header = self.create_header()
            main_layout.insertWidget(0, new_header)
    
    def update_user_info(self):
        """Cập nhật thông tin người dùng trong tiêu đề"""
        # Chức năng này sẽ được các lớp con triển khai nếu cần thiết
        pass
    
    def handle_logout(self):
        """Xử lý hành động đăng xuất"""
        self.logout_signal.emit()
    
    def show_profile(self):
        """Hiển thị tab hồ sơ - chức năng này sẽ được các lớp con triển khai"""
        # Đối với bảng điều khiển quản trị viên, chuyển sang tab hồ sơ
        if hasattr(self, 'switch_tab'):
            profile_tab_index = 5  # Tab hồ sơ thường ở chỉ mục 5
            self.switch_tab(profile_tab_index)
        else:
            print("Chức năng hồ sơ chưa được triển khai cho bảng điều khiển này")
    
    def on_tab_changed(self, index):
        """Được gọi khi tab được thay đổi - chức năng này sẽ được các lớp con triển khai"""
        pass
    
    # Các phương thức trừu tượng để được các lớp con triển khai
    def get_dashboard_title(self):
        """Trả về tiêu đề bảng điều khiển"""
        return "Dashboard"
    
    def get_navigation_items(self):
        """Trả về danh sách các bộ (văn bản, tên biểu tượng) cho điều hướng"""
        return [
            ("Trang chủ", "app_icon.png"),
        ]
    
    def show_welcome_toast(self):
        """Hiển thị thông điệp chào mừng - chức năng này sẽ được các lớp con triển khai"""
        if self.current_user:
            try:
                from gui.user.user_notifications_tab import show_welcome_message
                show_welcome_message(self.current_user, self)
            except Exception as e:
                print(f"Error showing welcome toast: {e}")
    
    # --- Hiển thị số lượng thông báo chưa đọc ---
        from data_manager.notification_manager import NotificationManager
        self.notification_manager = NotificationManager()
        unread_count = 0
        if self.current_user:
            unread_count = self.notification_manager.get_unread_count(self.current_user.get('user_id'))
        if unread_count > 0:
            self.notification_btn.setText(f'🔔 {unread_count}')
        else:
            self.notification_btn.setText('🔔')
        self.notification_btn.clicked.connect(self.show_user_notifications)
        # ---
    
    def show_user_notifications(self):
        """Hiển thị danh sách thông báo của user khi bấm chuông"""
        if not self.current_user:
            return
        user_id = self.current_user.get('user_id')
        notifications = self.notification_manager.get_user_notifications(user_id)
        if not notifications:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.information(self, 'Thông báo', 'Bạn không có thông báo nào!')
            return
        # Đánh dấu tất cả là đã đọc
        self.notification_manager.mark_all_as_read(user_id)
        # Hiển thị danh sách thông báo (dạng popup đơn giản)
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget
        dialog = QDialog(self)
        dialog.setWindowTitle('Thông báo của bạn')
        dialog.setMinimumWidth(420)
        layout = QVBoxLayout(dialog)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        vbox = QVBoxLayout(content)
        for n in sorted(notifications, key=lambda x: x.get('created_at', ''), reverse=True):
            label = QLabel(f"<b>{n.get('title')}</b><br>{n.get('content')}<br><span style='color:gray;font-size:12px'>{n.get('created_at')}</span>")
            label.setWordWrap(True)
            vbox.addWidget(label)
        content.setLayout(vbox)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        dialog.setLayout(layout)
        dialog.exec_()
        # Sau khi đóng popup, cập nhật lại số lượng trên nút chuông
        self.notification_btn.setText('🔔')
