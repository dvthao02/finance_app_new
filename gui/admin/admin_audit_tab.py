from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
from PyQt5.QtGui import QFont
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
        label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(label)
        self.audit_table = QTableWidget(0, 2)
        self.audit_table.setHorizontalHeaderLabels(["Thời gian", "Hành động"])
        self.audit_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.audit_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.audit_table.setAlternatingRowColors(True)
        self.audit_table.setStyleSheet("QTableWidget {border:1px solid #ccc;} QHeaderView::section {background:#f5f5f5; font-weight:bold;}")
        self.audit_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.audit_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.audit_table.setMinimumHeight(350)
        self.audit_table.setFont(QFont("Segoe UI", 10))
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
