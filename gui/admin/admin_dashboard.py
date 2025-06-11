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
from gui.admin.admin_profile_tab import AdminProfileTab

class AdminDashboard(QMainWindow):
    logout_signal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Dashboard")
        self.setMinimumSize(1100, 700)
        self.current_user = None
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
        # Truyền user cho tab profile nếu có
        if hasattr(self, 'profile_tab'):
            self.profile_tab.set_user(user)

    def refresh_all_tabs(self):
        self.user_tab.load_users_table()
        self.category_tab.load_categories_table()
        self.notify_tab.load_notifications_table(current_user_id=self.current_user.get('user_id') if self.current_user else None)
        self.overview_tab.load_dashboard_stats()
        self.audit_tab.load_audit_log_table()

    def init_ui(self, parent_widget):
        layout = QVBoxLayout(parent_widget)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        self.overview_tab = AdminOverviewTab(self.user_manager, self.transaction_manager)
        self.tabs.addTab(self.overview_tab, "Tổng quan")
        self.user_tab = AdminUserTab(self.user_manager, self.audit_log_manager)
        self.tabs.addTab(self.user_tab, "Quản lý Người dùng")
        self.category_tab = AdminCategoryTab(self.category_manager)
        self.tabs.addTab(self.category_tab, "Danh mục Mặc định")
        self.notify_tab = AdminNotifyTab(self.notification_manager)
        self.tabs.addTab(self.notify_tab, "Thông báo Hệ thống")
        self.audit_tab = AdminAuditTab(self.audit_log_manager)
        self.tabs.addTab(self.audit_tab, "Nhật ký Hệ thống")
        self.profile_tab = AdminProfileTab()
        self.tabs.addTab(self.profile_tab, "Hồ sơ cá nhân")
        self.tabs.currentChanged.connect(self.on_tab_changed)

        # Kết nối các signal/callback để các tab tự động refresh khi có thay đổi
        # Giả sử các tab có signal như: data_changed, bạn cần emit signal này sau mỗi thao tác thêm/sửa/xóa
        try:
            self.user_tab.data_changed.connect(self.refresh_all_tabs)
        except Exception:
            pass
        try:
            self.category_tab.data_changed.connect(self.refresh_all_tabs)
        except Exception:
            pass
        try:
            self.notify_tab.data_changed.connect(self.refresh_all_tabs)
        except Exception:
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Resize các bảng/treeview trong các tab cho vừa cửa sổ
        for tab in [self.user_tab, self.category_tab, self.notify_tab, self.overview_tab, self.audit_tab]:
            if hasattr(tab, 'user_table'):
                tab.user_table.setFixedWidth(self.width()-60)
                tab.user_table.setFixedHeight(self.height()-200)
            if hasattr(tab, 'category_table'):
                tab.category_table.setFixedWidth(self.width()-60)
                tab.category_table.setFixedHeight(self.height()-200)
            if hasattr(tab, 'notify_table'):
                tab.notify_table.setFixedWidth(self.width()-60)
                tab.notify_table.setFixedHeight(self.height()-200)
            if hasattr(tab, 'recent_table'):
                tab.recent_table.setFixedWidth(self.width()-60)
                tab.recent_table.setFixedHeight(180)
            # Nếu có treeview thì resize tương tự
            if hasattr(tab, 'treeview'):
                tab.treeview.setFixedWidth(self.width()-60)
                tab.treeview.setFixedHeight(self.height()-200)

    def handle_logout(self):
        self.logout_signal.emit()
        self.close()  # Đúng chuẩn QMainWindow, không dùng accept()

    def on_tab_changed(self, index):
        # Nếu chuyển sang tab Nhật ký Hệ thống thì tự động refresh
        if self.tabs.tabText(index) == "Nhật ký Hệ thống":
            self.audit_tab.load_audit_log_table()
