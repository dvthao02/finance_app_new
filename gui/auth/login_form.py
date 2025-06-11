print('[DEBUG] login_form.py loaded')
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QWidget, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import os

try:
    from data_manager.user_manager import UserManager
    print('[DEBUG] UserManager import OK')
except Exception as e:
    print('[ERROR] Lỗi import UserManager:', e)
    import traceback
    traceback.print_exc()
    raise

class LoginForm(QDialog):
    login_success = pyqtSignal(str)

    def __init__(self, parent=None):
        print('[DEBUG] LoginForm __init__ start')
        super().__init__(parent)
        print('[DEBUG] super().__init__ done')
        
        try:
            self.user_manager = UserManager()
            print('[DEBUG] UserManager created')
        except Exception as e:
            print('[ERROR] Lỗi khi khởi tạo UserManager:', e)
            import traceback
            traceback.print_exc()
            raise
            
        self.init_ui()
        print('[DEBUG] init_ui done')   
    def init_ui(self):
        print('[DEBUG] LoginForm init_ui start')
        self.setWindowTitle("Đăng nhập tài khoản")
        try:
            icon_path = self.get_asset_path("app_icon.png")
            print(f'[DEBUG] Icon path: {icon_path}')
            self.setWindowIcon(QIcon(icon_path))
            print('[DEBUG] Icon set successfully')
        except Exception as e:
            print(f'[ERROR] Could not set icon: {e}')
        self.setFixedSize(400, 450)

        self.setStyleSheet("QDialog { background-color: #f0f0f0; }")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(5, 5, 5, 5)
        self.main_layout.setAlignment(Qt.AlignCenter)

        login_card = QWidget()
        login_card.setFixedWidth(380)
        login_card.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 12px;
            }
        """)
        card_layout = QVBoxLayout(login_card)
        card_layout.setContentsMargins(25, 20, 25, 20)
        card_layout.setSpacing(18)

        title = QLabel("Đăng nhập tài khoản")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #333333; 
            margin-top: 5px;
            margin-bottom: 20px;
        """)
        card_layout.addWidget(title)

        # Email hoặc Tên đăng nhập
        id_label = QLabel("Email hoặc Tên đăng nhập")
        id_label.setStyleSheet("font-size: 14px; font-weight: bold; border: none; margin-bottom: 2px;")
        self.id_input = QLineEdit()
        self.id_input.setPlaceholderText("Nhập email hoặc tên đăng nhập")
        self.id_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 1px solid #1a73e8;
                background-color: white;
            }
        """)
        self.id_input.setFixedHeight(40)
        card_layout.addWidget(id_label)
        card_layout.addWidget(self.id_input)

        # Password
        password_label = QLabel("Mật khẩu")
        password_label.setStyleSheet("font-size: 14px; font-weight: bold; border: none; margin-bottom: 2px; margin-top: 5px;")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Nhập mật khẩu")
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                font-size: 14px;
                border: 1px solid #cccccc;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 1px solid #1a73e8;
                background-color: white;
            }
        """)
        self.password_input.setFixedHeight(40)

        # Toggle password visibility
        try:
            self.toggle_password_action = QAction(self)
            self.toggle_password_action.setIcon(QIcon(self.get_asset_path('eye_closed.png')))
            self.toggle_password_action.setToolTip("Hiện/Ẩn mật khẩu")
            self.toggle_password_action.triggered.connect(self.toggle_password_visibility)
            self.password_input.addAction(self.toggle_password_action, QLineEdit.TrailingPosition)
            print('[DEBUG] Password toggle action added')
        except Exception as e:
            print(f'[ERROR] Could not add password toggle: {e}')

        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_input)
        card_layout.addSpacing(15)

        # Login button
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.setFixedHeight(40)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #1256A1;
            }
        """)
        self.login_button.clicked.connect(self.handle_login)
        card_layout.addWidget(self.login_button)

        # Forgot password button
        self.forgot_button = QPushButton("Quên mật khẩu?")
        self.forgot_button.setCursor(Qt.PointingHandCursor)
        self.forgot_button.setStyleSheet("color: #1A73E8; border: none; background: transparent; font-size: 13px;")
        self.forgot_button.clicked.connect(self.show_forgot_password_dialog)
        card_layout.addWidget(self.forgot_button)

        # Register button
        self.register_button = QPushButton("Chưa có tài khoản? Đăng ký ngay")
        self.register_button.setCursor(Qt.PointingHandCursor)
        self.register_button.setStyleSheet("""
            QPushButton {
                color: #1A73E8; 
                border: none; 
                background-color: transparent;
                font-size: 13px;
                padding-top: 8px;
            }
            QPushButton:hover {
                text-decoration: underline;
            }
        """)
        self.register_button.clicked.connect(self.show_register_form)
        card_layout.addWidget(self.register_button)

        self.main_layout.addWidget(login_card)
        print('[DEBUG] LoginForm init_ui end')

    def handle_login(self):
        print('[DEBUG] handle_login called')
        identifier = self.id_input.text().strip()
        password = self.password_input.text()
        
        if not identifier or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập email hoặc tên đăng nhập và mật khẩu")
            return
            
        try:
            result = self.user_manager.authenticate_user(identifier, password)
            print(f'[DEBUG] Authentication result: {result}')
            
            if result.get("status") == "success":
                user = result["user"]
                print(f'[DEBUG] Login successful for user: {user.get("user_id")}')
                self.login_success.emit(user["user_id"])
                self.accept()
            else:
                QMessageBox.critical(self, "Đăng nhập thất bại", result.get("message", "Email/tên đăng nhập hoặc mật khẩu không đúng"))
        except Exception as e:
            print(f'[ERROR] Error during authentication: {e}')
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Lỗi", "Có lỗi xảy ra trong quá trình đăng nhập")

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.handle_login()

    def get_asset_path(self, filename):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_path, "assets", filename)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            try:
                self.toggle_password_action.setIcon(QIcon(self.get_asset_path('eye_open.png')))
            except:
                pass
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            try:
                self.toggle_password_action.setIcon(QIcon(self.get_asset_path('eye_closed.png')))
            except:
                pass

    def show_register_form(self):
        try:
            from gui.auth.register_form import RegisterForm
            register_form = RegisterForm(self)
            register_form.register_success.connect(self.on_register_success_from_dialog)
            
            dialog_result = register_form.exec_()
            
            self.activateWindow()
        except Exception as e:
            print(f'[ERROR] Could not show register form: {e}')
            QMessageBox.warning(self, "Lỗi", "Không thể mở form đăng ký")

    def on_register_success_from_dialog(self, user_id):
        # Đã thông báo ở RegisterForm, không cần thông báo lại ở đây
        pass

    def show_forgot_password_dialog(self):
        try:
            from PyQt5.QtWidgets import QInputDialog
            identifier, ok = QInputDialog.getText(self, "Quên mật khẩu", "Nhập email hoặc tên đăng nhập để nhận mã đặt lại mật khẩu:")
            if ok and identifier:
                result = self.user_manager.generate_reset_code(identifier.strip())
                if result["status"] == "success":
                    QMessageBox.information(self, "Gửi mã thành công", result["message"])
                    # Bổ sung: Cho phép nhập mã xác nhận và mật khẩu mới
                    code, ok2 = QInputDialog.getText(self, "Mã xác nhận", "Nhập mã xác nhận đã nhận:")
                    if not (ok2 and code):
                        return
                    new_password, ok3 = QInputDialog.getText(self, "Mật khẩu mới", "Nhập mật khẩu mới:")
                    if not (ok3 and new_password):
                        return
                    reset_result = self.user_manager.reset_password_with_code(identifier.strip(), code.strip(), new_password)
                    if reset_result["status"] == "success":
                        QMessageBox.information(self, "Thành công", reset_result["message"])
                    else:
                        QMessageBox.warning(self, "Lỗi", reset_result["message"])
                else:
                    QMessageBox.warning(self, "Lỗi", result["message"])
        except Exception as e:
            print(f'[ERROR] Error in forgot password dialog: {e}')
            QMessageBox.warning(self, "Lỗi", "Có lỗi xảy ra khi xử lý quên mật khẩu")
