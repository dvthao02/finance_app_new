from PyQt5.QtCore import pyqtSignal, QTimer
from base.base_dashboard import BaseDashboard
import logging
from data_manager.user_manager import UserManager
from data_manager.category_manager import CategoryManager
from data_manager.notification_manager import NotificationManager
from data_manager.audit_log_manager import AuditLogManager
from data_manager.transaction_manager import TransactionManager
from gui.admin.admin_user_tab import AdminUserTab
from gui.admin.admin_category_tab import AdminCategoryTab
from gui.admin.admin_notify_tab import AdminNotifyTab
from gui.admin.admin_overview_tab import AdminOverviewTab
from gui.admin.admin_audit_tab import AdminAuditTab
from gui.admin.admin_profile_tab import AdminProfileTab

class AdminDashboard(BaseDashboard):
    def __init__(self, user_manager, parent=None):
        self.user_manager = user_manager
        self.category_manager = CategoryManager()
        self.notification_manager = NotificationManager()
        self.audit_log_manager = AuditLogManager()
        self.transaction_manager = TransactionManager()
        super().__init__(parent)
        self.setWindowTitle("Admin Dashboard")
        self.init_admin_content()
        if self.content_stack is not None and self.content_stack.count() > 0:
            self.content_stack.setCurrentIndex(0)
        else:
            pass  # Content stack is none or empty
        
    def get_dashboard_title(self):
        return "🛡️ Admin Dashboard"
    
    def get_navigation_items(self):
        return [
            ("Tổng quan", "overview.png"),
            ("Quản lý Users", "repair-man.png"), 
            ("Quản lý Categories", "categories_icon.png"),
            ("Thông báo", "notifications_icon.png"),
            ("Audit Log", "process-management.png"),
            ("Hồ sơ cá nhân", "users_icon.png"),
        ]
    
    def init_admin_content(self):
        try:
            # Create admin tabs
            self.overview_tab = AdminOverviewTab(self.user_manager, self.transaction_manager)
            self.user_tab = AdminUserTab(self.user_manager, self.audit_log_manager)
            self.category_tab = AdminCategoryTab(self.category_manager)
            self.notify_tab = AdminNotifyTab(self.notification_manager, self.user_manager)
            self.audit_tab = AdminAuditTab(self.audit_log_manager)
            self.profile_tab = AdminProfileTab(self.user_manager)

            # Connect the profile updated signal to the header update
            self.profile_tab.profile_updated.connect(self.update_header)

            if self.content_stack is not None:
                try:
                    # Make sure all widgets are visible before adding
                    self.overview_tab.setVisible(True)
                    self.user_tab.setVisible(True)
                    self.category_tab.setVisible(True)
                    self.notify_tab.setVisible(True)
                    self.audit_tab.setVisible(True)
                    self.profile_tab.setVisible(True)
                    
                    self.content_stack.addWidget(self.overview_tab)
                    self.content_stack.addWidget(self.user_tab)
                    self.content_stack.addWidget(self.category_tab)
                    self.content_stack.addWidget(self.notify_tab)
                    self.content_stack.addWidget(self.audit_tab)
                    self.content_stack.addWidget(self.profile_tab)
                except Exception as e:
                    import logging
                    logging.error(f"Error adding widgets: {e}")
                    import traceback
                    traceback.print_exc()
            
            if self.content_stack is not None and self.content_stack.count() > 0:
                self.content_stack.setCurrentIndex(0)
                
        except Exception as e:
            import logging
            logging.error(f"Error in init_admin_content: {e}")
            import traceback
            traceback.print_exc()

    def set_current_user(self, user):
        """Set the current user and update the interface"""
        self.current_user = user
        
        # Update the header to show user info
        if hasattr(self, 'update_header'):
            self.update_header()
            
        # Refresh all admin tabs with current user data
        self.refresh_all_tabs()
            
        # Set user for profile tab if available
        if hasattr(self, 'profile_tab'):
            self.profile_tab.set_user(user)
            
        print(f"Admin dashboard loaded for user: {user.get('full_name', 'Admin')}")

    def refresh_all_tabs(self):
        """Refresh all admin tabs with current data"""
        try:
            if hasattr(self, 'user_tab'):
                self.user_tab.load_users_table()
            if hasattr(self, 'category_tab'):
                self.category_tab.refresh_table()
            if hasattr(self, 'notify_tab'):
                self.notify_tab.load_notifications_table()
            if hasattr(self, 'overview_tab'):
                self.overview_tab.load_dashboard_stats()
            if hasattr(self, 'audit_tab'):
                self.audit_tab.load_audit_log_table()
        except Exception as e:
            print(f"Error refreshing admin tabs: {e}")

    def on_tab_changed(self, index):
        """Handle tab changes and refresh data as needed"""
        try:
            tab_names = ["Overview", "Users", "Categories", "Notifications", "Audit", "Profile"]
            if 0 <= index < len(tab_names):
                print(f"Switched to {tab_names[index]} tab")
                # Refresh specific tab data when switching
                if index == 0 and hasattr(self, 'overview_tab'):
                    self.overview_tab.load_dashboard_stats()
                elif index == 1 and hasattr(self, 'user_tab'):
                    self.user_tab.load_users_table()
                elif index == 2 and hasattr(self, 'category_tab'):
                    self.category_tab.refresh_table()
                elif index == 3 and hasattr(self, 'notify_tab'):
                    self.notify_tab.load_notifications_table()
                elif index == 4 and hasattr(self, 'audit_tab'):
                    self.audit_tab.load_audit_log_table()
        except Exception as e:
            print(f"Error handling tab change: {e}")
