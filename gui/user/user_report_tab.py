# Copy nội dung từ user_report.py sang user_report_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                            QTabWidget, QPushButton, QComboBox, QDateEdit)
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QDate
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import datetime

class UserReport(QWidget):
    
    def __init__(self, user_manager, transaction_manager, category_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.current_month = datetime.datetime.now().month
        self.current_year = datetime.datetime.now().year
        self.selected_period = "month"  # 'month', 'quarter', 'year'
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                    stop: 0 #6366f1, stop: 1 #8b5cf6);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("Báo cáo tài chính")
        title_label.setFont(QFont('Segoe UI', 24, QFont.Bold))
        title_label.setStyleSheet("color: white; margin: 0;")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Phân tích chi tiết về tình hình tài chính của bạn")
        subtitle_label.setFont(QFont('Segoe UI', 14))
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
                padding: 15px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setContentsMargins(15, 15, 15, 15)
        filter_layout.setSpacing(15)
        
        # Period selection
        period_layout = QVBoxLayout()
        period_label = QLabel("Thời gian")
        period_label.setFont(QFont('Segoe UI', 12))
        period_layout.addWidget(period_label)
        
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
        period_layout.addWidget(period_combo)
        filter_layout.addLayout(period_layout)
        
        # Date selection
        date_layout = QVBoxLayout()
        date_label = QLabel("Chọn thời gian")
        date_label.setFont(QFont('Segoe UI', 12))
        date_layout.addWidget(date_label)
        
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
        date_layout.addWidget(date_selector)
        filter_layout.addLayout(date_layout)
        
        filter_layout.addStretch()
        
        # Generate report button
        generate_btn = QPushButton("Tạo báo cáo")
        generate_btn.setFont(QFont('Segoe UI', 12))
        generate_btn.setStyleSheet("""
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
        generate_btn.clicked.connect(self.generate_report)
        filter_layout.addWidget(generate_btn)
        
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
                min-width: 8ex;
                padding: 10px 20px;
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
        
        # Summary cards
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(20)
        
        self.income_card = self.create_summary_card("Thu nhập", "0đ", "#10b981")
        self.expense_card = self.create_summary_card("Chi tiêu", "0đ", "#ef4444")
        self.balance_card = self.create_summary_card("Chênh lệch", "0đ", "#3b82f6")
        self.savings_rate_card = self.create_summary_card("Tỷ lệ tiết kiệm", "0%", "#8b5cf6")
        
        summary_layout.addWidget(self.income_card)
        summary_layout.addWidget(self.expense_card)
        summary_layout.addWidget(self.balance_card)
        summary_layout.addWidget(self.savings_rate_card)
        
        overview_layout.addLayout(summary_layout)
        
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
        
        overview_layout.addWidget(income_expense_frame)
        
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
        self.tab_widget = tab_widget
        self.figure1 = figure1
        self.figure2 = figure2
        self.figure3 = figure3
        self.figure4 = figure4
        
    def create_summary_card(self, title, value, color):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 20px;
                min-height: 100px;
            }}
            QFrame:hover {{
                border-color: {color};
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 14))
        title_label.setStyleSheet("color: #64748b; margin: 0;")
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont('Segoe UI', 22, QFont.Bold))
        value_label.setStyleSheet(f"color: {color}; margin: 0;")
        layout.addWidget(value_label)
        
        # Store value label for updates
        card.value_label = value_label
        
        return card
        
    def on_date_changed(self, date):
        """Handle date change"""
        self.current_month = date.month()
        self.current_year = date.year()
        
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
            
    def generate_report(self):
        """Generate report based on selected period and date"""
        try:
            start_date, end_date = self.get_date_range()
            
            # Get transactions within range
            transactions = self.transaction_manager.get_transactions_in_range(start_date, end_date)
            
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
        self.balance_card.value_label.setText(f"{balance:,.0f}đ")
        
        # Color balance based on value
        if balance >= 0:
            self.balance_card.value_label.setStyleSheet("color: #10b981; font-size: 22px; font-weight: bold;")
        else:
            self.balance_card.value_label.setStyleSheet("color: #ef4444; font-size: 22px; font-weight: bold;")
            
        self.savings_rate_card.value_label.setText(f"{savings_rate:.1f}%")
        
    def update_income_expense_chart(self, transactions):
        """Update income vs expense bar chart"""
        try:
            # Clear the figure
            self.figure1.clear()
            ax = self.figure1.add_subplot(111)
            
            # Get income and expense by category
            income_by_category = {}
            expense_by_category = {}
            
            for t in transactions:
                if t.get('type') == 'income':
                    category = t.get('category', 'Khác')
                    income_by_category[category] = income_by_category.get(category, 0) + t.get('amount', 0)
                else:
                    category = t.get('category', 'Khác')
                    expense_by_category[category] = expense_by_category.get(category, 0) + t.get('amount', 0)
            
            # Sort categories by amount
            income_categories = sorted(income_by_category.items(), key=lambda x: x[1], reverse=True)
            expense_categories = sorted(expense_by_category.items(), key=lambda x: x[1], reverse=True)
            
            # Limit to top 5 categories
            income_categories = income_categories[:5]
            expense_categories = expense_categories[:5]
            
            # Prepare data
            income_labels = [cat[0] for cat in income_categories]
            income_values = [cat[1] for cat in income_categories]
            
            expense_labels = [cat[0] for cat in expense_categories]
            expense_values = [cat[1] for cat in expense_categories]
            
            # Bar positions
            bar_width = 0.35
            index = range(max(len(income_labels), len(expense_labels)))
            
            # Plot bars
            income_bars = ax.bar([i - bar_width/2 for i in index[:len(income_labels)]], 
                              income_values, bar_width, label='Thu nhập', color='#10b981')
                              
            expense_bars = ax.bar([i + bar_width/2 for i in index[:len(expense_labels)]], 
                               expense_values, bar_width, label='Chi tiêu', color='#ef4444')
            
            # Add labels
            all_labels = []
            for i in range(max(len(income_labels), len(expense_labels))):
                if i < len(income_labels):
                    in_label = income_labels[i]
                else:
                    in_label = ""
                    
                if i < len(expense_labels):
                    ex_label = expense_labels[i]
                else:
                    ex_label = ""
                    
                all_labels.append(f"{in_label}/{ex_label}" if in_label != ex_label else in_label)
            
            ax.set_xticks(index)
            ax.set_xticklabels(all_labels, rotation=45, ha='right')
            
            # Format y-axis as currency
            import matplotlib.ticker as ticker
            formatter = ticker.FuncFormatter(lambda x, p: format(int(x), ',') + 'đ')
            ax.yaxis.set_major_formatter(formatter)
            
            # Add value labels on bars
            def add_labels(bars):
                for bar in bars:
                    height = bar.get_height()
                    ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                         f'{height:,.0f}đ', ha='center', va='bottom', rotation=90,
                         fontsize=8)
            
            add_labels(income_bars)
            add_labels(expense_bars)
            
            ax.legend()
            ax.set_ylabel('Số tiền (VNĐ)')
            ax.set_title('Thu nhập và chi tiêu theo danh mục')
            
            self.figure1.tight_layout()
            self.income_expense_canvas.draw()
            
        except Exception as e:
            print(f"Error updating income expense chart: {e}")
            
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
            
            for i, period_start in enumerate(periods):
                # Determine period end
                if i < len(periods) - 1:
                    period_end = periods[i+1] - datetime.timedelta(days=1)
                else:
                    period_end = end_date
                
                # Get transactions for this period
                transactions = self.transaction_manager.get_transactions_in_range(period_start, period_end)
                
                income_total = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'income')
                expense_total = sum(t.get('amount', 0) for t in transactions if t.get('type') == 'expense')
                
                income_values.append(income_total)
                expense_values.append(expense_total)
            
            # Plot the data
            ax.plot(period_labels, income_values, label='Thu nhập', color='#10b981', marker='o')
            ax.plot(period_labels, expense_values, label='Chi tiêu', color='#ef4444', marker='o')
            
            # Plot balance as area between curves
            ax.fill_between(period_labels, income_values, expense_values, color='#bfdbfe', alpha=0.3)
            
            # Format and label
            ax.set_xlabel('Thời gian')
            ax.set_ylabel('Số tiền (VNĐ)')
            ax.set_title('Xu hướng thu nhập và chi tiêu theo thời gian')
            
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
            # Income by category
            self.figure3.clear()
            ax1 = self.figure3.add_subplot(111)
            
            income_by_category = {}
            for t in transactions:
                if t.get('type') == 'income':
                    category = t.get('category', 'Khác')
                    income_by_category[category] = income_by_category.get(category, 0) + t.get('amount', 0)
            
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
            
            self.income_cat_canvas.draw()
            
            # Expense by category
            self.figure4.clear()
            ax2 = self.figure4.add_subplot(111)
            
            expense_by_category = {}
            for t in transactions:
                if t.get('type') == 'expense':
                    category = t.get('category', 'Khác')
                    expense_by_category[category] = expense_by_category.get(category, 0) + t.get('amount', 0)
            
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
            
            self.expense_cat_canvas.draw()
            
        except Exception as e:
            print(f"Error updating category charts: {e}")
            
    def reload_data(self):
        """Reload all data and regenerate report"""
        self.generate_report()
