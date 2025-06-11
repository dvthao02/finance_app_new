from PyQt5.QtCore import pyqtSignal, QTimer
from base.base_dashboard import BaseDashboard
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
    def __init__(self, parent=None):
        print("DEBUG: AdminDashboard __init__ started")
        self.user_manager = UserManager()
        self.category_manager = CategoryManager()
        self.notification_manager = NotificationManager()
        self.audit_log_manager = AuditLogManager()
        self.transaction_manager = TransactionManager()
        
        print("DEBUG: About to call super().__init__")
        super().__init__(parent)
        print("DEBUG: super().__init__ completed")
        self.setWindowTitle("Admin Dashboard")
        print("DEBUG: About to call init_admin_content")
        self.init_admin_content()
        print("DEBUG: init_admin_content completed")
        
        if self.content_stack is not None and self.content_stack.count() > 0:
            self.content_stack.setCurrentIndex(0)
            print(f"DEBUG: Final - Set content stack to index 0, total widgets: {self.content_stack.count()}")
            print(f"DEBUG: Final - Current widget: {self.content_stack.currentWidget()}")
            print(f"DEBUG: Final - Widget visible: {self.content_stack.currentWidget().isVisible() if self.content_stack.currentWidget() else 'None'}")
        else:
            print(f"DEBUG: Final - Cannot set index - stack is None or empty")
        
    def get_dashboard_title(self):
        return "🛡️ Admin Dashboard"
    
    def get_navigation_items(self):
        return [
            ("Tổng quan", "app_icon.png"),
            ("Quản lý Users", "users_icon.png"), 
            ("Quản lý Categories", "categories_icon.png"),
            ("Thông báo", "notifications_icon.png"),
            ("Audit Log", "app_icon.png"),
            ("Hồ sơ cá nhân", "users_icon.png"),
        ]
    
    def init_admin_content(self):
        print("DEBUG: Starting init_admin_content")
        try:
            print("DEBUG: Creating admin tabs...")
            self.overview_tab = AdminOverviewTab(self.user_manager, self.transaction_manager)
            print("DEBUG: Overview tab created")
            self.user_tab = AdminUserTab(self.user_manager, self.audit_log_manager)
            print("DEBUG: User tab created")
            self.category_tab = AdminCategoryTab(self.category_manager)
            print("DEBUG: Category tab created")
            self.notify_tab = AdminNotifyTab(self.notification_manager)
            print("DEBUG: Notify tab created")
            self.audit_tab = AdminAuditTab(self.audit_log_manager)
            print("DEBUG: Audit tab created")
            self.profile_tab = AdminProfileTab()
            print("DEBUG: Profile tab created")
            
            print(f"DEBUG: Content stack available: {self.content_stack is not None}")
            print(f"DEBUG: Content stack object: {self.content_stack}")
            if self.content_stack is not None:
                print("DEBUG: Adding widgets to content stack...")
                try:
                    # Make sure all widgets are visible before adding
                    self.overview_tab.setVisible(True)
                    self.user_tab.setVisible(True)
                    self.category_tab.setVisible(True)
                    self.notify_tab.setVisible(True)
                    self.audit_tab.setVisible(True)
                    self.profile_tab.setVisible(True)
                    
                    self.content_stack.addWidget(self.overview_tab)
                    print("DEBUG: Added overview_tab")
                    self.content_stack.addWidget(self.user_tab)
                    print("DEBUG: Added user_tab")
                    self.content_stack.addWidget(self.category_tab)
                    print("DEBUG: Added category_tab")
                    self.content_stack.addWidget(self.notify_tab)
                    print("DEBUG: Added notify_tab")
                    self.content_stack.addWidget(self.audit_tab)
                    print("DEBUG: Added audit_tab")
                    self.content_stack.addWidget(self.profile_tab)
                    print("DEBUG: Added profile_tab")
                    print(f"DEBUG: Content stack now has {self.content_stack.count()} widgets")
                except Exception as e:
                    print(f"DEBUG: Error adding widgets: {e}")
                    import traceback
                    traceback.print_exc()
            else:
                print("DEBUG: Content stack is None!")
            
            if self.content_stack is not None and self.content_stack.count() > 0:
                self.content_stack.setCurrentIndex(0)
                print("DEBUG: Set current index to 0")
                print(f"DEBUG: Current widget: {self.content_stack.currentWidget()}")
            else:
                print(f"DEBUG: Cannot set index - stack count: {self.content_stack.count() if self.content_stack else 'None'}")
                
        except Exception as e:
            print(f"ERROR in init_admin_content: {e}")
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
                self.category_tab.load_categories_table()
            if hasattr(self, 'notify_tab'):
                self.notify_tab.load_notifications_table(
                    current_user_id=self.current_user.get('user_id') if self.current_user else None
                )
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
                    self.category_tab.load_categories_table()
                elif index == 3 and hasattr(self, 'notify_tab'):
                    self.notify_tab.load_notifications_table(
                        current_user_id=self.current_user.get('user_id') if self.current_user else None
                    )
                elif index == 4 and hasattr(self, 'audit_tab'):
                    self.audit_tab.load_audit_log_table()
        except Exception as e:
            print(f"Error handling tab change: {e}")
