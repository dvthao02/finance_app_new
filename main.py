import sys
import json
from PyQt5.QtWidgets import QApplication
from gui.auth.login_form import LoginForm
from gui.admin.admin_dashboard import AdminDashboard
from datetime import datetime
from utils.file_helper import load_json, save_json

def main():
    app = QApplication(sys.argv)
    app.admin_dashboard = None  # Giữ tham chiếu admin_dashboard
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
            login.accept()  # Đóng form login ngay khi đăng nhập thành công
            if user.get('role') == 'admin':
                app.admin_dashboard = AdminDashboard()
                app.admin_dashboard.set_current_user(user)  # Gán user hiện tại cho dashboard
                def on_logout():
                    log_history(user_id, 'logout')
                    # Đóng dashboard trước khi show lại login
                    if app.admin_dashboard:
                        app.admin_dashboard.close()
                        app.admin_dashboard = None
                    show_login()
                app.admin_dashboard.logout_signal.connect(on_logout)
                app.admin_dashboard.show()
                app.admin_dashboard.raise_()
                app.admin_dashboard.activateWindow()
            else:
                # TODO: mở dashboard user
                pass
        login.login_success.connect(on_login_success)
        login.exec_()
    show_login()
    app.exec_()

if __name__ == "__main__":
    main()
