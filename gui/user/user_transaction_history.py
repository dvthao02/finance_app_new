from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QPushButton, QLineEdit, 
                            QComboBox, QDateEdit, QFrame, QMessageBox, QMenu,
                            QAbstractItemView, QGridLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import QDate, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QBrush, QPixmap, QPainter
import datetime
import json

class UserTransactionHistory(QWidget):
    """
    Màn hình lịch sử giao dịch với tính năng tìm kiếm, filter và quản lý giao dịch
    """
    edit_transaction = pyqtSignal(dict)  # Signal để edit giao dịch
    transaction_deleted = pyqtSignal()   # Signal khi xóa giao dịch
    
    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.all_transactions = []
        self.filtered_transactions = []
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
                    stop:0 #4f46e5, stop:1 #7c3aed);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        header_layout = QVBoxLayout()
        
        title = QLabel('📊 Lịch sử giao dịch')
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        subtitle = QLabel('Quản lý và theo dõi tất cả giao dịch của bạn')
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
        
        # Filter section
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 20px;
            }
        """)
        
        filter_layout = QGridLayout()
        filter_layout.setSpacing(15)
        
        # Styles cho filter controls
        filter_control_style = """
            QLineEdit, QComboBox, QDateEdit {
                padding: 10px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 13px;
                background-color: #f8fafc;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #4f46e5;
                background-color: white;
            }
        """
        
        # Search box
        search_label = QLabel('🔍 Tìm kiếm:')
        search_label.setStyleSheet("font-weight: 600; color: #374151;")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('Tìm theo ghi chú, số tiền...')
        self.search_input.setStyleSheet(filter_control_style)
        self.search_input.textChanged.connect(self.apply_filters)
        
        # Type filter
        type_label = QLabel('💰 Loại:')
        type_label.setStyleSheet("font-weight: 600; color: #374151;")
        self.type_filter = QComboBox()
        self.type_filter.addItems(['Tất cả', 'Thu nhập', 'Chi tiêu'])
        self.type_filter.setStyleSheet(filter_control_style)
        self.type_filter.currentTextChanged.connect(self.apply_filters)
        
        # Category filter
        category_label = QLabel('🏷️ Danh mục:')
        category_label.setStyleSheet("font-weight: 600; color: #374151;")
        self.category_filter = QComboBox()
        self.category_filter.setStyleSheet(filter_control_style)
        self.category_filter.currentTextChanged.connect(self.apply_filters)
        
        # Date range
        date_from_label = QLabel('📅 Từ ngày:')
        date_from_label.setStyleSheet("font-weight: 600; color: #374151;")
        self.date_from = QDateEdit(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setDisplayFormat('dd/MM/yyyy')
        self.date_from.setStyleSheet(filter_control_style)
        self.date_from.dateChanged.connect(self.apply_filters)
        
        date_to_label = QLabel('📅 Đến ngày:')
        date_to_label.setStyleSheet("font-weight: 600; color: #374151;")
        self.date_to = QDateEdit(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setDisplayFormat('dd/MM/yyyy')
        self.date_to.setStyleSheet(filter_control_style)
        self.date_to.dateChanged.connect(self.apply_filters)
        
        # Layout filter controls
        filter_layout.addWidget(search_label, 0, 0)
        filter_layout.addWidget(self.search_input, 1, 0, 1, 2)
        
        filter_layout.addWidget(type_label, 0, 2)
        filter_layout.addWidget(self.type_filter, 1, 2)
        
        filter_layout.addWidget(category_label, 0, 3)
        filter_layout.addWidget(self.category_filter, 1, 3)
        
        filter_layout.addWidget(date_from_label, 2, 0)
        filter_layout.addWidget(self.date_from, 3, 0)
        
        filter_layout.addWidget(date_to_label, 2, 1)
        filter_layout.addWidget(self.date_to, 3, 1)
        
        # Clear filter button
        btn_clear = QPushButton('🗑️ Xóa bộ lọc')
        btn_clear.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        btn_clear.clicked.connect(self.clear_filters)
        filter_layout.addWidget(btn_clear, 3, 2, 1, 2)
        
        filter_frame.setLayout(filter_layout)
        layout.addWidget(filter_frame)
        
        # Table
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
        
        # Table header with summary
        table_header = QHBoxLayout()
        self.summary_label = QLabel('📋 Hiển thị 0 giao dịch')
        self.summary_label.setStyleSheet("""
            font-weight: 600;
            color: #374151;
            font-size: 16px;
        """)
        
        btn_export = QPushButton('📤 Xuất Excel')
        btn_export.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: 600;
                font-size: 13px;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        btn_export.clicked.connect(self.export_to_excel)
        
        table_header.addWidget(self.summary_label)
        table_header.addStretch()
        table_header.addWidget(btn_export)
        
        table_layout.addLayout(table_header)
        
        # Main table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            '📅 Ngày', '💰 Loại', '🏷️ Danh mục', '💵 Số tiền', 
            '📝 Ghi chú', '👛 Ví', '⚙️ Thao tác'
        ])
        
        # Table styling
        self.table.setStyleSheet("""
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
        
        # Table properties
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        
        # Set minimum column widths
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Ngày
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Loại
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Số tiền
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Thao tác
        
        table_layout.addWidget(self.table)
        table_frame.setLayout(table_layout)
        layout.addWidget(table_frame)
        
        self.setLayout(layout)
        
        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #f1f5f9;
            }
        """)    
        
    def load_data(self):
        """Tải dữ liệu giao dịch từ file JSON"""
        try:
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            if not user_id:
                return
            
            # Load transactions
            with open('data/transactions.json', 'r', encoding='utf-8') as f:
                all_transactions = json.load(f)
            
            # Filter by user
            self.all_transactions = [t for t in all_transactions if t.get('user_id') == user_id]
            
            # Load categories for filter
            self.load_categories()
            
            # Apply initial filters
            self.apply_filters()
            
        except Exception as e:
            print(f"Lỗi tải dữ liệu: {e}")
            self.all_transactions = []
            self.filtered_transactions = []
    
    def load_categories(self):
        """Tải danh mục cho filter"""
        try:
            with open('data/categories.json', 'r', encoding='utf-8') as f:
                all_categories = json.load(f)
            
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            
            # Filter categories by user
            user_categories = []
            for cat in all_categories:
                if cat.get('user_id') is None or cat.get('user_id') == user_id:
                    user_categories.append(cat)
            
            # Populate category filter
            self.category_filter.clear()
            self.category_filter.addItem('Tất cả danh mục', None)
            
            for cat in user_categories:
                name = cat.get('name', 'Không tên')
                cat_id = cat.get('id') or cat.get('category_id')
                self.category_filter.addItem(name, cat_id)
                
        except Exception as e:
            print(f"Lỗi tải danh mục: {e}")
    
    def apply_filters(self):
        """Áp dụng bộ lọc và cập nhật bảng"""
        if not self.all_transactions:
            self.filtered_transactions = []
            self.update_table()
            return
        
        filtered = self.all_transactions.copy()
        
        # Filter by search text
        search_text = self.search_input.text().lower().strip()
        if search_text:
            filtered = [t for t in filtered if 
                       search_text in t.get('note', '').lower() or 
                       search_text in str(t.get('amount', 0)) or
                       search_text in t.get('date', '').lower()]
        
        # Filter by type
        type_filter = self.type_filter.currentText()
        if type_filter == 'Thu nhập':
            filtered = [t for t in filtered if t.get('type') == 'income']
        elif type_filter == 'Chi tiêu':
            filtered = [t for t in filtered if t.get('type') == 'expense']
        
        # Filter by category
        cat_id = self.category_filter.currentData()
        if cat_id:
            filtered = [t for t in filtered if t.get('category_id') == cat_id]
        
        # Filter by date range
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()
        
        def parse_date(date_str):
            try:
                if 'T' in date_str:
                    date_str = date_str.split('T')[0]
                return datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except:
                return None
        
        filtered = [t for t in filtered 
                   if date_from <= parse_date(t.get('date', '')) <= date_to]
        
        self.filtered_transactions = filtered
        self.update_table()
    
    def update_table(self):
        """Cập nhật bảng với dữ liệu đã lọc"""
        self.table.setRowCount(len(self.filtered_transactions))
        
        # Load categories mapping
        try:
            with open('data/categories.json', 'r', encoding='utf-8') as f:
                all_categories = json.load(f)
            categories_map = {cat.get('id') or cat.get('category_id'): cat.get('name', 'Khác') 
                            for cat in all_categories}
        except:
            categories_map = {}
        
        # Sort by date (newest first)
        sorted_transactions = sorted(self.filtered_transactions, 
                                   key=lambda x: x.get('date', ''), reverse=True)
        
        total_income = 0
        total_expense = 0
        
        for i, transaction in enumerate(sorted_transactions):
            # Date
            date_str = transaction.get('date', '')
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            try:
                formatted_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').strftime('%d/%m/%Y')
            except:
                formatted_date = date_str
            
            date_item = QTableWidgetItem(formatted_date)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 0, date_item)
            
            # Type with icon and color
            tx_type = transaction.get('type', 'expense')
            if tx_type == 'income':
                type_item = QTableWidgetItem('📈 Thu nhập')
                type_item.setBackground(QBrush(QColor('#dcfce7')))
                type_item.setForeground(QBrush(QColor('#166534')))
                total_income += transaction.get('amount', 0)
            else:
                type_item = QTableWidgetItem('📉 Chi tiêu')
                type_item.setBackground(QBrush(QColor('#fee2e2')))
                type_item.setForeground(QBrush(QColor('#991b1b')))
                total_expense += transaction.get('amount', 0)
            
            type_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 1, type_item)
            
            # Category
            cat_id = transaction.get('category_id')
            cat_name = categories_map.get(cat_id, 'Khác')
            cat_item = QTableWidgetItem(cat_name)
            self.table.setItem(i, 2, cat_item)
            
            # Amount with formatting
            amount = transaction.get('amount', 0)
            amount_text = f"{amount:,.0f} đ"
            amount_item = QTableWidgetItem(amount_text)
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Color based on type
            if tx_type == 'income':
                amount_item.setForeground(QBrush(QColor('#059669')))
            else:
                amount_item.setForeground(QBrush(QColor('#dc2626')))
            
            self.table.setItem(i, 3, amount_item)
            
            # Note
            note = transaction.get('note', '')
            note_item = QTableWidgetItem(note if len(note) <= 50 else note[:47] + '...')
            self.table.setItem(i, 4, note_item)
            
            # Wallet
            wallet_item = QTableWidgetItem('💳 Ví mặc định')
            wallet_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(i, 5, wallet_item)
            
            # Action buttons
            self.create_action_buttons(i, transaction)
        
        # Update summary
        self.update_summary(len(sorted_transactions), total_income, total_expense)
    
    def create_action_buttons(self, row, transaction):
        """Tạo nút thao tác cho mỗi dòng"""
        actions_widget = QWidget()
        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(5, 2, 5, 2)
        actions_layout.setSpacing(5)
        
        # Edit button
        btn_edit = QPushButton('✏️')
        btn_edit.setToolTip('Chỉnh sửa giao dịch')
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
        btn_edit.clicked.connect(lambda: self.edit_transaction_clicked(transaction))
        
        # Delete button
        btn_delete = QPushButton('🗑️')
        btn_delete.setToolTip('Xóa giao dịch')
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
        btn_delete.clicked.connect(lambda: self.delete_transaction_clicked(transaction))
        
        actions_layout.addWidget(btn_edit)
        actions_layout.addWidget(btn_delete)
        actions_layout.addStretch()
        
        actions_widget.setLayout(actions_layout)
        self.table.setCellWidget(row, 6, actions_widget)
    
    def update_summary(self, count, total_income, total_expense):
        """Cập nhật thông tin tổng quan"""
        balance = total_income - total_expense
        balance_text = f"+{balance:,.0f} đ" if balance >= 0 else f"{balance:,.0f} đ"
        
        summary_text = (f"📋 Hiển thị {count} giao dịch | "
                       f"📈 Thu: {total_income:,.0f} đ | "
                       f"📉 Chi: {total_expense:,.0f} đ | "
                       f"💰 Chênh lệch: {balance_text}")
        
        self.summary_label.setText(summary_text)
    
    def clear_filters(self):
        """Xóa tất cả bộ lọc"""
        self.search_input.clear()
        self.type_filter.setCurrentIndex(0)
        self.category_filter.setCurrentIndex(0)
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_to.setDate(QDate.currentDate())
        self.apply_filters()
    
    def edit_transaction_clicked(self, transaction):
        """Xử lý khi click nút sửa"""
        self.edit_transaction.emit(transaction)
    
    def delete_transaction_clicked(self, transaction):
        """Xử lý khi click nút xóa"""
        reply = QMessageBox.question(self, '❓ Xác nhận xóa',
                                   f'Bạn có chắc muốn xóa giao dịch này?\n\n'
                                   f'💰 Số tiền: {transaction.get("amount", 0):,.0f} đ\n'
                                   f'📅 Ngày: {transaction.get("date", "")}\n'
                                   f'📝 Ghi chú: {transaction.get("note", "")}',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.delete_transaction(transaction)
    
    def delete_transaction(self, transaction):
        """Xóa giao dịch khỏi database"""
        try:
            # Load all transactions
            with open('data/transactions.json', 'r', encoding='utf-8') as f:
                all_transactions = json.load(f)
            
            # Remove the transaction
            tx_id = transaction.get('id')
            all_transactions = [t for t in all_transactions if t.get('id') != tx_id]
            
            # Save back to file
            with open('data/transactions.json', 'w', encoding='utf-8') as f:
                json.dump(all_transactions, f, ensure_ascii=False, indent=2)
            
            # Update manager if exists
            if hasattr(self.transaction_manager, 'transactions'):
                self.transaction_manager.transactions = all_transactions
            
            QMessageBox.information(self, '✅ Thành công', 'Đã xóa giao dịch thành công!')
            
            # Reload data
            self.load_data()
            
            # Emit signal
            self.transaction_deleted.emit()
            
        except Exception as e:
            QMessageBox.critical(self, '❌ Lỗi', f'Không thể xóa giao dịch:\n{str(e)}')
    
    def export_to_excel(self):
        """Xuất dữ liệu ra file Excel"""
        try:
            import pandas as pd
            from PyQt5.QtWidgets import QFileDialog
            
            if not self.filtered_transactions:
                QMessageBox.warning(self, '⚠️ Cảnh báo', 'Không có dữ liệu để xuất!')
                return
            
            # Prepare data for export
            export_data = []
            
            # Load categories
            try:
                with open('data/categories.json', 'r', encoding='utf-8') as f:
                    all_categories = json.load(f)
                categories_map = {cat.get('id') or cat.get('category_id'): cat.get('name', 'Khác') 
                                for cat in all_categories}
            except:
                categories_map = {}
            
            for tx in sorted(self.filtered_transactions, key=lambda x: x.get('date', '')):
                # Format date
                date_str = tx.get('date', '')
                if 'T' in date_str:
                    date_str = date_str.split('T')[0]
                
                export_data.append({
                    'Ngày': date_str,
                    'Loại': 'Thu nhập' if tx.get('type') == 'income' else 'Chi tiêu',
                    'Danh mục': categories_map.get(tx.get('category_id'), 'Khác'),
                    'Số tiền': tx.get('amount', 0),
                    'Ghi chú': tx.get('note', ''),
                    'Ví': 'Ví mặc định'
                })
            
            # Create DataFrame
            df = pd.DataFrame(export_data)
            
            # File dialog
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'Xuất file Excel', 
                f'giao_dich_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
                'Excel files (*.xlsx)'
            )
            
            if file_path:
                df.to_excel(file_path, index=False, engine='openpyxl')
                QMessageBox.information(self, '✅ Thành công', 
                                      f'Đã xuất {len(export_data)} giao dịch ra file:\n{file_path}')
        
        except ImportError:
            QMessageBox.warning(self, '⚠️ Thiếu thư viện', 
                              'Cần cài đặt pandas và openpyxl để xuất Excel:\n'
                              'pip install pandas openpyxl')
        except Exception as e:
            QMessageBox.critical(self, '❌ Lỗi', f'Không thể xuất file:\n{str(e)}')
    
    def reload_data(self):
        """Reload dữ liệu từ bên ngoài"""
        self.load_data()
