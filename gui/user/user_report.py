from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, 
                            QComboBox, QDateEdit, QPushButton, QGridLayout, 
                            QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
                            QSpacerItem, QSizePolicy, QScrollArea)
from PyQt5.QtCore import QDate, Qt
from PyQt5.QtGui import QFont, QColor, QBrush
import datetime
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class UserReport(QWidget):
    """
    Tab báo cáo chi tiêu với biểu đồ và thống kê chi tiết
    """
    def __init__(self, user_manager, transaction_manager, category_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.all_transactions = []
        self.categories_map = {}
        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b5cf6, stop:1 #ec4899);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        header_layout = QVBoxLayout()
        
        title = QLabel('📊 Báo cáo chi tiêu')
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        subtitle = QLabel('Phân tích chi tiết thu chi và xu hướng chi tiêu')
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                background: transparent;
                margin-top: 5px;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addWidget(subtitle)
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # Filter controls
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 20px;
            }
        """)
        
        filter_layout = QHBoxLayout()
        
        # Time period selector
        period_label = QLabel('📅 Thời gian:')
        period_label.setStyleSheet("font-weight: 600; color: #374151;")
        
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            'Tháng này', 'Tháng trước', '3 tháng gần đây', 
            '6 tháng gần đây', 'Năm nay', 'Năm trước', 'Tùy chọn'
        ])
        self.period_combo.setStyleSheet("""
            QComboBox {
                padding: 10px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 13px;
                background-color: #f8fafc;
            }
            QComboBox:focus {
                border-color: #8b5cf6;
                background-color: white;
            }
        """)
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        
        # Date range (hidden by default)
        self.date_from = QDateEdit(QDate.currentDate().addDays(-30))
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_from.setCalendarPopup(True)
        self.date_to.setCalendarPopup(True)
        self.date_from.setDisplayFormat('dd/MM/yyyy')
        self.date_to.setDisplayFormat('dd/MM/yyyy')
        
        date_style = """
            QDateEdit {
                padding: 10px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 13px;
                background-color: #f8fafc;
            }
            QDateEdit:focus {
                border-color: #8b5cf6;
                background-color: white;
            }
        """
        self.date_from.setStyleSheet(date_style)
        self.date_to.setStyleSheet(date_style)
        self.date_from.dateChanged.connect(self.update_reports)
        self.date_to.dateChanged.connect(self.update_reports)
        
        # Initially hide date selectors
        self.date_from.hide()
        self.date_to.hide()
        
        # Update button
        btn_update = QPushButton('🔄 Cập nhật')
        btn_update.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #8b5cf6, stop:1 #ec4899);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 25px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #7c3aed, stop:1 #db2777);
            }
        """)
        btn_update.clicked.connect(self.update_reports)
        
        filter_layout.addWidget(period_label)
        filter_layout.addWidget(self.period_combo)
        filter_layout.addWidget(QLabel('Từ:'))
        filter_layout.addWidget(self.date_from)
        filter_layout.addWidget(QLabel('Đến:'))
        filter_layout.addWidget(self.date_to)
        filter_layout.addWidget(btn_update)
        filter_layout.addStretch()
        
        filter_frame.setLayout(filter_layout)
        layout.addWidget(filter_frame)
        
        # Main content with tabs
        self.report_tabs = QTabWidget()
        self.report_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #f8fafc;
                color: #6b7280;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: white;
                color: #8b5cf6;
                border-bottom: 2px solid #8b5cf6;
            }
            QTabBar::tab:hover:!selected {
                background: #e2e8f0;
            }
        """)
        
        # Create tabs
        self.create_overview_tab()
        self.create_category_analysis_tab()
        self.create_trend_analysis_tab()
        self.create_comparison_tab()
        
        layout.addWidget(self.report_tabs)
        self.setLayout(layout)
        
        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #f1f5f9;
            }
        """)

    def create_overview_tab(self):
        """Tab tổng quan với các thống kê cơ bản"""
        overview_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Stats cards
        stats_frame = QFrame()
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Tạo các card thống kê
        self.total_income_card = self.create_stat_card('💰 Tổng thu nhập', '0 đ', '0%', '#10b981')
        self.total_expense_card = self.create_stat_card('💸 Tổng chi tiêu', '0 đ', '0%', '#ef4444')
        self.net_income_card = self.create_stat_card('💎 Thu nhập ròng', '0 đ', '0%', '#3b82f6')
        self.avg_daily_card = self.create_stat_card('📊 Trung bình/ngày', '0 đ', '0%', '#8b5cf6')
        
        stats_layout.addWidget(self.total_income_card)
        stats_layout.addWidget(self.total_expense_card)
        stats_layout.addWidget(self.net_income_card)
        stats_layout.addWidget(self.avg_daily_card)
        
        stats_frame.setLayout(stats_layout)
        layout.addWidget(stats_frame)
        
        # Charts row
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Monthly trend chart
        self.monthly_chart = self.create_chart_widget('Xu hướng thu chi theo tháng')
        charts_layout.addWidget(self.monthly_chart, 2)
        
        # Category pie chart
        self.category_pie_chart = self.create_chart_widget('Phân bổ chi tiêu theo danh mục')
        charts_layout.addWidget(self.category_pie_chart, 1)
        
        layout.addLayout(charts_layout)
        
        overview_widget.setLayout(layout)
        self.report_tabs.addTab(overview_widget, '📊 Tổng quan')

    def create_category_analysis_tab(self):
        """Tab phân tích theo danh mục"""
        category_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Category comparison chart
        self.category_bar_chart = self.create_chart_widget('So sánh chi tiêu theo danh mục')
        layout.addWidget(self.category_bar_chart)
        
        # Category details table
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e2e8f0;
                padding: 15px;
            }
        """)
        
        table_layout = QVBoxLayout()
        
        table_title = QLabel('📋 Chi tiết theo danh mục')
        table_title.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 10px;
        """)
        table_layout.addWidget(table_title)
        
        self.category_table = QTableWidget()
        self.category_table.setColumnCount(5)
        self.category_table.setHorizontalHeaderLabels([
            '🏷️ Danh mục', '💸 Tổng chi', '📊 % Tổng', '📈 Trung bình', '📝 Số giao dịch'
        ])
        
        self.category_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e2e8f0;
                background-color: white;
                alternate-background-color: #f8fafc;
                selection-background-color: #ddd6fe;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #e2e8f0;
            }
            QHeaderView::section {
                background: #f1f5f9;
                color: #374151;
                padding: 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;
                font-weight: 600;
            }
        """)
        
        self.category_table.setAlternatingRowColors(True)
        self.category_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.category_table.verticalHeader().setVisible(False)
        
        table_layout.addWidget(self.category_table)
        table_frame.setLayout(table_layout)
        layout.addWidget(table_frame)
        
        category_widget.setLayout(layout)
        self.report_tabs.addTab(category_widget, '🏷️ Phân tích danh mục')

    def create_trend_analysis_tab(self):
        """Tab phân tích xu hướng"""
        trend_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Daily trend chart
        self.daily_trend_chart = self.create_chart_widget('Xu hướng chi tiêu theo ngày')
        layout.addWidget(self.daily_trend_chart)
        
        # Weekly pattern chart
        self.weekly_pattern_chart = self.create_chart_widget('Mẫu hình theo ngày trong tuần')
        layout.addWidget(self.weekly_pattern_chart)
        
        trend_widget.setLayout(layout)
        self.report_tabs.addTab(trend_widget, '📈 Phân tích xu hướng')

    def create_comparison_tab(self):
        """Tab so sánh các kỳ"""
        comparison_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Period comparison chart
        self.comparison_chart = self.create_chart_widget('So sánh với kỳ trước')
        layout.addWidget(self.comparison_chart)
        
        comparison_widget.setLayout(layout)
        self.report_tabs.addTab(comparison_widget, '⚖️ So sánh kỳ')

    def create_stat_card(self, title, value, change, color):
        """Tạo card thống kê"""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 12px;
                border-left: 4px solid {color};
                padding: 20px;
                border: 1px solid #e2e8f0;
            }}
        """)
        
        layout = QVBoxLayout()
        
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            color: #6b7280;
            font-size: 14px;
            font-weight: 600;
            margin-bottom: 8px;
        """)
        
        value_label = QLabel(value)
        value_label.setStyleSheet(f"""
            color: {color};
            font-size: 24px;
            font-weight: bold;
            margin-bottom: 4px;
        """)
        
        change_label = QLabel(change)
        change_label.setStyleSheet("""
            color: #9ca3af;
            font-size: 12px;
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(change_label)
        
        card.setLayout(layout)
        return card

    def create_chart_widget(self, title):
        """Tạo widget chứa biểu đồ"""
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 15px;
        """)
        layout.addWidget(title_label)
        
        # Chart canvas
        figure = Figure(figsize=(8, 6), dpi=80)
        canvas = FigureCanvas(figure)
        layout.addWidget(canvas)
        
        frame.setLayout(layout)
        
        # Store references
        setattr(frame, 'figure', figure)
        setattr(frame, 'canvas', canvas)
        
        return frame

    def load_data(self):
        """Tải dữ liệu từ file JSON"""
        try:
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            if not user_id:
                return
            
            # Load transactions
            with open('data/transactions.json', 'r', encoding='utf-8') as f:
                all_transactions = json.load(f)
            
            self.all_transactions = [t for t in all_transactions if t.get('user_id') == user_id]
            
            # Load categories
            with open('data/categories.json', 'r', encoding='utf-8') as f:
                all_categories = json.load(f)
            
            self.categories_map = {cat.get('id') or cat.get('category_id'): cat.get('name', 'Khác') 
                                 for cat in all_categories}
            
            # Initial update
            self.update_reports()
            
        except Exception as e:
            print(f"Lỗi tải dữ liệu báo cáo: {e}")
    
    def on_period_changed(self, period):
        """Xử lý khi thay đổi kỳ báo cáo"""
        if period == 'Tùy chọn':
            self.date_from.show()
            self.date_to.show()
        else:
            self.date_from.hide()
            self.date_to.hide()
            
            # Set date range based on period
            today = datetime.date.today()
            
            if period == 'Tháng này':
                start_date = today.replace(day=1)
                end_date = today
            elif period == 'Tháng trước':
                first_day_this_month = today.replace(day=1)
                end_date = first_day_this_month - datetime.timedelta(days=1)
                start_date = end_date.replace(day=1)
            elif period == '3 tháng gần đây':
                start_date = today - datetime.timedelta(days=90)
                end_date = today
            elif period == '6 tháng gần đây':
                start_date = today - datetime.timedelta(days=180)
                end_date = today
            elif period == 'Năm nay':
                start_date = today.replace(month=1, day=1)
                end_date = today
            elif period == 'Năm trước':
                start_date = today.replace(year=today.year-1, month=1, day=1)
                end_date = today.replace(year=today.year-1, month=12, day=31)
            else:
                return
            
            self.date_from.setDate(QDate(start_date))
            self.date_to.setDate(QDate(end_date))
        
        self.update_reports()
    
    def get_filtered_transactions(self):
        """Lấy giao dịch trong khoảng thời gian được chọn"""
        start_date = self.date_from.date().toPyDate()
        end_date = self.date_to.date().toPyDate()
        
        filtered = []
        for tx in self.all_transactions:
            try:
                tx_date_str = tx.get('date', '')
                if 'T' in tx_date_str:
                    tx_date_str = tx_date_str.split('T')[0]
                tx_date = datetime.datetime.strptime(tx_date_str, '%Y-%m-%d').date()
                
                if start_date <= tx_date <= end_date:
                    filtered.append(tx)
            except:
                continue
        
        return filtered
    
    def update_reports(self):
        """Cập nhật tất cả các báo cáo"""
        filtered_transactions = self.get_filtered_transactions()
        
        # Update overview stats
        self.update_overview_stats(filtered_transactions)
        
        # Update charts
        self.update_monthly_chart(filtered_transactions)
        self.update_category_pie_chart(filtered_transactions)
        self.update_category_bar_chart(filtered_transactions)
        self.update_category_table(filtered_transactions)
        self.update_daily_trend_chart(filtered_transactions)
        self.update_weekly_pattern_chart(filtered_transactions)
        self.update_comparison_chart(filtered_transactions)
    
    def update_overview_stats(self, transactions):
        """Cập nhật thống kê tổng quan"""
        total_income = sum(tx.get('amount', 0) for tx in transactions if tx.get('type') == 'income')
        total_expense = sum(tx.get('amount', 0) for tx in transactions if tx.get('type') == 'expense')
        net_income = total_income - total_expense
        
        # Calculate daily average
        start_date = self.date_from.date().toPyDate()
        end_date = self.date_to.date().toPyDate()
        days = (end_date - start_date).days + 1
        avg_daily = total_expense / days if days > 0 else 0
        
        # Update cards
        self.update_stat_card(self.total_income_card, f'{total_income:,.0f} đ', 'so với kỳ trước')
        self.update_stat_card(self.total_expense_card, f'{total_expense:,.0f} đ', 'so với kỳ trước')
        self.update_stat_card(self.net_income_card, f'{net_income:,.0f} đ', 'so với kỳ trước')
        self.update_stat_card(self.avg_daily_card, f'{avg_daily:,.0f} đ', f'trong {days} ngày')
    
    def update_stat_card(self, card, value, change_text):
        """Cập nhật giá trị cho stat card"""
        labels = card.findChildren(QLabel)
        if len(labels) >= 2:
            labels[1].setText(value)  # Value label
        if len(labels) >= 3:
            labels[2].setText(change_text)  # Change label
    
    def update_monthly_chart(self, transactions):
        """Cập nhật biểu đồ xu hướng tháng"""
        if not hasattr(self, 'monthly_chart'):
            return
            
        figure = self.monthly_chart.figure
        figure.clear()
        
        # Group by month
        monthly_data = {}
        for tx in transactions:
            try:
                tx_date_str = tx.get('date', '')
                if 'T' in tx_date_str:
                    tx_date_str = tx_date_str.split('T')[0]
                tx_date = datetime.datetime.strptime(tx_date_str, '%Y-%m-%d')
                month_key = tx_date.strftime('%Y-%m')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'income': 0, 'expense': 0}
                
                if tx.get('type') == 'income':
                    monthly_data[month_key]['income'] += tx.get('amount', 0)
                else:
                    monthly_data[month_key]['expense'] += tx.get('amount', 0)
            except:
                continue
        
        if not monthly_data:
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Không có dữ liệu', ha='center', va='center', transform=ax.transAxes)
            self.monthly_chart.canvas.draw()
            return
        
        # Sort by month
        sorted_months = sorted(monthly_data.keys())
        months = [datetime.datetime.strptime(m, '%Y-%m').strftime('%m/%Y') for m in sorted_months]
        incomes = [monthly_data[m]['income'] for m in sorted_months]
        expenses = [monthly_data[m]['expense'] for m in sorted_months]
        
        ax = figure.add_subplot(111)
        ax.plot(months, incomes, marker='o', label='Thu nhập', color='#10b981', linewidth=2)
        ax.plot(months, expenses, marker='s', label='Chi tiêu', color='#ef4444', linewidth=2)
        
        ax.set_xlabel('Tháng')
        ax.set_ylabel('Số tiền (đ)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K' if x >= 1000 else f'{x:.0f}'))
        
        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45)
        
        figure.tight_layout()
        self.monthly_chart.canvas.draw()
    
    def update_category_pie_chart(self, transactions):
        """Cập nhật biểu đồ tròn phân bổ danh mục"""
        if not hasattr(self, 'category_pie_chart'):
            return
            
        figure = self.category_pie_chart.figure
        figure.clear()
        
        # Group expenses by category
        category_data = {}
        for tx in transactions:
            if tx.get('type') == 'expense':
                cat_id = tx.get('category_id')
                cat_name = self.categories_map.get(cat_id, 'Khác')
                
                if cat_name not in category_data:
                    category_data[cat_name] = 0
                category_data[cat_name] += tx.get('amount', 0)
        
        if not category_data:
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Không có dữ liệu chi tiêu', ha='center', va='center', transform=ax.transAxes)
            self.category_pie_chart.canvas.draw()
            return
        
        # Sort and get top categories
        sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 8 categories, group others
        if len(sorted_categories) > 8:
            top_categories = sorted_categories[:7]
            others_total = sum(amount for _, amount in sorted_categories[7:])
            top_categories.append(('Khác', others_total))
        else:
            top_categories = sorted_categories
        
        labels = [cat for cat, _ in top_categories]
        sizes = [amount for _, amount in top_categories]
        
        # Colors
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', 
                 '#dda0dd', '#ffb347', '#98d8c8', '#f7dc6f', '#bb8fce']
        
        ax = figure.add_subplot(111)
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         colors=colors[:len(labels)], startangle=90)
        
        # Format text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Phân bổ chi tiêu theo danh mục', fontweight='bold', pad=20)
        
        figure.tight_layout()
        self.category_pie_chart.canvas.draw()
    
    def update_category_bar_chart(self, transactions):
        """Cập nhật biểu đồ cột so sánh danh mục"""
        if not hasattr(self, 'category_bar_chart'):
            return
            
        figure = self.category_bar_chart.figure
        figure.clear()
        
        # Group expenses by category
        category_data = {}
        for tx in transactions:
            if tx.get('type') == 'expense':
                cat_id = tx.get('category_id')
                cat_name = self.categories_map.get(cat_id, 'Khác')
                
                if cat_name not in category_data:
                    category_data[cat_name] = 0
                category_data[cat_name] += tx.get('amount', 0)
        
        if not category_data:
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Không có dữ liệu chi tiêu', ha='center', va='center', transform=ax.transAxes)
            self.category_bar_chart.canvas.draw()
            return
        
        # Sort categories by amount
        sorted_categories = sorted(category_data.items(), key=lambda x: x[1], reverse=True)
        
        categories = [cat for cat, _ in sorted_categories[:10]]  # Top 10
        amounts = [amount for _, amount in sorted_categories[:10]]
        
        ax = figure.add_subplot(111)
        bars = ax.bar(categories, amounts, color='#8b5cf6', alpha=0.8)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('Danh mục')
        ax.set_ylabel('Số tiền (đ)')
        ax.set_title('Top 10 danh mục chi tiêu', fontweight='bold', pad=20)
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K' if x >= 1000 else f'{x:.0f}'))
        
        # Rotate x-axis labels
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
        
        figure.tight_layout()
        self.category_bar_chart.canvas.draw()
    
    def update_category_table(self, transactions):
        """Cập nhật bảng chi tiết danh mục"""
        if not hasattr(self, 'category_table'):
            return
        
        # Group data by category
        category_data = {}
        total_expense = 0
        
        for tx in transactions:
            if tx.get('type') == 'expense':
                cat_id = tx.get('category_id')
                cat_name = self.categories_map.get(cat_id, 'Khác')
                amount = tx.get('amount', 0)
                total_expense += amount
                
                if cat_name not in category_data:
                    category_data[cat_name] = {'total': 0, 'count': 0}
                
                category_data[cat_name]['total'] += amount
                category_data[cat_name]['count'] += 1
        
        # Sort by total amount
        sorted_categories = sorted(category_data.items(), key=lambda x: x[1]['total'], reverse=True)
        
        # Update table
        self.category_table.setRowCount(len(sorted_categories))
        
        for i, (cat_name, data) in enumerate(sorted_categories):
            total_amount = data['total']
            count = data['count']
            percentage = (total_amount / total_expense * 100) if total_expense > 0 else 0
            average = total_amount / count if count > 0 else 0
            
            # Category name
            self.category_table.setItem(i, 0, QTableWidgetItem(cat_name))
            
            # Total amount
            amount_item = QTableWidgetItem(f'{total_amount:,.0f} đ')
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.category_table.setItem(i, 1, amount_item)
            
            # Percentage
            pct_item = QTableWidgetItem(f'{percentage:.1f}%')
            pct_item.setTextAlignment(Qt.AlignCenter)
            self.category_table.setItem(i, 2, pct_item)
            
            # Average
            avg_item = QTableWidgetItem(f'{average:,.0f} đ')
            avg_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.category_table.setItem(i, 3, avg_item)
            
            # Transaction count
            count_item = QTableWidgetItem(str(count))
            count_item.setTextAlignment(Qt.AlignCenter)
            self.category_table.setItem(i, 4, count_item)
    
    def update_daily_trend_chart(self, transactions):
        """Cập nhật biểu đồ xu hướng hàng ngày"""
        if not hasattr(self, 'daily_trend_chart'):
            return
            
        figure = self.daily_trend_chart.figure
        figure.clear()
        
        # Group by date
        daily_data = {}
        for tx in transactions:
            try:
                tx_date_str = tx.get('date', '')
                if 'T' in tx_date_str:
                    tx_date_str = tx_date_str.split('T')[0]
                tx_date = datetime.datetime.strptime(tx_date_str, '%Y-%m-%d')
                date_key = tx_date.strftime('%Y-%m-%d')
                
                if date_key not in daily_data:
                    daily_data[date_key] = 0
                
                if tx.get('type') == 'expense':
                    daily_data[date_key] += tx.get('amount', 0)
            except:
                continue
        
        if not daily_data:
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Không có dữ liệu', ha='center', va='center', transform=ax.transAxes)
            self.daily_trend_chart.canvas.draw()
            return
        
        # Sort by date
        sorted_dates = sorted(daily_data.keys())
        dates = [datetime.datetime.strptime(d, '%Y-%m-%d') for d in sorted_dates]
        amounts = [daily_data[d] for d in sorted_dates]
        
        ax = figure.add_subplot(111)
        ax.plot(dates, amounts, marker='o', color='#ef4444', linewidth=2, alpha=0.8)
        ax.fill_between(dates, amounts, alpha=0.3, color='#ef4444')
        
        ax.set_xlabel('Ngày')
        ax.set_ylabel('Chi tiêu (đ)')
        ax.set_title('Xu hướng chi tiêu hàng ngày', fontweight='bold', pad=20)
        ax.grid(True, alpha=0.3)
        
        # Format dates on x-axis
        figure.autofmt_xdate()
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K' if x >= 1000 else f'{x:.0f}'))
        
        figure.tight_layout()
        self.daily_trend_chart.canvas.draw()
    
    def update_weekly_pattern_chart(self, transactions):
        """Cập nhật biểu đồ mẫu hình theo ngày trong tuần"""
        if not hasattr(self, 'weekly_pattern_chart'):
            return
            
        figure = self.weekly_pattern_chart.figure
        figure.clear()
        
        # Group by day of week
        weekday_data = {i: 0 for i in range(7)}  # Monday = 0, Sunday = 6
        
        for tx in transactions:
            if tx.get('type') == 'expense':
                try:
                    tx_date_str = tx.get('date', '')
                    if 'T' in tx_date_str:
                        tx_date_str = tx_date_str.split('T')[0]
                    tx_date = datetime.datetime.strptime(tx_date_str, '%Y-%m-%d')
                    weekday = tx_date.weekday()
                    
                    weekday_data[weekday] += tx.get('amount', 0)
                except:
                    continue
        
        weekday_names = ['Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 'Thứ 6', 'Thứ 7', 'Chủ nhật']
        amounts = [weekday_data[i] for i in range(7)]
        
        ax = figure.add_subplot(111)
        bars = ax.bar(weekday_names, amounts, color='#3b82f6', alpha=0.8)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:,.0f}', ha='center', va='bottom', fontweight='bold')
        
        ax.set_xlabel('Ngày trong tuần')
        ax.set_ylabel('Chi tiêu (đ)')
        ax.set_title('Mẫu hình chi tiêu theo ngày trong tuần', fontweight='bold', pad=20)
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K' if x >= 1000 else f'{x:.0f}'))
        
        figure.tight_layout()
        self.weekly_pattern_chart.canvas.draw()
    
    def update_comparison_chart(self, transactions):
        """Cập nhật biểu đồ so sánh với kỳ trước"""
        if not hasattr(self, 'comparison_chart'):
            return
            
        figure = self.comparison_chart.figure
        figure.clear()
        
        ax = figure.add_subplot(111)
        ax.text(0.5, 0.5, 'Tính năng so sánh kỳ đang phát triển', 
               ha='center', va='center', transform=ax.transAxes, fontsize=14)
        
        self.comparison_chart.canvas.draw()
    
    def reload_data(self):
        """Reload dữ liệu từ bên ngoài"""
        self.load_data()
    
    def reload_categories(self):
        """Callback khi danh mục thay đổi"""
        self.load_data()
