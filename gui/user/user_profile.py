from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QFrame, QGridLayout, QSpacerItem, QSizePolicy,
                            QMessageBox, QDateEdit, QComboBox, QTextEdit, QFileDialog)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor
import datetime
import json
import os

class UserProfile(QDialog):
    """
    Dialog hiển thị và chỉnh sửa thông tin profile của user
    """
    profile_updated = pyqtSignal()  # Signal khi cập nhật profile
    logout_requested = pyqtSignal()  # Signal khi logout
    
    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.current_user = getattr(user_manager, 'current_user', {})
        self.init_ui()
        self.load_user_data()

    def init_ui(self):
        self.setWindowTitle('👤 Thông tin cá nhân')
        self.setFixedSize(500, 650)
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header với avatar
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 25px;
                margin-bottom: 10px;
            }
        """)
        
        header_layout = QVBoxLayout()
        
        # Avatar placeholder
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(80, 80)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 0.3);
                border-radius: 40px;
                color: white;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        
        # User name
        self.header_name = QLabel()
        self.header_name.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
                margin-top: 10px;
            }
        """)
        self.header_name.setAlignment(Qt.AlignCenter)
        
        # User role
        self.header_role = QLabel()
        self.header_role.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                background: transparent;
                margin-top: 5px;
            }
        """)
        self.header_role.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(self.avatar_label, alignment=Qt.AlignCenter)
        header_layout.addWidget(self.header_name)
        header_layout.addWidget(self.header_role)
        
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # Form fields
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 25px;
            }
        """)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        # Input field style
        input_style = """
            QLineEdit, QComboBox, QDateEdit, QTextEdit {
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8fafc;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
        """
        
        label_style = """
            QLabel {
                color: #374151;
                font-weight: 600;
                font-size: 14px;
            }
        """
        
        # Tên đầy đủ
        name_label = QLabel('👤 Họ và tên:')
        name_label.setStyleSheet(label_style)
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(input_style)
        
        # Email
        email_label = QLabel('📧 Email:')
        email_label.setStyleSheet(label_style)
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(input_style)
        
        # Số điện thoại
        phone_label = QLabel('📱 Số điện thoại:')
        phone_label.setStyleSheet(label_style)
        self.phone_input = QLineEdit()
        self.phone_input.setStyleSheet(input_style)
        
        # Ngày sinh
        birthday_label = QLabel('🎂 Ngày sinh:')
        birthday_label.setStyleSheet(label_style)
        self.birthday_input = QDateEdit()
        self.birthday_input.setCalendarPopup(True)
        self.birthday_input.setDisplayFormat('dd/MM/yyyy')
        self.birthday_input.setStyleSheet(input_style)
        
        # Giới tính
        gender_label = QLabel('👥 Giới tính:')
        gender_label.setStyleSheet(label_style)
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(['Nam', 'Nữ', 'Khác'])
        self.gender_combo.setStyleSheet(input_style)
        
        # Địa chỉ
        address_label = QLabel('🏠 Địa chỉ:')
        address_label.setStyleSheet(label_style)
        self.address_input = QTextEdit()
        self.address_input.setMaximumHeight(80)
        self.address_input.setStyleSheet(input_style)
        
        # Layout form fields
        form_layout.addWidget(name_label, 0, 0)
        form_layout.addWidget(self.name_input, 0, 1)
        
        form_layout.addWidget(email_label, 1, 0)
        form_layout.addWidget(self.email_input, 1, 1)
        
        form_layout.addWidget(phone_label, 2, 0)
        form_layout.addWidget(self.phone_input, 2, 1)
        
        form_layout.addWidget(birthday_label, 3, 0)
        form_layout.addWidget(self.birthday_input, 3, 1)
        
        form_layout.addWidget(gender_label, 4, 0)
        form_layout.addWidget(self.gender_combo, 4, 1)
        
        form_layout.addWidget(address_label, 5, 0)
        form_layout.addWidget(self.address_input, 5, 1)
        
        form_frame.setLayout(form_layout)
        layout.addWidget(form_frame)
        
        # Buttons
        buttons_frame = QFrame()
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # Change password button
        btn_change_password = QPushButton('🔑 Đổi mật khẩu')
        btn_change_password.setStyleSheet("""
            QPushButton {
                background: #f59e0b;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #d97706;
            }
        """)
        btn_change_password.clicked.connect(self.change_password)
        
        # Logout button
        btn_logout = QPushButton('🚪 Đăng xuất')
        btn_logout.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        btn_logout.clicked.connect(self.logout)
        
        # Save button
        btn_save = QPushButton('💾 Lưu thay đổi')
        btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
        """)
        btn_save.clicked.connect(self.save_profile)
        
        # Cancel button
        btn_cancel = QPushButton('❌ Hủy')
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #6b7280;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #4b5563;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        buttons_layout.addWidget(btn_change_password)
        buttons_layout.addWidget(btn_logout)
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_save)
        
        buttons_frame.setLayout(buttons_layout)
        layout.addWidget(buttons_frame)
        
        self.setLayout(layout)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #f1f5f9;
            }
        """)

    def load_user_data(self):
        """Load dữ liệu user vào form"""
        if not self.current_user:
            return
        
        # Header info
        user_name = self.current_user.get('name', 'Unknown User')
        user_role = 'Người dùng' if self.current_user.get('role') == 'user' else 'Quản trị viên'
        
        self.header_name.setText(user_name)
        self.header_role.setText(f'🎯 {user_role}')
        
        # Avatar với chữ cái đầu
        initials = ''.join([word[0].upper() for word in user_name.split()[:2]])
        self.avatar_label.setText(initials)
        
        # Form fields
        self.name_input.setText(self.current_user.get('name', ''))
        self.email_input.setText(self.current_user.get('email', ''))
        self.phone_input.setText(self.current_user.get('phone', ''))
        
        # Birthday
        birthday_str = self.current_user.get('birthday', '')
        if birthday_str:
            try:
                birthday = datetime.datetime.strptime(birthday_str, '%Y-%m-%d').date()
                self.birthday_input.setDate(QDate(birthday))
            except:
                self.birthday_input.setDate(QDate.currentDate().addYears(-25))
        else:
            self.birthday_input.setDate(QDate.currentDate().addYears(-25))
        
        # Gender
        gender = self.current_user.get('gender', 'Nam')
        index = self.gender_combo.findText(gender)
        if index >= 0:
            self.gender_combo.setCurrentIndex(index)
        
        # Address
        self.address_input.setPlainText(self.current_user.get('address', ''))

    def save_profile(self):
        """Lưu thông tin profile"""
        try:
            # Validate data
            name = self.name_input.text().strip()
            email = self.email_input.text().strip()
            
            if not name:
                QMessageBox.warning(self, '⚠️ Lỗi', 'Vui lòng nhập họ tên!')
                return
            
            if not email:
                QMessageBox.warning(self, '⚠️ Lỗi', 'Vui lòng nhập email!')
                return
            
            # Update user data
            updated_user = self.current_user.copy()
            updated_user.update({
                'name': name,
                'email': email,
                'phone': self.phone_input.text().strip(),
                'birthday': self.birthday_input.date().toString('yyyy-MM-dd'),
                'gender': self.gender_combo.currentText(),
                'address': self.address_input.toPlainText().strip(),
                'updated_at': datetime.datetime.now().isoformat()
            })
            
            # Load all users
            with open('data/users.json', 'r', encoding='utf-8') as f:
                all_users = json.load(f)
            
            # Update user in list
            user_id = self.current_user.get('id')
            for i, user in enumerate(all_users):
                if user.get('id') == user_id:
                    all_users[i] = updated_user
                    break
            
            # Save to file
            with open('data/users.json', 'w', encoding='utf-8') as f:
                json.dump(all_users, f, ensure_ascii=False, indent=2)
            
            # Update user manager
            self.user_manager.current_user = updated_user
            if hasattr(self.user_manager, 'users'):
                self.user_manager.users = all_users
            
            QMessageBox.information(self, '✅ Thành công', 
                                  'Đã cập nhật thông tin cá nhân thành công!')
            
            # Emit signal
            self.profile_updated.emit()
            
            # Update header
            self.load_user_data()
            
        except Exception as e:
            QMessageBox.critical(self, '❌ Lỗi', 
                               f'Không thể lưu thông tin:\n{str(e)}')

    def change_password(self):
        """Dialog đổi mật khẩu"""
        from .user_change_password import ChangePasswordDialog
        
        dialog = ChangePasswordDialog(self.user_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            QMessageBox.information(self, '✅ Thành công', 
                                  'Đã đổi mật khẩu thành công!')

    def logout(self):
        """Xử lý logout"""
        reply = QMessageBox.question(self, '❓ Xác nhận đăng xuất',
                                   'Bạn có chắc muốn đăng xuất khỏi ứng dụng?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.logout_requested.emit()
            self.accept()
