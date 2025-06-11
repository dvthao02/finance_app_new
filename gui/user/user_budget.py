from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QComboBox, QLineEdit, QDateEdit, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QProgressBar, QMessageBox,
                            QDialog, QFormLayout, QSpinBox, QTextEdit, QGridLayout,
                            QSpacerItem, QSizePolicy, QTabWidget)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush
import datetime
import json
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

class UserBudget(QWidget):
    """
    Màn hình quản lý ngân sách với theo dõi chi tiêu và cảnh báo
    """
    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.budgets = []
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
                    stop:0 #10b981, stop:1 #059669);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        header_layout = QHBoxLayout()
        
        # Title section
        title_section = QVBoxLayout()
        title = QLabel('💰 Quản lý ngân sách')
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        subtitle = QLabel('Theo dõi và kiểm soát chi tiêu theo danh mục')
        subtitle.setStyleSheet("""
            QLabel {
                color: rgba(255, 255, 255, 0.8);
                font-size: 14px;
                background: transparent;
                margin-top: 5px;
            }
        """)
        
        title_section.addWidget(title)
        title_section.addWidget(subtitle)
        
        # Add budget button
        btn_add_budget = QPushButton('➕ Thêm ngân sách')
        btn_add_budget.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        btn_add_budget.clicked.connect(self.show_add_budget_dialog)
        
        header_layout.addLayout(title_section)
        header_layout.addStretch()
        header_layout.addWidget(btn_add_budget)
        
        header_frame.setLayout(header_layout)
        layout.addWidget(header_frame)
        
        # Main content with tabs
        self.budget_tabs = QTabWidget()
        self.budget_tabs.setStyleSheet("""
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
                color: #10b981;
                border-bottom: 2px solid #10b981;
            }
            QTabBar::tab:hover:!selected {
                background: #e2e8f0;
            }
        """)
        
        # Create tabs
        self.create_overview_tab()
        self.create_budget_list_tab()
        self.create_statistics_tab()
        
        layout.addWidget(self.budget_tabs)
        self.setLayout(layout)
        
        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #f1f5f9;
            }
        """)

    def create_overview_tab(self):
        """Tab tổng quan ngân sách"""
        overview_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Summary cards
        summary_frame = QFrame()
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(15)
        
        # Total budget card
        self.total_budget_card = self.create_summary_card(
            '💰 Tổng ngân sách', '0 đ', 'cho tháng này', '#10b981'
        )
        
        # Total spent card
        self.total_spent_card = self.create_summary_card(
            '💸 Đã chi tiêu', '0 đ', 'trong tháng', '#ef4444'
        )
        
        # Remaining card
        self.remaining_card = self.create_summary_card(
            '💎 Còn lại', '0 đ', 'có thể chi tiêu', '#3b82f6'
        )
        
        # Savings rate card
        self.savings_card = self.create_summary_card(
            '📊 Tỷ lệ tiết kiệm', '0%', 'so với ngân sách', '#8b5cf6'
        )
        
        summary_layout.addWidget(self.total_budget_card)
        summary_layout.addWidget(self.total_spent_card)
        summary_layout.addWidget(self.remaining_card)
        summary_layout.addWidget(self.savings_card)
        
        summary_frame.setLayout(summary_layout)
        layout.addWidget(summary_frame)
        
        # Budget progress section
        progress_frame = QFrame()
        progress_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 20px;
            }
        """)
        
        progress_layout = QVBoxLayout()
        
        progress_title = QLabel('📈 Tiến độ ngân sách theo danh mục')
        progress_title.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 15px;
        """)
        progress_layout.addWidget(progress_title)
        
        # Progress bars container
        self.progress_container = QVBoxLayout()
        progress_layout.addLayout(self.progress_container)
        
        progress_frame.setLayout(progress_layout)
        layout.addWidget(progress_frame)
        
        # Chart section
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(20)
        
        # Budget vs spending chart
        self.budget_chart = self.create_chart_widget('So sánh ngân sách và chi tiêu')
        charts_layout.addWidget(self.budget_chart, 2)
        
        # Category breakdown
        self.category_chart = self.create_chart_widget('Phân bổ ngân sách theo danh mục')
        charts_layout.addWidget(self.category_chart, 1)
        
        layout.addLayout(charts_layout)
        
        overview_widget.setLayout(layout)
        self.budget_tabs.addTab(overview_widget, '📊 Tổng quan')

    def create_budget_list_tab(self):
        """Tab danh sách ngân sách"""
        budget_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 15px;
            }
        """)
        
        filter_layout = QHBoxLayout()
        
        # Month filter
        month_label = QLabel('📅 Tháng:')
        month_label.setStyleSheet("font-weight: 600; color: #374151;")
        
        self.month_filter = QComboBox()
        self.month_filter.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 13px;
                background-color: #f8fafc;
            }
            QComboBox:focus {
                border-color: #10b981;
                background-color: white;
            }
        """)
        
        # Populate months
        current_date = datetime.date.today()
        for i in range(12):
            month_date = current_date.replace(day=1) - datetime.timedelta(days=30*i)
            month_text = month_date.strftime('%m/%Y')
            self.month_filter.addItem(month_text, month_date)
        
        self.month_filter.currentTextChanged.connect(self.filter_budgets)
        
        # Status filter
        status_label = QLabel('🎯 Trạng thái:')
        status_label.setStyleSheet("font-weight: 600; color: #374151;")
        
        self.status_filter = QComboBox()
        self.status_filter.addItems(['Tất cả', 'Đang thực hiện', 'Vượt ngân sách', 'Hoàn thành'])
        self.status_filter.setStyleSheet("""
            QComboBox {
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 13px;
                background-color: #f8fafc;
            }
            QComboBox:focus {
                border-color: #10b981;
                background-color: white;
            }
        """)
        self.status_filter.currentTextChanged.connect(self.filter_budgets)
        
        filter_layout.addWidget(month_label)
        filter_layout.addWidget(self.month_filter)
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_filter)
        filter_layout.addStretch()
        
        filter_frame.setLayout(filter_layout)
        layout.addWidget(filter_frame)
        
        # Budget table
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 20px;
            }
        """)
        
        table_layout = QVBoxLayout()
        
        table_title = QLabel('📋 Danh sách ngân sách')
        table_title.setStyleSheet("""
            font-size: 16px;
            font-weight: 600;
            color: #374151;
            margin-bottom: 15px;
        """)
        table_layout.addWidget(table_title)
        
        self.budget_table = QTableWidget()
        self.budget_table.setColumnCount(7)
        self.budget_table.setHorizontalHeaderLabels([
            '🏷️ Danh mục', '💰 Ngân sách', '💸 Đã chi', '📊 Tiến độ', 
            '📈 % Hoàn thành', '⏰ Thời gian', '⚙️ Thao tác'
        ])
        
        self.budget_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #e2e8f0;
                background-color: white;
                alternate-background-color: #f8fafc;
                selection-background-color: #dcfce7;
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
        
        self.budget_table.setAlternatingRowColors(True)
        self.budget_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.budget_table.verticalHeader().setVisible(False)
        
        table_layout.addWidget(self.budget_table)
        table_frame.setLayout(table_layout)
        layout.addWidget(table_frame)
        
        budget_widget.setLayout(layout)
        self.budget_tabs.addTab(budget_widget, '📋 Danh sách ngân sách')

    def create_statistics_tab(self):
        """Tab thống kê ngân sách"""
        stats_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Monthly trend chart
        self.monthly_trend_chart = self.create_chart_widget('Xu hướng ngân sách theo tháng')
        layout.addWidget(self.monthly_trend_chart)
        
        # Category performance chart
        self.performance_chart = self.create_chart_widget('Hiệu suất ngân sách theo danh mục')
        layout.addWidget(self.performance_chart)
        
        stats_widget.setLayout(layout)
        self.budget_tabs.addTab(stats_widget, '📈 Thống kê')

    def create_summary_card(self, title, value, subtitle, color):
        """Tạo card tổng quan"""
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
        
        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet("""
            color: #9ca3af;
            font-size: 12px;
        """)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        layout.addWidget(subtitle_label)
        
        card.setLayout(layout)
        
        # Store labels for updating
        setattr(card, 'value_label', value_label)
        setattr(card, 'subtitle_label', subtitle_label)
        
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
        """Tải dữ liệu ngân sách và categories"""
        try:
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            if not user_id:
                return
            
            # Load budgets
            try:
                with open('data/budgets.json', 'r', encoding='utf-8') as f:
                    all_budgets = json.load(f)
                self.budgets = [b for b in all_budgets if b.get('user_id') == user_id]
            except:
                self.budgets = []
            
            # Load categories
            try:
                with open('data/categories.json', 'r', encoding='utf-8') as f:
                    all_categories = json.load(f)
                self.categories_map = {cat.get('id') or cat.get('category_id'): cat.get('name', 'Khác') 
                                     for cat in all_categories}
            except:
                self.categories_map = {}
            
            # Update displays
            self.update_overview()
            self.update_budget_table()
            
        except Exception as e:
            print(f"Lỗi tải dữ liệu budget: {e}")

    def show_add_budget_dialog(self):
        """Hiển thị dialog thêm ngân sách mới"""
        dialog = AddBudgetDialog(self.user_manager, self.category_manager, self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def update_overview(self):
        """Cập nhật tab tổng quan"""
        current_month = datetime.date.today().replace(day=1)
        
        # Filter budgets for current month
        current_budgets = []
        for budget in self.budgets:
            try:
                budget_start = datetime.datetime.strptime(budget.get('start_date', ''), '%Y-%m-%d').date()
                budget_end = datetime.datetime.strptime(budget.get('end_date', ''), '%Y-%m-%d').date()
                
                if budget_start <= current_month <= budget_end:
                    current_budgets.append(budget)
            except:
                continue
        
        # Calculate totals
        total_budget = sum(b.get('amount', 0) for b in current_budgets)
        total_spent = self.calculate_spent_amount(current_budgets, current_month)
        remaining = total_budget - total_spent
        savings_rate = ((remaining / total_budget) * 100) if total_budget > 0 else 0
        
        # Update summary cards
        self.total_budget_card.value_label.setText(f'{total_budget:,.0f} đ')
        self.total_spent_card.value_label.setText(f'{total_spent:,.0f} đ')
        self.remaining_card.value_label.setText(f'{remaining:,.0f} đ')
        self.savings_card.value_label.setText(f'{savings_rate:.1f}%')
        
        # Update progress bars
        self.update_progress_bars(current_budgets, current_month)
        
        # Update charts
        self.update_budget_chart(current_budgets, current_month)
        self.update_category_chart(current_budgets)

    def calculate_spent_amount(self, budgets, month):
        """Tính tổng chi tiêu cho các ngân sách trong tháng"""
        try:
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            if not user_id:
                return 0
            
            # Load transactions
            with open('data/transactions.json', 'r', encoding='utf-8') as f:
                all_transactions = json.load(f)
            
            # Filter user transactions in month
            month_start = month
            month_end = (month + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
            
            total_spent = 0
            category_ids = [b.get('category_id') for b in budgets]
            
            for tx in all_transactions:
                if (tx.get('user_id') == user_id and 
                    tx.get('type') == 'expense' and 
                    tx.get('category_id') in category_ids):
                    
                    try:
                        tx_date_str = tx.get('date', '')
                        if 'T' in tx_date_str:
                            tx_date_str = tx_date_str.split('T')[0]
                        tx_date = datetime.datetime.strptime(tx_date_str, '%Y-%m-%d').date()
                        
                        if month_start <= tx_date <= month_end:
                            total_spent += tx.get('amount', 0)
                    except:
                        continue
            
            return total_spent
            
        except Exception as e:
            print(f"Lỗi tính toán chi tiêu: {e}")
            return 0

    def update_progress_bars(self, budgets, month):
        """Cập nhật thanh tiến độ cho từng danh mục"""
        # Clear existing progress bars
        for i in reversed(range(self.progress_container.count())):
            child = self.progress_container.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        for budget in budgets:
            category_name = self.categories_map.get(budget.get('category_id'), 'Khác')
            budget_amount = budget.get('amount', 0)
            spent_amount = self.calculate_category_spent(budget.get('category_id'), month)
            
            progress_widget = self.create_progress_item(category_name, budget_amount, spent_amount)
            self.progress_container.addWidget(progress_widget)

    def calculate_category_spent(self, category_id, month):
        """Tính chi tiêu cho một danh mục trong tháng"""
        try:
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            if not user_id:
                return 0
            
            with open('data/transactions.json', 'r', encoding='utf-8') as f:
                all_transactions = json.load(f)
            
            month_start = month
            month_end = (month + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(days=1)
            
            spent = 0
            for tx in all_transactions:
                if (tx.get('user_id') == user_id and 
                    tx.get('type') == 'expense' and 
                    tx.get('category_id') == category_id):
                    
                    try:
                        tx_date_str = tx.get('date', '')
                        if 'T' in tx_date_str:
                            tx_date_str = tx_date_str.split('T')[0]
                        tx_date = datetime.datetime.strptime(tx_date_str, '%Y-%m-%d').date()
                        
                        if month_start <= tx_date <= month_end:
                            spent += tx.get('amount', 0)
                    except:
                        continue
            
            return spent
            
        except Exception as e:
            print(f"Lỗi tính chi tiêu danh mục: {e}")
            return 0

    def create_progress_item(self, category_name, budget_amount, spent_amount):
        """Tạo item hiển thị tiến độ ngân sách"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border-radius: 8px;
                padding: 12px;
                margin-bottom: 8px;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(8)
        
        # Header with category name and amounts
        header_layout = QHBoxLayout()
        
        category_label = QLabel(f'🏷️ {category_name}')
        category_label.setStyleSheet("""
            font-weight: 600;
            color: #374151;
            font-size: 14px;
        """)
        
        amount_label = QLabel(f'{spent_amount:,.0f} / {budget_amount:,.0f} đ')
        amount_label.setStyleSheet("""
            color: #6b7280;
            font-size: 13px;
        """)
        
        header_layout.addWidget(category_label)
        header_layout.addStretch()
        header_layout.addWidget(amount_label)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMaximum(int(budget_amount) if budget_amount > 0 else 100)
        progress_bar.setValue(int(min(spent_amount, budget_amount)))
        
        # Color based on usage
        usage_percent = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
        
        if usage_percent <= 70:
            color = '#10b981'  # Green
        elif usage_percent <= 90:
            color = '#f59e0b'  # Yellow
        else:
            color = '#ef4444'  # Red
        
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 4px;
                background-color: #e5e7eb;
                height: 8px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 4px;
            }}
        """)
        
        # Percentage label
        percent_label = QLabel(f'{usage_percent:.1f}%')
        percent_label.setStyleSheet(f"""
            color: {color};
            font-weight: 600;
            font-size: 12px;
        """)
        percent_label.setAlignment(Qt.AlignRight)
        
        layout.addLayout(header_layout)
        layout.addWidget(progress_bar)
        layout.addWidget(percent_label)
        
        widget.setLayout(layout)
        return widget

    def update_budget_chart(self, budgets, month):
        """Cập nhật biểu đồ so sánh ngân sách vs chi tiêu"""
        if not hasattr(self, 'budget_chart'):
            return
            
        figure = self.budget_chart.figure
        figure.clear()
        
        if not budgets:
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Chưa có ngân sách nào', ha='center', va='center', transform=ax.transAxes)
            self.budget_chart.canvas.draw()
            return
        
        categories = []
        budget_amounts = []
        spent_amounts = []
        
        for budget in budgets:
            category_name = self.categories_map.get(budget.get('category_id'), 'Khác')
            budget_amount = budget.get('amount', 0)
            spent_amount = self.calculate_category_spent(budget.get('category_id'), month)
            
            categories.append(category_name)
            budget_amounts.append(budget_amount)
            spent_amounts.append(spent_amount)
        
        x = range(len(categories))
        width = 0.35
        
        ax = figure.add_subplot(111)
        ax.bar([i - width/2 for i in x], budget_amounts, width, label='Ngân sách', color='#10b981', alpha=0.8)
        ax.bar([i + width/2 for i in x], spent_amounts, width, label='Đã chi', color='#ef4444', alpha=0.8)
        
        ax.set_xlabel('Danh mục')
        ax.set_ylabel('Số tiền (đ)')
        ax.set_title('So sánh ngân sách và chi tiêu', fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format y-axis
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x/1000:.0f}K' if x >= 1000 else f'{x:.0f}'))
        
        figure.tight_layout()
        self.budget_chart.canvas.draw()

    def update_category_chart(self, budgets):
        """Cập nhật biểu đồ phân bổ ngân sách"""
        if not hasattr(self, 'category_chart'):
            return
            
        figure = self.category_chart.figure
        figure.clear()
        
        if not budgets:
            ax = figure.add_subplot(111)
            ax.text(0.5, 0.5, 'Chưa có ngân sách nào', ha='center', va='center', transform=ax.transAxes)
            self.category_chart.canvas.draw()
            return
        
        # Prepare data
        labels = []
        sizes = []
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', 
                 '#dda0dd', '#ffb347', '#98d8c8', '#f7dc6f', '#bb8fce']
        
        for budget in budgets:
            category_name = self.categories_map.get(budget.get('category_id'), 'Khác')
            budget_amount = budget.get('amount', 0)
            
            labels.append(category_name)
            sizes.append(budget_amount)
        
        ax = figure.add_subplot(111)
        wedges, texts, autotexts = ax.pie(sizes, labels=labels, autopct='%1.1f%%', 
                                         colors=colors[:len(labels)], startangle=90)
        
        # Format text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        ax.set_title('Phân bổ ngân sách theo danh mục', fontweight='bold', pad=20)
        
        figure.tight_layout()
        self.category_chart.canvas.draw()

    def update_budget_table(self):
        """Cập nhật bảng ngân sách"""
        if not hasattr(self, 'budget_table'):
            return
        
        current_month = datetime.date.today().replace(day=1)
        
        # Filter budgets based on selected filters
        filtered_budgets = self.budgets.copy()
        
        # Apply month filter if exists
        if hasattr(self, 'month_filter'):
            selected_month = self.month_filter.currentData()
            if selected_month:
                filtered_budgets = []
                for budget in self.budgets:
                    try:
                        budget_start = datetime.datetime.strptime(budget.get('start_date', ''), '%Y-%m-%d').date()
                        budget_end = datetime.datetime.strptime(budget.get('end_date', ''), '%Y-%m-%d').date()
                        
                        if budget_start <= selected_month <= budget_end:
                            filtered_budgets.append(budget)
                    except:
                        continue
        
        self.budget_table.setRowCount(len(filtered_budgets))
        
        for i, budget in enumerate(filtered_budgets):
            category_name = self.categories_map.get(budget.get('category_id'), 'Khác')
            budget_amount = budget.get('amount', 0)
            spent_amount = self.calculate_category_spent(budget.get('category_id'), current_month)
            
            # Category
            self.budget_table.setItem(i, 0, QTableWidgetItem(category_name))
            
            # Budget amount
            budget_item = QTableWidgetItem(f'{budget_amount:,.0f} đ')
            budget_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.budget_table.setItem(i, 1, budget_item)
            
            # Spent amount
            spent_item = QTableWidgetItem(f'{spent_amount:,.0f} đ')
            spent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.budget_table.setItem(i, 2, spent_item)
            
            # Progress bar
            progress_widget = QProgressBar()
            progress_widget.setMaximum(int(budget_amount) if budget_amount > 0 else 100)
            progress_widget.setValue(int(min(spent_amount, budget_amount)))
            progress_widget.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 4px;
                    background-color: #e5e7eb;
                    height: 20px;
                }
                QProgressBar::chunk {
                    background-color: #10b981;
                    border-radius: 4px;
                }
            """)
            self.budget_table.setCellWidget(i, 3, progress_widget)
            
            # Completion percentage
            completion = (spent_amount / budget_amount * 100) if budget_amount > 0 else 0
            completion_item = QTableWidgetItem(f'{completion:.1f}%')
            completion_item.setTextAlignment(Qt.AlignCenter)
            
            # Color based on completion
            if completion <= 70:
                completion_item.setBackground(QBrush(QColor('#dcfce7')))
                completion_item.setForeground(QBrush(QColor('#166534')))
            elif completion <= 90:
                completion_item.setBackground(QBrush(QColor('#fef3c7')))
                completion_item.setForeground(QBrush(QColor('#92400e')))
            else:
                completion_item.setBackground(QBrush(QColor('#fee2e2')))
                completion_item.setForeground(QBrush(QColor('#991b1b')))
            
            self.budget_table.setItem(i, 4, completion_item)
            
            # Time period
            start_date = budget.get('start_date', '')
            end_date = budget.get('end_date', '')
            period_text = f'{start_date} → {end_date}'
            self.budget_table.setItem(i, 5, QTableWidgetItem(period_text))
            
            # Action buttons
            self.create_budget_action_buttons(i, budget)

    def create_budget_action_buttons(self, row, budget):
        """Tạo nút thao tác cho ngân sách"""
        actions_widget = QWidget()
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(5, 2, 5, 2)
        actions_layout.setSpacing(5)
        
        # Edit button
        btn_edit = QPushButton('✏️')
        btn_edit.setToolTip('Chỉnh sửa ngân sách')
        btn_edit.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        btn_edit.clicked.connect(lambda: self.edit_budget(budget))
        
        # Delete button
        btn_delete = QPushButton('🗑️')
        btn_delete.setToolTip('Xóa ngân sách')
        btn_delete.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 8px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        btn_delete.clicked.connect(lambda: self.delete_budget(budget))
        
        actions_layout.addWidget(btn_edit)
        actions_layout.addWidget(btn_delete)
        actions_layout.addStretch()
        
        actions_widget.setLayout(actions_layout)
        self.budget_table.setCellWidget(row, 6, actions_widget)

    def filter_budgets(self):
        """Lọc ngân sách theo bộ lọc"""
        self.update_budget_table()

    def edit_budget(self, budget):
        """Chỉnh sửa ngân sách"""
        dialog = AddBudgetDialog(self.user_manager, self.category_manager, self, budget)
        if dialog.exec_() == QDialog.Accepted:
            self.load_data()

    def delete_budget(self, budget):
        """Xóa ngân sách"""
        reply = QMessageBox.question(self, '❓ Xác nhận xóa',
                                   f'Bạn có chắc muốn xóa ngân sách này?\n\n'
                                   f'🏷️ Danh mục: {self.categories_map.get(budget.get("category_id"), "Khác")}\n'
                                   f'💰 Số tiền: {budget.get("amount", 0):,.0f} đ',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                # Load all budgets
                with open('data/budgets.json', 'r', encoding='utf-8') as f:
                    all_budgets = json.load(f)
                
                # Remove budget
                budget_id = budget.get('id')
                all_budgets = [b for b in all_budgets if b.get('id') != budget_id]
                
                # Save back
                with open('data/budgets.json', 'w', encoding='utf-8') as f:
                    json.dump(all_budgets, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, '✅ Thành công', 'Đã xóa ngân sách thành công!')
                self.load_data()
                
            except Exception as e:
                QMessageBox.critical(self, '❌ Lỗi', f'Không thể xóa ngân sách:\n{str(e)}')

# Dialog thêm/sửa ngân sách
class AddBudgetDialog(QDialog):
    def __init__(self, user_manager, category_manager, parent=None, budget=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.category_manager = category_manager
        self.budget = budget
        self.is_edit = budget is not None
        self.init_ui()
        if self.is_edit:
            self.load_budget_data()

    def init_ui(self):
        title = '✏️ Chỉnh sửa ngân sách' if self.is_edit else '➕ Thêm ngân sách mới'
        self.setWindowTitle(title)
        self.setFixedSize(450, 500)
        self.setModal(True)
        
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_label = QLabel(title)
        header_label.setStyleSheet("""
            QLabel {
                color: #374151;
                font-size: 20px;
                font-weight: bold;
                margin-bottom: 10px;
            }
        """)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Form
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 25px;
            }
        """)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Input styles
        input_style = """
            QLineEdit, QComboBox, QDateEdit, QSpinBox {
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8fafc;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
                border-color: #10b981;
                background-color: white;
            }
        """
        
        label_style = """
            QLabel {
                color: #374151;
                font-weight: 600;
                font-size: 14px;
            }
        """
        
        # Category selection
        category_label = QLabel('🏷️ Danh mục:')
        category_label.setStyleSheet(label_style)
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(input_style)
        self.load_categories()
        
        # Budget amount
        amount_label = QLabel('💰 Số tiền ngân sách:')
        amount_label.setStyleSheet(label_style)
        self.amount_input = QLineEdit()
        self.amount_input.setStyleSheet(input_style)
        self.amount_input.setPlaceholderText('Nhập số tiền (VND)')
        
        # Start date
        start_date_label = QLabel('📅 Ngày bắt đầu:')
        start_date_label.setStyleSheet(label_style)
        self.start_date = QDateEdit(QDate.currentDate().addDays(-QDate.currentDate().day() + 1))
        self.start_date.setCalendarPopup(True)
        self.start_date.setDisplayFormat('dd/MM/yyyy')
        self.start_date.setStyleSheet(input_style)
        
        # End date
        end_date_label = QLabel('📅 Ngày kết thúc:')
        end_date_label.setStyleSheet(label_style)
        self.end_date = QDateEdit(QDate.currentDate())
        self.end_date.setCalendarPopup(True)
        self.end_date.setDisplayFormat('dd/MM/yyyy')
        self.end_date.setStyleSheet(input_style)
        
        # Description
        desc_label = QLabel('📝 Mô tả:')
        desc_label.setStyleSheet(label_style)
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setStyleSheet(input_style)
        self.description_input.setPlaceholderText('Mô tả ngân sách (tuỳ chọn)')
        
        # Add to form
        form_layout.addRow(category_label, self.category_combo)
        form_layout.addRow(amount_label, self.amount_input)
        form_layout.addRow(start_date_label, self.start_date)
        form_layout.addRow(end_date_label, self.end_date)
        form_layout.addRow(desc_label, self.description_input)
        
        form_frame.setLayout(form_layout)
        layout.addWidget(form_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        btn_cancel = QPushButton('❌ Hủy')
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #6b7280;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #4b5563;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_save = QPushButton('💾 Lưu ngân sách' if self.is_edit else '➕ Tạo ngân sách')
        btn_save.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        btn_save.clicked.connect(self.save_budget)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cancel)
        buttons_layout.addWidget(btn_save)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
        
        # Dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: #f1f5f9;
            }
        """)

    def load_categories(self):
        """Load danh mục vào combobox"""
        try:
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            
            with open('data/categories.json', 'r', encoding='utf-8') as f:
                all_categories = json.load(f)
            
            # Filter categories (user's + common categories for expenses)
            categories = []
            for cat in all_categories:
                if (cat.get('user_id') is None or cat.get('user_id') == user_id):
                    if cat.get('type') in [None, 'both', 'expense']:
                        categories.append(cat)
            
            for cat in categories:
                name = cat.get('name', 'Không tên')
                cat_id = cat.get('id') or cat.get('category_id')
                self.category_combo.addItem(name, cat_id)
                
        except Exception as e:
            print(f"Lỗi load categories: {e}")

    def load_budget_data(self):
        """Load dữ liệu ngân sách để edit"""
        if not self.budget:
            return
        
        # Set category
        cat_id = self.budget.get('category_id')
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == cat_id:
                self.category_combo.setCurrentIndex(i)
                break
        
        # Set amount
        self.amount_input.setText(str(self.budget.get('amount', 0)))
        
        # Set dates
        try:
            start_date = datetime.datetime.strptime(self.budget.get('start_date', ''), '%Y-%m-%d').date()
            self.start_date.setDate(QDate(start_date))
        except:
            pass
        
        try:
            end_date = datetime.datetime.strptime(self.budget.get('end_date', ''), '%Y-%m-%d').date()
            self.end_date.setDate(QDate(end_date))
        except:
            pass
        
        # Set description
        self.description_input.setPlainText(self.budget.get('description', ''))

    def save_budget(self):
        """Lưu ngân sách"""
        try:
            # Validate
            if self.category_combo.currentData() is None:
                QMessageBox.warning(self, '⚠️ Lỗi', 'Vui lòng chọn danh mục!')
                return
            
            amount_text = self.amount_input.text().replace(',', '').strip()
            if not amount_text:
                QMessageBox.warning(self, '⚠️ Lỗi', 'Vui lòng nhập số tiền!')
                return
            
            try:
                amount = float(amount_text)
                if amount <= 0:
                    QMessageBox.warning(self, '⚠️ Lỗi', 'Số tiền phải lớn hơn 0!')
                    return
            except ValueError:
                QMessageBox.warning(self, '⚠️ Lỗi', 'Số tiền không hợp lệ!')
                return
            
            start_date = self.start_date.date().toPyDate()
            end_date = self.end_date.date().toPyDate()
            
            if start_date > end_date:
                QMessageBox.warning(self, '⚠️ Lỗi', 'Ngày bắt đầu phải trước ngày kết thúc!')
                return
            
            # Load existing budgets
            try:
                with open('data/budgets.json', 'r', encoding='utf-8') as f:
                    all_budgets = json.load(f)
            except:
                all_budgets = []
            
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            
            if self.is_edit:
                # Update existing budget
                budget_id = self.budget.get('id')
                for i, budget in enumerate(all_budgets):
                    if budget.get('id') == budget_id:
                        all_budgets[i].update({
                            'category_id': self.category_combo.currentData(),
                            'amount': amount,
                            'start_date': start_date.strftime('%Y-%m-%d'),
                            'end_date': end_date.strftime('%Y-%m-%d'),
                            'description': self.description_input.toPlainText().strip(),
                            'updated_at': datetime.datetime.now().isoformat()
                        })
                        break
            else:
                # Create new budget
                new_budget = {
                    'id': f'budget_{user_id}_{len(all_budgets)+1}',
                    'user_id': user_id,
                    'category_id': self.category_combo.currentData(),
                    'amount': amount,
                    'start_date': start_date.strftime('%Y-%m-%d'),
                    'end_date': end_date.strftime('%Y-%m-%d'),
                    'description': self.description_input.toPlainText().strip(),
                    'created_at': datetime.datetime.now().isoformat(),
                    'updated_at': datetime.datetime.now().isoformat()
                }
                all_budgets.append(new_budget)
            
            # Save to file
            with open('data/budgets.json', 'w', encoding='utf-8') as f:
                json.dump(all_budgets, f, ensure_ascii=False, indent=2)
            
            action = 'cập nhật' if self.is_edit else 'tạo'
            QMessageBox.information(self, '✅ Thành công', f'Đã {action} ngân sách thành công!')
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, '❌ Lỗi', f'Không thể lưu ngân sách:\n{str(e)}')
