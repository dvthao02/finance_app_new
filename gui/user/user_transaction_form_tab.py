# Tạo file mới với tên user_transaction_form_tab.py
# Copy nội dung từ user_transaction_form.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QFrame, QComboBox, QDateEdit, QMessageBox, QCompleter)
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from utils.animated_widgets import pulse_widget, shake_widget
import datetime
import json

class UserTransactionForm(QWidget):
    
    transaction_added = pyqtSignal(dict)  # Signal phát khi thêm giao dịch mới
    
    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.init_ui()
        self.load_categories()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Title
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, 
                    stop: 0 #3b82f6, stop: 1 #06b6d4);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        title_layout = QVBoxLayout(title_frame)
        
        title_label = QLabel("Thêm giao dịch mới")
        title_label.setFont(QFont('Segoe UI', 24, QFont.Bold))
        title_label.setStyleSheet("color: white; margin: 0;")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Nhập thông tin chi tiết cho giao dịch của bạn")
        subtitle_label.setFont(QFont('Segoe UI', 14))
        subtitle_label.setStyleSheet("color: rgba(255,255,255,0.9); margin: 0;")
        title_layout.addWidget(subtitle_label)
        
        layout.addWidget(title_frame)
        
        # Form container
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 25px;
            }
        """)
        form_layout = QVBoxLayout(form_frame)
        form_layout.setSpacing(20)
        
        # Loại giao dịch
        type_label = QLabel("Loại giao dịch")
        type_label.setFont(QFont('Segoe UI', 14, QFont.Medium))
        form_layout.addWidget(type_label)
        
        type_buttons = QHBoxLayout()
        type_buttons.setSpacing(20)
        
        self.income_btn = QPushButton("Thu nhập")
        self.income_btn.setFont(QFont('Segoe UI', 14))
        self.income_btn.setCheckable(True)
        self.income_btn.setChecked(True)
        self.income_btn.setStyleSheet("""
            QPushButton {
                background: #ecfdf5;
                color: #059669;
                border: 1px solid #d1fae5;
                border-radius: 12px;
                padding: 12px 20px;
                font-weight: 600;
            }
            QPushButton:checked {
                background: #059669;
                color: white;
                border-color: #047857;
            }
        """)
        self.income_btn.clicked.connect(self.set_transaction_type)
        type_buttons.addWidget(self.income_btn)
        
        self.expense_btn = QPushButton("Chi tiêu")
        self.expense_btn.setFont(QFont('Segoe UI', 14))
        self.expense_btn.setCheckable(True)
        self.expense_btn.setStyleSheet("""
            QPushButton {
                background: #fee2e2;
                color: #dc2626;
                border: 1px solid #fecaca;
                border-radius: 12px;
                padding: 12px 20px;
                font-weight: 600;
            }
            QPushButton:checked {
                background: #dc2626;
                color: white;
                border-color: #b91c1c;
            }
        """)
        self.expense_btn.clicked.connect(self.set_transaction_type)
        type_buttons.addWidget(self.expense_btn)
        
        type_buttons.addStretch()
        form_layout.addLayout(type_buttons)
        
        # Input grid
        input_grid = QVBoxLayout()
        input_grid.setSpacing(20)
        
        # Tiêu đề / Mô tả
        description_layout = QVBoxLayout()
        description_label = QLabel("Tiêu đề / Mô tả")
        description_label.setFont(QFont('Segoe UI', 14, QFont.Medium))
        description_layout.addWidget(description_label)
        
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Nhập mô tả ngắn gọn...")
        self.description_input.setFont(QFont('Segoe UI', 14))
        self.description_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 12px 16px;
                background: #f9fafb;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: white;
            }
        """)
        description_layout.addWidget(self.description_input)
        input_grid.addLayout(description_layout)
        
        # Số tiền
        amount_layout = QVBoxLayout()
        amount_label = QLabel("Số tiền")
        amount_label.setFont(QFont('Segoe UI', 14, QFont.Medium))
        amount_layout.addWidget(amount_label)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Nhập số tiền...")
        self.amount_input.setFont(QFont('Segoe UI', 14))
        self.amount_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 12px 16px;
                background: #f9fafb;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: white;
            }
        """)
        amount_layout.addWidget(self.amount_input)
        input_grid.addLayout(amount_layout)
        
        # Danh mục
        category_layout = QVBoxLayout()
        category_label = QLabel("Danh mục")
        category_label.setFont(QFont('Segoe UI', 14, QFont.Medium))
        category_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.setFont(QFont('Segoe UI', 14))
        self.category_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 12px 16px;
                background: #f9fafb;
                min-width: 150px;
            }
            QComboBox:focus {
                border-color: #3b82f6;
                background: white;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: #d1d5db;
                border-left-style: solid;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        category_layout.addWidget(self.category_combo)
        input_grid.addLayout(category_layout)
        
        # Ngày
        date_layout = QVBoxLayout()
        date_label = QLabel("Ngày giao dịch")
        date_label.setFont(QFont('Segoe UI', 14, QFont.Medium))
        date_layout.addWidget(date_label)
        
        self.date_input = QDateEdit(QDate.currentDate())
        self.date_input.setFont(QFont('Segoe UI', 14))
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("dd/MM/yyyy")
        self.date_input.setStyleSheet("""
            QDateEdit {
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 12px 16px;
                background: #f9fafb;
            }
            QDateEdit:focus {
                border-color: #3b82f6;
                background: white;
            }
            QDateEdit::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 30px;
                border-left-width: 1px;
                border-left-color: #d1d5db;
                border-left-style: solid;
                border-top-right-radius: 10px;
                border-bottom-right-radius: 10px;
            }
        """)
        date_layout.addWidget(self.date_input)
        input_grid.addLayout(date_layout)
        
        # Ghi chú
        notes_layout = QVBoxLayout()
        notes_label = QLabel("Ghi chú (tùy chọn)")
        notes_label.setFont(QFont('Segoe UI', 14, QFont.Medium))
        notes_layout.addWidget(notes_label)
        
        self.notes_input = QLineEdit()
        self.notes_input.setPlaceholderText("Nhập ghi chú bổ sung...")
        self.notes_input.setFont(QFont('Segoe UI', 14))
        self.notes_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 10px;
                padding: 12px 16px;
                background: #f9fafb;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: white;
            }
        """)
        notes_layout.addWidget(self.notes_input)
        input_grid.addLayout(notes_layout)
        
        form_layout.addLayout(input_grid)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        self.clear_btn = QPushButton("Xóa form")
        self.clear_btn.setFont(QFont('Segoe UI', 14))
        self.clear_btn.setStyleSheet("""
            QPushButton {
                background: #e5e7eb;
                border: none;
                border-radius: 10px;
                padding: 12px 25px;
                color: #4b5563;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #d1d5db;
            }
            QPushButton:pressed {
                background: #9ca3af;
            }
        """)
        self.clear_btn.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.clear_btn)
        
        buttons_layout.addStretch()
        
        self.save_btn = QPushButton("Lưu giao dịch")
        self.save_btn.setFont(QFont('Segoe UI', 14))
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                border: none;
                border-radius: 10px;
                padding: 12px 25px;
                color: white;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #2563eb;
            }
            QPushButton:pressed {
                background: #1d4ed8;
            }
        """)
        self.save_btn.clicked.connect(self.save_transaction)
        buttons_layout.addWidget(self.save_btn)
        
        form_layout.addLayout(buttons_layout)
        
        layout.addWidget(form_frame)
        
        # Tự động hoàn thành mô tả
        self.setup_autocomplete()
        
    def setup_autocomplete(self):
        """Thiết lập tự động hoàn thành cho mô tả"""
        try:
            # Get existing transaction descriptions
            descriptions = []
            transactions = self.transaction_manager.get_all_transactions() 
            if transactions and isinstance(transactions, list):
                descriptions = list(set([t.get('description', '') for t in transactions if t.get('description')]))
            
            completer = QCompleter(descriptions)
            completer.setCaseSensitivity(Qt.CaseInsensitive)
            completer.setFilterMode(Qt.MatchContains)
            self.description_input.setCompleter(completer)
        except Exception as e:
            print(f"Error setting up autocomplete: {e}")
    
    def set_transaction_type(self):
        """Xử lý khi loại giao dịch được chọn"""
        if self.sender() == self.income_btn:
            self.income_btn.setChecked(True)
            self.expense_btn.setChecked(False)
        else:
            self.expense_btn.setChecked(True)
            self.income_btn.setChecked(False)
            
        # Tải lại danh mục
        self.load_categories()
        
    def load_categories(self):
        """Tải danh sách danh mục dựa trên loại giao dịch"""
        try:
            self.category_combo.clear()
            
            # Xác định loại giao dịch
            transaction_type = 'income' if self.income_btn.isChecked() else 'expense'
            
            # Tải danh mục phù hợp với loại giao dịch
            categories = self.category_manager.get_categories_by_type(transaction_type)
            
            if categories:
                for category in categories:
                    self.category_combo.addItem(category.get('name', 'Khác'))
            else:
                # Thêm danh mục mặc định nếu không có
                default_categories = ["Lương", "Thưởng"] if transaction_type == 'income' else ["Ăn uống", "Di chuyển", "Mua sắm"]
                for cat in default_categories:
                    self.category_combo.addItem(cat)
                    
        except Exception as e:
            print(f"Error loading categories: {e}")
    
    def clear_form(self):
        """Xóa form về trạng thái ban đầu"""
        self.description_input.clear()
        self.amount_input.clear()
        self.notes_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.income_btn.setChecked(True)
        self.expense_btn.setChecked(False)
        self.load_categories()
    
    def save_transaction(self):
        """Lưu giao dịch mới"""
        try:
            # Validate inputs
            description = self.description_input.text().strip()
            if not description:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập mô tả cho giao dịch")
                return
                
            # Parse amount
            amount_text = self.amount_input.text().strip()
            if not amount_text:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập số tiền")
                return
                
            try:
                # Convert to number and handle different formats
                amount_text = amount_text.replace(',', '')
                amount_text = amount_text.replace('.', '')
                amount = float(amount_text)
            except ValueError:
                QMessageBox.warning(self, "Lỗi", "Số tiền không hợp lệ")
                return
                
            if amount <= 0:
                QMessageBox.warning(self, "Lỗi", "Số tiền phải lớn hơn 0")
                return
            
            # Get other fields
            category = self.category_combo.currentText()
            transaction_type = 'income' if self.income_btn.isChecked() else 'expense'
            transaction_date = self.date_input.date().toString("yyyy-MM-dd")
            notes = self.notes_input.text().strip()
            
            # Create transaction
            transaction = {
                'description': description,
                'amount': amount,
                'type': transaction_type,
                'category': category,
                'date': transaction_date,
                'notes': notes,
                'created_at': datetime.datetime.now().isoformat(),
                'user_id': self.user_manager.current_user.get('id') if self.user_manager.current_user else None
            }
              # Save transaction
            success = self.transaction_manager.add_transaction(transaction)
            
            if success:
                # Animated success feedback
                self.show_success_animation()
                QMessageBox.information(self, "Thành công", "Đã lưu giao dịch thành công")
                self.transaction_added.emit(transaction)
                self.clear_form()
                self.setup_autocomplete()  # Update autocomplete with new entry
            else:
                # Shake animation for error
                shake_widget(self.save_btn)
                QMessageBox.warning(self, "Lỗi", "Không thể lưu giao dịch, vui lòng thử lại")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {str(e)}")
            print(f"Error saving transaction: {e}")
    
    def show_success_animation(self):
        """Show animated success feedback"""
        try:
            # Pulse the save button with green color
            pulse_widget(self.save_btn, "#10b981", 800)
            
            # Also pulse the form container
            pulse_widget(self, "#10b981", 1200)
            
        except Exception as e:
            print(f"Error in success animation: {e}")
