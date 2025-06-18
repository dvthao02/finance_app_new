from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QDateEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QInputDialog
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QColor
import logging
from utils.ui_styles import TableStyleHelper, ButtonStyleHelper, UIStyles

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
        
        # Cải thiện table với styling chung
        self.user_table = QTableWidget(0, 6)
        self.user_table.setHorizontalHeaderLabels(["ID", "Tên hiển thị", "Email", "Ngày đăng ký", "Lần đăng nhập cuối", "Trạng thái"])
          # Áp dụng styling chung cho table
        TableStyleHelper.apply_common_table_style(self.user_table)
        TableStyleHelper.setup_table_selection_events(
            self.user_table, 
            self.on_selection_changed, 
            self.on_item_clicked
        )
        
        # Fix display issues - ensure consistent row height
        self.user_table.verticalHeader().setDefaultSectionSize(35)
        self.user_table.verticalHeader().setMinimumSectionSize(35)
        
        # Ensure all columns are visible and have minimum width
        header = self.user_table.horizontalHeader()
        header.setMinimumSectionSize(80)
        
        layout.addWidget(self.user_table)
        
        btn_layout = QHBoxLayout()
        self.btn_view_detail = QPushButton("Xem chi tiết")
        self.btn_lock = QPushButton("Khóa tài khoản")
        self.btn_unlock = QPushButton("Mở khóa tài khoản")
        self.btn_reset_pw = QPushButton("Đặt lại mật khẩu")
        
        # Áp dụng styling chung cho buttons
        ButtonStyleHelper.style_primary_button(self.btn_view_detail)
        ButtonStyleHelper.style_danger_button(self.btn_lock)
        ButtonStyleHelper.style_success_button(self.btn_unlock)
        ButtonStyleHelper.style_normal_button(self.btn_reset_pw)
        
        btn_layout.addWidget(self.btn_view_detail)
        btn_layout.addWidget(self.btn_lock)
        btn_layout.addWidget(self.btn_unlock)
        btn_layout.addWidget(self.btn_reset_pw)
        layout.addLayout(btn_layout)
        self.btn_view_detail.clicked.connect(self.view_user_detail)
        self.btn_lock.clicked.connect(self.lock_user)
        self.btn_unlock.clicked.connect(self.unlock_user)
        self.btn_reset_pw.clicked.connect(self.reset_user_password)
        self.user_search_input.returnPressed.connect(self.search_user)
          # Initially disable buttons until selection is made
        self.btn_view_detail.setEnabled(False)
        self.btn_lock.setEnabled(False)
        self.btn_unlock.setEnabled(False)
        self.btn_reset_pw.setEnabled(False)
    
    def add_user_to_table(self, user):
        """Adds a single user to the table, handling potential data errors."""
        try:
            row = self.user_table.rowCount()
            self.user_table.insertRow(row)

            # Safely get user data
            user_id = user.get('user_id', 'N/A')
            full_name = user.get('full_name', 'N/A')
            email = user.get('email', 'N/A')
            created_at = user.get('created_at', '')
            last_login = user.get('last_login', '')
            is_active = user.get('is_active', True)

            # Format data for display
            created_at_fmt = self.format_datetime(created_at)
            last_login_fmt = self.format_datetime(last_login)
            status_text = 'Hoạt động' if is_active else 'Bị khóa'

            # Create and set table items
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user_id)))
            self.user_table.setItem(row, 1, QTableWidgetItem(full_name))
            self.user_table.setItem(row, 2, QTableWidgetItem(email))
            self.user_table.setItem(row, 3, QTableWidgetItem(created_at_fmt))
            self.user_table.setItem(row, 4, QTableWidgetItem(last_login_fmt))
            self.user_table.setItem(row, 5, QTableWidgetItem(status_text))

        except Exception as e:
            logging.error(f"Error adding user row for {user.get('user_id', 'UNKNOWN')}: {e}")
            # If adding a user fails, add an error row to make it visible
            try:
                row = self.user_table.rowCount()
                self.user_table.insertRow(row)
                self.user_table.setItem(row, 0, QTableWidgetItem(str(user.get('user_id', 'ERROR'))))
                self.user_table.setItem(row, 1, QTableWidgetItem("Lỗi khi tải dữ liệu"))
            except Exception as inner_e:
                logging.critical(f"Could not add error row to user table: {inner_e}")

    def load_users_table(self):
        """Load users data into table with proper display handling"""
        try:
            self.user_table.setRowCount(0)
            users = self.user_manager.load_users()
            logging.debug(f"Loading {len(users)} users into table...")
            for user in users:
                self.add_user_to_table(user)
            
            self.user_table.resizeColumnsToContents()
            self.user_table.viewport().update()
            logging.info(f"Table loading completed. Total rows: {self.user_table.rowCount()}")

        except Exception as e:
            logging.error(f"Critical error loading users table: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "Lỗi nghiêm trọng", f"Không thể tải danh sách người dùng: {e}")

    def search_user(self):
        keyword = self.user_search_input.text().lower().strip()
        status = self.user_status_filter.currentText()
        from_date = self.user_from_date.date().toString("yyyy-MM-dd")
        to_date = self.user_to_date.date().toString("yyyy-MM-dd")
        
        try:
            users = self.user_manager.load_users()
            filtered_users = []

            for user in users:
                # Keyword filter
                if keyword:
                    if keyword not in user.get('full_name', '').lower() and keyword not in user.get('email', '').lower():
                        continue
                
                # Status filter
                is_active = user.get('is_active', True)
                if status == 'Hoạt động' and not is_active:
                    continue
                if status == 'Bị khóa' and is_active:
                    continue
                
                # Date filter
                created_at = user.get('created_at', '')
                if created_at:
                    user_date = created_at[:10]
                    if from_date and user_date < from_date:
                        continue
                    if to_date and user_date > to_date:
                        continue
                
                filtered_users.append(user)

            self.user_table.setRowCount(0)
            for user in filtered_users:
                self.add_user_to_table(user)
        
        except Exception as e:
            logging.error(f"Error during user search: {e}")
            QMessageBox.warning(self, "Lỗi", f"Đã xảy ra lỗi khi tìm kiếm: {e}")

    def format_datetime(self, dt_str):
        from datetime import datetime
        from utils.file_helper import format_datetime_display
        try:
            if not dt_str:
                return ''
            return format_datetime_display(dt_str)
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
        
        created_at_fmt = self.format_datetime(user.get('created_at',''))
        last_login_fmt = self.format_datetime(user.get('last_login',''))
        
        info = f"ID: {user.get('user_id','')}\nTên: {user.get('full_name','')}\nEmail: {user.get('email','')}\nNgày đăng ký: {created_at_fmt}\nLần đăng nhập cuối: {last_login_fmt}\nTrạng thái: {'Hoạt động' if user.get('is_active', True) else 'Bị khóa'}\nĐịa chỉ IP đăng ký: {user.get('register_ip','N/A')}"
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
        try:
            self.user_manager.update_user(user['user_id'], is_active=False)
            self.audit_log_manager.add_log(f"User account {user['user_id']} locked", f"Reason: {reason}")
            QMessageBox.information(self, 'Thành công', 'Đã khóa tài khoản!')
            self.load_users_table()
        except Exception as e:
            logging.error(f"Failed to lock user {user['user_id']}: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể khóa tài khoản: {e}")

    def unlock_user(self):
        user = self.get_selected_user()
        if not user:
            return
        if user.get('is_active', True):
            QMessageBox.information(self, 'Thông báo', 'Tài khoản đang hoạt động!')
            return
        try:
            self.user_manager.update_user(user['user_id'], is_active=True)
            self.audit_log_manager.add_log(f"User account {user['user_id']} unlocked", "Account unlocked")
            QMessageBox.information(self, 'Thành công', 'Đã mở khóa tài khoản!')
            self.load_users_table()
        except Exception as e:
            logging.error(f"Failed to unlock user {user['user_id']}: {e}")
            QMessageBox.warning(self, "Lỗi", f"Không thể mở khóa tài khoản: {e}")

    def reset_user_password(self):
        user = self.get_selected_user()
        if not user:
            return
        from PyQt5.QtWidgets import QInputDialog
        from utils.file_helper import is_strong_password
        from data_manager.notification_manager import NotificationManager
        # Hỏi admin nhập mật khẩu mới
        new_password, ok = QInputDialog.getText(self, 'Đặt lại mật khẩu', f'Nhập mật khẩu mới cho {user.get("email") or user.get("username") or user.get("user_id")}:')
        if not ok or not new_password:
            return
        if not is_strong_password(new_password):
            QMessageBox.warning(self, 'Lỗi', 'Mật khẩu yếu. Phải gồm chữ hoa, thường, số và ký tự đặc biệt, ít nhất 8 ký tự.')
            return
        result = self.user_manager.admin_reset_password(user['user_id'], new_password)
        if result.get('status') == 'success':
            self.audit_log_manager.add_log(user['user_id'], f'Cấp lại mật khẩu mới (admin): {new_password}')
            info = user.get('email') or user.get('username') or user.get('user_id')
            # Gửi notification cho user
            notify_manager = NotificationManager()
            notify_manager.add_notification(
                title='Mật khẩu của bạn đã được đặt lại',
                content=f'Mật khẩu mới của bạn là: {new_password}',
                notify_type='Cảnh báo',
                user_id=user['user_id']
            )
            QMessageBox.information(self, 'Cấp lại mật khẩu', f"Mật khẩu mới cho {info}: {new_password}\nĐã gửi thông báo cho người dùng.")
        else:
            QMessageBox.warning(self, 'Lỗi', result.get('message', 'Không thể đặt lại mật khẩu!'))    
    def on_item_clicked(self, item):
        """Handle item click to ensure selection is visible"""
        if item:
            row = item.row()
            self.user_table.selectRow(row)
            
            # Force refresh the selection styling
            self.user_table.clearSelection()
            self.user_table.selectRow(row)
            
            # Ensure the selection is properly formatted
            for col in range(self.user_table.columnCount()):
                cell_item = self.user_table.item(row, col)
                if cell_item:
                    # Force item update
                    cell_item.setSelected(True)
    
    def on_selection_changed(self):
        """Handle table selection changes to provide visual feedback"""
        current_row = self.user_table.currentRow()
        has_selection = current_row >= 0
        
        # Force refresh table styling to ensure selection is visible
        if has_selection:
            # Force repaint of selected row
            for col in range(self.user_table.columnCount()):
                item = self.user_table.item(current_row, col)
                if item:
                    # Force update display
                    text = item.text()
                    item.setText(text)
                    item.setSelected(True)
            
            # Force table update
            self.user_table.viewport().update()
        
        if has_selection:
            # Enable/disable buttons based on selection
            try:
                user_id = self.user_table.item(current_row, 0).text()
                users = self.user_manager.load_users()
                user = None
                for u in users:
                    if u.get('user_id') == user_id:
                        user = u
                        break
                
                if user:
                    self.btn_view_detail.setEnabled(True)
                    self.btn_lock.setEnabled(user.get('is_active', True))
                    self.btn_unlock.setEnabled(not user.get('is_active', True))
                    self.btn_reset_pw.setEnabled(True)
                else:
                    self.btn_view_detail.setEnabled(False)
                    self.btn_lock.setEnabled(False)
                    self.btn_unlock.setEnabled(False)
                    self.btn_reset_pw.setEnabled(False)
            except Exception:
                # If there's any error, disable all buttons
                self.btn_view_detail.setEnabled(False)
                self.btn_lock.setEnabled(False)
                self.btn_unlock.setEnabled(False)
                self.btn_reset_pw.setEnabled(False)
        else:
            # No selection - disable buttons
            self.btn_view_detail.setEnabled(False)
            self.btn_lock.setEnabled(False)
            self.btn_unlock.setEnabled(False)
            self.btn_reset_pw.setEnabled(False)
