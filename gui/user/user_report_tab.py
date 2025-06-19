# Copy nội dung từ user_report.py sang user_report_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                            QTabWidget, QPushButton, QComboBox, QDateEdit, QFileDialog,
                            QCheckBox, QGroupBox, QMessageBox, QDialog, QRadioButton)
from PyQt5.QtGui import QFont, QColor, QIcon, QPixmap
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import datetime
import os
import tempfile

class UserReport(QWidget):
    
    def __init__(self, user_manager, transaction_manager, category_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.current_month = datetime.datetime.now().month
        self.current_year = datetime.datetime.now().year
        self.selected_period = "month"  # 'month', 'quarter', 'year'

        # Timer for debouncing report generation
        self.report_generation_timer = QTimer(self)
        self.report_generation_timer.setSingleShot(True)
        self.report_generation_timer.timeout.connect(self.generate_report)

        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(15)
        # Header nhỏ gọn
        header_frame = QFrame()
        header_frame.setFixedHeight(70)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #6366f1, stop: 1 #8b5cf6);
                border-radius: 10px;
                padding: 0 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(0, 10, 0, 10)
        header_layout.setSpacing(0)
        title_label = QLabel("Báo cáo tài chính")
        title_label.setFont(QFont('Segoe UI', 18, QFont.Bold))
        title_label.setStyleSheet("color: white; margin: 0;")
        header_layout.addWidget(title_label)
        subtitle_label = QLabel("Phân tích chi tiết về tình hình tài chính của bạn")
        subtitle_label.setFont(QFont('Segoe UI', 11))
        subtitle_label.setStyleSheet("color: rgba(255,255,255,0.9); margin: 0;")
        header_layout.addWidget(subtitle_label)
        layout.addWidget(header_frame)
        
        # Filter controls
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 10px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(10, 10, 10, 10)
        filter_layout.setSpacing(10)
        
        # Period selection
        period_combo = QComboBox()
        period_combo.setFont(QFont('Segoe UI', 12))
        period_combo.addItem("Tháng")
        period_combo.addItem("Quý")
        period_combo.addItem("Năm")
        period_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                background: #f9fafb;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #d1d5db;
                border-left-style: solid;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)
        period_combo.currentIndexChanged.connect(self.on_period_changed)
        filter_layout.addWidget(period_combo)
        
        # Date selection
        date_selector = QDateEdit()
        date_selector.setFont(QFont('Segoe UI', 12))
        date_selector.setDisplayFormat("MM/yyyy")
        date_selector.setCalendarPopup(True)
        
        # Set to current month
        current_date = QDate()
        current_date.setDate(self.current_year, self.current_month, 1)
        date_selector.setDate(current_date)
        
        date_selector.setStyleSheet("""
            QDateEdit {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                background: #f9fafb;
            }
        """)
        date_selector.dateChanged.connect(self.on_date_changed)
        filter_layout.addWidget(date_selector)
        
        # Transaction type filter
        type_combo = QComboBox()
        type_combo.setFont(QFont('Segoe UI', 12))
        type_combo.addItem("Tất cả")
        type_combo.addItem("Thu nhập")
        type_combo.addItem("Chi tiêu")
        type_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                background: #f9fafb;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 25px;
                border-left-width: 1px;
                border-left-color: #d1d5db;
                border-left-style: solid;
                border-top-right-radius: 8px;
                border-bottom-right-radius: 8px;
            }
        """)
        type_combo.currentIndexChanged.connect(self.schedule_report_generation)
        filter_layout.addWidget(type_combo)
        
        filter_layout.addStretch()
        
        # Button container for report actions
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        
        # Refresh report button
        refresh_btn = QPushButton(" Làm mới")
        refresh_btn.setFont(QFont('Segoe UI', 12))
        icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'function', 'refresh.png')
        if os.path.exists(icon_path):
            refresh_btn.setIcon(QIcon(icon_path))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #6366f1;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                margin-top: 22px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #4f46e5;
            }
        """)
        refresh_btn.clicked.connect(self.generate_report)
        action_layout.addWidget(refresh_btn)
        
        # Export button
        export_btn = QPushButton("Xuất báo cáo")
        export_btn.setFont(QFont('Segoe UI', 12))
        export_btn.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                margin-top: 22px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        export_btn.clicked.connect(self.show_export_options)
        action_layout.addWidget(export_btn)
        
        filter_layout.addLayout(action_layout)
        
        layout.addWidget(filter_frame)
        
        # Report content
        tab_widget = QTabWidget()
        tab_widget.setFont(QFont('Segoe UI', 12))
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                background: white;
            }
            QTabWidget::tab-bar {
                left: 10px;
            }
            QTabBar::tab {
                background: #f1f5f9;
                border: 1px solid #e2e8f0;
                border-bottom-color: #e2e8f0;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                padding: 10px 25px; /* Adjust padding */
                color: #64748b;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom-color: white;
                color: #3b82f6;
                font-weight: 600;
            }
            QTabBar::tab:!selected {
                margin-top: 2px;
            }
        """)
        
        # Overview tab
        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        overview_layout.setContentsMargins(20, 20, 20, 20)
        
        # Split layout for main content and insights
        overview_split = QHBoxLayout()
        
        # Main overview content (left side)
        main_overview = QVBoxLayout()
        main_overview.setSpacing(15)
          # Summary cards - 2 main cards for Income and Expense
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(30)
        
        self.income_card = self.create_main_summary_card("💰 Tổng Thu Nhập", "0đ", "#10b981", "#dcfce7")
        self.expense_card = self.create_main_summary_card("💸 Tổng Chi Tiêu", "0đ", "#ef4444", "#fef2f2")
        
        summary_layout.addWidget(self.income_card)
        summary_layout.addWidget(self.expense_card)
        
        main_overview.addLayout(summary_layout)
        
        # Income vs Expense chart
        income_expense_frame = QFrame()
        income_expense_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        income_expense_layout = QVBoxLayout(income_expense_frame)
        
        income_expense_title = QLabel("Thu nhập và chi tiêu")
        income_expense_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        income_expense_title.setStyleSheet("margin-bottom: 10px;")
        income_expense_layout.addWidget(income_expense_title)
        
        # Figure for bar chart
        figure1 = Figure(figsize=(8, 4))
        figure1.patch.set_facecolor('white')
        self.income_expense_canvas = FigureCanvas(figure1)
        income_expense_layout.addWidget(self.income_expense_canvas)
        
        main_overview.addWidget(income_expense_frame)
        
        # Add main overview to left side (70%)
        overview_split.addLayout(main_overview, 70)
        
        # Financial insights panel (right side, 30%)
        insights_frame = QFrame()
        insights_frame.setStyleSheet("""
            QFrame {
                background: #f8fafc;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 15px;
            }        """)
        
        insights_layout = QVBoxLayout(insights_frame)
        insights_layout.setContentsMargins(10, 10, 10, 10)
        insights_layout.setSpacing(15)
        
        insights_title = QLabel("💡 Gợi ý tài chính")
        insights_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        insights_title.setStyleSheet("color: #334155;")
        insights_layout.addWidget(insights_title)
        
        # Create a scroll area for insights
        self.insights_scroll_area = QWidget()
        self.insights_scroll_layout = QVBoxLayout(self.insights_scroll_area)
        self.insights_scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.insights_scroll_layout.setSpacing(10)
        
        # Add scroll area to main layout
        insights_layout.addWidget(self.insights_scroll_area)
        
        # Placeholder for insights (will be populated in update_financial_insights)
        insights_layout.addStretch()
        
        # Save reference to insights components
        self.insights_frame = insights_frame
        self.insights_layout = self.insights_scroll_layout
        
        # Add insights to right side (30%)
        overview_split.addWidget(insights_frame, 30)
        
        # Add split layout to overview
        overview_layout.addLayout(overview_split)
        
        tab_widget.addTab(overview_tab, "Tổng quan")
        
        # Trend analysis tab
        trend_tab = QWidget()
        trend_layout = QVBoxLayout(trend_tab)
        trend_layout.setContentsMargins(20, 20, 20, 20)
        
        # Line chart for trends
        trend_frame = QFrame()
        trend_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        trend_chart_layout = QVBoxLayout(trend_frame)
        
        trend_title = QLabel("Xu hướng theo thời gian")
        trend_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        trend_title.setStyleSheet("margin-bottom: 10px;")
        trend_chart_layout.addWidget(trend_title)
        
        # Figure for line chart
        figure2 = Figure(figsize=(8, 5))
        figure2.patch.set_facecolor('white')
        self.trend_canvas = FigureCanvas(figure2)
        trend_chart_layout.addWidget(self.trend_canvas)
        
        trend_layout.addWidget(trend_frame)
        
        tab_widget.addTab(trend_tab, "Xu hướng")
        
        # Category analysis tab
        category_tab = QWidget()
        category_layout = QVBoxLayout(category_tab)
        category_layout.setContentsMargins(20, 20, 20, 20)
        
        # Income by category
        income_cat_frame = QFrame()
        income_cat_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        income_cat_layout = QVBoxLayout(income_cat_frame)
        
        income_cat_title = QLabel("Thu nhập theo danh mục")
        income_cat_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        income_cat_layout.addWidget(income_cat_title)
        
        # Figure for income pie chart
        figure3 = Figure(figsize=(8, 4))
        figure3.patch.set_facecolor('white')
        self.income_cat_canvas = FigureCanvas(figure3)
        income_cat_layout.addWidget(self.income_cat_canvas)
        
        category_layout.addWidget(income_cat_frame)
        
        # Expense by category
        expense_cat_frame = QFrame()
        expense_cat_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        expense_cat_layout = QVBoxLayout(expense_cat_frame)
        
        expense_cat_title = QLabel("Chi tiêu theo danh mục")
        expense_cat_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        expense_cat_layout.addWidget(expense_cat_title)
        
        # Figure for expense pie chart
        figure4 = Figure(figsize=(8, 4))
        figure4.patch.set_facecolor('white')
        self.expense_cat_canvas = FigureCanvas(figure4)
        expense_cat_layout.addWidget(self.expense_cat_canvas)
        
        category_layout.addWidget(expense_cat_frame)
        
        tab_widget.addTab(category_tab, "Phân tích danh mục")
        
        layout.addWidget(tab_widget)
        
        # Store references to widgets and figures
        self.date_selector = date_selector
        self.period_combo = period_combo
        self.type_combo = type_combo  # Thêm reference cho type_combo
        self.tab_widget = tab_widget
        self.figure1 = figure1
        self.figure2 = figure2
        self.figure3 = figure3
        self.figure4 = figure4
        
        # Initially generate report for the current period
        self.schedule_report_generation()
        
    def create_main_summary_card(self, title, value, color, bg_color):
        """Create simpler summary cards for income and expense"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: {bg_color};
                border-radius: 12px;
                padding: 20px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        title_label.setStyleSheet(f"color: {color}; margin: 0; background-color: transparent;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont('Segoe UI', 28, QFont.Bold))
        value_label.setStyleSheet(f"color: {color}; margin: 0; background-color: transparent;")
        layout.addWidget(value_label)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
        
    def create_summary_card(self, title, value, color):
        """Legacy function - kept for compatibility"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 15px;
                min-height: 80px;
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
        title_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        title_label.setStyleSheet("color: #64748b; margin: 0;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont('Segoe UI', 20, QFont.Bold))
        value_label.setStyleSheet(f"color: {color}; margin: 0;")
        layout.addWidget(value_label)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
        
    def on_date_changed(self, date):
        """Handle date change"""
        self.current_month = date.month()
        self.current_year = date.year()
        self.schedule_report_generation()
        
    def on_period_changed(self, index):
        """Handle period selection change"""
        if index == 0:
            self.selected_period = "month"
            self.date_selector.setDisplayFormat("MM/yyyy")
        elif index == 1:
            self.selected_period = "quarter"
            self.date_selector.setDisplayFormat("MM/yyyy")  # Still show month but we'll use the quarter
        elif index == 2:
            self.selected_period = "year"
            self.date_selector.setDisplayFormat("yyyy")
        self.schedule_report_generation()
            
    def schedule_report_generation(self):
        """Schedules a report generation to avoid rapid updates."""
        self.report_generation_timer.start(250) # 250ms delay

    def generate_report(self):
        """Generate report based on selected period and date"""
        try:
            start_date, end_date = self.get_date_range()
            # Lấy user_id hiện tại
            user = self.user_manager.get_current_user()
            user_id = user.get('id') or user.get('user_id') if user else None
            
            # Get transactions within range, chỉ lấy của user hiện tại
            all_transactions = self.transaction_manager.get_transactions_in_range(start_date, end_date, user_id=user_id)
            
            # Áp dụng filter theo loại giao dịch
            transaction_type_index = self.type_combo.currentIndex()
            if transaction_type_index == 1:  # Thu nhập
                transactions = [t for t in all_transactions if t.get('type') == 'income']
            elif transaction_type_index == 2:  # Chi tiêu
                transactions = [t for t in all_transactions if t.get('type') == 'expense']
            else:  # Tất cả
                transactions = all_transactions
            
            # Update summary
            self.update_summary(transactions)
            
            # Update charts
            self.update_income_expense_chart(transactions)
            self.update_trend_chart(start_date, end_date)
            self.update_category_charts(transactions)
            
        except Exception as e:
            print(f"Error generating report: {e}")
            
    def get_date_range(self):
        """Get date range based on selected period and date"""
        selected_date = self.date_selector.date()
        year = selected_date.year()
        month = selected_date.month() if self.selected_period != "year" else 1
        
        if self.selected_period == "month":
            # First and last day of month
            start_date = datetime.date(year, month, 1)
            
            if month == 12:
                next_month = datetime.date(year + 1, 1, 1)
            else:
                next_month = datetime.date(year, month + 1, 1)
                
            end_date = next_month - datetime.timedelta(days=1)
            
        elif self.selected_period == "quarter":
            # Determine quarter
            quarter = (month - 1) // 3 + 1
            start_month = (quarter - 1) * 3 + 1
            
            start_date = datetime.date(year, start_month, 1)
            
            if start_month + 3 > 12:
                next_quarter = datetime.date(year + 1, 1, 1)
            else:
                next_quarter = datetime.date(year, start_month + 3, 1)
                
            end_date = next_quarter - datetime.timedelta(days=1)
            
        else:  # year
            start_date = datetime.date(year, 1, 1)
            end_date = datetime.date(year, 12, 31)
            
        return start_date, end_date
        
    def update_summary(self, transactions):
        """Update summary cards with transaction data"""
        income_total = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'income')
        expense_total = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'expense')
        balance = income_total - expense_total
        
        # Calculate savings rate
        if income_total > 0:
            savings_rate = (balance / income_total) * 100
        else:
            savings_rate = 0
              # Update cards
        self.income_card.value_label.setText(f"{income_total:,.0f}đ")
        self.expense_card.value_label.setText(f"{expense_total:,.0f}đ")
        
          # Add financial insights based on data
        self.update_financial_insights(income_total, expense_total, balance, savings_rate)
    
    def update_income_expense_chart(self, transactions):
        """Update the income vs expense bar chart."""
        try:
            self.figure1.clear()
            ax = self.figure1.add_subplot(111)
            self.figure1.patch.set_facecolor('white')
            ax.set_facecolor('white')

            income_total = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'income')
            expense_total = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'expense')

            labels = ['Thu nhập', 'Chi tiêu']
            values = [income_total, expense_total]
            colors = ['#10b981', '#ef4444']

            bars = ax.bar(labels, values, color=colors, width=0.5)

            ax.set_ylabel('Số tiền (VNĐ)', fontdict={'fontsize': 12})
            
            # Format y-axis
            import matplotlib.ticker as ticker
            formatter = ticker.FuncFormatter(lambda x, p: f'{int(x):,}đ')
            ax.yaxis.set_major_formatter(formatter)
            ax.grid(True, axis='y', linestyle='--', alpha=0.7)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color('#d1d5db')
            ax.spines['bottom'].set_color('#d1d5db')

            # Add value labels on top of bars
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2.0, yval, f'{int(yval):,}đ', va='bottom', ha='center', fontsize=11, weight='bold')

            self.figure1.tight_layout(pad=2)
            self.income_expense_canvas.draw()

        except Exception as e:
            print(f"Error updating income/expense chart: {e}")

    def update_financial_insights(self, income_total, expense_total, balance, savings_rate):
        """Show smart financial insights based on the current data"""
        # Clear existing insights
        for i in reversed(range(self.insights_layout.count())):
            child = self.insights_layout.itemAt(i)
            if child.widget():
                child.widget().setParent(None)

        insights = []
        
        # Analyze data and create insights
        if balance < 0:
            insights.append({
                "icon": "⚠️",
                "title": "Chi tiêu vượt mức",
                "message": f"Bạn đã chi tiêu vượt quá thu nhập {-balance:,.0f}đ trong kỳ này. Cần cân nhắc cắt giảm chi tiêu không cần thiết.",
                "bg_color": "#fef2f2",
                "border_color": "#ef4444",
                "text_color": "#991b1b"
            })
        elif balance > 0 and savings_rate < 10 and income_total > 0:
            insights.append({
                "icon": "💡",
                "title": "Cơ hội tiết kiệm",
                "message": f"Tỷ lệ tiết kiệm hiện tại ({savings_rate:.1f}%) thấp hơn mức khuyến nghị (20%). Hãy thử tăng tiết kiệm thêm {(income_total * 0.2 - balance):,.0f}đ.",
                "bg_color": "#fffbeb", 
                "border_color": "#f59e0b",
                "text_color": "#92400e"
            })
        elif savings_rate >= 20:
            insights.append({
                "icon": "🎉",
                "title": "Xuất sắc!",
                "message": f"Tỷ lệ tiết kiệm {savings_rate:.1f}% của bạn rất tốt! Hãy duy trì thói quen này và cân nhắc đầu tư để tăng thu nhập thụ động.",
                "bg_color": "#f0fdf4",
                "border_color": "#22c55e", 
                "text_color": "#166534"
            })

        # Spending pattern analysis
        if expense_total > income_total * 0.8 and income_total > 0:
            insights.append({
                "icon": "📊",
                "title": "Chi tiêu cao",
                "message": f"Chi tiêu chiếm {(expense_total/income_total)*100:.1f}% thu nhập. Hãy xem xét cắt giảm các khoản chi không thiết yếu.",
                "bg_color": "#fef3c7",
                "border_color": "#f59e0b",
                "text_color": "#92400e"
            })

        # Budget recommendation
        if income_total > 0:
            recommended_expense = income_total * 0.8
            if expense_total < recommended_expense:
                potential_savings = recommended_expense - expense_total
                insights.append({
                    "icon": "💰",
                    "title": "Tiềm năng tiết kiệm",
                    "message": f"Bạn có thể tiết kiệm thêm {potential_savings:,.0f}đ nữa mà vẫn duy trì mức chi tiêu hợp lý (80% thu nhập).",
                    "bg_color": "#dbeafe",
                    "border_color": "#3b82f6",
                    "text_color": "#1e40af"
                })

        if not insights:
            insights.append({
                "icon": "ℹ️",
                "title": "Không có dữ liệu",
                "message": "Không có đủ dữ liệu giao dịch để phân tích hoặc tình hình tài chính của bạn đang ổn định.",
                "bg_color": "#f8fafc",
                "border_color": "#64748b",
                "text_color": "#475569"
            })
        
        # Create insight widgets
        for insight in insights:
            insight_widget = self.create_insight_widget(
                insight["icon"], insight["title"], insight["message"],
                insight["bg_color"], insight["border_color"], insight["text_color"]
            )
            self.insights_layout.addWidget(insight_widget)
        
        # Add stretch to push insights to the top
        self.insights_layout.addStretch()

    def create_insight_widget(self, icon, title, message, bg_color, border_color, text_color):
        """Create a styled insight card widget"""
        widget = QFrame()
        widget.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-left: 4px solid {border_color};
                border-radius: 8px;
                padding: 12px;
                margin: 2px;
            }}
            QFrame:hover {{
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont('Segoe UI', 16))
        icon_label.setFixedSize(24, 24)
        header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        title_label.setStyleSheet(f"color: {text_color}; border: none; background: transparent;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Message
        message_label = QLabel(message)
        message_label.setFont(QFont('Segoe UI', 10))
        message_label.setStyleSheet(f"color: {text_color}; border: none; background: transparent; line-height: 1.4;")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        return widget

    def show_export_options(self):
        """Show dialog with export options"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Xuất báo cáo")
        dialog.setFixedWidth(400)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("Xuất báo cáo tài chính")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        # Format options
        format_group = QGroupBox("Định dạng")
        format_layout = QVBoxLayout(format_group)
        
        pdf_radio = QRadioButton("PDF (Tài liệu)")
        pdf_radio.setChecked(True)
        format_layout.addWidget(pdf_radio)
        
        image_radio = QRadioButton("PNG (Ảnh)")
        format_layout.addWidget(image_radio)
        
        layout.addWidget(format_group)
        
        # Content options
        content_group = QGroupBox("Nội dung")
        content_layout = QVBoxLayout(content_group)
        
        full_radio = QRadioButton("Toàn bộ báo cáo")
        full_radio.setChecked(True)
        content_layout.addWidget(full_radio)
        
        current_tab_radio = QRadioButton("Tab hiện tại")
        content_layout.addWidget(current_tab_radio)
        
        layout.addWidget(content_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Hủy")
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        
        export_btn = QPushButton("Xuất")
        export_btn.setStyleSheet("background-color: #10b981; color: white;")
        export_btn.clicked.connect(lambda: self.export_report(
            pdf=pdf_radio.isChecked(),
            full_report=full_radio.isChecked()
        ) or dialog.accept())
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec_()
    
    def export_report(self, pdf=True, full_report=True):
        """Export the report to PDF or PNG"""
        try:
            if pdf:
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Lưu báo cáo PDF", "", "PDF Files (*.pdf)")
                
                if not file_path:
                    return
                
                if not file_path.endswith(".pdf"):
                    file_path += ".pdf"
                
                with PdfPages(file_path) as pdf_pages:
                    # Get date range for title
                    start_date, end_date = self.get_date_range()
                    period_text = self.get_period_text(start_date, end_date)
                    
                    # Create figure for summary
                    fig, ax = plt.subplots(figsize=(8, 6))
                    ax.axis('off')
                    
                    # Add title and summary
                    ax.text(0.5, 0.95, f"Báo cáo tài chính - {period_text}", 
                           fontsize=16, ha='center', weight='bold')
                    
                    # Get data from summary cards
                    income = self.income_card.value_label.text()
                    expense = self.expense_card.value_label.text()
                    balance = self.balance_card.value_label.text()
                    savings = self.savings_rate_card.value_label.text()
                    
                    # Add summary text
                    summary_text = f"""
                    Thu nhập: {income}
                    Chi tiêu: {expense}
                    Chênh lệch: {balance}
                    Tỷ lệ tiết kiệm: {savings}
                    """
                    
                    ax.text(0.5, 0.8, summary_text, fontsize=12, ha='center')
                    
                    # Save the summary page
                    pdf_pages.savefig(fig)
                    plt.close(fig)
                    
                    if full_report:
                        # Export all charts from each tab
                        # Income vs Expense chart
                        pdf_pages.savefig(self.figure1.figure)
                        
                        # Trend chart
                        pdf_pages.savefig(self.figure2.figure)
                        
                        # Category charts
                        pdf_pages.savefig(self.figure3.figure)
                        pdf_pages.savefig(self.figure4.figure)
                    else:
                        # Only export current tab
                        current_tab = self.tab_widget.currentIndex()
                        if current_tab == 0:  # Overview
                            pdf_pages.savefig(self.figure1.figure)
                        elif current_tab == 1:  # Trend
                            pdf_pages.savefig(self.figure2.figure)
                        elif current_tab == 2:  # Category
                            pdf_pages.savefig(self.figure3.figure)
                            pdf_pages.savefig(self.figure4.figure)
                
                QMessageBox.information(self, "Xuất báo cáo", 
                                      f"Báo cáo đã được xuất thành công đến:\n{file_path}")
            else:
                # Export as PNG
                file_path, _ = QFileDialog.getSaveFileName(
                    self, "Lưu ảnh báo cáo", "", "PNG Files (*.png)")
                
                if not file_path:
                    return
                
                if not file_path.endswith(".png"):
                    file_path += ".png"
                
                # Determine which figure to export based on current tab
                current_tab = self.tab_widget.currentIndex()
                figure_to_save = None
                
                if current_tab == 0:  # Overview
                    figure_to_save = self.figure1.figure
                elif current_tab == 1:  # Trend
                    figure_to_save = self.figure2.figure
                elif current_tab == 2:  # Category analysis
                    # Ask which chart to export
                    chart_dialog = QDialog(self)
                    chart_dialog.setWindowTitle("Chọn biểu đồ")
                    chart_dialog.setFixedWidth(300)
                    chart_layout = QVBoxLayout(chart_dialog)
                    
                    income_radio = QRadioButton("Thu nhập theo danh mục")
                    income_radio.setChecked(True)
                    chart_layout.addWidget(income_radio)
                    
                    expense_radio = QRadioButton("Chi tiêu theo danh mục")
                    chart_layout.addWidget(expense_radio)
                    
                    button_layout = QHBoxLayout()
                    cancel_btn = QPushButton("Hủy")
                    cancel_btn.clicked.connect(chart_dialog.reject)
                    button_layout.addWidget(cancel_btn)
                    
                    ok_btn = QPushButton("OK")
                    ok_btn.clicked.connect(chart_dialog.accept)
                    button_layout.addWidget(ok_btn)
                    
                    chart_layout.addLayout(button_layout)
                    
                    result = chart_dialog.exec_()
                    if result:
                        if income_radio.isChecked():
                            figure_to_save = self.figure3.figure
                        else:
                            figure_to_save = self.figure4.figure
                    else:
                        return
                
                if figure_to_save:
                    figure_to_save.savefig(file_path, format='png', dpi=300, bbox_inches='tight')
                    QMessageBox.information(self, "Xuất báo cáo", 
                                          f"Ảnh báo cáo đã được lưu thành công đến:\n{file_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Lỗi xuất báo cáo", f"Không thể xuất báo cáo: {str(e)}")
    
    def get_period_text(self, start_date, end_date):
        """Get text description of period for report title"""
        if self.selected_period == "month":
            return f"Tháng {start_date.month}/{start_date.year}"
        elif self.selected_period == "quarter":
            quarter = (start_date.month - 1) // 3 + 1
            return f"Quý {quarter}/{start_date.year}"
        else:
            return f"Năm {start_date.year}"
    
    def update_trend_chart(self, start_date, end_date):
        """Update trend line chart"""
        try:
            # Clear the figure
            self.figure2.clear()
            ax = self.figure2.add_subplot(111)
            
            # Determine time periods based on the selected period
            periods = []
            period_labels = []
            
            if self.selected_period == "month":
                # Daily data for the month
                current_date = start_date
                while current_date <= end_date:
                    periods.append(current_date)
                    period_labels.append(current_date.strftime("%d/%m"))
                    current_date += datetime.timedelta(days=1)
                    
            elif self.selected_period == "quarter":
                # Weekly data for the quarter
                current_date = start_date
                while current_date <= end_date:
                    periods.append(current_date)
                    period_labels.append(f"T{current_date.isocalendar()[1]}")
                    current_date += datetime.timedelta(days=7)
                    
            else:  # year
                # Monthly data for the year
                for month in range(1, 13):
                    periods.append(datetime.date(start_date.year, month, 1))
                    period_labels.append(f"{month}/{start_date.year}")
            
            # Get income and expense for each period
            income_values = []
            expense_values = []
            
            # Lấy user_id hiện tại
            user = self.user_manager.get_current_user()
            user_id = user.get('id') or user.get('user_id') if user else None
            
            # Kiểm tra loại giao dịch đang được chọn
            transaction_type_index = self.type_combo.currentIndex()
            show_income = transaction_type_index in [0, 1]  # Tất cả hoặc Thu nhập
            show_expense = transaction_type_index in [0, 2]  # Tất cả hoặc Chi tiêu
            
            for i, period_start in enumerate(periods):
                # Determine period end
                if i < len(periods) - 1:
                    period_end = periods[i+1] - datetime.timedelta(days=1)
                else:
                    period_end = end_date
                
                # Get transactions for this period
                period_transactions = self.transaction_manager.get_transactions_in_range(period_start, period_end, user_id=user_id)
                
                if show_income:
                    income_total = sum(t.get('amount', 0) for t in period_transactions if t.get('type') == 'income')
                    income_values.append(income_total)
                
                if show_expense:
                    expense_total = sum(t.get('amount', 0) for t in period_transactions if t.get('type') == 'expense')
                    expense_values.append(expense_total)
            
            # Plot the data based on selected transaction type
            if show_income:
                ax.plot(period_labels, income_values, label='Thu nhập', color='#10b981', marker='o')
            
            if show_expense:
                ax.plot(period_labels, expense_values, label='Chi tiêu', color='#ef4444', marker='o')
            
            # Plot balance as area between curves only if showing both
            if show_income and show_expense:
                ax.fill_between(period_labels, income_values, expense_values, color='#bfdbfe', alpha=0.3)
            
            # Format and label
            ax.set_xlabel('Thời gian')
            ax.set_ylabel('Số tiền (VNĐ)')
            
            # Set title based on selected transaction type
            if transaction_type_index == 0:
                ax.set_title('Xu hướng thu nhập và chi tiêu theo thời gian')
            elif transaction_type_index == 1:
                ax.set_title('Xu hướng thu nhập theo thời gian')
            else:
                ax.set_title('Xu hướng chi tiêu theo thời gian')
            
            if self.selected_period in ["quarter", "year"]:
                ax.tick_params(axis='x', rotation=45)
            
            # Format y-axis as currency
            import matplotlib.ticker as ticker
            formatter = ticker.FuncFormatter(lambda x, p: format(int(x), ',') + 'đ')
            ax.yaxis.set_major_formatter(formatter)
            
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend()
            
            self.figure2.tight_layout()
            self.trend_canvas.draw()
            
        except Exception as e:
            print(f"Error updating trend chart: {e}")
    
    def update_category_charts(self, transactions):
        """Update category pie charts"""
        try:
            # Kiểm tra loại giao dịch đang được chọn
            transaction_type_index = self.type_combo.currentIndex()
            show_income = transaction_type_index in [0, 1]  # Tất cả hoặc Thu nhập
            show_expense = transaction_type_index in [0, 2]  # Tất cả hoặc Chi tiêu
            
            # Income by category
            self.figure3.clear()
            ax1 = self.figure3.add_subplot(111)
            
            if show_income:
                income_by_category = {}
                for t in transactions:
                    if t.get('type') == 'income':
                        category_id = t.get('category_id', 'unknown')
                        # Lấy tên danh mục nếu có
                        if category_id != 'unknown':
                            category = self.category_manager.get_category_by_id(category_id)
                            category_name = category.get('name', 'Khác') if category else 'Khác'
                        else:
                            category_name = 'Khác'
                        income_by_category[category_name] = income_by_category.get(category_name, 0) + t.get('amount', 0)
                
                if income_by_category:
                    labels = list(income_by_category.keys())
                    values = list(income_by_category.values())
                    
                    # Define colorful palette
                    colors = ['#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#f97316', '#eab308', '#06b6d4']
                    
                    ax1.pie(values, labels=labels, autopct='%1.1f%%', shadow=False, startangle=90, colors=colors)
                    ax1.axis('equal')
                    ax1.set_title('Thu nhập theo danh mục')
                else:
                    ax1.text(0.5, 0.5, 'Không có dữ liệu thu nhập trong giai đoạn này', 
                          ha='center', va='center', fontsize=12)
            else:
                ax1.text(0.5, 0.5, 'Đã lọc: không hiển thị thu nhập', 
                      ha='center', va='center', fontsize=12)
            
            self.income_cat_canvas.draw()
            
            # Expense by category
            self.figure4.clear()
            ax2 = self.figure4.add_subplot(111)
            
            if show_expense:
                expense_by_category = {}
                for t in transactions:
                    if t.get('type') == 'expense':
                        category_id = t.get('category_id', 'unknown')
                        # Lấy tên danh mục nếu có
                        if category_id != 'unknown':
                            category = self.category_manager.get_category_by_id(category_id)
                            category_name = category.get('name', 'Khác') if category else 'Khác'
                        else:
                            category_name = 'Khác'
                        expense_by_category[category_name] = expense_by_category.get(category_name, 0) + t.get('amount', 0)
                
                if expense_by_category:
                    labels = list(expense_by_category.keys())
                    values = list(expense_by_category.values())
                    
                    # Define colorful palette
                    colors = ['#ef4444', '#f97316', '#eab308', '#84cc16', '#06b6d4', '#8b5cf6', '#ec4899']
                    
                    ax2.pie(values, labels=labels, autopct='%1.1f%%', shadow=False, startangle=90, colors=colors)
                    ax2.axis('equal')
                    ax2.set_title('Chi tiêu theo danh mục')
                else:
                    ax2.text(0.5, 0.5, 'Không có dữ liệu chi tiêu trong giai đoạn này', 
                          ha='center', va='center', fontsize=12)
            else:
                ax2.text(0.5, 0.5, 'Đã lọc: không hiển thị chi tiêu', 
                      ha='center', va='center', fontsize=12)
            
            self.expense_cat_canvas.draw()
            
        except Exception as e:
            print(f"Error updating category charts: {e}")
