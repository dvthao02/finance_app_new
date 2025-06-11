from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem

class AdminAuditTab(QWidget):
    def __init__(self, audit_log_manager, parent=None):
        super().__init__(parent)
        self.audit_log_manager = audit_log_manager
        self.init_ui()
        self.load_audit_log_table()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Lịch sử hoạt động (Audit Log)"))
        self.audit_table = QTableWidget(0, 2)
        self.audit_table.setHorizontalHeaderLabels(["Thời gian", "Hành động"])
        layout.addWidget(self.audit_table)
        self.logout_btn = QPushButton("Đăng xuất")
        layout.addWidget(self.logout_btn)

    def load_audit_log_table(self):
        logs = self.audit_log_manager.get_all_logs()
        self.audit_table.setRowCount(0)
        for log in reversed(logs[-50:]):
            row = self.audit_table.rowCount()
            self.audit_table.insertRow(row)
            self.audit_table.setItem(row, 0, QTableWidgetItem(log.get('timestamp', '')))
            self.audit_table.setItem(row, 1, QTableWidgetItem(f"{log.get('action', '')} (user: {log.get('user_id', '')})"))
