from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QTableWidget, QTableWidgetItem, QFrame, QSizePolicy, QHeaderView, QHBoxLayout, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from utils.ui_styles import TableStyleHelper, ButtonStyleHelper, UIStyles

class AdminOverviewTab(QWidget):
    def __init__(self, user_manager, transaction_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.init_ui()
        self.load_dashboard_stats()

    def _stat_card(self, label, value_widget, bg_color):
        card = QFrame()
        card.setStyleSheet(f"background:{bg_color}; border-radius:10px; padding:8px 10px; margin:2px;")
        v = QVBoxLayout(card)
        v.setSpacing(4)
        v.setAlignment(Qt.AlignVCenter)
        lbl = QLabel(label)
        lbl.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl.setAlignment(Qt.AlignCenter)
        value_widget.setAlignment(Qt.AlignCenter)
        value_widget.setStyleSheet(value_widget.styleSheet() + "; font-size: 16px; font-weight: bold; margin-top: 2px; margin-bottom: 2px;")
        v.addStretch(1)
        v.addWidget(lbl)
        v.addWidget(value_widget)
        v.addStretch(1)
        return card

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(8)
        # --- Hàng trên cùng: Biểu đồ + 2 box thống kê ---
        top_row = QHBoxLayout()
        top_row.setSpacing(8)
        # Biểu đồ bên trái (chiếm 2 phần)
        import traceback
        try:
            import matplotlib
            matplotlib.use('Qt5Agg')
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
            from matplotlib.figure import Figure
            chart_vbox = QVBoxLayout()
            # Thêm label ngày tháng filter
            self.chart_date_label = QLabel()
            self.chart_date_label.setStyleSheet("font-size: 11px; color: #1976D2; font-weight: bold; margin-bottom: 2px;")
            chart_vbox.addWidget(self.chart_date_label)
            # Thêm filter thời gian
            filter_layout = QHBoxLayout()
            filter_layout.setSpacing(6)
            filter_label = QLabel("Lọc thời gian:")
            filter_label.setStyleSheet("font-size: 11px; font-weight: bold;")
            self.chart_time_filter = QComboBox()
            self.chart_time_filter.addItems(["Tháng này", "Tháng trước", "7 ngày gần nhất", "30 ngày gần nhất"])
            self.chart_time_filter.setCurrentIndex(0)
            self.chart_time_filter.setFixedWidth(140)
            filter_layout.addWidget(filter_label)
            filter_layout.addWidget(self.chart_time_filter)
            filter_layout.addStretch(1)
            chart_vbox.addLayout(filter_layout)
            self.chart_group = QGroupBox()
            chart_layout = QVBoxLayout(self.chart_group)
            chart_layout.setContentsMargins(8, 24, 8, 8)  # tăng margin top để không đè tiêu đề
            self.figure = Figure(figsize=(3.2,2.5))
            self.canvas = FigureCanvas(self.figure)
            chart_layout.addWidget(self.canvas)
            self.chart_group.setStyleSheet("margin-top:4px;margin-bottom:4px;")
            self.chart_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            chart_vbox.addWidget(self.chart_group)
            top_row.addLayout(chart_vbox, 2)
            self.chart_time_filter.currentIndexChanged.connect(self.load_dashboard_stats)
        except Exception as e:
            print(f'[ERROR] Lỗi khi khởi tạo chart: {e}')
            traceback.print_exc()
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
            top_row.addWidget(chart_placeholder, 2)
        # Box thống kê người dùng
        user_stats = QGroupBox("Thống kê người dùng")
        user_stats.setStyleSheet("QGroupBox { font-size: 12px; font-weight: bold; }")
        user_stats_layout = QVBoxLayout(user_stats)
        user_stats_layout.setAlignment(Qt.AlignTop)
        font_big = QFont("Segoe UI", 14, QFont.Bold)
        self.lbl_total_users = QLabel("0"); self.lbl_total_users.setFont(font_big); self.lbl_total_users.setStyleSheet("color: #1976D2;")
        self.lbl_new_users = QLabel("0"); self.lbl_new_users.setFont(font_big); self.lbl_new_users.setStyleSheet("color: #43A047;")
        user_stats_layout.addWidget(self._stat_card("Tổng người dùng", self.lbl_total_users, "#E3F2FD"))
        user_stats_layout.addWidget(self._stat_card("Người dùng mới trong tháng", self.lbl_new_users, "#E8F5E9"))
        user_stats_layout.addStretch(1)
        user_stats.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        top_row.addWidget(user_stats, 1)
        # Box thống kê giao dịch
        trans_stats = QGroupBox("Thống kê giao dịch")
        trans_stats.setStyleSheet("QGroupBox { font-size: 12px; font-weight: bold; }")
        trans_stats_layout = QVBoxLayout(trans_stats)
        trans_stats_layout.setAlignment(Qt.AlignTop)
        self.lbl_total_transactions = QLabel("0"); self.lbl_total_transactions.setFont(font_big); self.lbl_total_transactions.setStyleSheet("color: #F9A825;")
        self.lbl_today_transactions = QLabel("0"); self.lbl_today_transactions.setFont(font_big); self.lbl_today_transactions.setStyleSheet("color: #D32F2F;")
        trans_stats_layout.addWidget(self._stat_card("Tổng số giao dịch", self.lbl_total_transactions, "#FFFDE7"))
        trans_stats_layout.addWidget(self._stat_card("Giao dịch hôm nay", self.lbl_today_transactions, "#FFEBEE"))
        trans_stats_layout.addStretch(1)
        trans_stats.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        top_row.addWidget(trans_stats, 1)
        
        self.main_layout.addLayout(top_row)
        
        # --- Bảng recent users bên dưới ---
        users_group = QGroupBox("Người dùng đăng ký gần đây")
        users_layout = QVBoxLayout(users_group)
        
        self.recent_table = QTableWidget(0, 3)
        self.recent_table.setHorizontalHeaderLabels(["ID", "Tên", "Ngày đăng ký"])
        
        # Áp dụng styling chung
        TableStyleHelper.apply_common_table_style(self.recent_table)
        
        self.recent_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.recent_table.setMinimumHeight(180)
        users_layout.addWidget(self.recent_table)
        users_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(users_group)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Responsive: tăng cỡ chữ khi rộng > 1100, giảm khi nhỏ
        w = self.width()
        if w > 1100:
            font_big = QFont("Segoe UI", 22, QFont.Bold)
            font_label = QFont("Segoe UI", 13, QFont.Bold)
        elif w > 900:
            font_big = QFont("Segoe UI", 16, QFont.Bold)
            font_label = QFont("Segoe UI", 11, QFont.Bold)
        else:
            font_big = QFont("Segoe UI", 12, QFont.Bold)
            font_label = QFont("Segoe UI", 9, QFont.Bold)
        for lbl in [self.lbl_total_users, self.lbl_new_users, self.lbl_total_transactions, self.lbl_today_transactions]:
            lbl.setFont(font_big)
        # Responsive: nếu chiều rộng nhỏ, xếp dọc các box thống kê
        if self.width() < 900:
            if hasattr(self, 'stats_row'):
                # Xóa các widget khỏi layout cũ
                while self.stats_row.count():
                    item = self.stats_row.takeAt(0)
                    w = item.widget()
                    if w:
                        w.setParent(None)
                # Thêm lại theo chiều dọc
                vbox = QVBoxLayout()
                for box in [getattr(self, n) for n in ['_user_stats','_trans_stats'] if hasattr(self, n)]:
                    vbox.addWidget(box)
                self.main_layout.insertLayout(0, vbox)
        else:
            # Xếp lại theo chiều ngang nếu rộng
            pass

    def load_dashboard_stats(self):
        from datetime import datetime, timedelta
        try:
            users = self.user_manager.load_users()
            transactions = self.transaction_manager.get_all_transactions()
            now = datetime.now()
            filter_mode = getattr(self, 'chart_time_filter', None)
            if filter_mode:
                idx = filter_mode.currentIndex()
            else:
                idx = 0
            if idx == 0:  # Tháng này
                chart_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                chart_to = now
            elif idx == 1:  # Tháng trước
                first_this_month = now.replace(day=1)
                last_month = first_this_month - timedelta(days=1)
                chart_from = last_month.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                chart_to = last_month.replace(hour=23, minute=59, second=59, microsecond=999999)
            elif idx == 2:  # 7 ngày gần nhất
                chart_from = now - timedelta(days=6)
                chart_from = chart_from.replace(hour=0, minute=0, second=0, microsecond=0)
                chart_to = now
            elif idx == 3:  # 30 ngày gần nhất
                chart_from = now - timedelta(days=29)
                chart_from = chart_from.replace(hour=0, minute=0, second=0, microsecond=0)
                chart_to = now
            else:
                chart_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                chart_to = now
            # Hiển thị label ngày tháng filter
            if hasattr(self, 'chart_date_label'):
                self.chart_date_label.setText(f"Khoảng thời gian: {chart_from.strftime('%d-%m-%Y')} đến {chart_to.strftime('%d-%m-%Y')}")
            # Lọc user theo thời gian
            def in_range(dt_str):
                try:
                    dt = datetime.fromisoformat(dt_str.split('T')[0])
                    return chart_from.date() <= dt.date() <= chart_to.date()
                except:
                    return False
            new_users = [u for u in users if in_range(u.get('created_at', ''))]
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
            # Vẽ biểu đồ người dùng mới trong tháng nếu có matplotlib
            if hasattr(self, 'figure'):
                self.figure.clear()
                self.figure.set_figheight(2.5)
                self.figure.set_figwidth(3.2)
                ax = self.figure.add_subplot(111)
                from collections import Counter
                days = [u.get('created_at', '')[8:10] for u in new_users if len(u.get('created_at', '')) >= 10]
                count_by_day = Counter(days)
                x = sorted(count_by_day.keys())
                y = [count_by_day[d] for d in x]
                if len(x) <= 7:
                    wedges, texts, autotexts = ax.pie(y, labels=[f"Ngày {d}" for d in x], autopct='%1.1f%%', startangle=90, colors=['#1976D2','#43A047','#F9A825','#D32F2F','#6A1B9A','#B71C1C','#E1F5FE'], textprops={'fontsize': 11})
                    ax.set_title('Tỉ lệ người dùng mới theo ngày', fontsize=11, fontweight='bold', pad=12, loc='center')
                    ax.legend(wedges, [f"Ngày {d}" for d in x], title="Chú thích", loc="best", bbox_to_anchor=(1, 0.5), fontsize=10)
                else:
                    bars = ax.bar(x, y, color='#1976D2', label='Số user mới')
                    ax.set_title('Người dùng mới theo ngày', fontsize=11, fontweight='bold', pad=12, loc='center')
                    ax.set_xlabel('Ngày', fontsize=10)
                    ax.set_ylabel('Số lượng', fontsize=10)
                    ax.grid(axis='y', linestyle='--', alpha=0.5)
                    ax.legend([bars], ['Số user mới'], loc='best', fontsize=10)
                self.figure.tight_layout(rect=[0, 0, 1, 1])
                self.canvas.draw_idle()
                self.canvas.flush_events()
                self.canvas.updateGeometry()
                self.updateGeometry()
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
