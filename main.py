import sys
import json
import logging
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMessageBox
from gui.auth.login_form import LoginForm
from gui.admin.admin_dashboard import AdminDashboard
from gui.user.user_dashboard import UserDashboard
from utils.file_helper import load_json, save_json
from data_manager.category_manager import CategoryManager
from data_manager.transaction_manager import TransactionManager
from data_manager.notification_manager import NotificationManager
from data_manager.budget_manager import BudgetManager

# Cấu hình logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ApplicationManager:
    def __init__(self):
        """Khởi tạo quản lý ứng dụng"""
        self.app = QApplication(sys.argv)
        self.admin_dashboard = None
        self.user_dashboard = None
        self.current_user = None

    def log_history(self, user_id, action):
        """Ghi lại lịch sử hoạt động của người dùng
        
        Args:
            user_id: ID của người dùng
            action: Hành động được thực hiện (login/logout)
        """
        try:
            history = load_json('data/login_history.json')
        except Exception as e:
            logger.warning(f"Không thể tải file lịch sử: {e}")
            history = []
        
        history.append({
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.now().isoformat()
        })
        
        try:
            save_json('data/login_history.json', history)
        except Exception as e:
            logger.error(f"Không thể lưu lịch sử: {e}")

    def handle_admin_login(self, user):
        """Xử lý đăng nhập cho tài khoản admin
        
        Args:
            user: Thông tin người dùng admin
        """
        try:
            self.admin_dashboard = AdminDashboard()
            self.admin_dashboard.set_current_user(user)
            self.admin_dashboard.logout_signal.connect(self.handle_admin_logout)
            self.admin_dashboard.show()
            self.admin_dashboard.raise_()
            self.admin_dashboard.activateWindow()
        except Exception as e:
            logger.error(f"Lỗi bảng điều khiển admin: {e}")
            QMessageBox.critical(None, "Lỗi", f"Không thể mở bảng điều khiển admin: {str(e)}")

    def handle_user_login(self, user, user_manager):
        """Xử lý đăng nhập cho người dùng thông thường
        
        Args:
            user: Thông tin người dùng
            user_manager: Quản lý người dùng
        """
        try:
            category_manager = CategoryManager()
            transaction_manager = TransactionManager()
            notification_manager = NotificationManager()
            budget_manager = BudgetManager() # Instantiate BudgetManager

            self.user_dashboard = UserDashboard(
                user_manager=user_manager,
                transaction_manager=transaction_manager,
                category_manager=category_manager,
                wallet_manager=None, # Explicitly None if not used yet
                # budget_manager=budget_manager, # REMOVE this line
                notification_manager=notification_manager # Pass notification_manager
            )
            
            if hasattr(self.user_dashboard, 'set_current_user'):
                self.user_dashboard.set_current_user(user)
            
            self.user_dashboard.logout_signal.connect(self.handle_user_logout)
            self.user_dashboard.show()
            self.user_dashboard.raise_()  
            self.user_dashboard.activateWindow()
        except Exception as e:
            logger.error(f"Lỗi bảng điều khiển người dùng: {e}")
            QMessageBox.critical(None, "Lỗi", f"Không thể mở bảng điều khiển người dùng: {str(e)}")

    def handle_admin_logout(self):
        """Xử lý đăng xuất cho tài khoản admin"""
        if self.current_user:
            self.log_history(self.current_user.get('id'), 'logout')
        if self.admin_dashboard:
            self.admin_dashboard.close()
            self.admin_dashboard = None
        self.show_login()

    def handle_user_logout(self):
        """Xử lý đăng xuất cho người dùng thông thường"""
        if self.current_user:
            self.log_history(self.current_user.get('id'), 'logout')
        if self.user_dashboard:
            self.user_dashboard.close()
            self.user_dashboard = None
        self.show_login()

    def on_login_success(self, user_id, user_manager):
        """Xử lý khi đăng nhập thành công
        
        Args:
            user_id: ID của người dùng
            user_manager: Quản lý người dùng
        """
        user = user_manager.get_user_by_id(user_id)
        self.current_user = user
        logger.info(f"Đăng nhập thành công! Vai trò: {user.get('role')} | ID: {user_id}")
        self.log_history(user_id, 'login')

        if user.get('role') == 'admin':
            self.handle_admin_login(user)
        elif user.get('role') == 'user':
            self.handle_user_login(user, user_manager)
        else:
            logger.warning(f"Vai trò không xác định: {user.get('role')}")

    def show_login(self):
        """Hiển thị form đăng nhập"""
        login = LoginForm()
        login.login_success.connect(lambda user_id: self.on_login_success(user_id, login.user_manager))
        login.exec_()

    def run(self):
        """Chạy ứng dụng"""
        try:
            self.show_login()
            return self.app.exec_()
        except Exception as e:
            logger.error(f"Lỗi ứng dụng: {e}")
            QMessageBox.critical(None, "Lỗi", f"Lỗi ứng dụng: {str(e)}")
            return 1

def main():
    """Hàm chính khởi chạy ứng dụng"""
    app_manager = ApplicationManager()
    sys.exit(app_manager.run())

if __name__ == "__main__":
    main()
