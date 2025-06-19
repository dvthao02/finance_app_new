from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QFrame, QGridLayout, QMessageBox, QFileDialog,
                             QComboBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QBrush, QColor, QBitmap
import os
import shutil
from data_manager.user_manager import UserManager
from utils.file_helper import is_strong_password

class AdminProfileTab(QWidget):
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

        # Admin Info VBox
        info_vbox = QVBoxLayout()
        info_vbox.setSpacing(5)
        info_vbox.addStretch()
        self.name_display_label = QLabel("Administrator")
        self.name_display_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #333333;")
        self.email_display_label = QLabel("admin@email.com")
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
            "phone": "Số điện thoại:",
            "address": "Địa chỉ:"
        }
        
        label_style = "QLabel { color: #555555; font-weight: bold; }"
        input_style = """
            QLineEdit, QDateEdit {
                border: 1px solid #D0D0D0;
                border-radius: 8px;
                padding: 10px;
                background-color: #FFFFFF;
                color: #333;
            }
            QLineEdit:focus, QDateEdit:focus {
                border-color: #007BFF;
            }
        """

        self.entries = {}
        for i, (field, label_text) in enumerate(fields.items()):
            label = QLabel(label_text)
            label.setStyleSheet(label_style)
            form_layout.addWidget(label, i, 0)
            if field == "date_of_birth":
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
        self.change_password_button.clicked.connect(self.show_change_password_dialog)

        self.save_button = QPushButton("Lưu thay đổi")
        self.save_button.setCursor(Qt.PointingHandCursor)
        self.save_button.setStyleSheet("""
            QPushButton { background-color: #007BFF; color: white; border: none; border-radius: 8px; padding: 12px 20px; font-weight: bold; }
            QPushButton:hover { background-color: #0056b3; }
        """)
        self.save_button.clicked.connect(self.save_admin_data)

        buttons_layout.addWidget(self.change_password_button)
        buttons_layout.addWidget(self.save_button)
        main_layout.addWidget(button_frame)

    def show_avatar(self, image_path):
        try:
            # Ưu tiên dùng đường dẫn tương đối
            if not os.path.isabs(image_path):
                abs_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), image_path)
            else:
                abs_path = image_path
            if os.path.exists(abs_path):
                pixmap = QPixmap(abs_path)
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
            else:
                self.avatar_label.setPixmap(QPixmap())
                self.avatar_label.setText("No\nImage")
        except Exception as e:
            self.avatar_label.setPixmap(QPixmap())
            self.avatar_label.setText("No\nImage")

    def upload_avatar(self):
        if not self.current_user:
            QMessageBox.critical(self, "Lỗi", "Không có admin nào đang đăng nhập.")
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
                self.new_avatar_path = new_avatar_path.replace("\\", "/") # luôn lưu đường dẫn tương đối chuẩn hóa
                self.show_avatar(self.new_avatar_path)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể lưu ảnh đại diện: {e}")
        else:
            self.new_avatar_path = None

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
            self.entries["phone"].setText(self.current_user.get("phone", ""))
            self.entries["address"].setText(self.current_user.get("address", ""))
            avatar_path = self.current_user.get("avatar")
            if avatar_path:
                self.show_avatar(avatar_path)
            else:
                self.show_default_avatar()
        else:
            QMessageBox.critical(self, "Lỗi", "Không có admin nào đang đăng nhập.")
            self.show_default_avatar()

    def save_admin_data(self):
        if self.current_user:
            user_id = self.current_user.get('id') or self.current_user.get('user_id')
            if not user_id:
                QMessageBox.critical(self, "Lỗi", "Không tìm thấy ID admin.")
                return
            full_name = self.entries["full_name"].text().strip()
            email = self.entries["email"].text().strip()
            date_of_birth = self.entries["date_of_birth"].date().toString("dd/MM/yyyy")
            phone = self.entries["phone"].text().strip()
            address = self.entries["address"].text().strip()
            # Kiểm tra thay đổi
            changed = False
            updated_data = {
                "full_name": full_name,
                "email": email,
                "date_of_birth": date_of_birth,
                "phone": phone,
                "address": address,
            }
            for key, value in updated_data.items():
                if value != self.current_user.get(key, ""):
                    changed = True
                    break
            if self.new_avatar_path and self.new_avatar_path != self.current_user.get("avatar"):
                updated_data["avatar"] = self.new_avatar_path
                changed = True
            if not changed:
                QMessageBox.information(self, "Thông báo", "Không có thông tin nào thay đổi hoặc cập nhật thất bại!")
                return
            result = self.user_manager.update_user_profile(user_id, updated_data)
            if result and result.get("status") == "success":
                QMessageBox.information(self, "Thành công", "Cập nhật thông tin thành công!")
                self.new_avatar_path = None
                self.profile_updated.emit()
                self.load_user_data()
            else:
                error_message = "Không thể cập nhật thông tin."
                if result and result.get("message"):
                    error_message = result.get("message")
                QMessageBox.critical(self, "Lỗi", error_message)
        else:
            QMessageBox.critical(self, "Lỗi", "Không có admin nào đang đăng nhập.")

    def show_change_password_dialog(self):
        from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, QHBoxLayout, QToolButton
        from PyQt5.QtGui import QIcon
        import os
        dialog = QDialog(self)
        dialog.setWindowTitle("Đổi mật khẩu")
        layout = QVBoxLayout(dialog)
        lbl_old = QLabel("Mật khẩu cũ:")
        input_old = QLineEdit(); input_old.setEchoMode(QLineEdit.Password)
        lbl_new = QLabel("Mật khẩu mới:")
        input_new = QLineEdit(); input_new.setEchoMode(QLineEdit.Password)
        lbl_confirm = QLabel("Nhập lại mật khẩu mới:")
        input_confirm = QLineEdit(); input_confirm.setEchoMode(QLineEdit.Password)
        # Một toggle chung cho cả 3 ô
        btn_toggle = QToolButton()
        icon_eye = QIcon(os.path.join(os.path.dirname(__file__), '../../assets/eye_open.png'))
        icon_eye_closed = QIcon(os.path.join(os.path.dirname(__file__), '../../assets/eye_closed.png'))
        btn_toggle.setIcon(icon_eye_closed)
        btn_toggle.setCheckable(True)
        btn_toggle.setFixedWidth(30)
        def toggle_all():
            if btn_toggle.isChecked():
                input_old.setEchoMode(QLineEdit.Normal)
                input_new.setEchoMode(QLineEdit.Normal)
                input_confirm.setEchoMode(QLineEdit.Normal)
                btn_toggle.setIcon(icon_eye)
            else:
                input_old.setEchoMode(QLineEdit.Password)
                input_new.setEchoMode(QLineEdit.Password)
                input_confirm.setEchoMode(QLineEdit.Password)
                btn_toggle.setIcon(icon_eye_closed)
        btn_toggle.toggled.connect(toggle_all)
        # Layout cho 3 ô + toggle
        pw_layout = QHBoxLayout()
        pw_layout.addWidget(btn_toggle)
        # Nút
        btn_ok = QPushButton("Đổi mật khẩu")
        btn_cancel = QPushButton("Hủy")
        btns = QHBoxLayout(); btns.addWidget(btn_ok); btns.addWidget(btn_cancel)
        layout.addWidget(lbl_old); layout.addWidget(input_old)
        layout.addWidget(lbl_new); layout.addWidget(input_new)
        layout.addWidget(lbl_confirm); layout.addWidget(input_confirm)
        layout.addLayout(pw_layout)
        layout.addLayout(btns)
        def do_change():
            old_pw = input_old.text()
            new_pw = input_new.text()
            confirm_pw = input_confirm.text()
            if not old_pw or not new_pw or not confirm_pw:
                QMessageBox.warning(dialog, "Lỗi", "Vui lòng nhập đủ thông tin!")
                return
            if new_pw != confirm_pw:
                QMessageBox.warning(dialog, "Lỗi", "Mật khẩu mới nhập lại không khớp!")
                return
            if not is_strong_password(new_pw):
                QMessageBox.warning(dialog, "Lỗi", "Mật khẩu mới không đủ mạnh!")
                return
            # Đổi mật khẩu qua UserManager, lấy user từ current_user
            try:
                self.user_manager.change_password(self.current_user.get('username'), old_pw, new_pw)
                QMessageBox.information(dialog, "Thành công", "Đã đổi mật khẩu!")
                dialog.accept()
            except Exception as e:
                QMessageBox.warning(dialog, "Lỗi", str(e))
        btn_ok.clicked.connect(do_change)
        btn_cancel.clicked.connect(dialog.reject)
        dialog.exec_()

    def set_user(self, user):
        self.current_user = user
        self.load_user_data()

    def show_default_avatar(self):
        self.avatar_label.setPixmap(QPixmap())
        self.avatar_label.setText("No\nImage")
