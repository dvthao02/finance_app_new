# Copy nội dung từ user_budget.py sang user_budget_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QLineEdit, QFrame, QComboBox, QMessageBox, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QAbstractItemView, QProgressBar)
from PyQt5.QtGui import QFont, QIcon, QColor
from PyQt5.QtCore import Qt, pyqtSignal
import datetime
import json

class UserBudget(QWidget):
    
    budget_updated = pyqtSignal(dict)  # Signal khi cập nhật ngân sách
    
    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.budgets = []
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
                    stop: 0 #84cc16, stop: 1 #10b981);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        header_layout = QVBoxLayout(header_frame)
        
        title_label = QLabel("Ngân sách")
        title_label.setFont(QFont('Segoe UI', 24, QFont.Bold))
        title_label.setStyleSheet("color: white; margin: 0;")
        header_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Thiết lập và theo dõi ngân sách của bạn")
        subtitle_label.setFont(QFont('Segoe UI', 14))
        subtitle_label.setStyleSheet("color: rgba(255,255,255,0.9); margin: 0;")
        header_layout.addWidget(subtitle_label)
        
        layout.addWidget(header_frame)
        
        # Create new budget section
        new_budget_frame = QFrame()
        new_budget_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 20px;
            }
        """)
        new_budget_layout = QVBoxLayout(new_budget_frame)
        
        # Title
        new_budget_title = QLabel("Tạo ngân sách mới")
        new_budget_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        new_budget_layout.addWidget(new_budget_title)
        
        # Form layout
        form_layout = QHBoxLayout()
        form_layout.setSpacing(15)
        
        # Category
        category_layout = QVBoxLayout()
        category_label = QLabel("Danh mục")
        category_label.setFont(QFont('Segoe UI', 12))
        category_layout.addWidget(category_label)
        
        self.category_combo = QComboBox()
        self.category_combo.setFont(QFont('Segoe UI', 12))
        self.category_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                background: #f9fafb;
            }
        """)
        category_layout.addWidget(self.category_combo)
        form_layout.addLayout(category_layout)
        
        # Amount
        amount_layout = QVBoxLayout()
        amount_label = QLabel("Giới hạn chi tiêu")
        amount_label.setFont(QFont('Segoe UI', 12))
        amount_layout.addWidget(amount_label)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Nhập số tiền...")
        self.amount_input.setFont(QFont('Segoe UI', 12))
        self.amount_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                background: #f9fafb;
            }
        """)
        amount_layout.addWidget(self.amount_input)
        form_layout.addLayout(amount_layout)
        
        # Note
        note_layout = QVBoxLayout()
        note_label = QLabel("Ghi chú (tùy chọn)")
        note_label.setFont(QFont('Segoe UI', 12))
        note_layout.addWidget(note_label)
        
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Nhập ghi chú...")
        self.note_input.setFont(QFont('Segoe UI', 12))
        self.note_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                padding: 8px 12px;
                background: #f9fafb;
            }
        """)
        note_layout.addWidget(self.note_input)
        form_layout.addLayout(note_layout)
        
        # Save button
        self.save_btn = QPushButton("Lưu ngân sách")
        self.save_btn.setFont(QFont('Segoe UI', 12, QFont.Bold))
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #84cc16;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                color: white;
                margin-top: 22px;
            }
            QPushButton:hover {
                background: #65a30d;
            }
        """)
        self.save_btn.clicked.connect(self.save_budget)
        form_layout.addWidget(self.save_btn)
        
        new_budget_layout.addLayout(form_layout)
        layout.addWidget(new_budget_frame)
        
        # Budget list section
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
                padding: 20px;
            }
        """)
        list_layout = QVBoxLayout(list_frame)
        
        # Title
        list_title = QLabel("Ngân sách hiện tại (tháng này)")
        list_title.setFont(QFont('Segoe UI', 16, QFont.Bold))
        list_layout.addWidget(list_title)
        
        # Budgets table
        self.budget_table = QTableWidget()
        self.budget_table.setFont(QFont('Segoe UI', 12))
        self.budget_table.setColumnCount(5)
        self.budget_table.setHorizontalHeaderLabels(["Danh mục", "Giới hạn", "Đã chi tiêu", "Còn lại", "Tiến độ"])
        self.budget_table.verticalHeader().setVisible(False)
        self.budget_table.setShowGrid(True)
        self.budget_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.budget_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # Set column widths
        self.budget_table.setColumnWidth(0, 200)  # Danh mục
        self.budget_table.setColumnWidth(1, 150)  # Giới hạn
        self.budget_table.setColumnWidth(2, 150)  # Đã chi tiêu
        self.budget_table.setColumnWidth(3, 150)  # Còn lại
        self.budget_table.setColumnWidth(4, 300)  # Tiến độ
        
        # Apply table styles
        self.budget_table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #e5e7eb;
                selection-background-color: #dbeafe;
            }
            QHeaderView::section {
                background-color: #f9fafb;
                border: none;
                border-bottom: 1px solid #e5e7eb;
                padding: 10px;
                font-weight: bold;
                color: #4b5563;
            }
            QTableWidget::item {
                border-bottom: 1px solid #f3f4f6;
                padding: 10px;
            }
        """)
        
        self.budget_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
        self.budget_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Interactive)
        self.budget_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self.budget_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Interactive)
        self.budget_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        
        list_layout.addWidget(self.budget_table)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("Làm mới")
        refresh_btn.setFont(QFont('Segoe UI', 12))
        refresh_btn.setStyleSheet("""
            QPushButton {
                background: #f3f4f6;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                color: #4b5563;
            }
            QPushButton:hover {
                background: #e5e7eb;
            }
        """)
        refresh_btn.clicked.connect(self.load_data)
        buttons_layout.addWidget(refresh_btn)
        
        # Delete button
        delete_btn = QPushButton("Xóa ngân sách")
        delete_btn.setFont(QFont('Segoe UI', 12))
        delete_btn.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                color: white;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        delete_btn.clicked.connect(self.delete_budget)
        buttons_layout.addWidget(delete_btn)
        
        list_layout.addLayout(buttons_layout)
        
        layout.addWidget(list_frame)
        
        # Load initial data
        self.load_categories()
        self.load_data()
        
    def load_categories(self):
        """Load categories for expense"""
        try:
            self.category_combo.clear()
            
            # Get expense categories
            categories = self.category_manager.get_categories_by_type('expense')
            
            if categories:
                for category in categories:
                    self.category_combo.addItem(category.get('name', 'Khác'))
            else:
                # Add default categories if none exist
                default_categories = ["Ăn uống", "Di chuyển", "Mua sắm", "Giải trí", "Hóa đơn", "Khác"]
                for cat in default_categories:
                    self.category_combo.addItem(cat)
                    
        except Exception as e:
            print(f"Error loading categories: {e}")
            
    def load_data(self):
        """Load budget data"""
        try:
            # Get current month and year
            current_month = datetime.datetime.now().month
            current_year = datetime.datetime.now().year
            
            # Get budgets for the current month/year
            from data_manager.budget_manager import BudgetManager
            budget_manager = BudgetManager()
            
            self.budgets = budget_manager.get_budgets_by_month(current_year, current_month)
            
            # Get transactions for the current month/year
            transactions = self.transaction_manager.get_transactions_by_month(current_year, current_month)
            expense_transactions = [t for t in transactions if t.get('type') == 'expense']
            
            # Calculate spending by category
            spending_by_category = {}
            for t in expense_transactions:
                category = t.get('category', 'Khác')
                spending_by_category[category] = spending_by_category.get(category, 0) + t.get('amount', 0)
                
            # Clear table
            self.budget_table.setRowCount(0)
            
            # Populate table
            for budget in self.budgets:
                row_position = self.budget_table.rowCount()
                self.budget_table.insertRow(row_position)
                
                # Category
                category = budget.get('category', 'Khác')
                category_item = QTableWidgetItem(category)
                self.budget_table.setItem(row_position, 0, category_item)
                
                # Limit
                limit = budget.get('limit', 0)
                limit_item = QTableWidgetItem(f"{limit:,.0f}đ")
                limit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.budget_table.setItem(row_position, 1, limit_item)
                
                # Spent
                spent = spending_by_category.get(category, 0)
                spent_item = QTableWidgetItem(f"{spent:,.0f}đ")
                spent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self.budget_table.setItem(row_position, 2, spent_item)
                
                # Remaining
                remaining = limit - spent
                remaining_item = QTableWidgetItem(f"{remaining:,.0f}đ")
                remaining_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                
                # Color based on remaining amount
                if remaining < 0:
                    remaining_item.setForeground(QColor("#ef4444"))  # Red
                else:
                    remaining_item.setForeground(QColor("#10b981"))  # Green
                    
                self.budget_table.setItem(row_position, 3, remaining_item)
                
                # Progress
                progress_widget = QWidget()
                progress_layout = QVBoxLayout(progress_widget)
                progress_layout.setContentsMargins(5, 5, 5, 5)
                
                progress_bar = QProgressBar()
                progress_bar.setMinimum(0)
                progress_bar.setMaximum(100)
                
                if limit > 0:
                    percentage = min(int((spent / limit) * 100), 100)
                else:
                    percentage = 0
                    
                progress_bar.setValue(percentage)
                
                # Color based on percentage
                if percentage >= 90:
                    progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #e5e7eb;
                            border-radius: 5px;
                            text-align: center;
                            height: 25px;
                        }
                        QProgressBar::chunk {
                            background-color: #ef4444;
                            border-radius: 5px;
                        }
                    """)
                elif percentage >= 75:
                    progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #e5e7eb;
                            border-radius: 5px;
                            text-align: center;
                            height: 25px;
                        }
                        QProgressBar::chunk {
                            background-color: #f97316;
                            border-radius: 5px;
                        }
                    """)
                else:
                    progress_bar.setStyleSheet("""
                        QProgressBar {
                            border: 1px solid #e5e7eb;
                            border-radius: 5px;
                            text-align: center;
                            height: 25px;
                        }
                        QProgressBar::chunk {
                            background-color: #10b981;
                            border-radius: 5px;
                        }
                    """)
                    
                progress_layout.addWidget(progress_bar)
                self.budget_table.setCellWidget(row_position, 4, progress_widget)
                
                # Store budget ID in the first column item's data
                category_item.setData(Qt.UserRole, budget.get('id', ''))
                
        except Exception as e:
            print(f"Error loading budget data: {e}")
            
    def save_budget(self):
        """Save new budget"""
        try:
            # Get form inputs
            category = self.category_combo.currentText()
            amount_text = self.amount_input.text().strip()
            note = self.note_input.text().strip()
            
            # Validate amount
            if not amount_text:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập giới hạn chi tiêu")
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
                
            # Check if budget already exists for this category
            for budget in self.budgets:
                if budget.get('category') == category:
                    reply = QMessageBox.question(self, "Xác nhận", 
                                              f"Đã tồn tại ngân sách cho danh mục {category}. Bạn có muốn cập nhật không?",
                                              QMessageBox.Yes | QMessageBox.No)
                    if reply == QMessageBox.No:
                        return
                    # We'll update the existing budget
                    break
                    
            # Create budget
            from data_manager.budget_manager import BudgetManager
            budget_manager = BudgetManager()
            
            current_month = datetime.datetime.now().month
            current_year = datetime.datetime.now().year
            
            budget = {
                'category': category,
                'limit': amount,
                'note': note,
                'month': current_month,
                'year': current_year,
                'created_at': datetime.datetime.now().isoformat(),
                'user_id': self.user_manager.current_user.get('id') if self.user_manager.current_user else None
            }
            
            success = budget_manager.add_or_update_budget(budget)
            
            if success:
                QMessageBox.information(self, "Thành công", "Đã lưu ngân sách thành công")
                self.budget_updated.emit(budget)
                
                # Clear form
                self.amount_input.clear()
                self.note_input.clear()
                
                # Reload data
                self.load_data()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể lưu ngân sách, vui lòng thử lại")
                
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {str(e)}")
            print(f"Error saving budget: {e}")
            
    def delete_budget(self):
        """Delete selected budget"""
        try:
            selected_items = self.budget_table.selectedItems()
            
            if not selected_items:
                QMessageBox.warning(self, "Lỗi", "Vui lòng chọn ngân sách để xóa")
                return
                
            # Get budget ID from the first column item's data
            budget_id = selected_items[0].data(Qt.UserRole)
            
            if not budget_id:
                QMessageBox.warning(self, "Lỗi", "Không thể xác định ngân sách đã chọn")
                return
                
            # Confirm deletion
            reply = QMessageBox.question(self, "Xác nhận", 
                                     "Bạn có chắc chắn muốn xóa ngân sách này không?",
                                     QMessageBox.Yes | QMessageBox.No)
                                     
            if reply == QMessageBox.Yes:
                # Delete budget
                from data_manager.budget_manager import BudgetManager
                budget_manager = BudgetManager()
                
                success = budget_manager.delete_budget(budget_id)
                
                if success:
                    QMessageBox.information(self, "Thành công", "Đã xóa ngân sách thành công")
                    self.load_data()
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể xóa ngân sách")
                    
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Đã xảy ra lỗi: {str(e)}")
            print(f"Error deleting budget: {e}")
