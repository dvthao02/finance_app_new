from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton, QScrollArea
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from utils.ui_styles import UIStyles

# This file has been replaced by user_overview_tab_fixed.py
# Importing the fixed version to prevent errors
from gui.user.user_overview_tab_fixed import UserOverviewTab as FixedUserOverviewTab
from utils.animated_widgets import AnimatedStatCard, StaggeredAnimationGroup
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib.patheffects import withStroke
from matplotlib.collections import PolyCollection
import mplcursors
import datetime
import numpy as np

class UserOverviewTab(QWidget):
    
    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Header with user greeting - Thu nhỏ padding và font size
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                    stop: 0 #3b82f6, stop: 1 #06b6d4);
                border-radius: 8px;
                padding: 8px;  /* Giảm padding thêm nữa */
                border: none;
            }
        """)
        header_layout = QHBoxLayout(header_frame)  # Chuyển từ QVBox sang QHBox để tiết kiệm không gian dọc
        header_layout.setContentsMargins(8, 4, 8, 4)  # Thu nhỏ contentMargins hơn nữa
        
        greeting_layout = QVBoxLayout()  # Layout dọc cho phần chào và ngày
        greeting_layout.setSpacing(0)  # Giảm spacing giữa 2 dòng
        
        self.greeting_label = QLabel("Chào mừng!")
        self.greeting_label.setFont(QFont('Segoe UI', 16, QFont.Bold))  # Giảm font từ 18 xuống 16
        self.greeting_label.setStyleSheet("color: white; margin: 0;")
        greeting_layout.addWidget(self.greeting_label)
        
        self.date_label = QLabel(datetime.datetime.now().strftime("Hôm nay là %A, %d tháng %m, %Y"))
        self.date_label.setFont(QFont('Segoe UI', 10))  # Giảm font từ 11 xuống 10
        self.date_label.setStyleSheet("color: rgba(255,255,255,0.9); margin: 0;")
        greeting_layout.addWidget(self.date_label)
        
        header_layout.addLayout(greeting_layout)
        header_layout.addStretch(1)  # Thêm stretch để đẩy content sang trái
        
        layout.addWidget(header_frame)

        # --- Bộ lọc tháng/năm ---
        # Di chuyển bộ lọc xuống dưới khung chào mừng
        from PyQt5.QtWidgets import QComboBox
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        filter_layout.setContentsMargins(0, 0, 0, 0)
        filter_label = QLabel("Lọc theo:")
        filter_label.setFont(QFont('Segoe UI', 10, QFont.Bold))
        filter_layout.addWidget(filter_label)
          # Thêm bộ lọc khoảng thời gian
        self.time_range_filter = QComboBox()
        self.time_range_filter.addItem('Tháng hiện tại', 'current_month')
        self.time_range_filter.addItem('3 tháng gần đây', 'last_3_months')
        self.time_range_filter.addItem('6 tháng gần đây', 'last_6_months') 
        self.time_range_filter.addItem('Tất cả', 'all')
        self.time_range_filter.addItem('Tùy chọn', 'custom')
        self.time_range_filter.setToolTip("Lọc dữ liệu theo khoảng thời gian")
        self.time_range_filter.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 5px;
                padding: 3px 10px;
                background: white;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: right center;
                width: 20px;
                border-left: none;
            }
        """)
        filter_layout.addWidget(self.time_range_filter)
        
        # Bộ lọc tháng/năm cụ thể
        self.month_filter = QComboBox()
        self.year_filter = QComboBox()
        self.all_filter = QComboBox()
        
        # Lấy năm từ dữ liệu giao dịch
        import json, os
        years = set()
        months = set()
        try:
            with open(os.path.join(os.path.dirname(__file__), '../../data/transactions.json'), encoding='utf-8') as f:
                data = json.load(f)
                for t in data:
                    dt = t.get('date', '')[:7]  # yyyy-mm
                    if dt:
                        y, m = dt.split('-')
                        years.add(int(y))
                        months.add(int(m))
        except Exception:
            now = datetime.datetime.now()
            years = {now.year}
            months = {now.month}
            
        years = sorted(list(years))
        months = sorted(list(months))
        
        self.month_filter.addItem('Tất cả', 0)
        for m in range(1, 13):
            self.month_filter.addItem(f'Th{m}', m)
        self.year_filter.addItem('Tất cả', 0)
        for y in years:
            self.year_filter.addItem(str(y), y)
        filter_layout.addWidget(self.month_filter)
        filter_layout.addWidget(self.year_filter)
        layout.addLayout(filter_layout)
        
        # Set time range filter to current month by default
        self.time_range_filter.setCurrentIndex(0)  # Default to current month
        
        # Set current month (accounting for "Tất cả" at index 0)
        current_month = datetime.datetime.now().month
        self.month_filter.setCurrentIndex(current_month)  # Index is month number since we added Tất cả at index 0
        
        # Set current year
        current_year = str(datetime.datetime.now().year)
        year_index = self.year_filter.findText(current_year)
        if year_index >= 0:
            self.year_filter.setCurrentIndex(year_index)
        
        # Initially hide month/year filters as we're using time range by default
        self.month_filter.setVisible(False)
        self.year_filter.setVisible(False)
        
        # Connect signals
        self.time_range_filter.currentIndexChanged.connect(self.on_time_range_changed)
        self.month_filter.currentIndexChanged.connect(self.update_dashboard)
        self.year_filter.currentIndexChanged.connect(self.update_dashboard)
        
        # Animated Stats cards
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        # Tạo animated stat cards
        self.balance_card = AnimatedStatCard("Số dư hiện tại", 0, "Tổng tài khoản", "#10b981", "💰")
        self.income_card = AnimatedStatCard("Thu nhập tháng", 0, "Tháng này", "#3b82f6", "📈")
        self.expense_card = AnimatedStatCard("Chi tiêu tháng", 0, "Tháng này", "#ef4444", "📉")
        self.savings_card = AnimatedStatCard("Tiết kiệm tháng", 0, "Tháng này", "#8b5cf6", "💎")
        
        stats_layout.addWidget(self.balance_card, 0, 0)
        stats_layout.addWidget(self.income_card, 0, 1)
        stats_layout.addWidget(self.expense_card, 1, 0)
        stats_layout.addWidget(self.savings_card, 1, 1)
        
        # Thiết lập staggered animation cho các cards
        self.stat_cards = [self.balance_card, self.income_card, self.expense_card, self.savings_card]
        self.stats_animation_group = StaggeredAnimationGroup(self.stat_cards, delay=300)
        
        layout.addLayout(stats_layout)
        
        # Charts section - Tăng kích thước biểu đồ
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        # Line chart for monthly trend
        self.line_chart_widget = self.create_chart_widget("Xu hướng chi tiêu")
        self.line_chart_widget.setMinimumHeight(280)  # Tăng chiều cao tối thiểu
        charts_layout.addWidget(self.line_chart_widget)
        
        # Pie chart for category breakdown
        self.pie_chart_widget = self.create_chart_widget("Phân bổ theo danh mục")
        self.pie_chart_widget.setMinimumHeight(280)  # Tăng chiều cao tối thiểu
        charts_layout.addWidget(self.pie_chart_widget)
        
        layout.addLayout(charts_layout)
        
        # Recent transactions
        recent_frame = QFrame()
        recent_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: none;
            }
        """)
        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.setContentsMargins(10, 10, 10, 10)  # Giảm contentMargins tối đa
        
        # Thêm tiêu đề và nút xem tất cả trên cùng một hàng
        header_layout = QHBoxLayout()
        recent_title = QLabel("Giao dịch gần đây")
        recent_title.setFont(QFont('Segoe UI', 12, QFont.Bold))  # Giảm font
        recent_title.setStyleSheet("color: #1e293b; margin: 0px;")
        header_layout.addWidget(recent_title)
        
        # Thêm nút "Xem tất cả" (tuỳ chọn)
        view_all_btn = QPushButton("Xem tất cả")
        view_all_btn.setCursor(Qt.PointingHandCursor)
        view_all_btn.setStyleSheet("""
            QPushButton {
                color: #3b82f6;
                background: transparent;
                border: none;
                font-size: 10px;
                font-weight: bold;
                padding: 3px 6px;
            }
            QPushButton:hover {
                color: #2563eb;
                text-decoration: underline;
            }
        """)
        view_all_btn.clicked.connect(lambda: self.parent().parent().switch_tab(2))  # Switch to transaction history tab
        header_layout.addWidget(view_all_btn, alignment=Qt.AlignRight)
        
        recent_layout.addLayout(header_layout)
        
        # Tạo scrollable widget cho giao dịch gần đây
        from PyQt5.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #f1f5f9;
                width: 6px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #cbd5e1;
                border-radius: 3px;
                min-height: 20px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
        # Widget container cho danh sách giao dịch
        self.recent_transactions_widget = QWidget()
        self.recent_transactions_widget.setStyleSheet("background: transparent;")
        self.recent_transactions_layout = QVBoxLayout(self.recent_transactions_widget)
        self.recent_transactions_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_transactions_layout.setSpacing(1)  # Giảm spacing tối đa
        
        scroll_area.setWidget(self.recent_transactions_widget)
        scroll_area.setMaximumHeight(150)  # Giảm chiều cao tối đa xuống 150px
        
        recent_layout.addWidget(scroll_area)
        
        layout.addWidget(recent_frame)
        
    def create_stat_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 20px;
            }}
            QFrame:hover {{
                border-color: {color};
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 12))
        title_label.setStyleSheet("color: #64748b; margin: 0;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont('Segoe UI', 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {color}; margin: 0;")
        layout.addWidget(value_label)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
        
    def create_chart_widget(self, title):
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 8px;
                border: none;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)  # Giảm contentsMargins nhiều hơn
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 12, QFont.Bold))  # Giảm font từ 14 xuống 12
        title_label.setStyleSheet("color: #1e293b; margin-bottom: 0px;")  # Bỏ margin-bottom
        layout.addWidget(title_label)
        
        # Create matplotlib figure with larger size
        figure = Figure(figsize=(5, 4), dpi=90)  # Điều chỉnh kích thước và dpi
        figure.patch.set_facecolor('white')
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
          # Store canvas for updates
        widget.canvas = canvas
        widget.figure = figure
        
        return widget
        
    def update_dashboard(self):
        """Update all dashboard data"""
        try:
            self.update_greeting()
            self.update_stats()
            self.update_charts()
            self.update_recent_transactions()
        except Exception as e:
            print(f"Error updating dashboard: {e}")

    def update_greeting(self):
        """Update the greeting message with the user's name and current date"""
        try:
             # Get current user using current_user_id and get_user_by_id
            if hasattr(self.user_manager, 'current_user_id') and self.user_manager.current_user_id:
                current_user = self.user_manager.get_user_by_id(self.user_manager.current_user_id) 
                if current_user:
                    user_name = current_user.get('name', current_user.get('full_name', 'Người dùng'))
                    self.greeting_label.setText(f"Chào mừng, {user_name}!")
                else:
                    self.greeting_label.setText("Chào mừng!")
            else:
                self.greeting_label.setText("Chào mừng!")
            
            # Update date label
            now = datetime.datetime.now()
            # Map weekday names to Vietnamese
            weekday_names = {
                0: "Thứ Hai",
                1: "Thứ Ba",
                2: "Thứ Tư", 
                3: "Thứ Năm",
                4: "Thứ Sáu",
                5: "Thứ Bảy",
                6: "Chủ Nhật"
            }
            weekday_name = weekday_names[now.weekday()]
            date_text = f"Hôm nay là {weekday_name}, {now.day} tháng {now.month}, {now.year}"
            self.date_label.setText(date_text)
        except Exception as e:
            print(f"Error updating greeting: {e}")

    def get_selected_month_year(self):
        month = self.month_filter.currentData() if hasattr(self, 'month_filter') else 0
        year = self.year_filter.currentData() if hasattr(self, 'year_filter') else 0
        return month, year

    def update_line_chart(self):
        """Update line chart with monthly trends based on selected time range"""
        try:
            figure = self.line_chart_widget.figure
            figure.clear()
            ax = figure.add_subplot(111)
            
            # Get time range for filtering
            start_date, end_date = self.get_time_range()
            time_range_display = self.get_time_range_display()
            
            # Get the current user ID to filter transactions
            user_id = self.user_manager.current_user_id if hasattr(self.user_manager, 'current_user_id') else None
            
            # Update title to show selected time range
            time_range_title = f"Xu hướng chi tiêu ({time_range_display})"
            self.line_chart_widget.findChild(QLabel).setText(time_range_title)
            
            # Initialize data
            months_labels = []
            month_names = ["Th1", "Th2", "Th3", "Th4", "Th5", "Th6", "Th7", "Th8", "Th9", "Th10", "Th11", "Th12"]
            incomes = []
            expenses = []
            balances = []
            current_date = datetime.datetime.now()
            
            # Get all transactions filtered by user_id
            all_transactions = self.transaction_manager.get_all_transactions()
            if user_id:
                all_transactions = [t for t in all_transactions if t.get('user_id') == user_id]
            
            # Define the range of months to display based on selected time range
            if self.time_range_filter.currentData() == 'last_3_months':
                num_months = 3
            elif self.time_range_filter.currentData() == 'last_6_months':
                num_months = 6
            elif self.time_range_filter.currentData() == 'current_month':
                num_months = 1
            else:
                num_months = 6  # Default to 6 months for other ranges
            
            # Group transactions by month
            from collections import defaultdict
            data = defaultdict(lambda: {'income': 0, 'expense': 0})
            
            # If viewing all transactions or custom range span > 6 months, 
            # group by month for the last num_months
            if start_date is None or end_date is None:
                # "Tất cả" or very broad range - show last num_months
                for i in range(num_months):
                    m = (current_date.month - i) % 12
                    if m == 0:
                        m = 12
                    y = current_date.year - ((i - (current_date.month - 1)) // 12)
                    data[(y, m)]  # ensure key exists
                
                # Group transactions
                for t in all_transactions:
                    try:
                        tx_date = datetime.datetime.fromisoformat(t.get('date', '').replace('Z', '+00:00'))
                        # Only include transactions from the last num_months
                        date_threshold = current_date - datetime.timedelta(days=num_months * 30)
                        if tx_date >= date_threshold:
                            month = tx_date.month
                            year = tx_date.year
                            if t['type'] == 'income':
                                data[(year, month)]['income'] += t['amount']
                            else:
                                data[(year, month)]['expense'] += t['amount']
                    except Exception:
                        continue
            else:
                # Specific time range
                # Create month buckets within the range
                current = start_date
                while current <= end_date:
                    data[(current.year, current.month)]  # ensure key exists
                    # Move to next month
                    if current.month == 12:
                        current = current.replace(year=current.year+1, month=1)
                    else:
                        current = current.replace(month=current.month+1)
                
                # Only include transactions in the specified range
                transactions_in_range = self.transaction_manager.get_transactions_in_range(start_date, end_date, user_id)
                for t in transactions_in_range:
                    try:
                        tx_date = datetime.datetime.fromisoformat(t.get('date', '').replace('Z', '+00:00'))
                        month = tx_date.month
                        year = tx_date.year
                        if t['type'] == 'income':
                            data[(year, month)]['income'] += t['amount']
                        else:
                            data[(year, month)]['expense'] += t['amount']
                    except Exception:
                        continue
            
            # Sort months chronologically and prepare data for plotting
            sorted_months = sorted(data.keys())
            
            for year, month in sorted_months:
                month_data = data[(year, month)]
                month_income = month_data['income']
                month_expense = month_data['expense']
                month_balance = month_income - month_expense
                months_labels.append(f"{month_names[month-1]}/{year}")
                incomes.append(month_income / 1_000_000)
                expenses.append(month_expense / 1_000_000)
                balances.append(month_balance / 1_000_000)
            
            # Continue with the rest of the plotting code
            color_income = '#22c55e'
            color_expense = '#ef4444'
            color_balance = '#3b82f6'
            
            if not months_labels:
                # No data to display
                ax.text(0.5, 0.5, 'Không có dữ liệu cho khoảng thời gian này', 
                      ha='center', va='center', fontsize=12, transform=ax.transAxes)
                figure.tight_layout()
                self.line_chart_widget.canvas.draw()
                return
                
            bar_width = 0.35
            x = np.arange(len(months_labels))
            income_bars = ax.bar(x - bar_width/2, incomes, bar_width, label='Thu nhập', 
                                color=color_income, alpha=0.85, edgecolor='white', linewidth=0.8)
            expense_bars = ax.bar(x + bar_width/2, expenses, bar_width, label='Chi tiêu', 
                                 color=color_expense, alpha=0.85, edgecolor='white', linewidth=0.8)
            
            ax2 = ax.twinx()
            balance_line = ax2.plot(x, balances, label='Số dư', color=color_balance, 
                                   marker='o', markersize=8, markeredgecolor='white', 
                                   markeredgewidth=1.5, linestyle='-', linewidth=3)

            ax.set_xticks(x)
            ax.set_xticklabels(months_labels, fontsize=9)
            ax.tick_params(axis='x', rotation=45, labelcolor='#334155')
            ax.set_ylabel('Triệu VNĐ', fontsize=10, color='#334155')
            ax.tick_params(axis='y', labelcolor='#334155')
            ax2.tick_params(axis='y', labelcolor='#3b82f6')
            
            # Set appropriate axis limits
            max_income = max(incomes) if incomes else 0
            max_expense = max(expenses) if expenses else 0
            y_max = max(max_income, max_expense)
            # Nếu giá trị nhỏ, scale trục y nhỏ lại để nhìn rõ
            if y_max > 0 and y_max < 2:
                ax.set_ylim(0, 2.5)
            elif y_max > 0:
                ax.set_ylim(0, y_max * 1.2)
            else:
                ax.set_ylim(0, 2)
                
            min_balance = min(balances) if balances else 0
            max_balance = max(balances) if balances else 0
            balance_range = max_balance - min_balance
            if balance_range > 0 and balance_range < 2:
                ax2.set_ylim(min_balance - 0.5, max_balance + 0.5)
            elif balance_range > 0:
                padding = balance_range * 0.2
                ax2.set_ylim(min_balance - padding, max_balance + padding)
            else:
                ax2.set_ylim(-1, 1)
            
            for i, bal in enumerate(balances):
                ax2.annotate(f'{bal:.1f}', (i, bal), textcoords="offset points", xytext=(0,8), ha='center', fontsize=9, fontweight='bold', color='#3b82f6')
            for i, bar in enumerate(income_bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.05, f'{height:.1f}', ha='center', va='bottom', fontsize=8, color='#0f766e')
            for i, bar in enumerate(expense_bars):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.05, f'{height:.1f}', ha='center', va='bottom', fontsize=8, color='#9f1239')
            for spine in ax.spines.values():
                spine.set_visible(True)
                spine.set_linewidth(1)
                spine.set_edgecolor('#e2e8f0')
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines + lines2, labels + labels2, loc='upper left', framealpha=0.7, facecolor='white')
            ax.set_title(f'Xu hướng thu chi ({time_range_display})', fontsize=12, color='#1e293b', fontweight='bold')
            ax.grid(axis='y', linestyle='--', alpha=0.4, color='#cbd5e1')
            legend = ax.get_legend()
            frame = legend.get_frame()
            frame.set_facecolor('white')
            frame.set_edgecolor('#e2e8f0')

            # --- Custom hover event: tooltip luôn hiện khi hover vùng cột ---
            self._linechart_tooltip = getattr(self, '_linechart_tooltip', None)
            if self._linechart_tooltip is None:
                self._linechart_tooltip = ax.annotate("", xy=(0,0), xytext=(20,30), textcoords="offset points",
                    bbox=dict(boxstyle="round,pad=0.7", fc="#fef3c7", ec="#f59e0b", lw=1.5, alpha=0.97),
                    fontsize=11, ha='center', va='bottom', zorder=1000)
                self._linechart_tooltip.set_visible(False)            
            else:
                self._linechart_tooltip.set_visible(False)
                
            def on_motion(event):
                if event.inaxes != ax:
                    self._linechart_tooltip.set_visible(False)
                    figure.canvas.draw_idle()
                    return
                x_mouse = event.xdata
                if x_mouse is None:
                    self._linechart_tooltip.set_visible(False)
                    figure.canvas.draw_idle()
                    return
                nearest_index = int(round(x_mouse))
                if 0 <= nearest_index < len(months_labels):
                    month = months_labels[nearest_index]
                    income = incomes[nearest_index]
                    expense = expenses[nearest_index]
                    balance = balances[nearest_index]
                    
                    # Format values with thousand separators for better readability
                    income_formatted = f"{income * 1_000_000:,.0f}đ"
                    expense_formatted = f"{expense * 1_000_000:,.0f}đ"
                    balance_formatted = f"{balance * 1_000_000:,.0f}đ"
                    
                    # Calculate savings and savings rate
                    savings = income - expense
                    savings_rate = (savings / income * 100) if income > 0 else 0
                    savings_formatted = f"{savings * 1_000_000:,.0f}đ"
                    
                    # Enhanced tooltip with more information
                    tooltip_text = (f"Tháng: {month}\n"
                                   f"Thu nhập: {income_formatted} ({income:.1f} triệu)\n"
                                   f"Chi tiêu: {expense_formatted} ({expense:.1f} triệu)\n"
                                   f"Tiết kiệm: {savings_formatted} ({savings:.1f} triệu)\n"
                                   f"Tỉ lệ tiết kiệm: {savings_rate:.1f}%\n"
                                   f"Số dư: {balance_formatted} ({balance:.1f} triệu)")
                    
                    y_pos = max(income, expense)
                    self._linechart_tooltip.xy = (nearest_index, y_pos)
                    self._linechart_tooltip.set_text(tooltip_text)
                    
                    # Improve tooltip appearance
                    self._linechart_tooltip.get_bbox_patch().set_alpha(0.98)
                    self._linechart_tooltip.set_visible(True)
                    figure.canvas.draw_idle()
                else:
                    self._linechart_tooltip.set_visible(False)
                    figure.canvas.draw_idle()
            self.line_chart_widget.canvas.mpl_disconnect(getattr(self, '_motion_cid', None))
            self._motion_cid = self.line_chart_widget.canvas.mpl_connect('motion_notify_event', on_motion)

            figure.tight_layout()
            self.line_chart_widget.canvas.draw()
        except Exception as e:
            print(f"Error updating line chart: {e}")
            import traceback
            traceback.print_exc()
            
    def update_pie_chart(self):
        """Update pie chart with category breakdown"""
        try:
            figure = self.pie_chart_widget.figure
            figure.clear()
            
            ax = figure.add_subplot(111)
            
            # Get time range for filtering
            start_date, end_date = self.get_time_range()
            time_range_display = self.get_time_range_display()
            
            # Update chart title to reflect time range
            self.pie_chart_widget.findChild(QLabel).setText(f"Phân bổ theo danh mục ({time_range_display})")
            
            # Get the current user ID to filter transactions
            user_id = self.user_manager.current_user_id if hasattr(self.user_manager, 'current_user_id') else None
            
            # Get transactions in the selected time range
            if start_date is None or end_date is None:
                transactions = self.transaction_manager.get_all_transactions()
                if user_id:
                    transactions = [t for t in transactions if t.get('user_id') == user_id]
            else:
                transactions = self.transaction_manager.get_transactions_in_range(start_date, end_date, user_id)
                
            # Filter only expense transactions
            transactions = [t for t in transactions if t.get('type') == 'expense']
            
            # Lấy tất cả danh mục để mapping ID sang tên
            all_categories = self.category_manager.get_all_categories()
            category_dict = {cat['category_id']: cat for cat in all_categories}
            
            # Tính tổng theo category_id
            category_totals = {}
            total_expense = 0  # Initialize total_expense variable
            
            for transaction in transactions:
                category_id = transaction.get('category_id', 'unknown')
                # Lấy tên danh mục từ ID
                category_name = 'Khác'
                if category_id in category_dict:
                    category_name = category_dict[category_id].get('name', 'Khác')
                    # Thêm emoji icon nếu có
                    if 'icon' in category_dict[category_id]:
                        category_name = f"{category_dict[category_id]['icon']} {category_name}"
                
                # Cộng dồn số tiền vào danh mục
                amount = transaction['amount']
                total_expense += amount  # Add to total
                if category_name not in category_totals:
                    category_totals[category_name] = 0
                category_totals[category_name] = category_totals[category_name] + amount
            
            if category_totals:
                # Sắp xếp theo giá trị giảm dần
                sorted_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
                
                # Lấy top 6 danh mục, gộp các danh mục nhỏ vào "Khác"
                if len(sorted_categories) > 6:
                    top_categories = sorted_categories[:5]
                    others_sum = sum(amount for _, amount in sorted_categories[5:])
                    top_categories.append(("Khác", others_sum))
                    sorted_categories = top_categories
                
                categories = [cat[0] for cat in sorted_categories]
                amounts = [cat[1] for cat in sorted_categories]
                
                # Tạo màu sắc cho biểu đồ từ các danh mục
                colors = []
                for cat_name in categories:
                    # Tìm màu của danh mục nếu có
                    cat_color = '#64748b'  # Màu mặc định
                    for cat in all_categories:
                        if cat.get('name', '') in cat_name and 'color' in cat:
                            cat_color = cat['color']
                            break
                    colors.append(cat_color)
                
                # Vẽ biểu đồ tròn với màu sắc tương ứng
                wedges, texts, autotexts = ax.pie(
                    amounts, 
                    labels=categories, 
                    autopct='%1.1f%%', 
                    colors=colors,
                    shadow=False, 
                    startangle=90
                )
                
                # Tạo annotation cho tooltip khi hover
                annot = ax.annotate("", xy=(0,0), xytext=(10,10), textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.5", fc="white", alpha=0.9, ec="gray"),
                        fontsize=9, ha='center', va='center')
                annot.set_visible(False)
                
                # Lưu thông tin wedges để sử dụng trong hover
                self.pie_wedges_data = []
                for i, wedge in enumerate(wedges):
                    self.pie_wedges_data.append({
                        'wedge': wedge,
                        'category': categories[i],
                        'amount': amounts[i],
                        'percentage': amounts[i] / total_expense * 100 if total_expense > 0 else 0,
                        'color': colors[i]
                    })
                
                # Hàm cập nhật tooltip khi hover
                def update_annot(ind):
                    data = self.pie_wedges_data[ind]
                    category = data['category']
                    amount = data['amount']
                    percentage = data['percentage']
                    
                    # Format số với dấu phân cách hàng nghìn
                    amount_formatted = f"{amount:,.0f}đ"
                    
                    # Tạo nội dung tooltip
                    text = f"{category}\n{amount_formatted}\n({percentage:.1f}%)"
                    
                    # Lấy vị trí để hiển thị tooltip
                    theta = (data['wedge'].theta1 + data['wedge'].theta2) / 2
                    r = 0.5  # Radius của pie chart thường là 0.5
                    x = r * np.cos(np.deg2rad(theta))
                    y = r * np.sin(np.deg2rad(theta))
                    
                    annot.xy = (x, y)
                    annot.set_text(text)
                    annot.set_backgroundcolor(colors[ind])
                    annot.set_color('white')  # Text màu trắng
                    annot.set_visible(True)
                
                # Hàm xử lý sự kiện hover
                def hover(event):
                    if event.inaxes == ax:
                        for i, data in enumerate(self.pie_wedges_data):
                            wedge = data['wedge']
                            if wedge.contains_point([event.x, event.y]):
                                update_annot(i)
                                self.pie_chart_widget.canvas.draw_idle()
                                return
                        
                        # Nếu không hover trên phần nào của pie chart
                        annot.set_visible(False)
                        self.pie_chart_widget.canvas.draw_idle()
                
                # Kết nối sự kiện với hàm hover
                self.pie_hover_cid = self.pie_chart_widget.canvas.mpl_connect("motion_notify_event", hover)
                
                # Tạo kiểu cho các text
                for text in texts:
                    text.set_fontsize(9)
                for autotext in autotexts:
                    autotext.set_fontsize(8)
                    autotext.set_color('white')
                
                ax.set_title('Chi tiêu theo danh mục (tháng này)')
                ax.axis('equal')  # Equal aspect ratio đảm bảo hình tròn
            else:
                ax.text(0.5, 0.5, 'Chưa có dữ liệu chi tiêu', ha='center', va='center', fontsize=12, transform=ax.transAxes)
            
            self.pie_chart_widget.canvas.draw()
            
        except Exception as e:
            print(f"Error updating pie chart: {e}")
            import traceback
            traceback.print_exc()
            
    def update_recent_transactions(self):
        """Update recent transactions list"""
        try:
            # Clear existing transactions
            for i in reversed(range(self.recent_transactions_layout.count())):
                self.recent_transactions_layout.itemAt(i).widget().setParent(None)
            
            # Get the current user ID to filter transactions
            user_id = self.user_manager.current_user_id if hasattr(self.user_manager, 'current_user_id') else None
            
            # Get time range for filtering
            start_date, end_date = self.get_time_range()
            
            if start_date is None or end_date is None:
                # Get recent transactions filtered by current user
                recent_transactions = self.transaction_manager.get_recent_transactions(5, user_id)
            else:
                # Get transactions within time range
                transactions = self.transaction_manager.get_transactions_in_range(start_date, end_date, user_id)
                # Sort by date (newest first) and limit to 5
                recent_transactions = sorted(
                    transactions, 
                    key=lambda t: datetime.datetime.fromisoformat(t.get('date', '').replace('Z', '+00:00')), 
                    reverse=True
                )[:5]
            
            for transaction in recent_transactions:
                item_widget = self.create_transaction_item(transaction)
                self.recent_transactions_layout.addWidget(item_widget)
                
        except Exception as e:
            print(f"Error updating recent transactions: {e}")
            
    def create_transaction_item(self, transaction):
        """Create a transaction item widget"""
        item = QFrame()
        item.setStyleSheet("""
            QFrame {
                background: transparent;
                padding: 3px;
                margin: 0;
                border-bottom: 1px solid #f1f5f9;
            }
            QFrame:hover {
                background: #f1f5f9;
            }
        """)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(2, 2, 2, 2)  # Giảm margins tối đa
        
        # Transaction details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(0)  # Không spacing giữa các dòng
        
        title_label = QLabel(transaction.get('description', 'Không có mô tả'))
        title_label.setFont(QFont('Segoe UI', 10, QFont.Medium))  # Giảm font xuống 10
        title_label.setStyleSheet("color: #1e293b;")
        details_layout.addWidget(title_label)
        
        # Lấy thông tin danh mục
        category_name = "Khác"
        category_id = transaction.get('category_id', '')
        if hasattr(self.category_manager, 'get_all_categories'):
            all_categories = self.category_manager.get_all_categories()
            for cat in all_categories:
                if cat.get('category_id') == category_id:
                    category_name = cat.get('name', 'Khác')
                    if 'icon' in cat:
                        category_name = f"{cat['icon']} {category_name}"
                    break
        
        category_label = QLabel(category_name)
        category_label.setFont(QFont('Segoe UI', 8))  # Giảm font xuống 8
        category_label.setStyleSheet("color: #64748b;")
        details_layout.addWidget(category_label)
        
        layout.addLayout(details_layout)
        layout.addStretch()
        
        # Amount
        amount = transaction.get('amount', 0)
        amount_color = '#10b981' if transaction.get('type') == 'income' else '#ef4444'
        amount_prefix = '+' if transaction.get('type') == 'income' else '-'
        
        amount_label = QLabel(f"{amount_prefix}{amount:,.0f}đ")
        amount_label.setFont(QFont('Segoe UI', 10, QFont.Bold))  # Giảm font xuống 10
        amount_label.setStyleSheet(f"color: {amount_color};")
        layout.addWidget(amount_label)
        
        return item

    def update_stats(self):
        """Update statistics cards data"""
        try:
            # Get the current user ID to filter transactions
            user_id = self.user_manager.current_user_id if hasattr(self.user_manager, 'current_user_id') else None
            
            # Get time range for filtering
            start_date, end_date = self.get_time_range()
            time_range_display = self.get_time_range_display()
            
            # --- Thu nhập trong khoảng thời gian ---
            if start_date is None or end_date is None:
                # If no specific time range, get all transactions
                transactions_in_range = self.transaction_manager.get_all_transactions()
                if user_id:
                    transactions_in_range = [t for t in transactions_in_range if t.get('user_id') == user_id]
            else:
                # Get transactions in the specified time range
                transactions_in_range = self.transaction_manager.get_transactions_in_range(start_date, end_date, user_id)
            
            period_income = sum(
                t['amount'] for t in transactions_in_range 
                if t['type'] == 'income'
            )
            self.income_card.set_value(period_income)
            self.income_card.update_subtitle(f"{time_range_display}")
            
            # --- Chi tiêu trong khoảng thời gian ---
            period_expense = sum(
                t['amount'] for t in transactions_in_range 
                if t['type'] == 'expense'
            )
            self.expense_card.set_value(period_expense)
            self.expense_card.update_subtitle(f"{time_range_display}")
            
            # --- Số dư hiện tại (Tổng tài khoản) ---
            if self.wallet_manager and hasattr(self.wallet_manager, 'get_all_wallets'):
                # Use wallet manager if available
                total_balance = sum(wallet.get('balance', 0) for wallet in self.wallet_manager.get_all_wallets())
            else:
                # Calculate balance as (all income - all expense) from transactions
                all_transactions = self.transaction_manager.get_all_transactions()
                if user_id:
                    all_transactions = [t for t in all_transactions if t.get('user_id') == user_id]
                total_income = sum(t['amount'] for t in all_transactions if t['type'] == 'income')
                total_expense = sum(t['amount'] for t in all_transactions if t['type'] == 'expense')
                total_balance = total_income - total_expense
                
            self.balance_card.set_value(total_balance)
            
            # --- Tiết kiệm trong khoảng thời gian ---
            period_savings = period_income - period_expense
            self.savings_card.set_value(period_savings)
            self.savings_card.update_subtitle(f"{time_range_display}")
            
        except Exception as e:
            print(f"Error updating stats: {e}")
            import traceback
            traceback.print_exc()
        
    def update_charts(self):
        """Update all charts (line chart and pie chart)"""
        try:
            self.update_line_chart()
            self.update_pie_chart()
        except Exception as e:
            print(f"Error updating charts: {e}")
            import traceback
            traceback.print_exc()
    
    def on_time_range_changed(self, index):
        """Handle time range filter change"""
        time_range = self.time_range_filter.currentData()
        
        # Show/hide month/year filters based on the selected time range
        if time_range == 'custom':
            self.month_filter.setVisible(True)
            self.year_filter.setVisible(True)
        else:
            self.month_filter.setVisible(False)
            self.year_filter.setVisible(False)
              # Update the dashboard with the new time range
        self.update_dashboard()
        
    def get_time_range(self):
        """Get start date and end date based on selected time range"""
        time_range = self.time_range_filter.currentData()
        today = datetime.datetime.now()
        
        print(f"DEBUG: Getting time range for '{time_range}'")
        
        if time_range == 'current_month':
            # Current month: from the 1st day of current month to today
            start_date = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
            print(f"DEBUG: Current month range: {start_date} to {end_date}")
            
        elif time_range == 'last_3_months':
            # Last 3 months: from 3 months ago to today
            start_date = today - datetime.timedelta(days=90)
            start_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
            print(f"DEBUG: Last 3 months range: {start_date} to {end_date}")
            
        elif time_range == 'last_6_months':
            # Last 6 months: from 6 months ago to today
            start_date = today - datetime.timedelta(days=180)
            start_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
            print(f"DEBUG: Last 6 months range: {start_date} to {end_date}")
             elif time_range == 'custom':
            # Custom month/year from filters
            month = self.month_filter.currentData()
            year = self.year_filter.currentData()
            
            print(f"DEBUG: Custom filter with month={month}, year={year}")
            
            if month == 0 and year == 0:
                # Nếu cả tháng và năm đều là "Tất cả", trả về None để lấy tất cả giao dịch
                print("DEBUG: Both month and year are 'All', returning None")
                return None, None
                
            elif month == 0:
                # Tất cả các tháng của năm đã chọn
                start_date = datetime.datetime(year, 1, 1, 0, 0, 0)
                end_date = datetime.datetime(year, 12, 31, 23, 59, 59, 999999)
                print(f"DEBUG: All months of year {year}: {start_date} to {end_date}")
                
            elif year == 0:
                # Tháng đã chọn của tất cả các năm (sử dụng năm hiện tại)
                now = datetime.datetime.now()
                # Tháng đã chọn của năm hiện tại
                start_date = datetime.datetime(now.year, month, 1, 0, 0, 0)
                
                if month == 12:
                    end_date = datetime.datetime(now.year, 12, 31, 23, 59, 59, 999999)
                else:
                    end_date = datetime.datetime(now.year, month + 1, 1, 0, 0, 0) - datetime.timedelta(microseconds=1)
                    
                print(f"DEBUG: Month {month} of current year: {start_date} to {end_date}")
                
            else:
                # Tháng và năm cụ thể
                start_date = datetime.datetime(year, month, 1, 0, 0, 0)
                
                # Tính ngày cuối cùng của tháng
                if month == 12:
                    end_date = datetime.datetime(year, 12, 31, 23, 59, 59, 999999)
                else:
                    end_date = datetime.datetime(year, month + 1, 1, 0, 0, 0) - datetime.timedelta(microseconds=1)
                    
                print(f"DEBUG: Specific month {month}/{year}: {start_date} to {end_date}")
                
        else:  # 'all'
            # All time: return None to indicate no filtering
            return None, None
            
        return start_date, end_date
        
    def get_time_range_display(self):
        """Get display text for the current time range"""
        time_range = self.time_range_filter.currentData()
        
        if time_range == 'current_month':
            now = datetime.datetime.now()
            return f"tháng {now.month}/{now.year}"
            
        elif time_range == 'last_3_months':
            return "3 tháng gần đây"
            
        elif time_range == 'last_6_months':
            return "6 tháng gần đây"
            
        elif time_range == 'custom':
            month = self.month_filter.currentData()
            year = self.year_filter.currentData()
            
            if month == 0 and year == 0:
                return "tất cả thời gian"
            elif month == 0:
                return f"năm {year}"
            elif year == 0:
                return f"tháng {month} (tất cả các năm)"
            else:
                return f"tháng {month}/{year}"
                
        else:  # 'all'
            return "tất cả thời gian"
