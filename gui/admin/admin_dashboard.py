from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QTextEdit, QMessageBox, QInputDialog, QDateEdit, QHeaderView
from PyQt5.QtCore import pyqtSignal, QDate
from data_manager.user_manager import UserManager
from data_manager.category_manager import CategoryManager
from data_manager.notification_manager import NotificationManager
from data_manager.audit_log_manager import AuditLogManager
from data_manager.transaction_manager import TransactionManager
from datetime import datetime
from gui.admin.admin_user_tab import AdminUserTab
from gui.admin.admin_category_tab import AdminCategoryTab
from gui.admin.admin_notify_tab import AdminNotifyTab
# Re-enable AdminOverviewTab
from gui.admin.admin_overview_tab import AdminOverviewTab
from gui.admin.admin_audit_tab import AdminAuditTab

class AdminDashboard(QMainWindow):
    logout_signal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Dashboard")
        self.setMinimumSize(1100, 700)
        self.current_user = None
        # Khởi tạo data_manager trước khi init_ui
        self.user_manager = UserManager()
        self.category_manager = CategoryManager()
        self.notification_manager = NotificationManager()
        self.audit_log_manager = AuditLogManager()
        self.transaction_manager = TransactionManager()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.init_ui(central_widget)

    def set_current_user(self, user):
        self.current_user = user
        self.refresh_all_tabs()

    def refresh_all_tabs(self):
        self.user_tab.load_users_table()
        self.category_tab.load_categories_table()
        self.notify_tab.load_notifications_table()
        self.overview_tab.load_dashboard_stats()
        self.audit_tab.load_audit_log_table()

    def init_ui(self, parent_widget):
        layout = QVBoxLayout(parent_widget)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)        # 1. Tổng quan (Overview) lên đầu tiên
        self.overview_tab = AdminOverviewTab(self.user_manager, self.transaction_manager)
        self.tabs.addTab(self.overview_tab, "Tổng quan")
        # 2. User Management
        self.user_tab = AdminUserTab(self.user_manager, self.audit_log_manager)
        self.tabs.addTab(self.user_tab, "Quản lý Người dùng")
        # 3. Default Category Management
        self.category_tab = AdminCategoryTab(self.category_manager)
        self.tabs.addTab(self.category_tab, "Danh mục Mặc định")
        # 4. System Notifications
        self.notify_tab = AdminNotifyTab(self.notification_manager)
        self.tabs.addTab(self.notify_tab, "Thông báo Hệ thống")
        # 5. Admin Profile (Audit Log)
        self.audit_tab = AdminAuditTab(self.audit_log_manager)
        self.tabs.addTab(self.audit_tab, "Nhật ký Hệ thống")
        self.audit_tab.logout_btn.clicked.connect(self.handle_logout)

    def handle_logout(self):
        self.logout_signal.emit()
        self.close()  # Đúng chuẩn QMainWindow, không dùng accept()
