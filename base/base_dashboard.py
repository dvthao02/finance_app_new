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
        """Initialize the base UI structure"""
        self.setWindowTitle(self.get_dashboard_title())
        self.setMinimumSize(1350, 850)
          # Set comprehensive default styling for better harmony
        self.setStyleSheet("""
            /* Global default styles - Increased font sizes */
            QWidget { 
                background-color: #f8fafc; 
                font-family: 'Segoe UI', sans-serif;
                font-size: 16px;
                color: #1e293b;
            }
            
            /* Label styles */
            QLabel {
                color: #334155;
                font-size: 16px;
            }
            
            /* Button styles */
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
            
            /* Input styles */
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
            
            /* Table styles */
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
            
            /* Frame styles */
            QFrame {
                border-radius: 8px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Body với sidebar và content
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar
        sidebar = self.create_sidebar()
        body_layout.addWidget(sidebar)

        # Main content area
        self.content_stack = QStackedWidget()
        self.content_stack.setMinimumWidth(800)
        self.content_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
          # Add content stack to body layout
        body_layout.addWidget(self.content_stack)
        main_layout.addLayout(body_layout)

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(70)
        
        # FORCE BLUE BACKGROUND - đảm bảo chắc chắn có màu xanh
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
        
        # Logo và tên app
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
        
        # Search box
        search = QLineEdit()
        search.setPlaceholderText('Tìm kiếm...')
        search.setFixedWidth(280)
        search.setFixedHeight(38)
        search.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.95) !important;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 19px;
                padding: 0 16px;
                font-size: 14px;
                color: #374151 !important;
            }
            QLineEdit:focus {
                background: white !important;
                border-color: rgba(255,255,255,0.4);
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """)        
        layout.addWidget(search)
        
        layout.addStretch()
        
        # Notification bell
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
        
        # User info (clickable)
        user_name = self.current_user.get('full_name', 'User') if self.current_user else 'User'
        self.user_button = QPushButton(f'👤  {user_name}')
        self.user_button.setFont(QFont('Segoe UI', 13, QFont.Medium))
        self.user_button.setStyleSheet("""
            QPushButton {
                color: white !important;
                background: rgba(255,255,255,0.15) !important;
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 22px;
                padding: 8px 18px;
                text-align: left;
                font-weight: 500;
                min-width: 120px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.25) !important;
                border-color: rgba(255,255,255,0.3);
                color: white !important;
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.1) !important;
                color: white !important;
            }        """)
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
        
        # Menu items
        self.sidebar_buttons = []
        nav_items = self.get_navigation_items()
        
        for i, (text, icon_name) in enumerate(nav_items):
            btn = QPushButton(f"  {text}")
            btn.setFont(QFont('Segoe UI', 15, QFont.Medium))  # Tăng font size lên 15
            btn.setFixedHeight(52)  # Tăng height để phù hợp
            btn.setCursor(Qt.PointingHandCursor)
            btn.setCheckable(True)
            
            if i == 0:  # First item active by default
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
        
        # Logout button at bottom
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
        """Switch to a different tab with smooth transition"""
        print(f"DEBUG: Switching to tab index {index}")
          # Update button states with visual feedback
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
        
        # Switch content with error checking
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
        """Get the full path to an asset file"""
        # Get the directory where the script is located
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(current_dir, 'assets', filename)
    
    def add_content_widget(self, widget):
        """Add a widget to the content stack"""
        print(f"DEBUG: add_content_widget called, content_stack: {self.content_stack}")
        print(f"DEBUG: content_stack type: {type(self.content_stack)}")
        print(f"DEBUG: content_stack is not None: {self.content_stack is not None}")
        if self.content_stack is not None:
            self.content_stack.addWidget(widget)
            print(f"DEBUG: Widget added, stack count now: {self.content_stack.count()}")
        else:
            print("ERROR: content_stack is None in add_content_widget!")
    
    def set_current_user(self, user):
        """Set the current user and update UI"""
        self.current_user = user
        self.update_user_info()
        # Update header to show user info
        self.update_header()
        # Show welcome toast after a short delay
        QTimer.singleShot(1500, self.show_welcome_toast)
    
    def update_header(self):
        """Update header with current user info"""
        # Find and update the header
        main_layout = self.layout()
        if main_layout and main_layout.count() > 0:
            # Remove old header
            old_header = main_layout.itemAt(0).widget()
            if old_header:
                old_header.setParent(None)
            
            # Create new header with user info
            new_header = self.create_header()
            main_layout.insertWidget(0, new_header)
    
    def update_user_info(self):
        """Update user information in the header"""
        # This will be implemented by child classes if needed
        pass
    
    def handle_logout(self):
        """Handle logout action"""
        self.logout_signal.emit()
    
    def show_profile(self):
        """Show profile tab - to be implemented by child classes"""
        # For admin dashboard, switch to profile tab
        if hasattr(self, 'switch_tab'):
            profile_tab_index = 5  # Profile tab is usually at index 5
            self.switch_tab(profile_tab_index)
        else:
            print("Profile functionality not implemented for this dashboard")
    
    def on_tab_changed(self, index):
        """Called when tab is changed - to be implemented by child classes"""
        pass
    
    # Abstract methods to be implemented by child classes
    def get_dashboard_title(self):
        """Return the dashboard title"""
        return "Dashboard"
    
    def get_navigation_items(self):
        """Return list of (text, icon_name) tuples for navigation"""
        return [
            ("Trang chủ", "app_icon.png"),
        ]
    
    def show_welcome_toast(self):
        """Show welcome message - to be implemented by child classes"""
        if self.current_user:
            try:
                from gui.user.user_notifications import show_welcome_message
                show_welcome_message(self.current_user, self)
            except Exception as e:
                print(f"Error showing welcome toast: {e}")
