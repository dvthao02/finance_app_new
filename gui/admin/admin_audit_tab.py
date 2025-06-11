from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtCore import Qt

class AdminAuditTab(QWidget):
    def __init__(self, audit_log_manager, parent=None):
        super().__init__(parent)
        self.audit_log_manager = audit_log_manager
        self.init_ui()
        self.load_audit_log_table()

    def init_ui(self):
        layout = QVBoxLayout(self)
        label = QLabel("Lịch sử hoạt động (Audit Log)")
        label.setStyleSheet("font-size:14px;font-weight:bold;margin-bottom:8px;")
        layout.addWidget(label)
        self.audit_table = QTableWidget(0, 2)
        self.audit_table.setHorizontalHeaderLabels(["Thời gian", "Hành động"])
        self.audit_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.audit_table.setStyleSheet("font-size:14px;")
        self.audit_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.audit_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.audit_table)
        self.setLayout(layout)

    def load_audit_log_table(self):
        logs = self.audit_log_manager.get_all_logs()
        self.audit_table.setRowCount(0)
        for log in reversed(logs[-50:]):
            row = self.audit_table.rowCount()
            self.audit_table.insertRow(row)
            timestamp_fmt = self.format_datetime(log.get('timestamp', ''))
            self.audit_table.setItem(row, 0, QTableWidgetItem(timestamp_fmt))
            self.audit_table.setItem(row, 1, QTableWidgetItem(f"{log.get('action', '')} (user: {log.get('user_id', '')})"))

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
