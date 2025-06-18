from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QFrame, QGridLayout, QMessageBox, QFileDialog,
                             QComboBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QBitmap
import os
import shutil
from data_manager.user_manager import UserManager
from gui.user.user_change_password import ChangePasswordDialog

class UserProfileTab(QWidget):
    profile_updated = pyqtSignal()

    def __init__(self, user_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.current_user = self.user_manager.get_current_user() or {}
        self.new_avatar_path = None
        self.init_ui()
        self.load_user_data()

    def init_ui(self):
        self.setStyleSheet("background-color: #FFFFFF;")
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(50, 30, 50, 30)
        main_layout.setSpacing(30)

        # --- Top section for Avatar and basic info ---
        top_frame = QFrame(self)
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.setSpacing(20)

        # Avatar
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setAlignment(Qt.AlignCenter)
        self.avatar_label.setStyleSheet("background-color: #E0E0E0; border-radius: 50px; color: #333; font-size: 40px; font-weight: bold;")

        # User Info VBox
        info_vbox = QVBoxLayout()
        info_vbox.setSpacing(5)
        info_vbox.addStretch()
        self.name_display_label = QLabel("User Name")
        self.name_display_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333333;")
        self.email_display_label = QLabel("user@email.com")
        self.email_display_label.setStyleSheet("font-size: 14px; color: #757575;")
        info_vbox.addWidget(self.name_display_label)
        info_vbox.addWidget(self.email_display_label)
        info_vbox.addStretch()

        # Change Avatar Button
        self.upload_button = QPushButton("Thay đổi ảnh")
        self.upload_button.setCursor(Qt.PointingHandCursor)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #F0F0F0;
                color: #333333;
                border: 1px solid #DCDCDC;
                border-radius: 8px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #E0E0E0;
            }
        """)
        self.upload_button.clicked.connect(self.upload_avatar)

        top_layout.addWidget(self.avatar_label)
        top_layout.addLayout(info_vbox)
        top_layout.addStretch()
        top_layout.addWidget(self.upload_button)
        
        main_layout.addWidget(top_frame)

        # --- Bottom section for the form ---
        form_frame = QFrame(self)
        form_frame.setObjectName("formFrame")
        form_frame.setStyleSheet("#formFrame { background-color: #F9F9F9; border-radius: 10px; }")
        
        form_layout = QGridLayout(form_frame)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(20)

        fields = {
            "full_name": "Họ và tên:",
            "email": "Email:",
            "date_of_birth": "Ngày sinh:",
            "gender": "Giới tính:",
            "phone_number": "Số điện thoại:"
        }
        
        label_style = "QLabel { color: #555555; font-weight: bold; }"
        input_style = """
            QLineEdit, QComboBox, QDateEdit {
                border: 1px solid #D0D0D0;
                border-radius: 8px;
                padding: 10px;
                background-color: #FFFFFF;
                color: #333;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #007BFF;
            }
        """

        self.entries = {}
        for i, (field, label_text) in enumerate(fields.items()):
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            form_layout.addWidget(label, i, 0)
            
            if field == "gender":
                self.entries[field] = QComboBox()
                self.entries[field].addItems(["Nam", "Nữ", "Khác"])
            elif field == "date_of_birth":
                self.entries[field] = QDateEdit()
                self.entries[field].setCalendarPopup(True)
                self.entries[field].setDisplayFormat('dd/MM/yyyy')
            else:
                self.entries[field] = QLineEdit()
            
            self.entries[field].setStyleSheet(input_style)
            form_layout.addWidget(self.entries[field], i, 1)

        main_layout.addWidget(form_frame)
        main_layout.addStretch()

        # --- Button Frame (Bottom) ---
        button_frame = QFrame(self)
        buttons_layout = QHBoxLayout(button_frame)
        buttons_layout.setContentsMargins(0, 0, 0, 0)
        buttons_layout.addStretch()

        self.change_password_button = QPushButton("Đổi mật khẩu")
        self.change_password_button.setCursor(Qt.PointingHandCursor)
        self.change_password_button.setStyleSheet("""
            QPushButton { background-color: #6c757d; color: white; border: none; border-radius: 8px; padding: 12px 20px; font-weight: bold; }
            QPushButton:hover { background-color: #5a6268; }
        """)
        self.change_password_button.clicked.connect(self.open_change_password_form)

        self.save_button = QPushButton("Lưu thay đổi")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet("""
            QPushButton { background-color: #007BFF; color: white; border: none; border-radius: 8px; padding: 12px 20px; font-weight: bold; }
            QPushButton:hover { background-color: #0056b3; }
        """)
        self.save_button.clicked.connect(self.save_user_data)

        buttons_layout.addWidget(self.change_password_button)
        buttons_layout.addWidget(self.save_button)
        main_layout.addWidget(button_frame)

    def open_change_password_form(self):
        if self.current_user:
            dialog = ChangePasswordDialog(self.user_manager, self)
            dialog.exec_()

    def load_user_data(self):
        self.current_user = self.user_manager.get_current_user()
        if self.current_user:
            self.name_display_label.setText(self.current_user.get("full_name", "N/A"))
            self.email_display_label.setText(self.current_user.get("email", "N/A"))

            self.entries["full_name"].setText(self.current_user.get("full_name", ""))
            self.entries["email"].setText(self.current_user.get("email", ""))
            dob_str = self.current_user.get("date_of_birth", "")
            if dob_str:
                self.entries["date_of_birth"].setDate(QDate.fromString(dob_str, "dd/MM/yyyy"))

            self.entries["gender"].setCurrentText(self.current_user.get("gender", ""))
            self.entries["phone_number"].setText(self.current_user.get("phone_number", ""))
            
            avatar_path = self.current_user.get("avatar")
            if avatar_path and os.path.exists(avatar_path):
                self.show_avatar(avatar_path)
            else:
                self.show_default_avatar()
        else:
            QMessageBox.critical(self, "Lỗi", "Không có người dùng nào đang đăng nhập.")
            self.show_default_avatar()

    def show_avatar(self, image_path):
        try:
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            mask = QBitmap(pixmap.size())
            mask.fill(Qt.white)
            painter = QPainter(mask)
            painter.setBrush(Qt.black)
            painter.drawEllipse(0, 0, mask.width(), mask.height())
            painter.end()
            
            pixmap.setMask(mask)
            
            self.avatar_label.setPixmap(pixmap)
            self.avatar_label.setText("")
        except Exception as e:
            print(f"Error loading avatar: {e}")
            self.show_default_avatar()

    def show_default_avatar(self):
        full_name = self.current_user.get("full_name", "U") if self.current_user else "U"
        initial = full_name[0].upper() if full_name else "U"
        self.avatar_label.setText(initial)
        self.avatar_label.setPixmap(QPixmap())

    def upload_avatar(self):
        if not self.current_user:
            QMessageBox.critical(self, "Lỗi", "Không có người dùng nào đang đăng nhập.")
            return
            
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh đại diện", "", "Image files (*.png *.jpg *.jpeg *.gif)")
        
        if file_path:
            avatar_dir = os.path.join("assets", "avatar")
            os.makedirs(avatar_dir, exist_ok=True)
            
            file_extension = os.path.splitext(file_path)[1]
            user_id = self.current_user.get('id') or self.current_user.get('user_id')
            new_avatar_path = os.path.join(avatar_dir, f"avatar_user_{user_id}{file_extension}")
            
            try:
                shutil.copy(file_path, new_avatar_path)
                self.new_avatar_path = new_avatar_path
                self.show_avatar(new_avatar_path)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu ảnh đại diện: {e}")

    def save_user_data(self):
        if self.current_user:
            user_id = self.current_user.get('id') or self.current_user.get('user_id')
            if not user_id:
                QMessageBox.critical(self, "Lỗi", "Không tìm thấy ID người dùng.")
                return

            updated_data = {
                "full_name": self.entries["full_name"].text(),
                "email": self.entries["email"].text(),
                "date_of_birth": self.entries["date_of_birth"].date().toString("dd/MM/yyyy"),
                "gender": self.entries["gender"].currentText(),
                "phone_number": self.entries["phone_number"].text(),
            }
            
            if self.new_avatar_path:
                updated_data["avatar"] = self.new_avatar_path

            if self.user_manager.update_user_profile(user_id, updated_data):
                QMessageBox.information(self, "Thành công", "Cập nhật thông tin thành công!")
                self.new_avatar_path = None
                self.profile_updated.emit()
                self.load_user_data()
            else:
                QMessageBox.critical(self, "Lỗi", "Không thể cập nhật thông tin.")
        else:
            QMessageBox.critical(self, "Lỗi", "Không có người dùng nào đang đăng nhập.")
