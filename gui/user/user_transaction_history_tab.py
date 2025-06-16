# Tạo file mới với tên user_transaction_history_tab.py
# Copy nội dung từ user_transaction_history.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
                            QTableWidgetItem, QFrame, QPushButton, QComboBox, QDateEdit,
                            QHeaderView, QAbstractItemView, QLineEdit, QMessageBox,
                            QMenu, QAction)
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from utils.ui_styles import TableStyleHelper, UIStyles
import datetime
import json

class UserTransactionHistory(QWidget):
    
    transaction_deleted = pyqtSignal(str)  # Signal khi xóa giao dịch
    transaction_edited = pyqtSignal(dict)  # Signal khi sửa giao dịch
    
    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.transactions = []  # Danh sách giao dịch hiện tại
        self.current_month = datetime.datetime.now().month
        self.current_year = datetime.datetime.now().year
        self.filter_type = "all"  # Loại lọc: all, income, expense
        self.filter_text = ""  # Văn bản tìm kiếm
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
                    stop: 0 #334155, stop: 1 #1e293b);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("Lịch sử giao dịch")
        title_label.setFont(QFont('Segoe UI', 24, QFont.Bold))
        title_label.setStyleSheet("color: white; margin: 0;")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Xem và quản lý các giao dịch của bạn")
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
        
        # Month/Year selector
        date_layout = QVBoxLayout()
        date_label = QLabel("Tháng/Năm")
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
        
        # Type filter
        type_layout = QVBoxLayout()
        type_label = QLabel("Loại")
        type_label.setFont(QFont('Segoe UI', 12))
        type_layout.addWidget(type_label)
        
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
        type_combo.currentIndexChanged.connect(self.on_type_changed)
        type_layout.addWidget(type_combo)
        filter_layout.addLayout(type_layout)
        
        # Search box
        search_layout = QVBoxLayout()
        search_label = QLabel("Tìm kiếm")
        search_label.setFont(QFont('Segoe UI', 12))
        search_layout.addWidget(search_label)
        
        search_input = QLineEdit()
        search_input.setFont(QFont('Segoe UI', 12))
        search_input.setPlaceholderText("Tìm theo mô tả, danh mục...")
        search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                background: #f9fafb;
            }
        """)
        search_input.textChanged.connect(self.on_search_changed)
        search_layout.addWidget(search_input)
        filter_layout.addLayout(search_layout)
        
        # Export button
        export_button = QPushButton("Xuất CSV")
        export_button.setFont(QFont('Segoe UI', 12))
        export_button.setStyleSheet("""
            QPushButton {
                background: #4b5563;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                margin-top: 22px;
            }
            QPushButton:hover {
                background: #374151;
            }
        """)
        export_button.clicked.connect(self.export_to_csv)
        filter_layout.addWidget(export_button)
        
        layout.addWidget(filter_frame)
        
        # Transactions table
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 0px;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        self.transactions_table = QTableWidget()
        self.transactions_table.setFont(QFont('Segoe UI', 12))
        self.transactions_table.setColumnCount(6)
        self.transactions_table.setHorizontalHeaderLabels(["Ngày", "Mô tả", "Danh mục", "Số tiền", "Loại", "Thao tác"])
        self.transactions_table.verticalHeader().setVisible(False)
        self.transactions_table.setShowGrid(True)
        self.transactions_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.transactions_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.transactions_table.setAlternatingRowColors(True)
        
        # Set column widths
        self.transactions_table.setColumnWidth(0, 120)  # Ngày
        self.transactions_table.setColumnWidth(1, 300)  # Mô tả
        self.transactions_table.setColumnWidth(2, 150)  # Danh mục
        self.transactions_table.setColumnWidth(3, 150)  # Số tiền
        self.transactions_table.setColumnWidth(4, 100)  # Loại
        self.transactions_table.setColumnWidth(5, 100)  # Thao tác
        
        # Apply table styles
        TableStyleHelper.apply_common_table_style(self.transactions_table)
        self.transactions_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.transactions_table.customContextMenuRequested.connect(self.show_context_menu)
        
        table_layout.addWidget(self.transactions_table)
        
        # Summary section
        summary_layout = QHBoxLayout()
        
        self.transaction_count = QLabel("0 giao dịch")
        self.transaction_count.setFont(QFont('Segoe UI', 12))
        summary_layout.addWidget(self.transaction_count)
        
        summary_layout.addStretch()
        
        income_label = QLabel("Thu nhập:")
        income_label.setFont(QFont('Segoe UI', 12))
        summary_layout.addWidget(income_label)
        
        self.income_value = QLabel("0đ")
        self.income_value.setFont(QFont('Segoe UI', 12, QFont.Bold))
        self.income_value.setStyleSheet("color: #10b981;")
        summary_layout.addWidget(self.income_value)
        
        summary_layout.addSpacing(20)
        
        expense_label = QLabel("Chi tiêu:")
        expense_label.setFont(QFont('Segoe UI', 12))
        summary_layout.addWidget(expense_label)
        
        self.expense_value = QLabel("0đ")
        self.expense_value.setFont(QFont('Segoe UI', 12, QFont.Bold))
        self.expense_value.setStyleSheet("color: #ef4444;")
        summary_layout.addWidget(self.expense_value)
        
        summary_layout.addSpacing(20)
        
        balance_label = QLabel("Chênh lệch:")
        balance_label.setFont(QFont('Segoe UI', 12))
        summary_layout.addWidget(balance_label)
        
        self.balance_value = QLabel("0đ")
        self.balance_value.setFont(QFont('Segoe UI', 12, QFont.Bold))
        self.balance_value.setStyleSheet("color: #3b82f6;")
        summary_layout.addWidget(self.balance_value)
        
        table_layout.addLayout(summary_layout)
        
        layout.addWidget(table_frame)
        
        # Store widgets for later access
        self.date_selector = date_selector
        self.type_combo = type_combo
        self.search_input = search_input
        
        # Load initial data
        self.reload_data()
        
    def reload_data(self):
        """Reload transaction data with current filters"""
        # Reset search input
        self.search_input.clear()
        
        # Load transactions
        self.load_transactions()
        
    def load_transactions(self):
        """Load transactions with current filters"""
        try:
            # Get transactions for selected month/year
            transactions = self.transaction_manager.get_transactions_by_month(self.current_year, self.current_month)
            
            # Apply type filter
            if self.filter_type == "income":
                transactions = [t for t in transactions if t.get('type') == 'income']
            elif self.filter_type == "expense":
                transactions = [t for t in transactions if t.get('type') == 'expense']
                
            # Apply text search if any
            if self.filter_text:
                search_text = self.filter_text.lower()
                filtered_transactions = []
                for t in transactions:
                    if (search_text in t.get('description', '').lower() or 
                        search_text in t.get('category', '').lower() or
                        search_text in t.get('notes', '').lower()):
                        filtered_transactions.append(t)
                transactions = filtered_transactions
            
            # Save current list
            self.transactions = transactions
            
            # Update table
            self.update_table()
            
            # Update summary
            self.update_summary()
            
        except Exception as e:
            print(f"Error loading transactions: {e}")
            
    def update_table(self):
        """Update table with current transactions"""
        self.transactions_table.setRowCount(0)
        
        for transaction in self.transactions:
            row_position = self.transactions_table.rowCount()
            self.transactions_table.insertRow(row_position)
            
            # Date
            date_item = QTableWidgetItem(self.format_date(transaction.get('date', '')))
            date_item.setTextAlignment(Qt.AlignCenter)
            self.transactions_table.setItem(row_position, 0, date_item)
            
            # Description
            desc_item = QTableWidgetItem(transaction.get('description', ''))
            self.transactions_table.setItem(row_position, 1, desc_item)
            
            # Category
            category_item = QTableWidgetItem(transaction.get('category', ''))
            self.transactions_table.setItem(row_position, 2, category_item)
            
            # Amount
            amount = transaction.get('amount', 0)
            amount_item = QTableWidgetItem(f"{amount:,.0f}đ")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.transactions_table.setItem(row_position, 3, amount_item)
            
            # Type
            type_text = "Thu nhập" if transaction.get('type') == 'income' else "Chi tiêu"
            type_item = QTableWidgetItem(type_text)
            type_color = QColor("#10b981") if transaction.get('type') == 'income' else QColor("#ef4444")
            type_item.setForeground(type_color)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.transactions_table.setItem(row_position, 4, type_item)
            
            # Actions - just store the ID for now, buttons will be added via setCellWidget
            action_item = QTableWidgetItem(transaction.get('id', ''))
            self.transactions_table.setItem(row_position, 5, action_item)
            
            # Add action buttons
            actions_widget = self.create_actions_widget(transaction.get('id', ''))
            self.transactions_table.setCellWidget(row_position, 5, actions_widget)
            
            # Set row data
            # Store transaction ID in the first column item's data
            date_item.setData(Qt.UserRole, transaction.get('id', ''))
            
            # Color formatting based on type
            if transaction.get('type') == 'income':
                amount_item.setForeground(QColor("#10b981"))
            else:
                amount_item.setForeground(QColor("#ef4444"))
                
    def create_actions_widget(self, transaction_id):
        """Create a widget with action buttons"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(8)
        
        # Edit button
        edit_btn = QPushButton()
        edit_btn.setFixedSize(28, 28)
        edit_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        edit_btn.setText("✏️")
        edit_btn.setToolTip("Chỉnh sửa")
        edit_btn.clicked.connect(lambda: self.edit_transaction(transaction_id))
        layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QPushButton()
        delete_btn.setFixedSize(28, 28)
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        delete_btn.setText("❌")
        delete_btn.setToolTip("Xóa")
        delete_btn.clicked.connect(lambda: self.delete_transaction(transaction_id))
        layout.addWidget(delete_btn)
        
        layout.addStretch()
        
        return widget
        
    def on_date_changed(self, date):
        """Handle date change"""
        self.current_month = date.month()
        self.current_year = date.year()
        self.load_transactions()
        
    def on_type_changed(self, index):
        """Handle type filter change"""
        if index == 0:
            self.filter_type = "all"
        elif index == 1:
            self.filter_type = "income"
        elif index == 2:
            self.filter_type = "expense"
        
        self.load_transactions()
        
    def on_search_changed(self, text):
        """Handle search text change"""
        self.filter_text = text
        self.load_transactions()
    
    def update_summary(self):
        """Update summary values"""
        income_total = sum(t.get('amount', 0) for t in self.transactions if t.get('type') == 'income')
        expense_total = sum(t.get('amount', 0) for t in self.transactions if t.get('type') == 'expense')
        balance = income_total - expense_total
        
        self.transaction_count.setText(f"{len(self.transactions)} giao dịch")
        self.income_value.setText(f"{income_total:,.0f}đ")
        self.expense_value.setText(f"{expense_total:,.0f}đ")
        self.balance_value.setText(f"{balance:,.0f}đ")
        
        # Color balance based on value
        if balance >= 0:
            self.balance_value.setStyleSheet("color: #10b981;")
        else:
            self.balance_value.setStyleSheet("color: #ef4444;")
            
    def format_date(self, date_str):
        """Format date string from ISO to display format"""
        try:
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        except:
            return date_str
            
    def edit_transaction(self, transaction_id):
        """Edit a transaction"""
        try:
            # Find the transaction
            transaction = next((t for t in self.transactions if t.get('id') == transaction_id), None)
            
            if not transaction:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy giao dịch.")
                return
                
            # Open edit dialog
            from gui.user.user_transaction_form_tab import UserTransactionForm
            
            # TODO: Implement edit functionality
            QMessageBox.information(self, "Chức năng đang phát triển", 
                                  "Chức năng chỉnh sửa giao dịch đang được phát triển.")
                                  
            # After editing, reload data
            self.load_transactions()
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi chỉnh sửa giao dịch: {str(e)}")
            
    def delete_transaction(self, transaction_id):
        """Delete a transaction"""
        try:
            # Confirm deletion
            confirmation = QMessageBox.question(self, "Xác nhận xóa", 
                                             "Bạn có chắc chắn muốn xóa giao dịch này không?",
                                             QMessageBox.Yes | QMessageBox.No)
                                             
            if confirmation == QMessageBox.Yes:
                # Delete transaction
                success = self.transaction_manager.delete_transaction(transaction_id)
                
                if success:
                    QMessageBox.information(self, "Thành công", "Đã xóa giao dịch thành công.")
                    self.transaction_deleted.emit(transaction_id)
                    self.load_transactions()
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể xóa giao dịch.")
                    
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xóa giao dịch: {str(e)}")
            
    def export_to_csv(self):
        """Export current transactions to CSV"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            import csv
            
            # Ask for save location
            file_path, _ = QFileDialog.getSaveFileName(self, "Lưu file CSV", "", "CSV Files (*.csv)")
            
            if not file_path:
                return
                
            # Add .csv extension if missing
            if not file_path.endswith('.csv'):
                file_path += '.csv'
                
            # Write to CSV
            with open(file_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(["Ngày", "Mô tả", "Danh mục", "Số tiền", "Loại", "Ghi chú"])
                
                # Write data
                for transaction in self.transactions:
                    type_text = "Thu nhập" if transaction.get('type') == 'income' else "Chi tiêu"
                    writer.writerow([
                        self.format_date(transaction.get('date', '')),
                        transaction.get('description', ''),
                        transaction.get('category', ''),
                        transaction.get('amount', 0),
                        type_text,
                        transaction.get('notes', '')
                    ])
                    
            QMessageBox.information(self, "Thành công", f"Đã xuất dữ liệu thành công tới file {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Lỗi khi xuất dữ liệu: {str(e)}")
            
    def show_context_menu(self, position):
        """Show context menu for right-click on table"""
        # Get transaction at clicked position
        row = self.transactions_table.rowAt(position.y())
        
        if row >= 0:
            # Get transaction ID from the first column
            transaction_id = self.transactions_table.item(row, 0).data(Qt.UserRole)
            
            # Create menu
            menu = QMenu(self)
            
            edit_action = QAction("✏️ Chỉnh sửa", self)
            edit_action.triggered.connect(lambda: self.edit_transaction(transaction_id))
            menu.addAction(edit_action)
            
            delete_action = QAction("❌ Xóa", self)
            delete_action.triggered.connect(lambda: self.delete_transaction(transaction_id))
            menu.addAction(delete_action)
            
            menu.exec_(self.transactions_table.mapToGlobal(position))
