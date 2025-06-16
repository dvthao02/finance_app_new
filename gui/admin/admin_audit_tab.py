from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout, QDateEdit
from PyQt5.QtCore import Qt, QDate
from utils.ui_styles import TableStyleHelper, ButtonStyleHelper, UIStyles
from utils.file_helper import format_datetime_display

class AdminAuditTab(QWidget):
    def __init__(self, audit_log_manager, parent=None):
        super().__init__(parent)
        self.audit_log_manager = audit_log_manager
        self.init_ui()
        self.load_audit_log_table()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header_layout = QHBoxLayout()
        label = QLabel("Lịch sử hoạt động (Audit Log)")
        label.setStyleSheet("font-size:14px;font-weight:bold;margin-bottom:8px;")
        header_layout.addWidget(label)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Search controls
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 10)  # Thêm margin dưới
        
        # From date
        from_date_label = QLabel("Từ ngày:")
        search_layout.addWidget(from_date_label)
        
        self.from_date = QDateEdit(calendarPopup=True)
        self.from_date.setDisplayFormat("dd-MM-yyyy")
        last_week = QDate.currentDate().addDays(-7)
        self.from_date.setDate(last_week)
        self.from_date.setFixedWidth(120)
        search_layout.addWidget(self.from_date)
        
        # To date
        to_date_label = QLabel("Đến ngày:")
        search_layout.addWidget(to_date_label)
        
        self.to_date = QDateEdit(calendarPopup=True)
        self.to_date.setDisplayFormat("dd-MM-yyyy")
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setFixedWidth(120)
        search_layout.addWidget(self.to_date)
        
        # Search button
        self.search_button = QPushButton("Tìm kiếm")
        self.search_button.setFixedWidth(140)
        self.search_button.setFixedHeight(20)
        self.search_button.clicked.connect(self.search_logs)
        ButtonStyleHelper.style_primary_button(self.search_button)
        search_layout.addWidget(self.search_button)
        
        # Reset button
        self.reset_button = QPushButton("Xem tất cả")
        self.reset_button.setFixedWidth(140)
        self.reset_button.setFixedHeight(20)
        self.reset_button.clicked.connect(self.load_audit_log_table)
        ButtonStyleHelper.style_normal_button(self.reset_button)
        search_layout.addWidget(self.reset_button)
        
        search_layout.addStretch()
        layout.addLayout(search_layout)
        
        # Table
        self.audit_table = QTableWidget(0, 2)
        self.audit_table.setHorizontalHeaderLabels(["Thời gian", "Hành động"])
        
        # Áp dụng styling chung
        TableStyleHelper.apply_common_table_style(self.audit_table)
          # Cấu hình hiển thị bảng - cố định kích thước theo form
        header = self.audit_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Interactive)  # Cho phép người dùng thay đổi kích thước cột thời gian
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Hành động sẽ lấp đầy không gian còn lại
        
        # Đặt các thuộc tính khác
        self.audit_table.setColumnWidth(0, 180)  # Đặt chiều rộng cố định cho cột thời gian
        self.audit_table.verticalHeader().setVisible(False)  # Ẩn header dọc
        self.audit_table.setAlternatingRowColors(True)  # Màu dòng xen kẽ
        self.audit_table.horizontalHeader().setStretchLastSection(True)  # Đảm bảo cột cuối cùng kéo dài hết chiều rộng bảng
        self.audit_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)  # Hiển thị thanh cuộn ngang khi cần
          # Đặt bảng vào layout chính - sẽ theo kích thước của form
        layout.addWidget(self.audit_table)
        
        # Cấu hình layout chính
        self.setLayout(layout)

    def load_audit_log_table(self):
        """Tải toàn bộ log history"""
        logs = self.audit_log_manager.get_all_logs()
        self._display_logs(logs)

    def search_logs(self):
        """Tìm kiếm logs theo khoảng thời gian"""
        from_date = self.from_date.date().toString("yyyy-MM-dd")
        to_date = self.to_date.date().toString("yyyy-MM-dd")
        
        logs = self.audit_log_manager.get_logs_by_date_range(from_date, to_date)
        self._display_logs(logs)

    def _display_logs(self, logs):
        """Hiển thị logs lên bảng"""
        self.audit_table.setRowCount(0)
        
        # Hiển thị từ mới đến cũ nhất
        for log in reversed(logs):
            row = self.audit_table.rowCount()
            self.audit_table.insertRow(row)
            
            # Cài đặt item thời gian
            timestamp_fmt = self.format_datetime(log.get('timestamp', ''))
            time_item = QTableWidgetItem(timestamp_fmt)
            time_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.audit_table.setItem(row, 0, time_item)
            
            # Cài đặt item hành động
            action_item = QTableWidgetItem(f"{log.get('action', '')} (user: {log.get('user_id', '')})") 
            action_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            self.audit_table.setItem(row, 1, action_item)
            
            # Thiết lập chiều cao hàng
            self.audit_table.setRowHeight(row, 30)
        
        # Tối ưu hóa kích thước bảng
        self.audit_table.resizeColumnsToContents()
          # Đảm bảo thời gian hiển thị đúng kích thước
        self.audit_table.setColumnWidth(0, 180)
            
        # Đảm bảo dữ liệu được hiển thị đúng ngay khi mở tab
        self.audit_table.horizontalHeader().setStretchLastSection(True)
        
        # Thiết lập chiều cao dòng cố định cho tất cả các dòng
        for row in range(self.audit_table.rowCount()):
            self.audit_table.setRowHeight(row, 30)
        
        # Cập nhật giao diện ngay lập tức
        self.audit_table.update()

    def format_datetime(self, dt_str):
        return format_datetime_display(dt_str)    # Phương thức xử lý sự kiện hiển thị để đảm bảo bảng hiển thị đúng theo form
    def showEvent(self, event):
        """Được gọi khi widget trở nên hiển thị"""
        super().showEvent(event)
        # Đảm bảo kích thước cột và form hiển thị đúng
        self.audit_table.setColumnWidth(0, 180)
        self.audit_table.horizontalHeader().setStretchLastSection(True)
        self.audit_table.update()
