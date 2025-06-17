from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QComboBox, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QStackedWidget
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
from base.base_dashboard import BaseDashboard
from utils.ui_styles import TableStyleHelper, ButtonStyleHelper, UIStyles
from utils.quick_actions import add_quick_actions_to_widget
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import datetime
import json
from data_manager.budget_manager import BudgetManager
from data_manager.notification_manager import NotificationManager

class UserDashboard(BaseDashboard):
    
    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager, notification_manager, parent=None):
        super().__init__(parent) # Call superclass constructor first

        # Store manager instances
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager # Might be None
        self.budget_manager = BudgetManager() # Own instance
        self.notification_manager = notification_manager # Passed instance

        # BaseDashboard.init_ui() should have been called by super().__init__()
        # self.current_user will be set by set_current_user()
        # self.setup_user_content() will be called by set_current_user()
        # Ensure content_stack exists (usually created in BaseDashboard.init_ui)
        if not hasattr(self, 'content_stack'):
            print("WARN: UserDashboard.__init__ - self.content_stack not found after super().__init__().")
            # If BaseDashboard is supposed to create it, this is an issue.
            # For now, we assume BaseDashboard's init_ui (called via super) creates self.content_stack.
        
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
            ("Hồ sơ", "users_icon.png"),
        ]
    
    def setup_user_content(self):
        """Setup user-specific content in the stacked widget"""
        try:
            # Import user tabs
            from gui.user.user_overview_tab import UserOverviewTab
            from gui.user.user_transaction_form_tab import UserTransactionForm
            from gui.user.user_transaction_history_tab import UserTransactionHistory
            from gui.user.user_report_tab import UserReport
            from gui.user.user_budget_tab import UserBudget
            from gui.user.user_category_tab import UserCategoryTab
            from gui.user.user_notifications_tab import NotificationCenter
            from gui.user.user_settings_tab import UserSettings
            from gui.user.user_profile_tab import UserProfile
            
            user_id = None
            # self.current_user should be set by set_current_user via super().set_current_user()
            if hasattr(self, 'current_user') and self.current_user:
                user_id = self.current_user.get('id') or self.current_user.get('user_id')
            
            if not user_id:
                print("ERROR: UserDashboard.setup_user_content - user_id is not available. Cannot create tabs.")
                # Clear existing widgets if any, to prevent using old data
                if hasattr(self, 'content_stack'):
                    while self.content_stack.count():
                        widget = self.content_stack.widget(0)
                        self.content_stack.removeWidget(widget)
                        widget.deleteLater()
                return

            print(f"DEBUG: UserDashboard.setup_user_content using user_id={user_id} for tabs")
            
            # Create tabs
            self.overview_tab = UserOverviewTab(
                user_manager=self.user_manager, 
                transaction_manager=self.transaction_manager, 
                category_manager=self.category_manager, 
                wallet_manager=self.wallet_manager, 
                budget_manager=self.budget_manager, # Pass the instance from UserDashboard
                notification_manager=self.notification_manager # Pass the instance from UserDashboard
            )
            self.transaction_form = UserTransactionForm(self.user_manager, self.transaction_manager, self.category_manager, self.wallet_manager)
            self.transaction_history = UserTransactionHistory(self.user_manager, self.transaction_manager, self.category_manager, self.wallet_manager)
            self.report_tab = UserReport(self.user_manager, self.transaction_manager, self.category_manager)
            self.budget_tab = UserBudget(self.user_manager, self.transaction_manager, self.category_manager, self.wallet_manager, self.budget_manager)
            self.category_tab = UserCategoryTab(self.category_manager, user_id, reload_callback=self.reload_categories)
            self.notifications_tab = NotificationCenter(self.user_manager, self.notification_manager) # Pass notification_manager
            self.settings_tab = UserSettings(self.user_manager, self.wallet_manager, self.category_manager)
            self.profile_tab = UserProfile(self.user_manager)
            
            # Clear existing widgets
            while self.content_stack.count():
                widget = self.content_stack.widget(0)
                self.content_stack.removeWidget(widget)
                widget.deleteLater()
            
            # Add tabs to content stack
            self.content_stack.addWidget(self.overview_tab)
            self.content_stack.addWidget(self.transaction_form)
            self.content_stack.addWidget(self.transaction_history)
            self.content_stack.addWidget(self.report_tab)
            self.content_stack.addWidget(self.budget_tab)
            self.content_stack.addWidget(self.category_tab)
            self.content_stack.addWidget(self.notifications_tab)
            self.content_stack.addWidget(self.settings_tab)
            self.content_stack.addWidget(self.profile_tab)
            
            print(f"DEBUG: User dashboard setup complete, {self.content_stack.count()} tabs added")
            
            # Setup Quick Actions
            self.setup_quick_actions()
            
        except Exception as e:
            print(f"Error setting up user content: {e}")
            import traceback
            traceback.print_exc()
    
    def on_tab_changed(self, index):
        """Called when tab is changed"""
        try:
            if not hasattr(self, 'content_stack') or self.content_stack.count() == 0:
                print("DEBUG: Content stack not initialized")
                return
                
            print(f"DEBUG: Switching to tab index {index}")
            if 0 <= index < self.content_stack.count():
                self.content_stack.setCurrentIndex(index)
                
                # Refresh data for specific tabs
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
                elif index == 8:  # Profile tab
                    if hasattr(self.profile_tab, 'load_user_data'):
                        self.profile_tab.load_user_data()
            else:
                print(f"DEBUG: Invalid tab index {index}")
        except Exception as e:
            print(f"Error in on_tab_changed: {e}")
            import traceback
            traceback.print_exc()
    
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
                from gui.user.user_notifications_tab import show_welcome_message
                show_welcome_message(self.current_user, self)
            except Exception as e:
                print(f"Error showing welcome toast: {e}")
    
    def show_profile(self):
        """Show profile tab"""
        self.switch_tab(8)  # Profile tab is now at index 8 (9th item in the list)
    def set_current_user(self, user):
        """Set current user, update managers, and setup UI content"""
        super().set_current_user(user) # This should set self.current_user in BaseDashboard

        # Ensure user_manager also has the current user object if it's designed to hold it
        if hasattr(self.user_manager, 'current_user'):
            self.user_manager.current_user = user
        
        user_id = None
        if self.current_user: # Access self.current_user set by BaseDashboard
            user_id = self.current_user.get('id') or self.current_user.get('user_id')
        
        if user_id:
            # Consistently set current_user_id in all relevant managers
            managers_to_update = [
                self.user_manager, self.category_manager, self.transaction_manager,
                self.budget_manager, self.notification_manager
            ]
            if self.wallet_manager: # If wallet_manager is ever not None
                managers_to_update.append(self.wallet_manager)

            for manager in managers_to_update:
                if manager: # Ensure manager is not None
                    if hasattr(manager, 'current_user_id'):
                        manager.current_user_id = user_id
                    elif hasattr(manager, 'set_current_user_id'): # If it has a setter method
                        manager.set_current_user_id(user_id)

            print(f"DEBUG: UserDashboard.set_current_user - user_id set to {user_id} in managers")
            
            # Now that user_id is set and managers are updated, setup/refresh content
            self.setup_user_content() 
        else:
            print("DEBUG: UserDashboard.set_current_user - user_id not found in user object. Clearing content.")
            # Clear or show placeholder in content_stack if user becomes None or invalid
            if hasattr(self, 'content_stack'):
                 while self.content_stack.count():
                    widget = self.content_stack.widget(0)
                    self.content_stack.removeWidget(widget)
                    widget.deleteLater()
            
        self.update_dashboard() # General refresh, should use the new user context
        # Show welcome toast after a short delay
        QTimer.singleShot(1000, self.show_welcome_toast)
    
    def setup_quick_actions(self):
        """Setup Quick Actions Floating Action Button"""
        try:
            # Add quick actions to the main dashboard widget
            self.quick_actions = add_quick_actions_to_widget(self)
            
            # Connect quick action signals to corresponding tabs
            self.quick_actions.add_income_requested.connect(self.handle_add_income)
            self.quick_actions.add_expense_requested.connect(self.handle_add_expense)
            self.quick_actions.view_report_requested.connect(self.handle_view_report)
            self.quick_actions.view_budget_requested.connect(self.handle_view_budget)
            
            print("DEBUG: Quick actions setup complete")
            
        except Exception as e:
            print(f"Error setting up quick actions: {e}")
    
    def handle_add_income(self):
        """Handle quick action: Add Income"""
        self.switch_tab(1)  # Switch to transaction form
        # Pre-select income type if possible
        try:
            if hasattr(self.transaction_form, 'transaction_type_combo'):
                self.transaction_form.transaction_type_combo.setCurrentText("Thu nhập")
        except Exception as e:
            print(f"Error setting income type: {e}")
    
    def handle_add_expense(self):
        """Handle quick action: Add Expense"""
        self.switch_tab(1)  # Switch to transaction form
        # Pre-select expense type if possible
        try:
            if hasattr(self.transaction_form, 'transaction_type_combo'):
                self.transaction_form.transaction_type_combo.setCurrentText("Chi tiêu")
        except Exception as e:
            print(f"Error setting expense type: {e}")
    
    def handle_view_report(self):
        """Handle quick action: View Report"""
        self.switch_tab(3)  # Switch to report tab
    
    def handle_view_budget(self):
        """Handle quick action: View Budget"""
        self.switch_tab(4)  # Switch to budget tab
