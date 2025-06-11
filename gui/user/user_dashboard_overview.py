from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QPushButton
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from utils.ui_styles import UIStyles
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import datetime

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
        layout.setSpacing(20)
        
        # Header with user greeting
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                    stop: 0 #3b82f6, stop: 1 #06b6d4);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        self.greeting_label = QLabel("Chào mừng!")
        self.greeting_label.setFont(QFont('Segoe UI', 24, QFont.Bold))
        self.greeting_label.setStyleSheet("color: white; margin: 0;")
        header_layout.addWidget(self.greeting_label)
        
        self.date_label = QLabel(datetime.datetime.now().strftime("Hôm nay là %A, %d tháng %m, %Y"))
        self.date_label.setFont(QFont('Segoe UI', 14))
        self.date_label.setStyleSheet("color: rgba(255,255,255,0.9); margin: 0;")
        header_layout.addWidget(self.date_label)
        
        layout.addWidget(header_frame)
        
        # Stats cards
        stats_layout = QGridLayout()
        stats_layout.setSpacing(15)
        
        self.balance_card = self.create_stat_card("Số dư hiện tại", "0đ", "#10b981")
        self.income_card = self.create_stat_card("Thu nhập tháng", "0đ", "#3b82f6")
        self.expense_card = self.create_stat_card("Chi tiêu tháng", "0đ", "#ef4444")
        self.savings_card = self.create_stat_card("Tiết kiệm tháng", "0đ", "#8b5cf6")
        
        stats_layout.addWidget(self.balance_card, 0, 0)
        stats_layout.addWidget(self.income_card, 0, 1)
        stats_layout.addWidget(self.expense_card, 1, 0)
        stats_layout.addWidget(self.savings_card, 1, 1)
        
        layout.addLayout(stats_layout)
        
        # Charts section
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(15)
        
        # Line chart for monthly trend
        self.line_chart_widget = self.create_chart_widget("Xu hướng chi tiêu")
        charts_layout.addWidget(self.line_chart_widget)
        
        # Pie chart for category breakdown
        self.pie_chart_widget = self.create_chart_widget("Phân bổ theo danh mục")
        charts_layout.addWidget(self.pie_chart_widget)
        
        layout.addLayout(charts_layout)
        
        # Recent transactions
        recent_frame = QFrame()
        recent_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        recent_layout = QVBoxLayout(recent_frame)
        recent_layout.setContentsMargins(20, 20, 20, 20)
        
        recent_title = QLabel("Giao dịch gần đây")
        recent_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        recent_title.setStyleSheet("color: #1e293b; margin-bottom: 10px;")
        recent_layout.addWidget(recent_title)
        
        self.recent_transactions_widget = QWidget()
        self.recent_transactions_layout = QVBoxLayout(self.recent_transactions_widget)
        recent_layout.addWidget(self.recent_transactions_widget)
        
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
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 16, QFont.Bold))
        title_label.setStyleSheet("color: #1e293b; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Create matplotlib figure
        figure = Figure(figsize=(6, 4), dpi=80)
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
        """Update greeting with current user name"""
        if hasattr(self.user_manager, 'current_user') and self.user_manager.current_user:
            name = self.user_manager.current_user.get('full_name', 'User')
            self.greeting_label.setText(f"Chào {name}!")
            
    def update_stats(self):
        """Update statistics cards"""
        try:
            # Get current month transactions
            current_month = datetime.datetime.now().month
            current_year = datetime.datetime.now().year
            
            transactions = self.transaction_manager.get_transactions_by_month(current_year, current_month)
            
            total_income = sum(t['amount'] for t in transactions if t['type'] == 'income')
            total_expense = sum(t['amount'] for t in transactions if t['type'] == 'expense')
            balance = total_income - total_expense
            
            # Update cards
            self.balance_card.value_label.setText(f"{balance:,.0f}đ")
            self.income_card.value_label.setText(f"{total_income:,.0f}đ")
            self.expense_card.value_label.setText(f"{total_expense:,.0f}đ")
            self.savings_card.value_label.setText(f"{balance:,.0f}đ")
            
        except Exception as e:
            print(f"Error updating stats: {e}")
            
    def update_charts(self):
        """Update charts with current data"""
        try:
            self.update_line_chart()
            self.update_pie_chart()
        except Exception as e:
            print(f"Error updating charts: {e}")
            
    def update_line_chart(self):
        """Update line chart with monthly trends"""
        try:
            figure = self.line_chart_widget.figure
            figure.clear()
            
            ax = figure.add_subplot(111)
            
            # Get last 6 months data
            months = []
            incomes = []
            expenses = []
            
            for i in range(6):
                date = datetime.datetime.now() - datetime.timedelta(days=30*i)
                month_transactions = self.transaction_manager.get_transactions_by_month(date.year, date.month)
                
                month_income = sum(t['amount'] for t in month_transactions if t['type'] == 'income')
                month_expense = sum(t['amount'] for t in month_transactions if t['type'] == 'expense')
                
                months.append(date.strftime("%m/%Y"))
                incomes.append(month_income)
                expenses.append(month_expense)
            
            months.reverse()
            incomes.reverse()
            expenses.reverse()
            
            ax.plot(months, incomes, label='Thu nhập', color='#3b82f6', marker='o')
            ax.plot(months, expenses, label='Chi tiêu', color='#ef4444', marker='o')
            
            ax.set_title('Xu hướng 6 tháng gần đây')
            ax.legend()
            ax.tick_params(axis='x', rotation=45)
            
            figure.tight_layout()
            self.line_chart_widget.canvas.draw()
            
        except Exception as e:
            print(f"Error updating line chart: {e}")
            
    def update_pie_chart(self):
        """Update pie chart with category breakdown"""
        try:
            figure = self.pie_chart_widget.figure
            figure.clear()
            
            ax = figure.add_subplot(111)
            
            # Get current month expenses by category
            current_month = datetime.datetime.now().month
            current_year = datetime.datetime.now().year
            
            transactions = self.transaction_manager.get_transactions_by_month(current_year, current_month)
            expense_transactions = [t for t in transactions if t['type'] == 'expense']
            
            category_totals = {}
            for transaction in expense_transactions:
                category = transaction.get('category', 'Khác')
                category_totals[category] = category_totals.get(category, 0) + transaction['amount']
            
            if category_totals:
                categories = list(category_totals.keys())
                amounts = list(category_totals.values())
                
                ax.pie(amounts, labels=categories, autopct='%1.1f%%')
                ax.set_title('Chi tiêu theo danh mục (tháng này)')
            else:
                ax.text(0.5, 0.5, 'Chưa có dữ liệu', ha='center', va='center', transform=ax.transAxes)
            
            self.pie_chart_widget.canvas.draw()
            
        except Exception as e:
            print(f"Error updating pie chart: {e}")
            
    def update_recent_transactions(self):
        """Update recent transactions list"""
        try:
            # Clear existing transactions
            for i in reversed(range(self.recent_transactions_layout.count())):
                self.recent_transactions_layout.itemAt(i).widget().setParent(None)
            
            # Get recent transactions
            recent_transactions = self.transaction_manager.get_recent_transactions(5)
            
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
                background: #f8fafc;
                border-radius: 8px;
                padding: 10px;
                margin: 2px 0;
            }
            QFrame:hover {
                background: #f1f5f9;
            }
        """)
        
        layout = QHBoxLayout(item)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # Transaction details
        details_layout = QVBoxLayout()
        
        title_label = QLabel(transaction.get('description', 'Không có mô tả'))
        title_label.setFont(QFont('Segoe UI', 12, QFont.Medium))
        title_label.setStyleSheet("color: #1e293b;")
        details_layout.addWidget(title_label)
        
        category_label = QLabel(transaction.get('category', 'Khác'))
        category_label.setFont(QFont('Segoe UI', 10))
        category_label.setStyleSheet("color: #64748b;")
        details_layout.addWidget(category_label)
        
        layout.addLayout(details_layout)
        layout.addStretch()
        
        # Amount
        amount = transaction.get('amount', 0)
        amount_color = '#10b981' if transaction.get('type') == 'income' else '#ef4444'
        amount_prefix = '+' if transaction.get('type') == 'income' else '-'
        
        amount_label = QLabel(f"{amount_prefix}{amount:,.0f}đ")
        amount_label.setFont(QFont('Segoe UI', 12, QFont.Bold))
        amount_label.setStyleSheet(f"color: {amount_color};")
        layout.addWidget(amount_label)
        
        return item
