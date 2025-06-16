import sys
import json
from PyQt5.QtWidgets import QApplication
from gui.auth.login_form import LoginForm
from gui.admin.admin_dashboard import AdminDashboard
from gui.user.user_dashboard import UserDashboard
from datetime import datetime
from utils.file_helper import load_json, save_json
from data_manager.category_manager import CategoryManager
from data_manager.transaction_manager import TransactionManager

def main():
    app = QApplication(sys.argv)
    app.admin_dashboard = None  # Giữ tham chiếu đến admin_dashboard
    def log_history(user_id, action):
        try:
            history = load_json('data/login_history.json')
        except Exception:
            history = []
        history.append({
            'user_id': user_id,
            'action': action,
            'timestamp': datetime.now().isoformat()
        })
        save_json('data/login_history.json', history)

    def show_login():
        login = LoginForm()
        def on_login_success(user_id):
            user = login.user_manager.get_user_by_id(user_id)
            print(f"Đăng nhập thành công! Vai trò: {user.get('role')} | User ID: {user_id}")
            log_history(user_id, 'login')
            login.accept()  # Đóng form đăng nhập ngay khi đăng nhập thành công
            if user.get('role') == 'admin':
                try:
                    app.admin_dashboard = AdminDashboard()
                    app.admin_dashboard.set_current_user(user)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    return
                def on_logout():
                    log_history(user_id, 'logout')
                    if app.admin_dashboard:
                        app.admin_dashboard.close()
                        app.admin_dashboard = None
                    show_login()
                app.admin_dashboard.logout_signal.connect(on_logout)
                app.admin_dashboard.show()
                app.admin_dashboard.raise_()
                app.admin_dashboard.activateWindow()
            elif user.get('role') == 'user':
                try:
                    # Khởi tạo các manager cho user dashboard
                    category_manager = CategoryManager()
                    transaction_manager = TransactionManager()
                    app.user_dashboard = UserDashboard(
                        user_manager=login.user_manager,
                        transaction_manager=transaction_manager,
                        category_manager=category_manager,
                        wallet_manager=None
                    )
                    # Nếu muốn truyền người dùng hiện tại:
                    if hasattr(app.user_dashboard, 'set_current_user'):
                        app.user_dashboard.set_current_user(user)
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    return
                def on_logout_user():
                    log_history(user_id, 'logout')
                    if hasattr(app, 'user_dashboard') and app.user_dashboard:
                        app.user_dashboard.close()
                        app.user_dashboard = None
                    show_login()
                if hasattr(app.user_dashboard, 'logout_signal'):
                    app.user_dashboard.logout_signal.connect(on_logout_user)
                app.user_dashboard.show()
                app.user_dashboard.raise_()
                app.user_dashboard.activateWindow()
            else:
                pass # Bỏ qua nếu vai trò không xác định
        login.login_success.connect(on_login_success)
        login.exec_()
    show_login()
    app.exec_()


if __name__ == "__main__":
    main()
