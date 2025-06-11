from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog
from PyQt5.QtCore import QDate

class AdminUserTab(QWidget):
    def __init__(self, user_manager, audit_log_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.audit_log_manager = audit_log_manager
        self.init_ui()
        self.load_users_table()

    def init_ui(self):
        layout = QVBoxLayout(self)
        search_layout = QHBoxLayout()
        self.user_search_input = QLineEdit()
        self.user_search_input.setPlaceholderText("Tìm kiếm tên hoặc email...")
        search_layout.addWidget(self.user_search_input)
        self.user_status_filter = QComboBox()
        self.user_status_filter.addItems(["Tất cả", "Hoạt động", "Bị khóa"])
        search_layout.addWidget(self.user_status_filter)
        self.user_from_date = QDateEdit(calendarPopup=True)
        self.user_from_date.setDisplayFormat("dd-MM-yyyy")
        self.user_from_date.setDate(QDate(2000, 1, 1))
        self.user_from_date.setSpecialValueText("")
        self.user_from_date.setDateRange(QDate(2000, 1, 1), QDate(2100, 12, 31))
        self.user_from_date.setMinimumWidth(120)
        search_layout.addWidget(self.user_from_date)
        self.user_to_date = QDateEdit(calendarPopup=True)
        self.user_to_date.setDisplayFormat("dd-MM-yyyy")
        self.user_to_date.setDate(QDate.currentDate())
        self.user_to_date.setSpecialValueText("")
        self.user_to_date.setDateRange(QDate(2000, 1, 1), QDate(2100, 12, 31))
        self.user_to_date.setMinimumWidth(120)
        search_layout.addWidget(self.user_to_date)
        search_btn = QPushButton("Tìm/Lọc")
        search_btn.clicked.connect(self.search_user)
        search_layout.addWidget(search_btn)
        layout.addLayout(search_layout)
        self.user_table = QTableWidget(0, 6)
        self.user_table.setHorizontalHeaderLabels(["ID", "Tên hiển thị", "Email", "Ngày đăng ký", "Lần đăng nhập cuối", "Trạng thái"])
        self.user_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.user_table.horizontalHeader().setStretchLastSection(True)
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.user_table)
        btn_layout = QHBoxLayout()
        self.btn_view_detail = QPushButton("Xem chi tiết")
        self.btn_lock = QPushButton("Khóa tài khoản")
        self.btn_unlock = QPushButton("Mở khóa tài khoản")
        self.btn_reset_pw = QPushButton("Đặt lại mật khẩu")
        btn_layout.addWidget(self.btn_view_detail)
        btn_layout.addWidget(self.btn_lock)
        btn_layout.addWidget(self.btn_unlock)
        btn_layout.addWidget(self.btn_reset_pw)
        layout.addLayout(btn_layout)
        self.btn_view_detail.clicked.connect(self.view_user_detail)
        self.btn_lock.clicked.connect(self.lock_user)
        self.btn_unlock.clicked.connect(self.unlock_user)
        self.btn_reset_pw.clicked.connect(self.reset_user_password)

    def load_users_table(self):
        users = self.user_manager.load_users()
        self.user_table.setRowCount(0)
        for user in users:
            row = self.user_table.rowCount()
            self.user_table.insertRow(row)
            self.user_table.setItem(row, 0, QTableWidgetItem(user.get('user_id', '')))
            self.user_table.setItem(row, 1, QTableWidgetItem(user.get('full_name', '')))
            self.user_table.setItem(row, 2, QTableWidgetItem(user.get('email', '')))
            created_at = user.get('created_at', '')
            last_login = user.get('last_login', '')
            created_at_fmt = self.format_datetime(created_at)
            last_login_fmt = self.format_datetime(last_login)
            self.user_table.setItem(row, 3, QTableWidgetItem(created_at_fmt))
            self.user_table.setItem(row, 4, QTableWidgetItem(last_login_fmt))
            is_active = user.get('is_active', True)
            self.user_table.setItem(row, 5, QTableWidgetItem('Hoạt động' if is_active else 'Bị khóa'))

    def search_user(self):
        keyword = self.user_search_input.text().lower()
        status = self.user_status_filter.currentText()
        from_date = self.user_from_date.date().toString("yyyy-MM-dd")
        to_date = self.user_to_date.date().toString("yyyy-MM-dd")
        users = self.user_manager.load_users()
        filtered = []
        for user in users:
            if keyword and keyword not in user.get('full_name', '').lower() and keyword not in user.get('email', '').lower():
                continue
            is_active = user.get('is_active', True)
            if status == 'Hoạt động' and not is_active:
                continue
            if status == 'Bị khóa' and is_active:
                continue
            created_at = user.get('created_at', '')[:10]
            if from_date and created_at and created_at < from_date:
                continue
            if to_date and created_at and created_at > to_date:
                continue
            filtered.append(user)
        self.user_table.setRowCount(0)
        for user in filtered:
            row = self.user_table.rowCount()
            self.user_table.insertRow(row)
            self.user_table.setItem(row, 0, QTableWidgetItem(user.get('user_id', '')))
            self.user_table.setItem(row, 1, QTableWidgetItem(user.get('full_name', '')))
            self.user_table.setItem(row, 2, QTableWidgetItem(user.get('email', '')))
            created_at = user.get('created_at', '')
            last_login = user.get('last_login', '')
            created_at_fmt = self.format_datetime(created_at)
            last_login_fmt = self.format_datetime(last_login)
            self.user_table.setItem(row, 3, QTableWidgetItem(created_at_fmt))
            self.user_table.setItem(row, 4, QTableWidgetItem(last_login_fmt))
            is_active = user.get('is_active', True)
            self.user_table.setItem(row, 5, QTableWidgetItem('Hoạt động' if is_active else 'Bị khóa'))

    def format_datetime(self, dt_str):
        from datetime import datetime
        try:
            if not dt_str:
                return ''
            if 'T' in dt_str:
                dt = datetime.fromisoformat(dt_str.split('.')[0])
            else:
                dt = datetime.strptime(dt_str, "%Y-%m-%d")
            return dt.strftime("%d-%m-%Y %H:%M:%S")
        except Exception:
            return dt_str

    def get_selected_user(self):
        row = self.user_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, 'Chọn người dùng', 'Vui lòng chọn một người dùng!')
            return None
        user_id = self.user_table.item(row, 0).text()
        users = self.user_manager.load_users()
        for user in users:
            if user.get('user_id') == user_id:
                return user
        return None

    def view_user_detail(self):
        user = self.get_selected_user()
        if not user:
            return
        info = f"ID: {user.get('user_id','')}\nTên: {user.get('full_name','')}\nEmail: {user.get('email','')}\nNgày đăng ký: {user.get('created_at','')}\nLần đăng nhập cuối: {user.get('last_login','')}\nTrạng thái: {'Hoạt động' if user.get('is_active', True) else 'Bị khóa'}\nĐịa chỉ IP đăng ký: {user.get('register_ip','N/A')}"
        QMessageBox.information(self, 'Chi tiết người dùng', info)

    def lock_user(self):
        user = self.get_selected_user()
        if not user:
            return
        if not user.get('is_active', True):
            QMessageBox.information(self, 'Thông báo', 'Tài khoản đã bị khóa!')
            return
        reason, ok = QInputDialog.getText(self, 'Lý do khóa', 'Nhập lý do khóa tài khoản:')
        if not ok or not reason.strip():
            return
        user['is_active'] = False
        users = self.user_manager.load_users()
        for u in users:
            if u.get('user_id') == user['user_id']:
                u['is_active'] = False
        self.user_manager.save_users(users)
        self.audit_log_manager.add_log(user['user_id'], f'Khóa tài khoản: {reason}')
        QMessageBox.information(self, 'Thành công', 'Đã khóa tài khoản!')
        self.load_users_table()

    def unlock_user(self):
        user = self.get_selected_user()
        if not user:
            return
        if user.get('is_active', True):
            QMessageBox.information(self, 'Thông báo', 'Tài khoản đang hoạt động!')
            return
        user['is_active'] = True
        users = self.user_manager.load_users()
        for u in users:
            if u.get('user_id') == user['user_id']:
                u['is_active'] = True
        self.user_manager.save_users(users)
        self.audit_log_manager.add_log(user['user_id'], 'Mở khóa tài khoản')
        QMessageBox.information(self, 'Thành công', 'Đã mở khóa tài khoản!')
        self.load_users_table()

    def reset_user_password(self):
        user = self.get_selected_user()
        if not user:
            return
        import random, string
        new_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        user['password'] = new_password
        users = self.user_manager.load_users()
        for u in users:
            if u.get('user_id') == user['user_id']:
                u['password'] = new_password
        self.user_manager.save_users(users)
        self.audit_log_manager.add_log(user['user_id'], f'Cấp lại mật khẩu mới: {new_password}')
        QMessageBox.information(self, 'Cấp lại mật khẩu', f"Mật khẩu mới cho {user.get('email','')}: {new_password}")
