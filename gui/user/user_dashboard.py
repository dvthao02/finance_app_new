from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QComboBox, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QStackedWidget
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from base.base_dashboard import BaseDashboard
from utils.ui_styles import TableStyleHelper, ButtonStyleHelper, UIStyles
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import datetime
import json

class UserDashboard(BaseDashboard):
    
    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager, parent=None):
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        super().__init__(parent)  # This will call BaseDashboard.__init__ which calls init_ui()
        self.setup_user_content()  # Add user-specific content after base UI is ready
        
    def get_dashboard_title(self):
        """Return the dashboard title"""
        return "Quản lý Chi Tiêu Cá Nhân"
    
    def get_navigation_items(self):
        """Return list of (text, icon_name) tuples for navigation"""
        return [
            ("Tổng quan", "app_icon.png"),
            ("Thêm giao dịch", "income_icon.png"),
            ("Lịch sử giao dịch", "expense_icon.png"),
            ("Báo cáo", "active_users_icon.png"),
            ("Ngân sách", "categories_icon.png"),
            ("Danh mục", "categories_icon.png"),
            ("Thông báo", "notifications_icon.png"),
            ("Cài đặt", "app_icon.png"),
        ]
    
    def setup_user_content(self):
        """Setup user-specific content in the stacked widget"""
        try:
            # Import user tabs
            from gui.user.user_dashboard_overview import UserOverviewTab
            from gui.user.user_transaction_form import UserTransactionForm
            from gui.user.user_transaction_history import UserTransactionHistory
            from gui.user.user_report import UserReport
            from gui.user.user_budget import UserBudget
            from gui.user.user_category_tab import UserCategoryTab
            from gui.user.user_notifications import NotificationCenter
            from gui.user.user_settings import UserSettings
            
            # Create tabs
            self.overview_tab = UserOverviewTab(self.user_manager, self.transaction_manager, self.category_manager, self.wallet_manager)
            self.transaction_form = UserTransactionForm(self.user_manager, self.transaction_manager, self.category_manager, self.wallet_manager)
            self.transaction_history = UserTransactionHistory(self.user_manager, self.transaction_manager, self.category_manager, self.wallet_manager)
            self.report_tab = UserReport(self.user_manager, self.transaction_manager, self.category_manager)
            
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            self.budget_tab = UserBudget(self.user_manager, self.transaction_manager, self.category_manager, self.wallet_manager)
            self.category_tab = UserCategoryTab(self.category_manager, user_id, reload_callback=self.reload_categories)
            self.notifications_tab = NotificationCenter(self.user_manager)
            self.settings_tab = UserSettings(self.user_manager, self.wallet_manager, self.category_manager)
            
            # Add tabs to content stack
            self.add_content_widget(self.overview_tab)
            self.add_content_widget(self.transaction_form)
            self.add_content_widget(self.transaction_history)
            self.add_content_widget(self.report_tab)
            self.add_content_widget(self.budget_tab)
            self.add_content_widget(self.category_tab)
            self.add_content_widget(self.notifications_tab)
            self.add_content_widget(self.settings_tab)
            
            print(f"DEBUG: User dashboard setup complete, {self.content_stack.count()} tabs added")
            
        except Exception as e:
            print(f"Error setting up user content: {e}")
            import traceback
            traceback.print_exc()
    
    def on_tab_changed(self, index):
        """Called when tab is changed"""
        # Refresh data for specific tabs
        try:
            if index == 0:  # Overview tab
                self.overview_tab.update_dashboard()
            elif index == 2:  # Transaction history
                if hasattr(self.transaction_history, 'reload_data'):
                    self.transaction_history.reload_data()
            elif index == 3:  # Report tab
                if hasattr(self.report_tab, 'reload_data'):
                    self.report_tab.reload_data()
            elif index == 6:  # Notifications tab
                if hasattr(self.notifications_tab, 'load_notifications'):
                    self.notifications_tab.load_notifications()
        except Exception as e:
            print(f"Error in on_tab_changed: {e}")
    
    def reload_categories(self):
        """Callback to reload category in other tabs when there are changes"""
        try:
            if hasattr(self.transaction_form, 'reload_categories'):
                self.transaction_form.reload_categories()
            if hasattr(self.transaction_history, 'load_categories'):
                self.transaction_history.load_categories()
            if hasattr(self.report_tab, 'reload_categories'):
                self.report_tab.reload_categories()
            self.update_dashboard()
        except Exception as e:
            print(f"Error reloading categories: {e}")

    def update_dashboard(self):
        """Update dashboard data"""
        try:
            if hasattr(self, 'overview_tab'):
                self.overview_tab.update_dashboard()
            if hasattr(self, 'transaction_history'):
                if hasattr(self.transaction_history, 'reload_data'):
                    self.transaction_history.reload_data()
            if hasattr(self, 'report_tab'):
                if hasattr(self.report_tab, 'reload_data'):
                    self.report_tab.reload_data()
        except Exception as e:
            print(f"Error updating dashboard: {e}")
    
    def show_welcome_toast(self):
        """Show welcome message"""
        if self.current_user:
            try:
                from gui.user.user_notifications import show_welcome_message
                show_welcome_message(self.current_user, self)
            except Exception as e:
                print(f"Error showing welcome toast: {e}")
    
    def show_profile(self):
        """Show profile tab"""
        self.switch_tab(5)  # Category tab is at index 5, we don't have profile in navigation
    
    def set_current_user(self, user):
        """Set current user"""
        super().set_current_user(user)
        self.user_manager.current_user = user
        self.update_dashboard()
        # Show welcome toast after a short delay
        QTimer.singleShot(1000, self.show_welcome_toast)
