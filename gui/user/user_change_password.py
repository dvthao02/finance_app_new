from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QFrame, QMessageBox, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from datetime import datetime
import os

class ChangePasswordDialog(QDialog):
    """
    Dialog đổi mật khẩu cho user với giao diện nền trắng, tối giản, có nút ẩn/hiện mật khẩu.
    """
    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.current_user = getattr(user_manager, 'current_user', {})
        self.show_pwd = False
        self.show_new_pwd = False
        self.show_confirm_pwd = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('🔑 Đổi mật khẩu')
        self.setFixedSize(420, 520)
        self.setModal(True)
        self.setStyleSheet("QDialog { background-color: white; }")

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(28, 22, 28, 22)

        # Header
        header_label = QLabel('🔑 Đổi mật khẩu')
        header_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #374151; margin-bottom: 8px;")
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)

        # Form
        form_frame = QFrame()
        form_frame.setStyleSheet("QFrame { background-color: #fff; border-radius: 10px; border: 1px solid #e2e8f0; padding: 18px; }")
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(14)

        input_style = """
            QLineEdit {
                padding: 12px 14px;
                border: 1.2px solid #e2e8f0;
                border-radius: 7px;
                font-size: 15px;
                background-color: #f8fafc;
            }
            QLineEdit:focus {
                border-color: #1976D2;
                background-color: #fff;
            }
        """
        label_style = "color: #374151; font-weight: 600; font-size: 14px; margin-bottom: 2px;"

        # Current password
        current_pwd_label = QLabel('🔒 Mật khẩu hiện tại:')
        current_pwd_label.setStyleSheet(label_style + "border: none; background: none; padding: 0; margin-top: 0; margin-bottom: 2px;")
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.Password)
        self.current_password.setStyleSheet(input_style)
        self.current_password.setPlaceholderText('Nhập mật khẩu hiện tại')
        # Toggle action
        self.toggle_pwd_action = QAction(self)
        self.toggle_pwd_action.setIcon(QIcon(self.get_eye_icon(False)))
        self.toggle_pwd_action.setToolTip("Hiện/Ẩn mật khẩu")
        self.toggle_pwd_action.triggered.connect(self.toggle_current_pwd)
        self.current_password.addAction(self.toggle_pwd_action, QLineEdit.TrailingPosition)

        # New password
        new_pwd_label = QLabel('🔑 Mật khẩu mới:')
        new_pwd_label.setStyleSheet(label_style + "border: none; background: none; padding: 0; margin-top: 0; margin-bottom: 2px;")
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setStyleSheet(input_style)
        self.new_password.setPlaceholderText('Nhập mật khẩu mới (tối thiểu 6 ký tự)')
        self.toggle_new_pwd_action = QAction(self)
        self.toggle_new_pwd_action.setIcon(QIcon(self.get_eye_icon(False)))
        self.toggle_new_pwd_action.setToolTip("Hiện/Ẩn mật khẩu")
        self.toggle_new_pwd_action.triggered.connect(self.toggle_new_pwd)
        self.new_password.addAction(self.toggle_new_pwd_action, QLineEdit.TrailingPosition)

        # Confirm password
        confirm_pwd_label = QLabel('🔐 Xác nhận mật khẩu:')
        confirm_pwd_label.setStyleSheet(label_style + "border: none; background: none; padding: 0; margin-top: 0; margin-bottom: 2px;")
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setStyleSheet(input_style)
        self.confirm_password.setPlaceholderText('Nhập lại mật khẩu mới')
        self.toggle_confirm_pwd_action = QAction(self)
        self.toggle_confirm_pwd_action.setIcon(QIcon(self.get_eye_icon(False)))
        self.toggle_confirm_pwd_action.setToolTip("Hiện/Ẩn mật khẩu")
        self.toggle_confirm_pwd_action.triggered.connect(self.toggle_confirm_pwd)
        self.confirm_password.addAction(self.toggle_confirm_pwd_action, QLineEdit.TrailingPosition)

        # Add to form layout
        form_layout.addWidget(current_pwd_label)
        form_layout.addWidget(self.current_password)
        form_layout.addWidget(new_pwd_label)
        form_layout.addWidget(self.new_password)
        form_layout.addWidget(confirm_pwd_label)
        form_layout.addWidget(self.confirm_password)
        form_frame.setLayout(form_layout)
        layout.addWidget(form_frame)

        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(12)
        btn_cancel = QPushButton('❌ Hủy')
        btn_cancel.setStyleSheet("""
            QPushButton { background: #6b7280; color: white; border: none; border-radius: 7px; padding: 11px 22px; font-weight: 600; font-size: 14px; }
            QPushButton:hover { background: #4b5563; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_save = QPushButton('🔑 Đổi mật khẩu')
        btn_save.setStyleSheet("""
            QPushButton { background: #1976D2; color: white; border: none; border-radius: 7px; padding: 11px 22px; font-weight: 600; font-size: 14px; }
            QPushButton:hover { background: #1256A1; }
        """)
        btn_save.clicked.connect(self.change_password)
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_save)
        layout.addLayout(buttons_layout)
        self.setLayout(layout)

    def get_eye_icon(self, is_open):
        # Trả về đường dẫn icon con mắt (open/closed)
        base_dir = os.path.join(os.path.dirname(__file__), '../../assets/function')
        if is_open:
            return os.path.abspath(os.path.join(base_dir, 'eye_open.png'))
        else:
            return os.path.abspath(os.path.join(base_dir, 'eye_closed.png'))

    def toggle_current_pwd(self):
        self.show_pwd = not self.show_pwd
        self.current_password.setEchoMode(QLineEdit.Normal if self.show_pwd else QLineEdit.Password)
        self.toggle_pwd_action.setIcon(QIcon(self.get_eye_icon(self.show_pwd)))

    def toggle_new_pwd(self):
        self.show_new_pwd = not self.show_new_pwd
        self.new_password.setEchoMode(QLineEdit.Normal if self.show_new_pwd else QLineEdit.Password)
        self.toggle_new_pwd_action.setIcon(QIcon(self.get_eye_icon(self.show_new_pwd)))

    def toggle_confirm_pwd(self):
        self.show_confirm_pwd = not self.show_confirm_pwd
        self.confirm_password.setEchoMode(QLineEdit.Normal if self.show_confirm_pwd else QLineEdit.Password)
        self.toggle_confirm_pwd_action.setIcon(QIcon(self.get_eye_icon(self.show_confirm_pwd)))

    def validate_current_password(self, password):
        """Kiểm tra mật khẩu hiện tại bằng bcrypt"""
        user = self.user_manager.get_current_user()
        if not user:
            return False
        current_password_hash = user.get('password', '')
        return self.user_manager.check_password(password, current_password_hash)

    def change_password(self):
        """Xử lý đổi mật khẩu"""
        try:
            # Get input values
            current_pwd = self.current_password.text().strip()
            new_pwd = self.new_password.text().strip()
            confirm_pwd = self.confirm_password.text().strip()
            
            # Validate inputs
            if not current_pwd:
                QMessageBox.warning(self, '⚠️ Lỗi', 'Vui lòng nhập mật khẩu hiện tại!')
                self.current_password.setFocus()
                return
            
            if not new_pwd:
                QMessageBox.warning(self, '⚠️ Lỗi', 'Vui lòng nhập mật khẩu mới!')
                self.new_password.setFocus()
                return
            
            if len(new_pwd) < 6:
                QMessageBox.warning(self, '⚠️ Lỗi', 'Mật khẩu mới phải có ít nhất 6 ký tự!')
                self.new_password.setFocus()
                return
            
            if new_pwd != confirm_pwd:
                QMessageBox.warning(self, '⚠️ Lỗi', 'Mật khẩu xác nhận không khớp!')
                self.confirm_password.setFocus()
                return
            
            # Verify current password
            if not self.validate_current_password(current_pwd):
                QMessageBox.warning(self, '⚠️ Lỗi', 'Mật khẩu hiện tại không đúng!')
                self.current_password.setFocus()
                self.current_password.selectAll()
                return
            
            # Hash new password bằng bcrypt
            new_password_hash = self.user_manager.hash_password(new_pwd)
            
            # Update user data
            user = self.user_manager.get_current_user()
            user_id = user.get('id') or user.get('user_id')
            # Cập nhật mật khẩu mới vào user
            users = self.user_manager.load_users()
            for u in users:
                if u.get('id') == user_id or u.get('user_id') == user_id:
                    u['password'] = new_password_hash
                    u['updated_at'] = datetime.now().isoformat()
            self.user_manager.save_users(users)
            if hasattr(self.user_manager, 'users'):
                self.user_manager.users = self.user_manager.load_users()
            QMessageBox.information(self, '✅ Thành công', 
                                  'Đã đổi mật khẩu thành công!\nVui lòng ghi nhớ mật khẩu mới.')
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, '❌ Lỗi', 
                               f'Không thể đổi mật khẩu:\n{str(e)}')
