from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QComboBox, QSizePolicy, QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QStackedWidget
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette
from PyQt5.QtCore import Qt, QSize, pyqtSignal, QTimer
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import datetime

class UserDashboard(QWidget):
    logout_signal = pyqtSignal()
    
    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.current_user = None
        self.init_ui()    
    def set_current_user(self, user):
        self.current_user = user
        self.user_manager.current_user = user
        self.update_dashboard()
          # Show welcome toast after a short delay
        QTimer.singleShot(1000, self.show_welcome_toast)

    def init_ui(self):
        self.setWindowTitle('Quản lý Chi Tiêu Cá Nhân')
        self.setMinimumSize(1350, 850)
          # Set comprehensive default styling for better harmony
        self.setStyleSheet("""
            /* Global default styles */
            QWidget { 
                background-color: #f8fafc; 
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                color: #1e293b;
            }
            
            /* Label styles */
            QLabel {
                color: #334155;
                font-size: 13px;
            }
            
            /* Button styles */
            QPushButton {
                font-size: 13px;
                font-weight: 500;
                padding: 8px 16px;
                border-radius: 6px;
                border: 1px solid #e2e8f0;
                background: white;
                color: #374151;
                min-height: 20px;
            }
            QPushButton:hover {
                background: #f9fafb;
                border-color: #d1d5db;
            }
            QPushButton:pressed {
                background: #f3f4f6;
            }
            
            /* Input styles */
            QLineEdit, QComboBox {
                font-size: 13px;
                padding: 8px 12px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
                color: #374151;
                min-height: 16px;
            }
            QLineEdit:focus, QComboBox:focus {
                border-color: #3b82f6;
            }
            
            /* Table styles */
            QTableWidget {
                font-size: 13px;
                gridline-color: #f1f5f9;
                background: white;
                selection-background-color: #eff6ff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 10px 12px;
                border-bottom: 1px solid #f1f5f9;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 12px;
                border: none;
                border-bottom: 1px solid #e2e8f0;
                font-weight: 600;
                font-size: 12px;
                color: #6b7280;
            }
            
            /* Frame styles */
            QFrame {
                border-radius: 8px;
            }
        """)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = self.create_header()
        main_layout.addWidget(header)        # Body với sidebar và content
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # Sidebar
        sidebar = self.create_sidebar()
        body_layout.addWidget(sidebar)

        # Main content area
        self.content_stack = QStackedWidget()
        self.content_stack.setMinimumWidth(800)  # Đảm bảo content có width tối thiểu
        self.content_stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Dashboard tab
        dashboard_widget = self.create_dashboard_content()
        self.content_stack.addWidget(dashboard_widget)
        
        # Import other tabs
        from .user_transaction_form import UserTransactionForm
        from .user_transaction_history import UserTransactionHistory
        from .user_report import UserReport
        from .user_budget import UserBudget
        from .user_category_tab import UserCategoryTab
        from .user_settings import UserSettings
          # Initialize other tabs
        self.transaction_form = UserTransactionForm(self.user_manager, self.transaction_manager, self.category_manager, self.wallet_manager)
        self.transaction_history = UserTransactionHistory(self.user_manager, self.transaction_manager, self.category_manager, self.wallet_manager)
        self.report_tab = UserReport(self.user_manager, self.transaction_manager, self.category_manager)
         
        user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
        self.budget_tab = UserBudget(self.user_manager, self.transaction_manager, self.category_manager, self.wallet_manager)
        self.category_tab = UserCategoryTab(self.category_manager, user_id, reload_callback=self.reload_categories)
        self.settings_tab = UserSettings(self.user_manager, self.wallet_manager, self.category_manager)
        
        # Connect signals between tabs
        self.connect_tab_signals()
          # Add tabs to stack
        self.content_stack.addWidget(self.transaction_form)      # index 1
        self.content_stack.addWidget(self.transaction_history)   # index 2
        self.content_stack.addWidget(self.report_tab)           # index 3
        self.content_stack.addWidget(self.budget_tab)           # index 4
        self.content_stack.addWidget(self.category_tab)         # index 5
        self.content_stack.addWidget(self.settings_tab)         # index 6

        # Add content stack to body layout
        body_layout.addWidget(self.content_stack)
        main_layout.addLayout(body_layout)
        
        # Add quick actions floating button
        self.setup_quick_actions()

    def create_header(self):
        header = QFrame()
        header.setFixedHeight(70)
        header.setStyleSheet("""
            QFrame {
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                border: none;
                border-radius: 0px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(20)
        
        # Logo và tên app
        logo_layout = QHBoxLayout()
        logo_layout.setSpacing(12)
        
        logo = QLabel()
        try:
            logo.setPixmap(QPixmap('assets/app_icon.png').scaled(36, 36, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        except:
            logo.setText('💼')
            logo.setFont(QFont('Segoe UI', 20))
        logo_layout.addWidget(logo)
        
        app_name = QLabel('FinanceTracker')
        app_name.setFont(QFont('Segoe UI', 18, QFont.Bold))
        app_name.setStyleSheet('color: white; font-weight: 600;')
        logo_layout.addWidget(app_name)
        
        layout.addLayout(logo_layout)
        layout.addStretch()
        
        # Search box
        search = QLineEdit()
        search.setPlaceholderText('Tìm kiếm giao dịch, danh mục...')
        search.setFixedWidth(280)
        search.setFixedHeight(38)
        search.setStyleSheet("""
            QLineEdit {
                background: rgba(255,255,255,0.95);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 19px;
                padding: 0 16px;
                font-size: 14px;
                color: #374151;
            }
            QLineEdit:focus {
                background: white;
                border-color: rgba(255,255,255,0.4);
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """)        
        layout.addWidget(search)
        
        layout.addStretch()
        
        # Notification bell
        self.notification_btn = QPushButton('🔔')
        self.notification_btn.setFont(QFont('Segoe UI', 16))
        self.notification_btn.setFixedSize(44, 44)
        self.notification_btn.setStyleSheet("""
            QPushButton {
                color: white;
                background: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 22px;
                font-size: 16px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.25);
                border-color: rgba(255,255,255,0.3);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.1);
            }
        """)
        self.notification_btn.clicked.connect(self.show_notifications)
        layout.addWidget(self.notification_btn)
        
        # User info (clickable)
        user_name = getattr(self.user_manager, 'current_user', {}).get('name', 'User')
        self.user_button = QPushButton(f'👤  {user_name}')
        self.user_button.setFont(QFont('Segoe UI', 13, QFont.Medium))
        self.user_button.setStyleSheet("""
            QPushButton {
                color: white;
                background: rgba(255,255,255,0.15);
                border: 1px solid rgba(255,255,255,0.2);
                border-radius: 22px;
                padding: 8px 18px;
                text-align: left;
                font-weight: 500;
                min-width: 120px;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.25);
                border-color: rgba(255,255,255,0.3);
            }
            QPushButton:pressed {
                background: rgba(255,255,255,0.1);
            }
        """)
        self.user_button.clicked.connect(self.show_user_profile)
        layout.addWidget(self.user_button)
        
        return header

    def create_sidebar(self):
        sidebar = QFrame()
        sidebar.setFixedWidth(250)
        sidebar.setStyleSheet("""
            QFrame {
                background: white;
                border-right: 1px solid #e2e8f0;
                border-radius: 0px;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 24, 0, 24)
        layout.setSpacing(4)
        
        # Menu items
        self.menu_buttons = []
        menu_items = [
            ('📊  Tổng quan', 0),
            ('💰  Nhập giao dịch', 1),
            ('📋  Danh sách giao dịch', 2),
            ('📈  Báo cáo thống kê', 3),
            ('🎯  Ngân sách', 4),
            ('📂  Danh mục', 5),
            ('⚙️  Cài đặt', 6),
        ]
        
        for i, (text, tab_index) in enumerate(menu_items):
            btn = QPushButton(text)
            btn.setFont(QFont('Segoe UI', 13, QFont.Medium))
            btn.setFixedHeight(48)
            btn.setCursor(Qt.PointingHandCursor)
            
            if i == 0:  # Dashboard active by default
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding-left: 20px;
                        border: none;
                        border-radius: 8px;
                        background: #f0f9ff;
                        color: #0369a1;
                        margin: 2px 12px;
                        font-weight: 600;
                        border-left: 3px solid #3b82f6;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding-left: 20px;
                        border: none;
                        border-radius: 8px;
                        background: transparent;
                        color: #64748b;
                        margin: 2px 12px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background: #f8fafc;
                        color: #1e293b;
                        border-left: 3px solid #e2e8f0;
                    }
                """)
            
            btn.clicked.connect(lambda checked, idx=tab_index: self.switch_tab(idx))
            layout.addWidget(btn)
            self.menu_buttons.append(btn)
        
        layout.addStretch()
        return sidebar

    def create_dashboard_content(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Page header
        header_layout = QHBoxLayout()
        title = QLabel('Tổng quan tài chính')
        title.setFont(QFont('Segoe UI', 24, QFont.Bold))
        title.setStyleSheet('color: #1e293b;')
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        time_filter = QComboBox()
        time_filter.addItems(['Tháng 6, 2025'])
        time_filter.setFixedHeight(35)
        time_filter.setStyleSheet("""
            QComboBox {
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 0 10px;
                min-width: 120px;
            }
        """)
        header_layout.addWidget(time_filter)
        
        layout.addLayout(header_layout)
        
        # Stats cards
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(20)
          # Lấy dữ liệu thống kê thực
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
        
        # Khởi tạo với giá trị mặc định
        income = 0
        expense = 0
        balance = 0
        savings = 0
        income_change = 0
        expense_change = 0
        year_income = 0
        year_expense = 0
        
        if user_id:
            # Lấy dữ liệu thực từ file JSON
            try:
                import json
                with open('data/transactions.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    user_transactions = [t for t in data if t.get('user_id') == user_id]
                    
                # Tính toán cho tháng hiện tại
                current_month_income = 0
                current_month_expense = 0
                previous_month_income = 0
                previous_month_expense = 0
                
                for t in user_transactions:
                    try:
                        tx_date = datetime.datetime.fromisoformat(t['date'].replace('Z', '+00:00'))
                        amount = t.get('amount', 0)
                        tx_type = t.get('type')
                        
                        # Thống kê theo năm
                        if tx_date.year == year:
                            if tx_type == 'income':
                                year_income += amount
                            elif tx_type == 'expense':
                                year_expense += amount
                                
                            # Thống kê theo tháng
                            if tx_date.month == month:
                                if tx_type == 'income':
                                    current_month_income += amount
                                elif tx_type == 'expense':
                                    current_month_expense += amount
                            elif tx_date.month == (month - 1 if month > 1 else 12):
                                if tx_type == 'income':
                                    previous_month_income += amount
                                elif tx_type == 'expense':
                                    previous_month_expense += amount
                    except Exception:
                        continue
                
                income = current_month_income
                expense = current_month_expense
                balance = income - expense
                savings = year_income - year_expense
                
                # Tính phần trăm thay đổi
                if previous_month_income > 0:
                    income_change = ((income - previous_month_income) / previous_month_income) * 100
                if previous_month_expense > 0:
                    expense_change = ((expense - previous_month_expense) / previous_month_expense) * 100
                    
            except Exception as e:
                print(f"Lỗi đọc dữ liệu thống kê: {e}")
                # Đảm bảo các biến được khởi tạo ngay cả khi có lỗi
                year_income = 0
                year_expense = 0        # Tạo các card với dữ liệu thực
        try:
            from .animated_widgets import AnimatedStatCard, StaggeredAnimationGroup
            
            card1 = AnimatedStatCard('Tổng thu', income, 
                                    f'{income_change:+.1f}% so với tháng trước', 
                                    '#10b981', '↗' if income_change >= 0 else '↘')
            card2 = AnimatedStatCard('Tổng chi', expense, 
                                    f'{expense_change:+.1f}% so với tháng trước', 
                                    '#ef4444', '↗' if expense_change >= 0 else '↘')
            card3 = AnimatedStatCard('Số dư', balance, 
                                    f'{((balance/income)*100 if income > 0 else 0):.1f}% của thu nhập', 
                                    '#3b82f6', '↗')
            card4 = AnimatedStatCard('Tiết kiệm', savings, 
                                    f'{((savings/year_income)*100 if year_income > 0 else 0):.1f}% tích luỹ năm', 
                                    '#8b5cf6', '↗')
            
            # Store cards for later animation
            self.stat_cards = [card1, card2, card3, card4]
        except Exception as e:
            print(f"Error creating animated cards: {e}")
            # Fallback to regular stat cards
            card1 = self.create_stat_card('Tổng thu', f'{income:,.0f} đ', 
                                        f'{income_change:+.1f}% so với tháng trước', 
                                        '#10b981', '↗' if income_change >= 0 else '↘')
            card2 = self.create_stat_card('Tổng chi', f'{expense:,.0f} đ', 
                                        f'{expense_change:+.1f}% so với tháng trước', 
                                        '#ef4444', '↗' if expense_change >= 0 else '↘')
            card3 = self.create_stat_card('Số dư', f'{balance:,.0f} đ', 
                                        f'{((balance/income)*100 if income > 0 else 0):.1f}% của thu nhập', 
                                        '#3b82f6', '↗')
            card4 = self.create_stat_card('Tiết kiệm', f'{savings:,.0f} đ', 
                                        f'{((savings/year_income)*100 if year_income > 0 else 0):.1f}% tích luỹ năm', 
                                        '#8b5cf6', '↗')
            
            # Store cards for later updates
            self.stat_cards = [card1, card2, card3, card4]
        
        stats_layout.addWidget(card1)
        stats_layout.addWidget(card2)
        stats_layout.addWidget(card3)
        stats_layout.addWidget(card4)
        
        layout.addLayout(stats_layout)
        
        # Charts row
        charts_layout = QHBoxLayout()
        charts_layout.setSpacing(25)
        
        # Line chart
        line_chart_widget = self.create_line_chart()
        charts_layout.addWidget(line_chart_widget, 2)
        
        # Pie chart
        pie_chart_widget = self.create_pie_chart()
        charts_layout.addWidget(pie_chart_widget, 1)
        
        layout.addLayout(charts_layout)
        
        # Transactions table
        table_widget = self.create_transactions_table()
        layout.addWidget(table_widget)
        
        return widget
    
    def create_stat_card(self, title, value, subtitle, color, trend_icon):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
            QFrame:hover {
                border-color: #cbd5e1;
                background: #fafafa;
            }
        """)
        card.setFixedHeight(130)
        card.setMinimumWidth(250)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(12)
        
        # Header với title và trend
        header_layout = QHBoxLayout()
        title_label = QLabel(title)
        title_label.setFont(QFont('Segoe UI', 13, QFont.Medium))
        title_label.setStyleSheet('color: #6b7280; font-weight: 500; letter-spacing: 0.3px;')
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        trend_label = QLabel(trend_icon)
        trend_label.setFont(QFont('Segoe UI', 16))
        trend_label.setStyleSheet(f'color: {color}; font-weight: 600;')
        header_layout.addWidget(trend_label)
        
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(value)
        value_label.setFont(QFont('Segoe UI', 22, QFont.Bold))
        value_label.setStyleSheet(f'color: {color}; font-weight: 700; line-height: 1.2;')
        layout.addWidget(value_label)
        
        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_label.setFont(QFont('Segoe UI', 11))
        subtitle_label.setStyleSheet('color: #9ca3af; font-weight: 400; line-height: 1.4;')
        layout.addWidget(subtitle_label)
        
        return card

    def create_line_chart(self):
        widget = QFrame()        
        widget.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel('Biểu đồ thu chi')
        title.setFont(QFont('Segoe UI', 17, QFont.Bold))
        title.setStyleSheet('color: #1e293b; font-weight: 600; letter-spacing: -0.3px;')
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Filter buttons
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)
        
        for period in ['Tuần', 'Tháng', 'Năm']:
            btn = QPushButton(period)
            btn.setFixedSize(65, 32)
            btn.setFont(QFont('Segoe UI', 12, QFont.Medium))
            if period == 'Tháng':
                btn.setStyleSheet("""
                    QPushButton {
                        background: #3b82f6;
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background: #2563eb;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #f8fafc;
                        color: #64748b;
                        border: 1px solid #e2e8f0;
                        border-radius: 8px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background: #f1f5f9;
                        color: #1e293b;
                        border-color: #cbd5e1;
                    }
                """)
            filter_layout.addWidget(btn)
        
        header_layout.addLayout(filter_layout)
        layout.addLayout(header_layout)
        
        # Chart with better spacing
        self.line_chart_canvas = FigureCanvas(Figure(figsize=(8, 4)))
        self.line_chart_canvas.setStyleSheet('background: transparent;')
        layout.addWidget(self.line_chart_canvas)
        
        return widget
    
    def create_pie_chart(self):
        widget = QFrame()        
        widget.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel('Phân bổ chi tiêu')
        title.setFont(QFont('Segoe UI', 17, QFont.Bold))
        title.setStyleSheet('color: #1e293b; font-weight: 600; letter-spacing: -0.3px;')
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        view_all = QLabel('Xem chi tiết →')
        view_all.setFont(QFont('Segoe UI', 12, QFont.Medium))
        view_all.setStyleSheet('color: #3b82f6; font-weight: 500;')
        view_all.setCursor(Qt.PointingHandCursor)
        header_layout.addWidget(view_all)
        
        layout.addLayout(header_layout)
        
        # Chart with better styling
        self.pie_chart_canvas = FigureCanvas(Figure(figsize=(4, 4)))
        self.pie_chart_canvas.setStyleSheet('background: transparent;')
        layout.addWidget(self.pie_chart_canvas)
        
        return widget
    
    def create_transactions_table(self):
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel('Giao dịch gần đây')
        title.setFont(QFont('Segoe UI', 17, QFont.Bold))
        title.setStyleSheet('color: #1e293b; font-weight: 600; letter-spacing: -0.3px;')        
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Search and filter with better styling
        search_box = QLineEdit()
        search_box.setPlaceholderText('Tìm kiếm giao dịch')
        search_box.setFixedWidth(220)
        search_box.setFixedHeight(38)
        search_box.setStyleSheet("""
            QLineEdit {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 13px;
                color: #374151;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: white;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """)
        header_layout.addWidget(search_box)
        
        filter_btn = QPushButton('🔍 Lọc')
        filter_btn.setFixedSize(70, 38)
        filter_btn.setFont(QFont('Segoe UI', 12, QFont.Medium))
        filter_btn.setStyleSheet("""
            QPushButton {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                color: #64748b;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #f1f5f9;
                color: #1e293b;
                border-color: #cbd5e1;
            }
        """)
        header_layout.addWidget(filter_btn)
        
        layout.addLayout(header_layout)
          # Table with improved styling
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels(['Ngày tháng', 'Loại', 'Danh mục', 'Số tiền', 'Ghi chú', 'Thao tác'])
        
        # Enhanced table styling
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #f1f5f9;
                background: white;
                selection-background-color: #f0f9ff;
                selection-color: #1e40af;
                font-size: 13px;
            }
            QTableWidget::item {
                padding: 14px 12px;
                border-bottom: 1px solid #f1f5f9;
                color: #374151;
            }
            QTableWidget::item:selected {
                background: #f0f9ff;
                color: #1e40af;
            }
            QTableWidget::item:hover {
                background: #f8fafc;
            }
            QHeaderView::section {
                background: #f8fafc;
                padding: 16px 12px;
                border: none;
                border-bottom: 2px solid #e2e8f0;                font-weight: 600;
                font-size: 12px;
                color: #6b7280;
                letter-spacing: 0.5px;
            }
        """)
        
        # Better table configuration
        self.transactions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transactions_table.setAlternatingRowColors(True)
        self.transactions_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.transactions_table.setShowGrid(False)
        self.transactions_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.transactions_table)
        
        return widget

    def update_dashboard(self):
        self.update_line_chart()
        self.update_pie_chart()
        self.update_transactions_table()
        # Cập nhật stat cards với dữ liệu thực
        self.update_stat_cards()
        
        # Trigger staggered animation for stat cards after a short delay
        if hasattr(self, 'stat_cards'):
            QTimer.singleShot(500, self.animate_stat_cards)
    
    def animate_stat_cards(self):
        """Trigger staggered animation for stat cards"""
        try:
            from .animated_widgets import StaggeredAnimationGroup
            
            if hasattr(self, 'stat_cards'):
                animation_group = StaggeredAnimationGroup(self.stat_cards, delay=200)
                animation_group.start_animations()
        except Exception as e:
            print(f"Error animating stat cards: {e}")    
    
    def update_stat_cards(self):
        if not hasattr(self, 'stat_cards'):
            return
            
        # Lấy dữ liệu thực
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
        
        if not user_id:
            return
            
        # Lấy tất cả giao dịch của user
        all_transactions = []
        try:
            import json
            with open('data/transactions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_transactions = [t for t in data if t.get('user_id') == user_id]
        except Exception as e:
            print(f"Lỗi đọc dữ liệu giao dịch: {e}")
            return
            
        # Tính toán thống kê tháng hiện tại
        current_month_income = 0
        current_month_expense = 0
        previous_month_income = 0
        previous_month_expense = 0
        
        for t in all_transactions:
            try:
                # Parse date từ ISO format
                tx_date = datetime.datetime.fromisoformat(t['date'].replace('Z', '+00:00'))
                tx_month = tx_date.month
                tx_year = tx_date.year
                amount = t.get('amount', 0)
                
                if tx_year == year:
                    if tx_month == month:  # Tháng hiện tại
                        if t.get('type') == 'income':
                            current_month_income += amount
                        elif t.get('type') == 'expense':
                            current_month_expense += amount
                    elif tx_month == (month - 1 if month > 1 else 12):  # Tháng trước
                        if t.get('type') == 'income':
                            previous_month_income += amount
                        elif t.get('type') == 'expense':
                            previous_month_expense += amount
            except Exception as e:
                print(f"Lỗi parse ngày tháng: {e}")
                continue
        
        balance = current_month_income - current_month_expense
        
        # Tính phần trăm thay đổi
        income_change = ((current_month_income - previous_month_income) / previous_month_income * 100) if previous_month_income > 0 else 0
        expense_change = ((current_month_expense - previous_month_expense) / previous_month_expense * 100) if previous_month_expense > 0 else 0
        
        # Tiết kiệm = tổng thu nhập từ đầu năm - tổng chi tiêu từ đầu năm
        year_income = sum(t.get('amount', 0) for t in all_transactions 
                         if t.get('type') == 'income' and 
                         datetime.datetime.fromisoformat(t['date'].replace('Z', '+00:00')).year == year)
        year_expense = sum(t.get('amount', 0) for t in all_transactions 
                          if t.get('type') == 'expense' and 
                          datetime.datetime.fromisoformat(t['date'].replace('Z', '+00:00')).year == year)
        savings = year_income - year_expense
        
        # Update animated cards with new values
        if len(self.stat_cards) >= 4:
            self.stat_cards[0].set_value(current_month_income)  # Thu nhập
            self.stat_cards[0].update_subtitle(f'{income_change:+.1f}% so với tháng trước')
            self.stat_cards[0].update_trend('↗' if income_change >= 0 else '↘')
            
            self.stat_cards[1].set_value(current_month_expense)  # Chi tiêu
            self.stat_cards[1].update_subtitle(f'{expense_change:+.1f}% so với tháng trước')
            self.stat_cards[1].update_trend('↗' if expense_change >= 0 else '↘')
            
            self.stat_cards[2].set_value(balance)  # Số dư
            self.stat_cards[2].update_subtitle(f'{((balance/current_month_income)*100 if current_month_income > 0 else 0):.1f}% của thu nhập')
            
            self.stat_cards[3].set_value(savings)  # Tiết kiệm
            self.stat_cards[3].update_subtitle(f'{((savings/year_income)*100 if year_income > 0 else 0):.1f}% tích luỹ năm')
        
        print(f"Thống kê tháng {month}/{year}:")
        print(f"Thu nhập: {current_month_income:,.0f} đ ({income_change:+.1f}%)")
        print(f"Chi tiêu: {current_month_expense:,.0f} đ ({expense_change:+.1f}%)")
        print(f"Số dư: {balance:,.0f} đ")
        print(f"Tiết kiệm năm: {savings:,.0f} đ")

    def update_line_chart(self):
        if not hasattr(self, 'line_chart_canvas'):
            return
            
        fig = self.line_chart_canvas.figure
        fig.clear()
        
        ax = fig.add_subplot(111)
        ax.set_facecolor('#fafafa')
        
        # Lấy dữ liệu thực từ transactions
        user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
        if not user_id:
            return
            
        # Đọc dữ liệu từ file
        all_transactions = []
        try:
            import json
            with open('data/transactions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_transactions = [t for t in data if t.get('user_id') == user_id]
        except Exception as e:
            print(f"Lỗi đọc dữ liệu: {e}")
            return
        
        # Chuẩn bị dữ liệu theo tháng (6 tháng gần nhất)
        now = datetime.datetime.now()
        months_data = []
        income_data = []
        expense_data = []
        
        for i in range(6):
            target_month = now.month - i
            target_year = now.year
            if target_month <= 0:
                target_month += 12
                target_year -= 1
                
            month_income = 0
            month_expense = 0
            
            for t in all_transactions:
                try:
                    tx_date = datetime.datetime.fromisoformat(t['date'].replace('Z', '+00:00'))
                    if tx_date.month == target_month and tx_date.year == target_year:
                        amount = t.get('amount', 0)
                        if t.get('type') == 'income':
                            month_income += amount
                        elif t.get('type') == 'expense':
                            month_expense += amount
                except Exception:
                    continue
            
            months_data.append(f"{target_month:02d}/{str(target_year)[2:]}")
            income_data.append(month_income / 1000)  # Chuyển sang nghìn đồng
            expense_data.append(month_expense / 1000)
        
        # Reverse để hiển thị từ cũ đến mới
        months_data.reverse()
        income_data.reverse()
        expense_data.reverse()
        
        ax.plot(months_data, income_data, marker='o', linewidth=3, color='#10b981', label='Thu nhập', markersize=6)
        ax.plot(months_data, expense_data, marker='o', linewidth=3, color='#ef4444', label='Chi tiêu', markersize=6)
        
        ax.set_ylabel('Số tiền (nghìn đ)', fontsize=10, color='#64748b')
        ax.legend(loc='upper left', frameon=False)
        ax.grid(True, linestyle='-', alpha=0.1)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color('#e2e8f0')
        ax.spines['bottom'].set_color('#e2e8f0')
        
        plt.setp(ax.get_xticklabels(), color='#64748b', fontsize=9)
        plt.setp(ax.get_yticklabels(), color='#64748b', fontsize=9)
        
        fig.tight_layout()
        self.line_chart_canvas.draw()

    def update_pie_chart(self):
        if not hasattr(self, 'pie_chart_canvas'):
            return
            
        fig = self.pie_chart_canvas.figure
        fig.clear()
        
        ax = fig.add_subplot(111)
        
        # Lấy dữ liệu thực
        user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
        if not user_id:
            return
            
        # Đọc dữ liệu giao dịch và categories
        all_transactions = []
        categories_map = {}
        
        try:
            import json
            # Đọc transactions
            with open('data/transactions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Lọc giao dịch chi tiêu của user trong tháng hiện tại
                now = datetime.datetime.now()
                for t in data:
                    if (t.get('user_id') == user_id and 
                        t.get('type') == 'expense'):
                        try:
                            tx_date = datetime.datetime.fromisoformat(t['date'].replace('Z', '+00:00'))
                            if tx_date.month == now.month and tx_date.year == now.year:
                                all_transactions.append(t)
                        except Exception:
                            continue
            
            # Đọc categories
            with open('data/categories.json', 'r', encoding='utf-8') as f:
                categories = json.load(f)
                for cat in categories:
                    categories_map[cat.get('category_id')] = {
                        'name': cat.get('name', 'Khác'),
                        'color': cat.get('color', '#6b7280')
                    }
        except Exception as e:
            print(f"Lỗi đọc dữ liệu: {e}")
            return
        
        # Tính toán chi tiêu theo danh mục
        expense_by_category = {}
        colors = []
        
        for t in all_transactions:
            cat_id = t.get('category_id')
            cat_info = categories_map.get(cat_id, {'name': 'Khác', 'color': '#6b7280'})
            cat_name = cat_info['name']
            amount = t.get('amount', 0)
            
            if cat_name in expense_by_category:
                expense_by_category[cat_name] += amount
            else:
                expense_by_category[cat_name] = amount
                colors.append(cat_info['color'])
        
        if not expense_by_category:
            ax.text(0.5, 0.5, 'Không có dữ liệu chi tiêu\ntrong tháng này', 
                   ha='center', va='center', fontsize=12, color='#64748b')
            fig.tight_layout()
            self.pie_chart_canvas.draw()
            return
        
        # Tạo pie chart
        categories = list(expense_by_category.keys())
        values = list(expense_by_category.values())
        
        # Nếu có quá nhiều danh mục, gộp các danh mục nhỏ vào "Khác"
        if len(categories) > 6:
            sorted_items = sorted(zip(categories, values, colors), key=lambda x: x[1], reverse=True)
            top_categories = sorted_items[:5]
            other_total = sum(item[1] for item in sorted_items[5:])
            
            categories = [item[0] for item in top_categories] + ['Khác']
            values = [item[1] for item in top_categories] + [other_total]
            colors = [item[2] for item in top_categories] + ['#6b7280']
        
        wedges, texts, autotexts = ax.pie(values, labels=categories, autopct='%1.0f%%', 
                                         colors=colors, startangle=90, pctdistance=0.85)
        
        # Style the text
        for text in texts:
            text.set_fontsize(9)
            text.set_color('#64748b')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(8)
            autotext.set_fontweight('bold')
        
        # Create donut chart
        centre_circle = plt.Circle((0, 0), 0.60, fc='white')
        ax.add_artist(centre_circle)
        
        ax.axis('equal')
        fig.tight_layout()
        self.pie_chart_canvas.draw()

    def update_transactions_table(self):
        if not hasattr(self, 'transactions_table'):
            return
            
        user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
        if not user_id:
            return
            
        # Đọc dữ liệu thực
        all_transactions = []
        categories_map = {}
        
        try:
            import json
            # Đọc transactions
            with open('data/transactions.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_transactions = [t for t in data if t.get('user_id') == user_id]
            
            # Đọc categories
            with open('data/categories.json', 'r', encoding='utf-8') as f:
                categories = json.load(f)
                for cat in categories:
                    categories_map[cat.get('category_id')] = cat.get('name', 'Khác')
        except Exception as e:
            print(f"Lỗi đọc dữ liệu: {e}")
            return
        
        # Sắp xếp giao dịch theo ngày mới nhất
        all_transactions.sort(key=lambda t: t.get('date', ''), reverse=True)
        recent_tx = all_transactions[:10]  # Lấy 10 giao dịch gần nhất
        
        self.transactions_table.setRowCount(len(recent_tx))
        
        for i, t in enumerate(recent_tx):
            # Ngày tháng
            try:
                tx_date = datetime.datetime.fromisoformat(t['date'].replace('Z', '+00:00'))
                date_str = tx_date.strftime('%d/%m/%Y')
            except Exception:
                date_str = t.get('date', '')
            self.transactions_table.setItem(i, 0, QTableWidgetItem(date_str))
            
            # Type với colored indicator
            tx_type = t.get('type', 'expense')
            type_text = '● Chi tiêu' if tx_type == 'expense' else '● Thu nhập'
            type_item = QTableWidgetItem(type_text)
            type_item.setForeground(QColor('#ef4444' if tx_type == 'expense' else '#10b981'))
            self.transactions_table.setItem(i, 1, type_item)
            
            # Danh mục
            cat_name = categories_map.get(t.get('category_id'), 'Khác')
            self.transactions_table.setItem(i, 2, QTableWidgetItem(cat_name))
            
            # Số tiền với màu sắc
            amount = t.get('amount', 0)
            amount_item = QTableWidgetItem(f"{amount:,.0f} đ")
            amount_item.setForeground(QColor('#10b981' if tx_type == 'income' else '#ef4444'))
            self.transactions_table.setItem(i, 3, amount_item)
            
            # Ghi chú
            note = t.get('description', t.get('note', ''))
            self.transactions_table.setItem(i, 4, QTableWidgetItem(note))
            
            # Action buttons
            action_item = QTableWidgetItem('✏️ 🗑️')
            self.transactions_table.setItem(i, 5, action_item)    
            
    def switch_tab(self, index):
        self.content_stack.setCurrentIndex(index)
        
        # Update button styles with consistent design
        for i, btn in enumerate(self.menu_buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding-left: 20px;
                        border: none;
                        border-radius: 8px;
                        background: #f0f9ff;
                        color: #0369a1;
                        margin: 2px 12px;
                        font-weight: 600;
                        border-left: 3px solid #3b82f6;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding-left: 20px;
                        border: none;
                        border-radius: 8px;
                        background: transparent;
                        color: #64748b;
                        margin: 2px 12px;
                        font-weight: 500;
                    }
                    QPushButton:hover {
                        background: #f8fafc;
                        color: #1e293b;
                        border-left: 3px solid #e2e8f0;
                    }
                """)

    def connect_tab_signals(self):
        """Kết nối signals giữa các tab"""
        # Khi thêm giao dịch thành công -> cập nhật dashboard và history
        if hasattr(self.transaction_form, 'transaction_added'):
            self.transaction_form.transaction_added.connect(self.on_transaction_changed)
        
        # Khi xóa giao dịch -> cập nhật dashboard
        if hasattr(self.transaction_history, 'transaction_deleted'):
            self.transaction_history.transaction_deleted.connect(self.on_transaction_changed)
        
        # Khi click edit giao dịch từ history -> chuyển sang form edit
        if hasattr(self.transaction_history, 'edit_transaction'):
            self.transaction_history.edit_transaction.connect(self.on_edit_transaction)
    
    def on_transaction_changed(self):
        """Xử lý khi có thay đổi giao dịch"""
        # Cập nhật dashboard
        self.update_dashboard()
        
        # Reload history
        if hasattr(self.transaction_history, 'reload_data'):
            self.transaction_history.reload_data()
        
        # Reload reports nếu có
        if hasattr(self.report_tab, 'reload_data'):
            self.report_tab.reload_data()
    
    def on_edit_transaction(self, transaction):
        """Xử lý khi edit giao dịch từ history"""
        # Chuyển sang tab transaction form
        self.switch_tab(1)
        
        # Set data cho form edit
        if hasattr(self.transaction_form, 'set_transaction_for_edit'):
            self.transaction_form.set_transaction_for_edit(transaction)

    def reload_categories(self):
        # Callback để reload category ở các tab khác khi có thay đổi
        if hasattr(self.transaction_form, 'reload_categories'):
            self.transaction_form.reload_categories()
        if hasattr(self.transaction_history, 'load_categories'):
            self.transaction_history.load_categories()
        if hasattr(self.report_tab, 'reload_categories'):
            self.report_tab.reload_categories()
        self.update_dashboard()

    def _on_add_transaction(self):
        self.switch_tab(1)  # Switch to transaction form

    def show_user_profile(self):
        """Hiển thị dialog thông tin cá nhân của user"""
        try:
            from .user_profile import UserProfile
            
            profile_dialog = UserProfile(self.user_manager, self)
            
            # Connect signals
            profile_dialog.profile_updated.connect(self.on_profile_updated)
            profile_dialog.logout_requested.connect(self.on_logout_requested)
            
            profile_dialog.exec_()
        except Exception as e:
            print(f"Error showing user profile: {e}")
    
    def show_notifications(self):
        """Hiển thị trung tâm thông báo"""
        try:
            from .user_notifications import NotificationCenter
            
            notification_center = NotificationCenter(self.user_manager, self)
            notification_center.show()
        except Exception as e:
            print(f"Error showing notifications: {e}")
    
    def show_welcome_toast(self):
        """Hiển thị thông báo chào mừng khi đăng nhập"""
        try:
            from .user_notifications import show_welcome_message
            
            if self.current_user:
                show_welcome_message(self.current_user, self)
        except Exception as e:
            print(f"Error showing welcome toast: {e}")
            
    def on_profile_updated(self):
        """Callback khi profile được cập nhật"""
        # Reload user info và cập nhật hiển thị
        if self.current_user:
            # Reload user from database
            updated_user = self.user_manager.get_user_by_id(self.current_user.get('user_id'))
            if updated_user:
                self.current_user = updated_user
                self.user_manager.current_user = updated_user
                
                # Update display
                user_name = updated_user.get('full_name', updated_user.get('name', updated_user.get('username', 'User')))
                self.user_button.setText(f'👤  {user_name}')
                
                # Show success toast
                from .user_notifications import show_toast                
                show_toast(self, "Thông tin cá nhân đã được cập nhật!", "success")

    def on_logout_requested(self):
        """Callback khi user yêu cầu đăng xuất"""
        self.logout_signal.emit()
    
    def setup_quick_actions(self):
        """Thiết lập quick actions floating button"""
        try:
            from .quick_actions import add_quick_actions_to_widget
            
            self.quick_actions = add_quick_actions_to_widget(self)
            
            # Connect quick actions signals
            self.quick_actions.add_income_requested.connect(lambda: self.on_quick_add_transaction('income'))
            self.quick_actions.add_expense_requested.connect(lambda: self.on_quick_add_transaction('expense'))
            self.quick_actions.view_report_requested.connect(lambda: self.switch_tab(3))
            self.quick_actions.view_budget_requested.connect(lambda: self.switch_tab(4))
            
        except Exception as e:
            print(f"Error setting up quick actions: {e}")
    
    def on_quick_add_transaction(self, transaction_type):
        """Xử lý thêm giao dịch nhanh"""
        # Chuyển sang tab transaction form
        self.switch_tab(1)
        
        # Pre-select transaction type if form supports it
        if hasattr(self.transaction_form, 'set_transaction_type'):
            QTimer.singleShot(100, lambda: self.transaction_form.set_transaction_type(transaction_type))
            
        # Show success toast
        from .user_notifications import show_toast
        type_text = "thu nhập" if transaction_type == 'income' else "chi tiêu"
        show_toast(self, f"Chuyển đến form thêm {type_text}", "info", 2000)
