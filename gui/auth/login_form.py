from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QWidget, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import os
from data_manager.user_manager import UserManager

class LoginForm(QDialog):
    login_success = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserManager()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Đăng nhập tài khoản")
        self.setWindowIcon(QIcon(self.get_asset_path("app_icon.png")))
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

        # Email hoặc Tên đăng nhập (chỉ 1 ô)
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

        self.toggle_password_action = QAction(self)
        self.toggle_password_action.setIcon(QIcon(self.get_asset_path('eye_closed.png')))
        self.toggle_password_action.setToolTip("Hiện/Ẩn mật khẩu")
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)
        self.password_input.addAction(self.toggle_password_action, QLineEdit.TrailingPosition)

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

        # Forgot password button
        self.forgot_button = QPushButton("Quên mật khẩu?")
        self.forgot_button.setCursor(Qt.PointingHandCursor)
        self.forgot_button.setStyleSheet("color: #1A73E8; border: none; background: transparent; font-size: 13px;")
        self.forgot_button.clicked.connect(self.show_forgot_password_dialog)
        card_layout.addWidget(self.forgot_button)

        self.main_layout.addWidget(login_card)

    def toggle_password_visibility(self):
        if self.password_input.echoMode() == QLineEdit.Password:
            self.password_input.setEchoMode(QLineEdit.Normal)
            self.toggle_password_action.setIcon(QIcon(self.get_asset_path('eye_open.png')))
        else:
            self.password_input.setEchoMode(QLineEdit.Password)
            self.toggle_password_action.setIcon(QIcon(self.get_asset_path('eye_closed.png')))

    def handle_login(self):
        identifier = self.id_input.text().strip()
        password = self.password_input.text()
        if not identifier or not password:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập email hoặc tên đăng nhập và mật khẩu")
            return
        result = self.user_manager.authenticate_user(identifier, password)
        if result.get("status") == "success":
            user = result["user"]
            if user.get("role") == "admin":
                # Chuyển hướng dashboard admin
                pass
            else:
                # Chuyển hướng dashboard user
                pass
            self.login_success.emit(user["user_id"])
            self.accept()
        else:
            QMessageBox.critical(self, "Đăng nhập thất bại", result.get("message", "Email/tên đăng nhập hoặc mật khẩu không đúng"))

    def show_register_form(self):
        from gui.auth.register_form import RegisterForm
        register_form = RegisterForm(self)
        register_form.register_success.connect(self.on_register_success_from_dialog)
        
        dialog_result = register_form.exec_()
        
        self.activateWindow()

    def on_register_success_from_dialog(self, user_id):
        # Đã thông báo ở RegisterForm, không cần thông báo lại ở đây
        pass

    def show_forgot_password_dialog(self):
        from PyQt5.QtWidgets import QInputDialog
        identifier, ok = QInputDialog.getText(self, "Quên mật khẩu", "Nhập email hoặc tên đăng nhập để nhận mã đặt lại mật khẩu:")
        if ok and identifier:
            result = self.user_manager.generate_reset_code(identifier.strip())
            if result["status"] == "success":
                QMessageBox.information(self, "Gửi mã thành công", result["message"])
            else:
                QMessageBox.warning(self, "Lỗi", result["message"])

    def get_asset_path(self, filename):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_path, "assets", filename)

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.handle_login()
