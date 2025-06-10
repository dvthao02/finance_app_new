from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                             QPushButton, QMessageBox, QFrame, QAction, QInputDialog)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
import os
from data_manager.user_manager import UserManager


class RegisterForm(QDialog):
    """Form đăng ký người dùng mới"""
    register_success = pyqtSignal(str)  # Changed to emit user_id like login
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user_manager = UserManager()  # Add user_manager instance
        self.setWindowTitle("Đăng Ký Tài Khoản")
        self.setWindowIcon(QIcon(self.get_asset_path("app_icon.png")))
        self.setFixedSize(400, 720)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        self.setStyleSheet("QDialog { background-color: #f0f0f0; }")
        self.setup_ui()

    def get_asset_path(self, filename):
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        return os.path.join(base_path, "assets", filename)

    def validate_email(self):
        email = self.email_edit.text().strip()
        if not email:
            self.email_error_label.setText("Vui lòng nhập email.")
            self.email_error_label.show()
            return False
        elif not "@" in email or not "." in email:
            self.email_error_label.setText("Email không hợp lệ.")
            self.email_error_label.show()
            return False
        self.email_error_label.hide()
        return True

    def validate_fullname(self):
        fullname = self.fullname_edit.text().strip()
        if not fullname:
            self.fullname_error_label.setText("Vui lòng nhập họ và tên.")
            self.fullname_error_label.show()
            return False
        self.fullname_error_label.hide()
        return True

    def validate_username(self):
        username = self.username_edit.text().strip()
        if not username:
            self.username_error_label.setText("Vui lòng nhập tên đăng nhập.")
            self.username_error_label.show()
            return False
        elif len(username) < 4:
            self.username_error_label.setText("Tên đăng nhập phải có ít nhất 4 ký tự.")
            self.username_error_label.show()
            return False
        self.username_error_label.hide()
        return True

    def validate_password(self):
        password = self.password_edit.text()
        if not password:
            self.password_error_label.setText("Vui lòng nhập mật khẩu.")
            self.password_error_label.show()
            return False
        
        # Kiểm tra độ mạnh của mật khẩu
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(not c.isalnum() for c in password)
        
        if len(password) < 8 or not (has_upper and has_lower and has_digit and has_special):
            self.password_error_label.setText("Mật khẩu không đủ mạnh. Vui lòng đảm bảo các yêu cầu.")
            self.password_error_label.show()
            return False
        
        self.password_error_label.hide()
        return True

    def validate_confirm_password(self):
        password = self.password_edit.text()
        confirm = self.confirm_edit.text()
        if not confirm:
            self.confirm_error_label.setText("Vui lòng xác nhận mật khẩu.")
            self.confirm_error_label.show()
            return False
        elif password != confirm:
            self.confirm_error_label.setText("Mật khẩu xác nhận không khớp.")
            self.confirm_error_label.show()
            return False
        self.confirm_error_label.hide()
        return True

    def setup_ui(self):
        """Thiết lập giao diện người dùng"""
        dialog_main_layout = QVBoxLayout(self)
        dialog_main_layout.setContentsMargins(5, 5, 5, 5)
        dialog_main_layout.setAlignment(Qt.AlignCenter)

        # Form container (white card)
        form_card = QFrame()
        form_card.setFixedWidth(380)
        form_card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
            }
        """)
        
        card_layout = QVBoxLayout(form_card)
        card_layout.setContentsMargins(25, 20, 25, 20)
        card_layout.setSpacing(15)

        # Title
        title = QLabel("ĐĂNG KÝ TÀI KHOẢN")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #1a73e8;
            margin-top: 5px;
            margin-bottom: 20px;
        """)
        card_layout.addWidget(title)

        # Standard error label style
        error_label_style = "font-size: 11px; color: red; border: none; margin-top: 1px; margin-bottom: 3px;"

        # Email
        email_label = QLabel("Email *")
        email_label.setStyleSheet("font-size: 14px; font-weight: bold; border: none; margin-bottom: 2px;")
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("Nhập email")
        self.email_edit.setStyleSheet("""
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
        self.email_edit.setFixedHeight(40)
        self.email_error_label = QLabel()
        self.email_error_label.setStyleSheet(error_label_style)
        self.email_error_label.setWordWrap(True)
        self.email_error_label.hide()
        card_layout.addWidget(email_label)
        card_layout.addWidget(self.email_edit)
        card_layout.addWidget(self.email_error_label)
        self.email_edit.textChanged.connect(self.validate_email)

        # Username
        username_label = QLabel("Tên đăng nhập *")
        username_label.setStyleSheet("font-size: 14px; font-weight: bold; border: none; margin-bottom: 2px;")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Nhập tên đăng nhập (ít nhất 4 ký tự)")
        self.username_edit.setStyleSheet("""
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
        self.username_edit.setFixedHeight(40)
        self.username_error_label = QLabel()
        self.username_error_label.setStyleSheet(error_label_style)
        self.username_error_label.setWordWrap(True)
        self.username_error_label.hide()
        card_layout.addWidget(username_label)
        card_layout.addWidget(self.username_edit)
        card_layout.addWidget(self.username_error_label)
        self.username_edit.textChanged.connect(self.validate_username)

        # Fullname
        fullname_label = QLabel("Họ và tên *")
        fullname_label.setStyleSheet("font-size: 14px; font-weight: bold; border: none; margin-bottom: 2px; margin-top: 5px;")
        self.fullname_edit = QLineEdit()
        self.fullname_edit.setPlaceholderText("Nhập họ và tên")
        self.fullname_edit.setStyleSheet("""
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
        self.fullname_edit.setFixedHeight(40)
        self.fullname_error_label = QLabel()
        self.fullname_error_label.setStyleSheet(error_label_style)
        self.fullname_error_label.setWordWrap(True)
        self.fullname_error_label.hide()
        card_layout.addWidget(fullname_label)
        card_layout.addWidget(self.fullname_edit)
        card_layout.addWidget(self.fullname_error_label)
        self.fullname_edit.textChanged.connect(self.validate_fullname)

        # Password
        password_label = QLabel("Mật khẩu *")
        password_label.setStyleSheet("font-size: 14px; font-weight: bold; border: none; margin-bottom: 2px; margin-top: 5px;")
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Nhập mật khẩu")
        self.password_edit.setStyleSheet("""
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
        self.password_edit.setFixedHeight(40)
        self.toggle_password_action = QAction(self)
        self.toggle_password_action.setIcon(QIcon(self.get_asset_path('eye_closed.png')))
        self.toggle_password_action.setToolTip("Hiện/Ẩn mật khẩu")
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)
        self.password_edit.addAction(self.toggle_password_action, QLineEdit.TrailingPosition)
        self.password_error_label = QLabel()
        self.password_error_label.setStyleSheet(error_label_style)
        self.password_error_label.setWordWrap(True)
        self.password_error_label.hide()
        card_layout.addWidget(password_label)
        card_layout.addWidget(self.password_edit)
        card_layout.addWidget(self.password_error_label)
        self.password_edit.textChanged.connect(self.validate_password)

        # Confirm Password
        confirm_label = QLabel("Xác nhận mật khẩu *")
        confirm_label.setStyleSheet("font-size: 14px; font-weight: bold; border: none; margin-bottom: 2px; margin-top: 5px;")
        self.confirm_edit = QLineEdit()
        self.confirm_edit.setEchoMode(QLineEdit.Password)
        self.confirm_edit.setPlaceholderText("Nhập lại mật khẩu")
        self.confirm_edit.setStyleSheet("""
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
        self.confirm_edit.setFixedHeight(40)
        self.toggle_confirm_action = QAction(self)
        self.toggle_confirm_action.setIcon(QIcon(self.get_asset_path('eye_closed.png')))
        self.toggle_confirm_action.setToolTip("Hiện/Ẩn mật khẩu")
        self.toggle_confirm_action.triggered.connect(self.toggle_confirm_visibility)
        self.confirm_edit.addAction(self.toggle_confirm_action, QLineEdit.TrailingPosition)
        self.confirm_error_label = QLabel()
        self.confirm_error_label.setStyleSheet(error_label_style)
        self.confirm_error_label.setWordWrap(True)
        self.confirm_error_label.hide()
        card_layout.addWidget(confirm_label)
        card_layout.addWidget(self.confirm_edit)
        card_layout.addWidget(self.confirm_error_label)
        self.confirm_edit.textChanged.connect(self.validate_confirm_password)

        # Register button
        register_btn = QPushButton("Đăng ký")
        register_btn.setFixedHeight(40)
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #1976D2;
                color: white;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                border: none;
            }
            QPushButton:hover { background-color: #1565C0; }
            QPushButton:pressed { background-color: #1256A1; }
        """)
        register_btn.clicked.connect(self.register)
        card_layout.addWidget(register_btn)

        # Login link
        login_btn = QPushButton("Đã có tài khoản? Đăng nhập ngay")
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.setStyleSheet("""
            QPushButton {
                color: #1A73E8; 
                border: none; 
                background-color: transparent;
                font-size: 13px;
                padding-top: 8px;
            }
            QPushButton:hover { text-decoration: underline; }
        """)
        login_btn.clicked.connect(self.accept)
        card_layout.addWidget(login_btn)

        dialog_main_layout.addWidget(form_card)

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        if self.password_edit.echoMode() == QLineEdit.Password:
            self.password_edit.setEchoMode(QLineEdit.Normal)
            self.toggle_password_action.setIcon(QIcon(self.get_asset_path('eye_open.png')))
        else:
            self.password_edit.setEchoMode(QLineEdit.Password)
            self.toggle_password_action.setIcon(QIcon(self.get_asset_path('eye_closed.png')))

    def toggle_confirm_visibility(self):
        """Toggle confirm password visibility"""
        if self.confirm_edit.echoMode() == QLineEdit.Password:
            self.confirm_edit.setEchoMode(QLineEdit.Normal)
            self.toggle_confirm_action.setIcon(QIcon(self.get_asset_path('eye_open.png')))
        else:
            self.confirm_edit.setEchoMode(QLineEdit.Password)
            self.toggle_confirm_action.setIcon(QIcon(self.get_asset_path('eye_closed.png')))

    def register(self):
        """Xử lý đăng ký"""
        # Validate all fields
        is_valid = all([
            self.validate_email(),
            self.validate_username(),
            self.validate_fullname(),
            self.validate_password(),
            self.validate_confirm_password()
        ])
        
        if not is_valid:
            return

        # Call to UserManager
        result = self.user_manager.add_user(
            email=self.email_edit.text().strip(),
            username=self.username_edit.text().strip(),
            password=self.password_edit.text(),
            full_name=self.fullname_edit.text().strip()
        )

        if result.get("status") == "success":
            QMessageBox.information(
                self,
                "Đăng ký thành công",
                "Tài khoản đã được tạo thành công. Bạn có thể đăng nhập ngay.",
                QMessageBox.Ok
            )
            self.register_success.emit(result["user"]["user_id"])
            self.accept()
        else:
            error_message = result.get("message", "Không thể tạo tài khoản.")
            if "email" in error_message.lower():
                self.email_error_label.setText(error_message)
                self.email_error_label.show()
            elif "tên đăng nhập" in error_message.lower() or "username" in error_message.lower():
                self.username_error_label.setText(error_message)
                self.username_error_label.show()
            elif "mật khẩu" in error_message.lower():
                self.password_error_label.setText(error_message)
                self.password_error_label.show()
            else:
                QMessageBox.warning(
                    self,
                    "Đăng ký thất bại",
                    error_message,
                    QMessageBox.Ok
                )

    def show_reset_password_dialog(self):
        identifier, ok = QInputDialog.getText(self, "Đặt lại mật khẩu", "Nhập email hoặc tên đăng nhập:")
        if not (ok and identifier):
            return
        code, ok2 = QInputDialog.getText(self, "Mã xác nhận", "Nhập mã xác nhận đã nhận:")
        if not (ok2 and code):
            return
        new_password, ok3 = QInputDialog.getText(self, "Mật khẩu mới", "Nhập mật khẩu mới:")
        if not (ok3 and new_password):
            return
        result = self.user_manager.reset_password_with_code(identifier.strip(), code.strip(), new_password)
        if result["status"] == "success":
            QMessageBox.information(self, "Thành công", result["message"])
        else:
            QMessageBox.warning(self, "Lỗi", result["message"])

    def keyPressEvent(self, event):
        """Handle key press events"""
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.register()