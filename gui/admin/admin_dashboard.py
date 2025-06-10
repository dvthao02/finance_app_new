from PyQt5.QtWidgets import QDialog, QTabWidget, QVBoxLayout, QWidget, QLabel, QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QTextEdit, QMessageBox, QInputDialog, QDateEdit, QHeaderView
from PyQt5.QtCore import pyqtSignal, QDate
from data_manager.user_manager import UserManager
from data_manager.category_manager import CategoryManager
from data_manager.notification_manager import NotificationManager
from data_manager.audit_log_manager import AuditLogManager
from data_manager.transaction_manager import TransactionManager
from datetime import datetime

class AdminDashboard(QDialog):
    logout_signal = pyqtSignal()
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Admin Dashboard")
        self.setMinimumSize(1100, 700)
        self.current_user = None
        self.init_ui()

    def set_current_user(self, user):
        self.current_user = user
        self.user_manager = UserManager()
        self.category_manager = CategoryManager()
        self.notification_manager = NotificationManager()
        self.audit_log_manager = AuditLogManager()
        self.transaction_manager = TransactionManager()
        self.refresh_all_tabs()

    def refresh_all_tabs(self):
        self.load_users_table()
        self.load_categories_table()
        self.load_notifications_table()
        self.load_dashboard_stats()
        self.load_audit_log_table()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        # 1. User Management
        self.user_tab = QWidget()
        self.tabs.addTab(self.user_tab, "Quản lý Người dùng")
        self.init_user_tab()
        # 2. Default Category Management
        self.category_tab = QWidget()
        self.tabs.addTab(self.category_tab, "Danh mục Mặc định")
        self.init_category_tab()
        # 3. System Notifications
        self.notify_tab = QWidget()
        self.tabs.addTab(self.notify_tab, "Thông báo Hệ thống")
        self.init_notify_tab()
        # 4. Dashboard
        self.dashboard_tab = QWidget()
        self.tabs.addTab(self.dashboard_tab, "Tổng quan")
        self.init_dashboard_tab()
        # 5. Admin Profile
        self.profile_tab = QWidget()
        self.tabs.addTab(self.profile_tab, "Tài khoản Admin")
        self.init_profile_tab()

    # 1. User Management Tab
    def init_user_tab(self):
        layout = QVBoxLayout(self.user_tab)
        search_layout = QHBoxLayout()
        self.user_search_input = QLineEdit()
        self.user_search_input.setPlaceholderText("Tìm kiếm tên hoặc email...")
        search_layout.addWidget(self.user_search_input)
        self.user_status_filter = QComboBox()
        self.user_status_filter.addItems(["Tất cả", "Hoạt động", "Bị khóa"])
        search_layout.addWidget(self.user_status_filter)
        # Định dạng ngày dd-MM-yyyy
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
        # Thêm các nút chức năng quản lý user
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
            # Sử dụng is_active để xác định trạng thái
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
        # Chuyển ISO -> dd-MM-yyyy HH:mm:ss
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

    # 2. Default Category Management Tab
    def init_category_tab(self):
        layout = QVBoxLayout(self.category_tab)
        self.category_table = QTableWidget(0, 2)
        self.category_table.setHorizontalHeaderLabels(["Tên danh mục", "Biểu tượng"])
        layout.addWidget(self.category_table)
        btn_layout = QHBoxLayout()
        btn_layout.addWidget(QPushButton("Thêm danh mục"))
        btn_layout.addWidget(QPushButton("Sửa danh mục"))
        btn_layout.addWidget(QPushButton("Xóa danh mục"))
        layout.addLayout(btn_layout)

    def load_categories_table(self):
        categories = self.category_manager.load_categories()
        self.category_table.setRowCount(0)
        for cat in categories:
            if cat.get('user_id', 'system') == 'system':
                row = self.category_table.rowCount()
                self.category_table.insertRow(row)
                self.category_table.setItem(row, 0, QTableWidgetItem(cat.get('name', '')))
                self.category_table.setItem(row, 1, QTableWidgetItem(cat.get('icon', '')))

    # 3. System Notifications Tab
    def init_notify_tab(self):
        layout = QVBoxLayout(self.notify_tab)
        self.notify_title = QLineEdit(); self.notify_title.setPlaceholderText("Tiêu đề thông báo")
        self.notify_content = QTextEdit(); self.notify_content.setPlaceholderText("Nội dung thông báo")
        self.notify_type = QComboBox(); self.notify_type.addItems(["Tin tức", "Cảnh báo", "Bảo trì"])
        send_btn = QPushButton("Gửi thông báo")
        send_btn.clicked.connect(self.send_notification)
        layout.addWidget(self.notify_title)
        layout.addWidget(self.notify_content)
        layout.addWidget(self.notify_type)
        layout.addWidget(send_btn)
        self.notify_table = QTableWidget(0, 3)
        self.notify_table.setHorizontalHeaderLabels(["Tiêu đề", "Ngày gửi", "Loại"])
        layout.addWidget(self.notify_table)

    def load_notifications_table(self):
        notifications = self.notification_manager.get_all_notifications()
        self.notify_table.setRowCount(0)
        for n in notifications:
            row = self.notify_table.rowCount()
            self.notify_table.insertRow(row)
            self.notify_table.setItem(row, 0, QTableWidgetItem(n.get('title', '')))
            self.notify_table.setItem(row, 1, QTableWidgetItem(n.get('created_at', '')))
            self.notify_table.setItem(row, 2, QTableWidgetItem(n.get('type', '')))

    def send_notification(self):
        title = self.notify_title.text().strip()
        content = self.notify_content.toPlainText().strip()
        notify_type = self.notify_type.currentText()
        if not title or not content:
            QMessageBox.warning(self, 'Thiếu thông tin', 'Vui lòng nhập tiêu đề và nội dung!')
            return
        self.notification_manager.add_notification(title, content, notify_type)
        QMessageBox.information(self, 'Thành công', 'Đã gửi thông báo!')
        self.load_notifications_table()

    # 4. Dashboard Tab
    def init_dashboard_tab(self):
        layout = QVBoxLayout(self.dashboard_tab)
        layout.addWidget(QLabel("Tổng người dùng: ..."))
        layout.addWidget(QLabel("Người dùng mới trong tháng: ..."))
        layout.addWidget(QLabel("Giao dịch hôm nay: ..."))
        layout.addWidget(QLabel("[Biểu đồ tăng trưởng sẽ hiển thị ở đây]"))
        self.recent_table = QTableWidget(0, 3)
        self.recent_table.setHorizontalHeaderLabels(["ID", "Tên", "Ngày đăng ký"])
        layout.addWidget(self.recent_table)

    def load_dashboard_stats(self):
        users = self.user_manager.load_users()
        transactions = self.transaction_manager.get_all_transactions()
        now = datetime.now()
        month = now.strftime('%Y-%m')
        new_users = [u for u in users if u.get('created_at', '').startswith(month)]
        today = now.strftime('%Y-%m-%d')
        today_transactions = [t for t in transactions if t.get('created_at', '').startswith(today)]
        # Update labels
        self.dashboard_tab.layout().itemAt(0).widget().setText(f"Tổng người dùng: {len(users)}")
        self.dashboard_tab.layout().itemAt(1).widget().setText(f"Người dùng mới trong tháng: {len(new_users)}")
        self.dashboard_tab.layout().itemAt(2).widget().setText(f"Giao dịch hôm nay: {len(today_transactions)}")
        # Recent users
        recent = sorted(users, key=lambda u: u.get('created_at', ''), reverse=True)[:5]
        self.recent_table.setRowCount(0)
        for u in recent:
            row = self.recent_table.rowCount()
            self.recent_table.insertRow(row)
            self.recent_table.setItem(row, 0, QTableWidgetItem(u.get('user_id', '')))
            self.recent_table.setItem(row, 1, QTableWidgetItem(u.get('full_name', '')))
            self.recent_table.setItem(row, 2, QTableWidgetItem(u.get('created_at', '')))

    # 5. Admin Profile Tab
    def init_profile_tab(self):
        layout = QVBoxLayout(self.profile_tab)
        layout.addWidget(QLabel("Đổi mật khẩu"))
        self.old_pw = QLineEdit(); self.old_pw.setEchoMode(QLineEdit.Password); self.old_pw.setPlaceholderText("Mật khẩu cũ")
        self.new_pw = QLineEdit(); self.new_pw.setEchoMode(QLineEdit.Password); self.new_pw.setPlaceholderText("Mật khẩu mới")
        self.confirm_pw = QLineEdit(); self.confirm_pw.setEchoMode(QLineEdit.Password); self.confirm_pw.setPlaceholderText("Nhập lại mật khẩu mới")
        change_btn = QPushButton("Đổi mật khẩu")
        change_btn.clicked.connect(self.change_password)
        layout.addWidget(self.old_pw)
        layout.addWidget(self.new_pw)
        layout.addWidget(self.confirm_pw)
        layout.addWidget(change_btn)
        layout.addWidget(QLabel("Lịch sử hoạt động (Audit Log)"))
        self.audit_table = QTableWidget(0, 2)
        self.audit_table.setHorizontalHeaderLabels(["Thời gian", "Hành động"])
        layout.addWidget(self.audit_table)
        logout_btn = QPushButton("Đăng xuất")
        logout_btn.clicked.connect(self.handle_logout)
        layout.addWidget(logout_btn)

    def load_audit_log_table(self):
        logs = self.audit_log_manager.get_all_logs()
        self.audit_table.setRowCount(0)
        for log in reversed(logs[-50:]):
            row = self.audit_table.rowCount()
            self.audit_table.insertRow(row)
            self.audit_table.setItem(row, 0, QTableWidgetItem(log.get('timestamp', '')))
            self.audit_table.setItem(row, 1, QTableWidgetItem(f"{log.get('action', '')} (user: {log.get('user_id', '')})"))

    def change_password(self):
        pass  # TODO: Implement change password

    def handle_logout(self):
        self.logout_signal.emit()
        self.accept()

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
        # Thực hiện gửi email đặt lại mật khẩu thực tế (nếu có hệ thống email)
        # Ở đây sẽ tạo một mã đặt lại và lưu vào user, đồng thời gửi email nếu có cấu hình
        import random, string
        reset_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        user['reset_code'] = reset_code
        users = self.user_manager.load_users()
        for u in users:
            if u.get('user_id') == user['user_id']:
                u['reset_code'] = reset_code
        self.user_manager.save_users(users)
        self.audit_log_manager.add_log(user['user_id'], f'Gửi mã đặt lại mật khẩu: {reset_code}')
        # Nếu có hệ thống gửi email thực tế, gọi hàm gửi email ở đây
        QMessageBox.information(self, 'Đặt lại mật khẩu', f"Mã đặt lại mật khẩu cho {user.get('email','')}: {reset_code}")
