from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QComboBox, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QStackedWidget
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
import logging
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
import logging

# Impo rt the new transaction tab
from gui.user.user_transaction_tab import UserTransactionTab

class UserDashboard(BaseDashboard):
    
    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager, notification_manager, parent=None):
        super().__init__(parent) # Call superclass constructor first

        # Store manager instances
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager # Might be None
        self.notification_manager = notification_manager # Passed instance
        # Pass all required managers to BudgetManager, including user_manager
        self.budget_manager = BudgetManager(
            notification_manager=self.notification_manager, 
            category_manager=self.category_manager,
            user_manager=self.user_manager # Added user_manager
        )

        # Connect the notification_added signal to a handler
        if hasattr(self.notification_manager, 'notification_added'):
            self.notification_manager.notification_added.connect(self.handle_new_notification)

        # BaseDashboard.init_ui() should have been called by super().__init__()
        # self.current_user will be set by set_current_user()        # self.setup_user_content() will be called by set_current_user()        # Ensure content_stack exists (usually created in BaseDashboard.init_ui)
        if not hasattr(self, 'content_stack'):
            logging.warning("UserDashboard.__init__ - self.content_stack not found after super().__init__().")
            # If BaseDashboard is supposed to create it, this is an issue.
            # For now, we assume BaseDashboard's init_ui (called via super) creates self.content_stack.
    
    def get_dashboard_title(self):
        """Return the dashboard title"""
        return "Quản lý Chi Tiêu Cá Nhân"
    
    def get_navigation_items(self):
        """Return list of (text, icon_name) tuples for navigation"""
        return [
            ("Tổng quan", "overview.png"),
            ("Giao dịch", "transaction.png"),
            ("Ngân sách", "budgeting.png"),
            ("Danh mục", "categories_icon.png"),
            ("Báo cáo", "report.png"),
            ("Thông báo", "notifications_icon.png"),
            ("Cài đặt", "setting.png"),
            ("Hồ sơ", "users_icon.png"),
        ]
    
    def setup_user_content(self):
        """Setup user-specific content in the stacked widget"""
        try:
            from gui.user.user_overview_tab import UserOverviewTab
            from gui.user.user_transaction_tab import UserTransactionTab 
            from gui.user.user_budget_tab import UserBudgetTab
            from gui.user.user_category_tab import UserCategoryTab
            from gui.user.user_report_tab import UserReport
            from gui.user.user_notifications_tab import NotificationCenter 
            from gui.user.user_settings_tab import UserSettings
            from gui.user.user_profile_tab import UserProfileTab
            
            user_id = None
            # self.current_user should be set by set_current_user via super().set_current_user()
            if hasattr(self, 'current_user') and self.current_user:
                user_id = self.current_user.get('id') or self.current_user.get('user_id')
            if not user_id:
                logging.error("UserDashboard.setup_user_content - user_id is not available. Cannot create tabs.")
                # Clear existing widgets if any, to prevent using old data
                if hasattr(self, 'content_stack'):
                    while self.content_stack.count():
                        widget = self.content_stack.widget(0)
                        self.content_stack.removeWidget(widget)
                        widget.deleteLater()
                return

            logging.debug(f"UserDashboard.setup_user_content using user_id={user_id} for tabs")
            
            # Create tabs (ensure instantiation order doesn't strictly matter here, only addWidget order)
            self.overview_tab = UserOverviewTab(
                user_manager=self.user_manager, 
                transaction_manager=self.transaction_manager, 
                category_manager=self.category_manager, 
                wallet_manager=self.wallet_manager, 
                budget_manager=self.budget_manager, 
                notification_manager=self.notification_manager
            )
            
            self.transaction_tab = UserTransactionTab(
                user_manager=self.user_manager,
                transaction_manager=self.transaction_manager,
                category_manager=self.category_manager,
                wallet_manager=self.wallet_manager, 
                budget_manager=self.budget_manager,
                notification_manager=self.notification_manager
            )
            self.transaction_tab.transaction_added_or_updated.connect(self.refresh_overview_and_related_tabs)

            self.budget_tab = UserBudgetTab( # Corrected class name
                current_user_id=user_id,  # Pass user_id directly
                user_manager=self.user_manager, 
                transaction_manager=self.transaction_manager, 
                category_manager=self.category_manager, 
                wallet_manager=self.wallet_manager,
                budget_manager=self.budget_manager,
                notification_manager=self.notification_manager
            )
            if hasattr(self.budget_tab, 'budget_changed'): # Connect signal if it exists
                self.budget_tab.budget_changed.connect(self.refresh_overview_and_related_tabs) # Or a more specific handler

            self.category_tab = UserCategoryTab(self.user_manager, self.category_manager)
            self.report_tab = UserReport(self.user_manager, self.transaction_manager, self.category_manager)
            self.notifications_tab = NotificationCenter(self.user_manager, self.notification_manager)
            
            from data_manager.user_manager import UserManager
            class DummySettingsManager:
                def load_settings(self):
                    return {}
                def save_settings(self, settings):
                    pass
            # Nếu bạn đã có SettingsManager thực sự, thay DummySettingsManager bằng class thật
            self.settings_manager = DummySettingsManager()
            self.settings_tab = UserSettings(self.user_manager, self.wallet_manager, self.category_manager, self.settings_manager)
            
            self.profile_tab = UserProfileTab(self.user_manager)
            
            # Clear existing widgets
            while self.content_stack.count():
                widget = self.content_stack.widget(0)
                self.content_stack.removeWidget(widget)
                widget.deleteLater()
            
            # Add tabs to content stack in the new order
            self.content_stack.addWidget(self.overview_tab)      # 0
            self.content_stack.addWidget(self.transaction_tab)  # 1
            self.content_stack.addWidget(self.budget_tab)       # 2 
            self.content_stack.addWidget(self.category_tab)     # 3 
            self.content_stack.addWidget(self.report_tab)       # 4 
            self.content_stack.addWidget(self.notifications_tab) # 5
            self.content_stack.addWidget(self.settings_tab)     # 6
            self.content_stack.addWidget(self.profile_tab)      # 7
            logging.debug(f"User dashboard setup complete, {self.content_stack.count()} tabs added")
            
            # Setup Quick Actions
            self.setup_quick_actions()
            
        except Exception as e:
            logging.error(f"Error setting up user content: {e}")
            import traceback
            traceback.print_exc()
    
    def refresh_overview_and_related_tabs(self):
        """Refreshes tabs that depend on transaction or budget data."""
        logging.debug("UserDashboard: refresh_overview_and_related_tabs CALLED") # Changed from print
        if hasattr(self, 'overview_tab') and self.overview_tab:
            logging.debug("UserDashboard: Refreshing Overview Tab") # Changed from print
            self.overview_tab.update_dashboard()
        
        if hasattr(self, 'budget_tab') and self.budget_tab:
            logging.debug("UserDashboard: Refreshing Budget Tab") # Changed from print
            if hasattr(self.budget_tab, 'load_budgets_and_categories'):
                self.budget_tab.load_budgets_and_categories()
            elif hasattr(self.budget_tab, 'load_data_to_ui'): # Fallback for older name
                 self.budget_tab.load_data_to_ui()

        if hasattr(self, 'transaction_tab') and self.transaction_tab:
            logging.debug("UserDashboard: Refreshing Transaction Tab") # Changed from print
            if hasattr(self.transaction_tab, 'load_transactions_to_table'):
                self.transaction_tab.load_transactions_to_table()
        
        if hasattr(self, 'report_tab') and self.report_tab:
            if hasattr(self.report_tab, 'reload_data'): 
                logging.debug("UserDashboard: Refreshing Report Tab") # Changed from print
                self.report_tab.reload_data()


    def handle_new_notification(self, notification_data):
        """Handles new notifications, e.g., by showing a toast or updating the notification tab."""
        logging.info(f"UserDashboard: New notification received: {notification_data.get('title')}")
        
        # 1. Show a Toast Notification
        if hasattr(self, 'show_toast_notification'): # Check if BaseDashboard has this method
            self.show_toast_notification(
                message=f"{notification_data.get('title')}: {notification_data.get('content')}", 
                type=notification_data.get('type', 'info'),
                duration=5000 # Show for 5 seconds
            )
        else:
            # Fallback or alternative way to show toast if not in BaseDashboard
            # For example, directly creating and showing ToastNotification if it's accessible
            from .user_notifications_tab import ToastNotification # Relative import
            toast = ToastNotification(
                message=f"{notification_data.get('title')}: {notification_data.get('content')}",
                type=notification_data.get('type', 'info'),
                duration=5000,
                parent=self # Show relative to the dashboard
            )
            toast.show_notification(self) # Pass self as parent_widget for positioning

        # 2. Refresh the NotificationCenter tab if it's created and visible or active
        if hasattr(self, 'notifications_tab') and self.notifications_tab:
            # Option A: Always reload data (simplest)
            if hasattr(self.notifications_tab, 'load_notifications'):
                self.notifications_tab.load_notifications()
                logging.debug("UserDashboard: Refreshed NotificationCenter tab due to new notification.")
            
            # Option B: Reload only if the tab is currently visible (more complex, might need to check self.content_stack.currentWidget())
            # current_widget = self.content_stack.currentWidget()
            # if current_widget == self.notifications_tab:
            #     if hasattr(self.notifications_tab, 'load_notifications'):
            #         self.notifications_tab.load_notifications()
            #         logging.debug("UserDashboard: Refreshed visible NotificationCenter tab.")

        # 3. Optionally, update a badge count on the "Thông báo" navigation button
        # This is more complex and would require the navigation buttons to support badges.
        # For now, we'll skip this, but it's a potential enhancement.

    def on_tab_changed(self, index):
        """Called when tab is changed"""
        # New mapping based on get_navigation_items():
        # 0: Tổng quan
        # 1: Giao dịch
        # 2: Ngân sách (NEW ORDER)
        # 3: Danh mục (NEW ORDER)
        # 4: Báo cáo (NEW ORDER)
        # 5: Thông báo
        # 6: Cài đặt
        # 7: Hồ sơ

        nav_items = self.get_navigation_items()
        current_tab_name = nav_items[index][0] if 0 <= index < len(nav_items) else None

        try:            
            if not hasattr(self, 'content_stack') or self.content_stack.count() == 0:
                logging.debug("Content stack not initialized or empty")
                return
                
            logging.debug(f"Switching to tab index {index} (Name: {current_tab_name})")
            
            if 0 <= index < self.content_stack.count():
                self.content_stack.setCurrentIndex(index)
                current_widget = self.content_stack.widget(index) # Get current widget for safer checks

                if current_tab_name == "Tổng quan": # Index 0
                    if hasattr(self, 'overview_tab') and self.overview_tab == current_widget:
                        self.overview_tab.update_dashboard()
                elif current_tab_name == "Giao dịch": # Index 1
                    if hasattr(self, 'transaction_tab') and self.transaction_tab == current_widget:
                        pass # Manages its own state, or add a refresh if general context changes
                elif current_tab_name == "Ngân sách": # Index 2
                    if hasattr(self, 'budget_tab') and self.budget_tab == current_widget:
                        if hasattr(self.budget_tab, 'load_budgets_and_categories'): 
                            self.budget_tab.load_budgets_and_categories()
                elif current_tab_name == "Danh mục": # Index 3
                    if hasattr(self, 'category_tab') and self.category_tab == current_widget:
                        if hasattr(self.category_tab, 'reload_data'): 
                            self.category_tab.reload_data()
                elif current_tab_name == "Báo cáo": # Index 4
                    if hasattr(self, 'report_tab') and self.report_tab == current_widget:
                        if hasattr(self.report_tab, 'reload_data'):
                            self.report_tab.reload_data()
                elif current_tab_name == "Thông báo": # Index 5
                    if hasattr(self, 'notifications_tab') and self.notifications_tab == current_widget:
                        if hasattr(self.notifications_tab, 'load_notifications'):
                            self.notifications_tab.load_notifications()
                elif current_tab_name == "Cài đặt": # Index 6
                    if hasattr(self, 'settings_tab') and self.settings_tab == current_widget:
                        if hasattr(self.settings_tab, 'load_settings'): # Assuming a load_settings method
                            self.settings_tab.load_settings()
                elif current_tab_name == "Hồ sơ": # Index 7
                    if hasattr(self, 'profile_tab') and self.profile_tab == current_widget:
                        if hasattr(self.profile_tab, 'load_user_data'):
                            self.profile_tab.load_user_data()            
                        else:
                            logging.debug(f"Invalid tab index {index} for content_stack with {self.content_stack.count()} widgets")
        except Exception as e:
            logging.error(f"Error in on_tab_changed: {e}")
            import traceback
            traceback.print_exc()
    
    def reload_categories(self):
        """Callback to reload category in other tabs when there are changes"""
        try:
            if hasattr(self, 'transaction_tab') and hasattr(self.transaction_tab, 'load_categories'):
                self.transaction_tab.load_categories()
            if hasattr(self, 'overview_tab') and hasattr(self.overview_tab, 'update_dashboard'): # Overview might use categories in charts
                self.overview_tab.update_dashboard()
            if hasattr(self, 'budget_tab') and hasattr(self.budget_tab, 'load_budgets_and_categories'): # Budget tab likely needs category refresh                self.budget_tab.load_budgets_and_categories()
            # Add other tabs that depend on category list if necessary
                logging.debug("UserDashboard.reload_categories called and propagated.")
        except Exception as e:
            logging.error(f"Error in reload_categories: {e}")
            import traceback
            traceback.print_exc()

    def update_dashboard(self):
        """Update dashboard data"""
        try:
            if hasattr(self, 'overview_tab'):
                self.overview_tab.update_dashboard()
            if hasattr(self, 'transaction_tab'):
                if hasattr(self.transaction_tab, 'load_transactions_to_table'):
                    self.transaction_tab.load_transactions_to_table()
            if hasattr(self, 'report_tab'):
                if hasattr(self.report_tab, 'reload_data'):
                    self.report_tab.reload_data()        
        except Exception as e:
            logging.error(f"Error updating dashboard: {e}")
    
    def show_welcome_toast(self):
        """Show welcome message"""
        if self.current_user:
            try:
                from gui.user.user_notifications_tab import show_welcome_message                
                show_welcome_message(self.current_user, self)
            except Exception as e:
                logging.error(f"Error showing welcome toast: {e}")
    
    def show_profile(self):
        """Show profile tab"""
        self.switch_tab(7)  # Profile tab is at index 7
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
                        logging.debug(f"UserDashboard.set_current_user - user_id set to {user_id} in managers")
            
            # Now that user_id is set and managers are updated, setup/refresh content
            self.setup_user_content() 
        else:
            logging.debug("UserDashboard.set_current_user - user_id not found in user object. Clearing content.")
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
            logging.debug("Quick actions setup complete")
            
        except Exception as e:
            logging.error(f"Error setting up quick actions: {e}")
    
    def handle_add_income(self):
        """Handle quick action: Add Income"""
        self.switch_tab(1)  # Switch to transaction tab (index 1)
        try:
            if hasattr(self, 'transaction_tab') and hasattr(self.transaction_tab, 'open_add_transaction_dialog'):
                self.transaction_tab.open_add_transaction_dialog(transaction_type="income")        
        except Exception as e:
            logging.error(f"Error in handle_add_income: {e}")
    
    def handle_add_expense(self):
        """Handle quick action: Add Expense"""
        self.switch_tab(1) # Switch to transaction tab (index 1)
        try:
            if hasattr(self, 'transaction_tab') and hasattr(self.transaction_tab, 'open_add_transaction_dialog'):
                self.transaction_tab.open_add_transaction_dialog(transaction_type="expense")
        except Exception as e:
            logging.error(f"Error in handle_add_expense: {e}")
    
    def handle_view_report(self):
        """Handle quick action: View Report"""
        self.switch_tab(4)  # Switch to report tab (index 4)
    
    def handle_view_budget(self):
        """Handle quick action: View Budget"""
        self.switch_tab(2)  # Switch to budget tab (index 2)
