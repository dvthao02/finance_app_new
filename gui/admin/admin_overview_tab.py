from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QTableWidget, QTableWidgetItem, QFrame, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

class AdminOverviewTab(QWidget):
    def __init__(self, user_manager, transaction_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.init_ui()
        self.load_dashboard_stats()

    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Stats cards
        stats_group = QGroupBox("Thống kê tổng quan")
        stats_layout = QGridLayout(stats_group)
        
        font_big = QFont("Segoe UI", 18, QFont.Bold)
        
        self.lbl_total_users = QLabel("0")
        self.lbl_total_users.setFont(font_big)
        self.lbl_total_users.setStyleSheet("color: #1976D2;")
        
        self.lbl_new_users = QLabel("0")
        self.lbl_new_users.setFont(font_big)
        self.lbl_new_users.setStyleSheet("color: #43A047;")
        
        self.lbl_total_transactions = QLabel("0")
        self.lbl_total_transactions.setFont(font_big)
        self.lbl_total_transactions.setStyleSheet("color: #F9A825;")
        
        self.lbl_today_transactions = QLabel("0")
        self.lbl_today_transactions.setFont(font_big)
        self.lbl_today_transactions.setStyleSheet("color: #D32F2F;")
        
        stats_layout.addWidget(self._stat_card("Tổng người dùng", self.lbl_total_users, "#E3F2FD"), 0, 0)
        stats_layout.addWidget(self._stat_card("Người dùng mới trong tháng", self.lbl_new_users, "#E8F5E9"), 0, 1)
        stats_layout.addWidget(self._stat_card("Tổng số giao dịch", self.lbl_total_transactions, "#FFFDE7"), 1, 0)
        stats_layout.addWidget(self._stat_card("Giao dịch hôm nay", self.lbl_today_transactions, "#FFEBEE"), 1, 1)
        
        layout.addWidget(stats_group)
        
        # Charts placeholder
        chart_placeholder = QLabel("Biểu đồ thống kê (Cần cài đặt matplotlib để hiển thị)")
        chart_placeholder.setStyleSheet("""
            text-align: center; 
            padding: 40px; 
            background-color: #f0f0f0; 
            border-radius: 10px;
            font-size: 14px;
            color: #666;
        """)
        chart_placeholder.setAlignment(Qt.AlignCenter)
        layout.addWidget(chart_placeholder)
        
        # Recent users table
        users_group = QGroupBox("Người dùng đăng ký gần đây")
        users_layout = QVBoxLayout(users_group)
        
        self.recent_table = QTableWidget(0, 3)
        self.recent_table.setHorizontalHeaderLabels(["ID", "Tên", "Ngày đăng ký"])
        self.recent_table.setStyleSheet("font-size:14px;")
        self.recent_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.recent_table.setMinimumHeight(180)
        
        users_layout.addWidget(self.recent_table)
        layout.addWidget(users_group)

    def _stat_card(self, label, value_widget, bg_color):
        card = QFrame()
        card.setStyleSheet(f"background:{bg_color}; border-radius:10px; padding:12px 18px;")
        v = QVBoxLayout(card)
        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 11))
        v.addWidget(lbl)
        v.addWidget(value_widget)
        return card

    def load_dashboard_stats(self):
        from datetime import datetime
        
        try:
            users = self.user_manager.load_users()
            transactions = self.transaction_manager.get_all_transactions()
            
            now = datetime.now()
            month = now.strftime('%Y-%m')
            new_users = [u for u in users if u.get('created_at', '').startswith(month)]
            today = now.strftime('%Y-%m-%d')
            today_transactions = [t for t in transactions if t.get('created_at', '').startswith(today)]
            
            self.lbl_total_users.setText(str(len(users)))
            self.lbl_new_users.setText(str(len(new_users)))
            self.lbl_total_transactions.setText(str(len(transactions)))
            self.lbl_today_transactions.setText(str(len(today_transactions)))
            
            # Load recent users table
            recent = sorted(users, key=lambda u: u.get('created_at', ''), reverse=True)[:5]
            self.recent_table.setRowCount(0)
            for u in recent:
                row = self.recent_table.rowCount()
                self.recent_table.insertRow(row)
                self.recent_table.setItem(row, 0, QTableWidgetItem(u.get('user_id', '')))
                self.recent_table.setItem(row, 1, QTableWidgetItem(u.get('full_name', '')))
                created_at_fmt = self.format_datetime(u.get('created_at', ''))
                self.recent_table.setItem(row, 2, QTableWidgetItem(created_at_fmt))
                
        except Exception as e:
            print(f"Error loading dashboard stats: {e}")

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
