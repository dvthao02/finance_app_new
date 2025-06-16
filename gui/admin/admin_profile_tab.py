from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QFormLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox, QHBoxLayout, QSpacerItem, QSizePolicy, QDateEdit
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QDate
from datetime import datetime
from utils.file_helper import load_json, save_json, is_valid_email, is_valid_phone, is_strong_password
from data_manager.user_manager import UserManager
import os

class AdminProfileTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.user = None
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        # Ảnh đại diện
        self.avatar_label = QLabel()
        self.avatar_label.setFixedSize(100, 100)
        self.avatar_label.setStyleSheet("border:1px solid #ccc; border-radius:50px; background:#f5f5f5;")
        self.avatar_label.setAlignment(Qt.AlignCenter)
        # Thông tin cá nhân
        self.info_group = QGroupBox("Thông tin cá nhân")
        self.form = QFormLayout(self.info_group)
        self.txt_id = QLabel(); self.txt_role = QLabel()
        self.input_name = QLineEdit(); self.input_email = QLineEdit(); self.input_phone = QLineEdit()
        self.input_dob = QDateEdit(calendarPopup=True); self.input_dob.setDisplayFormat("dd-MM-yyyy")
        self.input_address = QLineEdit(); self.input_avatar = QLineEdit()
        self.btn_avatar = QPushButton("Chọn ảnh")
        self.btn_avatar.clicked.connect(self.choose_avatar)
        avatar_input_layout = QHBoxLayout()
        avatar_input_layout.addWidget(self.input_avatar)
        avatar_input_layout.addWidget(self.btn_avatar)
        # Nút đổi mật khẩu riêng
        self.btn_change_pw = QPushButton("Đổi mật khẩu")
        self.btn_change_pw.clicked.connect(self.show_change_password_dialog)
        # Thêm các trường vào form
        self.form.addRow("ID:", self.txt_id)
        self.form.addRow("Vai trò:", self.txt_role)
        self.form.addRow("Tên hiển thị:", self.input_name)
        self.form.addRow("Email:", self.input_email)
        self.form.addRow("Số điện thoại:", self.input_phone)
        self.form.addRow("Ngày sinh:", self.input_dob)
        self.form.addRow("Địa chỉ:", self.input_address)
        self.form.addRow("Ảnh đại diện:", avatar_input_layout)
        # Nút cập nhật, đổi mật khẩu cùng hàng, căn giữa
        btn_update = QPushButton("Cập nhật thông tin")
        btn_update.setMinimumWidth(130)
        btn_update.clicked.connect(self.update_profile)
        btn_change_pw = self.btn_change_pw  # Đã tạo ở trên
        btn_change_pw.setMinimumWidth(110)
        btns = QHBoxLayout()
        btns.addStretch(1)
        btns.addWidget(btn_update)
        btns.addSpacing(10)
        btns.addWidget(btn_change_pw)
        btns.addStretch(1)
        
        # Layout tổng hợp
        top_layout = QHBoxLayout()
        # Căn giữa avatar theo chiều dọc
        avatar_vbox = QVBoxLayout()
        avatar_vbox.addStretch(1)
        avatar_vbox.addWidget(self.avatar_label, alignment=Qt.AlignCenter)
        avatar_vbox.addStretch(1)
        top_layout.addLayout(avatar_vbox)
        top_layout.addSpacing(20)
        top_layout.addWidget(self.info_group, 1)
        main_layout.addLayout(top_layout)
        main_layout.addSpacing(10)
        main_layout.addLayout(btns)
        main_layout.addSpacing(5)
        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def set_user(self, user):
        self.user = user
        if not user:
            self.txt_id.setText("")
            self.txt_role.setText("")
            self.input_name.setText("")
            self.input_email.setText("")
            self.input_phone.setText("")
            self.input_dob.setDate(QDate(2000, 1, 1))
            self.input_address.setText("")
            self.input_avatar.setText("")
            self.avatar_label.clear()
            return
        self.txt_id.setText(str(user.get('user_id', '')))
        self.txt_role.setText(user.get('role', ''))
        self.input_name.setText(user.get('full_name', ''))
        self.input_email.setText(user.get('email', ''))
        self.input_phone.setText(user.get('phone', ''))        # Ngày sinh: ISO -> dd-MM-yyyy
        dob = user.get('date_of_birth', '')
        try:
            if dob:
                dt = datetime.strptime(dob, "%Y-%m-%d")
                self.input_dob.setDate(QDate(dt.year, dt.month, dt.day))
            else:
                self.input_dob.setDate(QDate(2000, 1, 1))
        except Exception:
            self.input_dob.setDate(QDate(2000, 1, 1))
        self.input_address.setText(user.get('address', ''))
        self.input_avatar.setText(user.get('avatar', ''))
        self.load_avatar(user.get('avatar', ''))
        
    def choose_avatar(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Chọn ảnh đại diện", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            # Nếu người dùng chọn ảnh, lưu đường dẫn và hiển thị preview
            self.input_avatar.setText(file_path)
            self.load_avatar(file_path)
            QMessageBox.information(self, "Thông báo", "Đã chọn ảnh đại diện mới. Nhấn 'Cập nhật thông tin' để lưu thay đổi.")
            
    def load_avatar(self, path):
        if path and os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                self.avatar_label.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                return
        
        # Nếu không có ảnh hoặc ảnh không hợp lệ
        self.avatar_label.setPixmap(QPixmap())
        self.avatar_label.setText("No\nImage")
        self.avatar_label.setStyleSheet("border:1px solid #ccc; border-radius:50px; background:#f5f5f5; color:#999;")
        
    def update_profile(self):
        if not self.user:
            return
        name = self.input_name.text().strip()
        email = self.input_email.text().strip()
        phone = self.input_phone.text().strip()
        dob = self.input_dob.date().toString("yyyy-MM-dd")
        address = self.input_address.text().strip()
        avatar = self.input_avatar.text().strip()
        
        # Validate
        if not name:
            QMessageBox.warning(self, "Lỗi", "Tên hiển thị không được để trống!")
            return
        if email and not is_valid_email(email):
            QMessageBox.warning(self, "Lỗi", "Email không hợp lệ!")
            return
        if phone and not is_valid_phone(phone):
            QMessageBox.warning(self, "Lỗi", "Số điện thoại không hợp lệ!")
            return
            
        # Kiểm tra ảnh đại diện
        if avatar and not os.path.exists(avatar):
            QMessageBox.warning(self, "Lỗi", f"Không tìm thấy tệp ảnh: {avatar}")
            return
            
        # Sao chép avatar vào thư mục assets nếu đường dẫn khác với avatar hiện tại
        current_avatar = self.user.get('avatar', '')
        if avatar and avatar != current_avatar:
            from utils.file_helper import copy_avatar_to_assets
            user_id = self.user.get('user_id', '')
            new_avatar_path = copy_avatar_to_assets(avatar, user_id)
            
            if new_avatar_path:
                avatar = new_avatar_path  # Cập nhật đường dẫn avatar thành đường dẫn mới trong assets
            else:
                QMessageBox.warning(self, "Cảnh báo", "Không thể sao chép ảnh đại diện vào thư mục assets. Sử dụng đường dẫn gốc.")
          # Cập nhật qua UserManager
        um = UserManager()
        try:
            # Kiểm tra xem ảnh đại diện có thay đổi không
            avatar_changed = avatar and avatar != self.user.get('avatar', '')
            
            ok = um.update_user(
                self.user.get('user_id'),
                full_name=name,
                email=email,
                phone=phone,
                date_of_birth=dob,
                address=address,
                avatar=avatar
            )
            
            if ok:
                # Thông báo phù hợp với việc có cập nhật ảnh hay không
                if avatar_changed:
                    QMessageBox.information(self, "Thành công", "Đã cập nhật thông tin cá nhân và ảnh đại diện!")
                else:
                    QMessageBox.information(self, "Thành công", "Đã cập nhật thông tin cá nhân!")
                
                # Reload lại user từ file để đồng bộ
                users = um.load_users()
                for u in users:
                    if u.get('user_id') == self.user.get('user_id'):
                        self.set_user(u)
                        break
            else:
                QMessageBox.warning(self, "Thông báo", "Không có thay đổi hoặc cập nhật thất bại!")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi: {str(e)}")

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
            # Đổi mật khẩu qua UserManager
            um = UserManager()
            try:
                um.change_password(self.user.get('username'), old_pw, new_pw)
                QMessageBox.information(dialog, "Thành công", "Đã đổi mật khẩu!")
                dialog.accept()
            except Exception as e:
                QMessageBox.warning(dialog, "Lỗi", str(e))
        btn_ok.clicked.connect(do_change)
        btn_cancel.clicked.connect(dialog.reject)
        dialog.exec_()
