import traceback
from collections import Counter
from datetime import datetime, timedelta

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QComboBox, QFrame, QGroupBox, QHBoxLayout,
                             QHeaderView, QLabel, QSizePolicy, QTableWidget,
                             QTableWidgetItem, QVBoxLayout, QWidget)

# Conditional import for Matplotlib
try:
    import matplotlib
    matplotlib.use('Qt5Agg')
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class AdminOverviewTab(QWidget):
    def __init__(self, user_manager, transaction_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.init_ui()
        self.load_dashboard_stats()

    def _stat_card(self, label_text, value_widget, bg_color):
        """Creates a styled frame for displaying a single statistic."""
        card = QFrame()
        # CHANGE: Increased padding for a more spacious look like in the image.
        card.setStyleSheet(f"background-color: {bg_color}; border-radius: 8px; padding: 15px;")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)
        layout.setAlignment(Qt.AlignCenter)

        # CHANGE: The label is now created inside the function for better encapsulation.
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 11))
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("color: #334155; font-weight: bold;")

        value_widget.setAlignment(Qt.AlignCenter)
        # CHANGE: Adjusted font for better visual hierarchy.
        value_widget.setFont(QFont("Segoe UI", 18, QFont.Bold))

        layout.addStretch()
        layout.addWidget(label)
        layout.addWidget(value_widget)
        layout.addStretch()
        return card

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        # CHANGE: Added margins and increased spacing for the main layout.
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        # --- Top row: Chart + Stats Boxes ---
        top_row_layout = QHBoxLayout()
        top_row_layout.setSpacing(15)

        # CHANGE: The entire top-left section is now a single styled QFrame.
        chart_container = QFrame()
        chart_container.setObjectName("chartContainer")
        chart_container.setStyleSheet("#chartContainer { border: 1px solid #e2e8f0; border-radius: 8px; }")
        chart_panel_layout = QVBoxLayout(chart_container)
        chart_panel_layout.setContentsMargins(15, 10, 15, 15)
        chart_panel_layout.setSpacing(10)
        
        # --- Top Bar with Filters ---
        self.date_range_label = QLabel()
        self.date_range_label.setStyleSheet("font-size: 13px; color: #1e293b; font-weight: bold; margin-bottom: 5px;")

        filter_layout = QHBoxLayout()
        filter_label = QLabel("Lọc thời gian:")
        filter_label.setStyleSheet("font-size: 12px; font-weight: bold; color: #1e293b;")
        self.chart_time_filter = QComboBox()
        self.chart_time_filter.addItems(["Tháng này", "Tháng trước", "7 ngày gần nhất", "30 ngày gần nhất"])
        self.chart_time_filter.setFixedWidth(160)
        self.chart_time_filter.setStyleSheet("""
            QComboBox { padding: 5px; border: 1px solid #CBD5E1; border-radius: 4px; background-color: white; }
            QComboBox::drop-down { border: none; }
        """)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.chart_time_filter)
        filter_layout.addStretch(1)

        chart_panel_layout.addWidget(self.date_range_label)
        chart_panel_layout.addLayout(filter_layout)

        # CHANGE: The chart title is now a QLabel for better styling and positioning.
        self.chart_title_label = QLabel()
        self.chart_title_label.setAlignment(Qt.AlignCenter)
        self.chart_title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #1E293B; margin-top: 10px;")
        chart_panel_layout.addWidget(self.chart_title_label)
        
        # --- Matplotlib Canvas ---
        if MATPLOTLIB_AVAILABLE:
            self.figure = Figure(figsize=(5, 4), dpi=100)
            self.figure.patch.set_facecolor('none')  # Transparent background
            self.canvas = FigureCanvas(self.figure)
            self.canvas.setStyleSheet("background-color: transparent;")
            chart_panel_layout.addWidget(self.canvas)
            self.chart_time_filter.currentIndexChanged.connect(self.load_dashboard_stats)
        else:
            chart_placeholder = QLabel("Biểu đồ không thể hiển thị.\nVui lòng cài đặt thư viện matplotlib.")
            chart_placeholder.setAlignment(Qt.AlignCenter)
            chart_placeholder.setStyleSheet("padding: 40px; background-color: #f8fafc; border: 1px dashed #e2e8f0; color: #64748b; border-radius: 5px;")
            chart_panel_layout.addWidget(chart_placeholder)

        # Add the chart panel to the top row layout
        top_row_layout.addWidget(chart_container, 2)  # Stretch factor 2

        # --- Statistics Panels ---
        user_stats_group = QGroupBox("Thống kê người dùng")
        user_stats_group.setStyleSheet("QGroupBox { font-size: 13px; font-weight: bold; color: #334155; } QGroupBox::title { subcontrol-origin: margin; left: 10px; }")
        user_stats_layout = QVBoxLayout(user_stats_group)
        user_stats_layout.setSpacing(10)
        
        self.lbl_total_users = QLabel("0")
        self.lbl_new_users = QLabel("0")
        user_stats_layout.addWidget(self._stat_card("Tổng người dùng", self.lbl_total_users, "#EFF6FF"))
        self.new_users_card_label = self._stat_card("Người dùng mới trong tháng", self.lbl_new_users, "#F0FDF4")
        user_stats_layout.addWidget(self.new_users_card_label)
        user_stats_layout.addStretch(1)

        trans_stats_group = QGroupBox("Thống kê giao dịch")
        trans_stats_group.setStyleSheet("QGroupBox { font-size: 13px; font-weight: bold; color: #334155; } QGroupBox::title { subcontrol-origin: margin; left: 10px; }")
        trans_stats_layout = QVBoxLayout(trans_stats_group)
        trans_stats_layout.setSpacing(10)

        self.lbl_total_transactions = QLabel("0")
        self.lbl_today_transactions = QLabel("0")
        trans_stats_layout.addWidget(self._stat_card("Tổng số giao dịch", self.lbl_total_transactions, "#FEFCE8"))
        trans_stats_layout.addWidget(self._stat_card("Giao dịch hôm nay", self.lbl_today_transactions, "#FEF2F2"))
        trans_stats_layout.addStretch(1)

        top_row_layout.addWidget(user_stats_group, 1) # Stretch factor 1
        top_row_layout.addWidget(trans_stats_group, 1) # Stretch factor 1
        
        self.main_layout.addLayout(top_row_layout)
        
        # --- Bottom Panel: Recent Users Table ---
        recent_users_group = QGroupBox("Người dùng đăng ký gần đây")
        recent_users_group.setStyleSheet("QGroupBox { font-size: 13px; font-weight: bold; color: #334155; } QGroupBox::title { subcontrol-origin: margin; left: 10px; padding-bottom: 5px; }")
        users_layout = QVBoxLayout(recent_users_group)

        self.recent_table = QTableWidget(0, 3)
        self.recent_table.setHorizontalHeaderLabels(["ID", "Tên", "Ngày đăng ký"])
        
        # CHANGE: Specific styling applied to match the screenshot perfectly.
        self.recent_table.verticalHeader().setVisible(False)
        self.recent_table.setShowGrid(False)
        self.recent_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recent_table.setSelectionMode(QTableWidget.SingleSelection)
        self.recent_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.recent_table.setStyleSheet("""
            QTableWidget { background-color: white; border: none; font-size: 13px; }
            QTableWidget::item { padding: 10px; border-bottom: 1px solid #f1f5f9; }
            QHeaderView::section {
                background-color: #f8fafc;
                padding: 10px;
                border: none;
                font-size: 12px;
                font-weight: bold;
                color: #475569;
                text-align: left;
            }
        """)

        header = self.recent_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        
        self.recent_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        users_layout.addWidget(self.recent_table)
        self.main_layout.addWidget(recent_users_group)

    def load_dashboard_stats(self):
        try:
            all_users = self.user_manager.load_users()
            all_transactions = self.transaction_manager.get_all_transactions()
            now = datetime.now()
            
            # --- Determine date range from filter ---
            filter_index = self.chart_time_filter.currentIndex()
            if filter_index == 0:  # Tháng này
                start_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = now
            elif filter_index == 1:  # Tháng trước
                first_this_month = now.replace(day=1)
                last_month_end = first_this_month - timedelta(days=1)
                start_date = last_month_end.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                end_date = last_month_end.replace(hour=23, minute=59, second=59, microsecond=999999)
            elif filter_index == 2:  # 7 ngày gần nhất
                start_date = (now - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now
            else:  # 30 ngày gần nhất
                start_date = (now - timedelta(days=29)).replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = now
            
            self.date_range_label.setText(f"Khoảng thời gian: {start_date.strftime('%d-%m-%Y')} đến {end_date.strftime('%d-%m-%Y')}")
            
            # --- Calculate statistics ---
            new_users_in_period = [u for u in all_users if start_date.date() <= self.parse_date(u.get('created_at')).date() <= end_date.date()]
            today_str = now.strftime('%Y-%m-%d')
            today_transactions = [t for t in all_transactions if t.get('created_at', '').startswith(today_str)]

            # Update stat card colors to match text colors
            self.lbl_total_users.setStyleSheet("color: #1D4ED8;") # Blue
            self.lbl_new_users.setStyleSheet("color: #16A34A;") # Green
            self.lbl_total_transactions.setStyleSheet("color: #D97706;") # Orange/Yellow
            self.lbl_today_transactions.setStyleSheet("color: #DC2626;") # Red
            
            self.lbl_total_users.setText(str(len(all_users)))
            self.lbl_new_users.setText(str(len(new_users_in_period)))
            self.lbl_total_transactions.setText(str(len(all_transactions)))
            self.lbl_today_transactions.setText(str(len(today_transactions)))

            # --- Update Recent Users Table (Top 5 newest overall) ---
            recent_users = sorted(all_users, key=lambda u: self.parse_date(u.get('created_at')), reverse=True)[:5]
            self.recent_table.setRowCount(len(recent_users))
            for i, user in enumerate(recent_users):
                self.recent_table.setItem(i, 0, QTableWidgetItem(user.get('user_id', 'N/A')))
                self.recent_table.setItem(i, 1, QTableWidgetItem(user.get('full_name', 'N/A')))
                formatted_date = self.parse_date(user.get('created_at')).strftime("%d-%m-%Y %H:%M:%S")
                self.recent_table.setItem(i, 2, QTableWidgetItem(formatted_date))
                self.recent_table.setRowHeight(i, 40) # Ensure enough row height

            # --- Update Chart ---
            if MATPLOTLIB_AVAILABLE:
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.patch.set_facecolor('none')

                days_counter = Counter(self.parse_date(u.get('created_at')).strftime('%d') for u in new_users_in_period)
                
                if not days_counter:
                    self.chart_title_label.setText("Thống kê người dùng mới")
                    ax.text(0.5, 0.5, 'Không có dữ liệu cho khoảng thời gian này.', horizontalalignment='center', va='center', transform=ax.transAxes)
                    ax.set_xticks([])
                    ax.set_yticks([])
                # CHANGE: Pie chart logic adjusted to match the screenshot's style.
                elif len(days_counter) <= 7:
                    self.chart_title_label.setText("Tỉ lệ người dùng mới theo ngày")
                    labels = sorted(days_counter.keys())
                    sizes = [days_counter[label] for label in labels]
                    colors = ['#3B82F6', '#60A5FA', '#93C5FD', '#BFDBFE', '#DBEAFE', '#EFF6FF']
                    
                    wedges, _ = ax.pie(sizes, colors=colors, startangle=90)
                    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.
                    
                    # CHANGE: Legend is placed below the chart as in the image.
                    legend_labels = [f"Ngày {l} ({days_counter[l]})" for l in labels]
                    ax.legend(wedges, legend_labels, title="Chú thích", loc='upper center', bbox_to_anchor=(0.5, -0.01), ncol=len(labels), frameon=False)
                    self.figure.subplots_adjust(bottom=0.25)
                else: # Bar chart for more than 7 data points
                    self.chart_title_label.setText("Số lượng người dùng mới theo ngày")
                    labels = sorted(days_counter.keys())
                    values = [days_counter[label] for label in labels]
                    ax.bar(labels, values, color='#60A5FA')
                    ax.set_xlabel('Ngày', fontsize=10, color='#334155')
                    ax.set_ylabel('Số lượng', fontsize=10, color='#334155')
                    ax.grid(axis='y', linestyle='--', alpha=0.7)
                    self.figure.tight_layout()
                    
                self.canvas.draw_idle()

        except Exception as e:
            print(f"Lỗi khi tải dữ liệu thống kê: {e}")
            traceback.print_exc()

    def parse_date(self, date_str):
        """
        Safely parses various date formats into a NAIVE datetime object.
        It strips any timezone information to ensure consistent comparisons.
        """
        if not date_str:
            return datetime.min

        dt = None
        try:
            # fromisoformat handles formats with 'T' and timezone info
            dt = datetime.fromisoformat(date_str)
        except (ValueError, TypeError):
            # Fallback for formats like 'YYYY-MM-DD HH:MM:SS'
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            except (ValueError, TypeError):
                # If all parsing fails, return a very old date
                return datetime.min

        # --- THIS IS THE FIX ---
        # If the parsed datetime object is "aware" (has tzinfo),
        # convert it to "naive" by removing the timezone.
        if dt and dt.tzinfo is not None:
            return dt.replace(tzinfo=None)

        return dt