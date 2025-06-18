# Tạo file mới với tên user_transaction_form_tab.py
# Copy nội dung từ user_transaction_form.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QLineEdit, QFrame, QComboBox, QDateEdit, QMessageBox, QCompleter,
                            QTableWidget, QTableWidgetItem, QGroupBox, QHeaderView, QScrollArea,
                            QSizePolicy, QSpacerItem, QAbstractItemView) # Added QTableWidget, QTableWidgetItem, QGroupBox, QHeaderView, QScrollArea
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
import datetime # Added missing import
import json     # Added missing import for test block
import os       # Added missing import for test block
import logging
from utils.animated_widgets import pulse_widget, shake_widget
from data_manager.transaction_manager import TransactionManager # Ensure this is imported
from data_manager.category_manager import CategoryManager   # Ensure this is imported
from data_manager.budget_manager import BudgetManager     # Ensure this is imported


class UserTransactionTab(QWidget): # Renamed from UserTransactionForm
    transaction_added_or_updated = pyqtSignal() # Signal to indicate data change

    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager, budget_manager, notification_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.budget_manager = budget_manager
        self.notification_manager = notification_manager

        self.user_id = self.user_manager.current_user_id
        self.current_edit_transaction_id = None # To store the ID of the transaction being edited

        self.init_ui()
        # self.load_categories() # Removed: Handled by init_ui -> clear_form -> set_transaction_type_style
        self.load_transactions_to_table()

    def init_ui(self):
        tab_layout = QVBoxLayout(self)
        tab_layout.setContentsMargins(0,0,0,0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content_widget = QWidget()
        main_layout = QVBoxLayout(scroll_content_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15) # Add some spacing

        # --- Header Section ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 5, 5, 5)

        title_label = QLabel("Quản lý Giao dịch")
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
            padding: 0px;
            background-color: transparent;
            border: none;
        """)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        date_label = QLabel(f"{datetime.datetime.now():%A, %d/%m/%Y}")
        date_label.setStyleSheet("""
            font-size: 12px;
            color: white;
            padding: 0px;
            background-color: transparent;
            border: none;
        """)
        date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(date_label)
        header_widget.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #06b6d4, stop:1 #3b82f6);
            border-radius: 6px;
            padding: 8px 12px;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(header_widget)

        # --- Form and Table Layout ---
        content_layout = QHBoxLayout()

        # --- Transaction Form Group ---
        form_group = QGroupBox("Thêm/Sửa Giao dịch")
        form_group.setFixedWidth(400) # Set a fixed width for the form
        form_group_layout = QVBoxLayout(form_group)
        form_group_layout.setSpacing(15)

        # Loại giao dịch
        type_label = QLabel("Loại giao dịch:")
        type_label.setFont(QFont('Segoe UI', 10, QFont.Medium))
        form_group_layout.addWidget(type_label)
        type_buttons_layout = QHBoxLayout()
        self.income_btn = QPushButton("Thu nhập")
        self.income_btn.setCheckable(True)
        self.income_btn.setChecked(True) # Default to income
        self.income_btn.setStyleSheet(self.get_type_button_style("income"))
        self.income_btn.clicked.connect(lambda: self.set_transaction_type_style("income"))
        type_buttons_layout.addWidget(self.income_btn)
        self.expense_btn = QPushButton("Chi tiêu")
        self.expense_btn.setCheckable(True)
        self.expense_btn.setStyleSheet(self.get_type_button_style("expense"))
        self.expense_btn.clicked.connect(lambda: self.set_transaction_type_style("expense"))
        type_buttons_layout.addWidget(self.expense_btn)
        form_group_layout.addLayout(type_buttons_layout)
        # self.set_transaction_type_style("income") # Removed: Handled by self.clear_form() below

        # Tiêu đề / Mô tả
        description_label = QLabel("Tiêu đề / Mô tả:")
        description_label.setFont(QFont('Segoe UI', 10, QFont.Medium))
        form_group_layout.addWidget(description_label)
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("VD: Tiền ăn trưa")
        self.description_input.setFont(QFont('Segoe UI', 10))
        self.description_input.setStyleSheet(self.get_line_edit_style())
        form_group_layout.addWidget(self.description_input)

        # Số tiền
        amount_label = QLabel("Số tiền:")
        amount_label.setFont(QFont('Segoe UI', 10, QFont.Medium))
        form_group_layout.addWidget(amount_label)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("VD: 50000")
        self.amount_input.setFont(QFont('Segoe UI', 10))
        self.amount_input.setStyleSheet(self.get_line_edit_style())
        form_group_layout.addWidget(self.amount_input)

        # Danh mục
        category_label = QLabel("Danh mục:")
        category_label.setFont(QFont('Segoe UI', 10, QFont.Medium))
        form_group_layout.addWidget(category_label)
        self.category_combo = QComboBox()
        self.category_combo.setFont(QFont('Segoe UI', 10))
        self.category_combo.setStyleSheet(self.get_combo_box_style())
        form_group_layout.addWidget(self.category_combo)

        # Ngày giao dịch
        date_label = QLabel("Ngày giao dịch:")
        date_label.setFont(QFont('Segoe UI', 10, QFont.Medium))
        form_group_layout.addWidget(date_label)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setFont(QFont('Segoe UI', 10))
        self.date_edit.setStyleSheet(self.get_date_edit_style())
        form_group_layout.addWidget(self.date_edit)
        
        form_group_layout.addStretch() # Push buttons to bottom

        # Action Buttons for Form
        form_buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton(QIcon.fromTheme("list-add"), "Thêm mới")
        self.add_btn.setStyleSheet(self.get_action_button_style("add"))
        self.add_btn.clicked.connect(self.add_or_update_transaction)
        form_buttons_layout.addWidget(self.add_btn)

        self.clear_btn = QPushButton(QIcon.fromTheme("edit-clear"), "Làm mới")
        self.clear_btn.setStyleSheet(self.get_action_button_style("clear"))
        self.clear_btn.clicked.connect(self.clear_form)
        form_buttons_layout.addWidget(self.clear_btn)
        form_group_layout.addLayout(form_buttons_layout)

        content_layout.addWidget(form_group)

        # --- Transactions Table Group ---
        table_group = QGroupBox("Danh sách Giao dịch")
        table_group_layout = QVBoxLayout(table_group)

        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(6) # ID, Ngày, Mô tả, Số tiền, Loại, Danh mục
        self.transactions_table.setHorizontalHeaderLabels(["ID", "Ngày", "Mô tả", "Số tiền", "Loại", "Danh mục"])
        self.transactions_table.verticalHeader().setVisible(False)
        self.transactions_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.transactions_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.transactions_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.transactions_table.setShowGrid(True) # Show grid
        self.transactions_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                font-size: 10pt;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f1f5f9;
                padding: 6px;
                border: none; /* No border for header sections */
                border-bottom: 1px solid #e2e8f0; /* Bottom border for separation */
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
                border-bottom: 1px solid #f1f5f9; /* Lighter border for rows */
            }
            QTableWidget::item:selected {
                background-color: #dbeafe; /* Light blue for selection */
                color: #1e40af;
            }
        """)
        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch) # ID
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents) # Ngày
        header.setSectionResizeMode(2, QHeaderView.Stretch) # Mô tả
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Số tiền
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents) # Loại
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents) # Danh mục
        self.transactions_table.hideColumn(0) # Hide ID column by default

        self.transactions_table.itemSelectionChanged.connect(self.on_table_selection_changed)
        table_group_layout.addWidget(self.transactions_table)

        # Action Buttons for Table
        table_actions_layout = QHBoxLayout()
        table_actions_layout.addStretch()
        self.edit_btn = QPushButton(QIcon.fromTheme("document-edit"), "Sửa")
        self.edit_btn.setStyleSheet(self.get_action_button_style("edit"))
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.edit_selected_transaction)
        table_actions_layout.addWidget(self.edit_btn)

        self.delete_btn = QPushButton(QIcon.fromTheme("edit-delete"), "Xóa")
        self.delete_btn.setStyleSheet(self.get_action_button_style("delete"))
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_selected_transaction)
        table_actions_layout.addWidget(self.delete_btn)
        table_group_layout.addLayout(table_actions_layout)

        content_layout.addWidget(table_group) # Add table group to the right

        main_layout.addLayout(content_layout)
        scroll_content_widget.setLayout(main_layout)
        scroll_area.setWidget(scroll_content_widget)
        tab_layout.addWidget(scroll_area)
        self.setLayout(tab_layout)
        self.clear_form() # Initialize form state

    def get_type_button_style(self, type_name):
        if type_name == "income":
            return """
                QPushButton { background: #ecfdf5; color: #059669; border: 1px solid #d1fae5; border-radius: 8px; padding: 10px; font-weight: 600; font-size: 10pt;}
                QPushButton:checked { background: #059669; color: white; border-color: #047857; }
                QPushButton:hover:!checked { background: #d1fae5; }
            """
        else: # expense
            return """
                QPushButton { background: #fee2e2; color: #dc2626; border: 1px solid #fecaca; border-radius: 8px; padding: 10px; font-weight: 600; font-size: 10pt;}
                QPushButton:checked { background: #dc2626; color: white; border-color: #b91c1c; }
                QPushButton:hover:!checked { background: #fecaca; }
            """

    def get_line_edit_style(self):
        return """
            QLineEdit { border: 1px solid #d1d5db; border-radius: 8px; padding: 8px 12px; background: #f9fafb; font-size: 10pt;}
            QLineEdit:focus { border-color: #3b82f6; background: white; }
        """

    def get_combo_box_style(self):
        return """
            QComboBox { border: 1px solid #d1d5db; border-radius: 8px; padding: 8px 12px; background: #f9fafb; min-width: 150px; font-size: 10pt;}
            QComboBox:focus { border-color: #3b82f6; background: white; }
            QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 25px; border-left-width: 1px; border-left-color: #d1d5db; border-left-style: solid; border-top-right-radius: 8px; border-bottom-right-radius: 8px; }
            QComboBox QAbstractItemView { border: 1px solid #d1d5db; background: white; selection-background-color: #dbeafe; color: #1e3a8a; padding: 4px; }
        """
    def get_date_edit_style(self):
        return """
            QDateEdit { border: 1px solid #d1d5db; border-radius: 8px; padding: 8px 12px; background: #f9fafb; font-size: 10pt;}
            QDateEdit:focus { border-color: #3b82f6; background: white; }
            QDateEdit::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 25px; border-left-width: 1px; border-left-color: #d1d5db; border-left-style: solid; border-top-right-radius: 8px; border-bottom-right-radius: 8px; }
        """

    def get_action_button_style(self, type):
        base_style = "QPushButton { border-radius: 8px; padding: 10px 15px; font-size: 10pt; font-weight: bold; }"
        if type == "add":
            return base_style + "QPushButton { background-color: #22c55e; color: white; border: 1px solid #16a34a;} QPushButton:hover { background-color: #16a34a; }"
        elif type == "edit":
            return base_style + "QPushButton { background-color: #f97316; color: white; border: 1px solid #ea580c;} QPushButton:hover { background-color: #ea580c; } QPushButton:disabled { background-color: #fdba74; border-color: #fed7aa; color: #f9fafb;}"
        elif type == "delete":
            return base_style + "QPushButton { background-color: #ef4444; color: white; border: 1px solid #dc2626;} QPushButton:hover { background-color: #dc2626; } QPushButton:disabled { background-color: #fca5a5; border-color: #fecaca; color: #f9fafb;}"
        elif type == "clear":
            return base_style + "QPushButton { background-color: #64748b; color: white; border: 1px solid #475569;} QPushButton:hover { background-color: #475569; }"
        return base_style


    def set_transaction_type_style(self, selected_type):
        if selected_type == "income":
            self.income_btn.setChecked(True)
            self.expense_btn.setChecked(False)
        else: # expense
            self.income_btn.setChecked(False)
            self.expense_btn.setChecked(True)
        # Reload categories based on selected type
        self.load_categories()


    def load_categories(self):
        self.category_combo.clear()
        current_type = "income" if self.income_btn.isChecked() else "expense"
        # Fetch categories for the current user and system defaults, filtered by type
        # Corrected method name from get_categories_by_user to get_user_categories
        user_categories = self.category_manager.get_user_categories(self.user_id) 
        system_categories = self.category_manager.get_user_categories("system") # Assuming "system" for defaults
        
        all_available_categories = user_categories + [cat for cat in system_categories if cat not in user_categories]

        # Filter by current_type and ensure they are active
        filtered_categories = [
            cat for cat in all_available_categories 
            if cat.get('type') == current_type and cat.get('is_active', True)
        ]
        
        if not filtered_categories:
            self.category_combo.addItem(f"Không có danh mục {current_type}", None)
            self.category_combo.setEnabled(False)
        else:
            self.category_combo.setEnabled(True)
            for category in sorted(filtered_categories, key=lambda x: x['name']):
                self.category_combo.addItem(f"{category['icon']} {category['name']}", category['category_id'])
        self.category_combo.setCurrentIndex(0)


    def load_transactions_to_table(self):
        self.transactions_table.setRowCount(0) # Clear existing rows
        if not self.user_id:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy ID người dùng.")
            return

        transactions = self.transaction_manager.get_transactions_by_user(self.user_id)
        if not transactions:
            # Optional: Show a message in the table or a label if no transactions
            return

        for row, tx in enumerate(sorted(transactions, key=lambda x: x.get('date', ''), reverse=True)):
            self.transactions_table.insertRow(row)
            category_name = "N/A"
            category_id = tx.get('category_id')
            if category_id:
                category = self.category_manager.get_category_by_id(category_id)
                if category:
                    category_name = f"{category.get('icon', '')} {category.get('name', 'Không rõ')}"
                else:
                    category_name = "Không tìm thấy DM" # Category not found
            
            # Format date nicely
            try:
                date_obj = datetime.datetime.fromisoformat(tx.get('date', '').replace('Z', '+00:00'))
                date_str = date_obj.strftime("%d/%m/%Y")
            except ValueError:
                date_str = tx.get('date', 'N/A')


            self.transactions_table.setItem(row, 0, QTableWidgetItem(str(tx.get('transaction_id', ''))))
            self.transactions_table.setItem(row, 1, QTableWidgetItem(date_str))
            self.transactions_table.setItem(row, 2, QTableWidgetItem(str(tx.get('description', ''))))
            
            amount_item = QTableWidgetItem(f"{tx.get('amount', 0):,.0f} đ") # Format amount
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if tx.get('type') == 'expense':
                amount_item.setForeground(QColor("red"))
            else:
                amount_item.setForeground(QColor("green"))
            self.transactions_table.setItem(row, 3, amount_item)
            
            type_display = "Thu nhập" if tx.get('type') == 'income' else "Chi tiêu"
            self.transactions_table.setItem(row, 4, QTableWidgetItem(type_display))
            self.transactions_table.setItem(row, 5, QTableWidgetItem(category_name))
        
        self.transactions_table.resizeColumnsToContents()
        header = self.transactions_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.Stretch) # Mô tả
        self.transactions_table.hideColumn(0) # Ensure ID column is hidden


    def clear_form(self):
        self.current_edit_transaction_id = None
        self.description_input.clear()
        self.amount_input.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.income_btn.setChecked(True) # Default to income
        self.set_transaction_type_style("income") # This will also reload categories
        self.category_combo.setCurrentIndex(0)
        self.add_btn.setText("Thêm mới")
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.description_input.setFocus()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
        if self.transactions_table.selectionModel() is not None:
            self.transactions_table.clearSelection()


    def on_table_selection_changed(self):
        selected_items = self.transactions_table.selectedItems()
        is_item_selected = bool(selected_items)
        self.edit_btn.setEnabled(is_item_selected)
        self.delete_btn.setEnabled(is_item_selected)

    def add_or_update_transaction(self):
        description = self.description_input.text().strip()
        amount_str = self.amount_input.text().strip()
        category_id = self.category_combo.currentData()
        transaction_date = self.date_edit.date().toString("yyyy-MM-ddT00:00:00") # ISO format
        transaction_type = "income" if self.income_btn.isChecked() else "expense"

        if not description:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập mô tả giao dịch.")
            shake_widget(self.description_input)
            return
        if not amount_str:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập số tiền.")
            shake_widget(self.amount_input)
            return
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Số tiền phải lớn hơn 0")
        except ValueError:
            QMessageBox.warning(self, "Số tiền không hợp lệ", "Vui lòng nhập một số hợp lệ cho số tiền.")
            shake_widget(self.amount_input)
            return
        if not category_id:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng chọn một danh mục.")
            shake_widget(self.category_combo)
            return

        transaction_data = {
            "user_id": self.user_id,
            "description": description,
            "amount": amount,
            "category_id": category_id,
            "date": transaction_date,
            "type": transaction_type,
            # "created_at" and "updated_at" will be handled by manager or set here
        }

        try:
            old_transaction_for_budget_update = None
            if self.current_edit_transaction_id: # Editing existing transaction
                transaction_data["transaction_id"] = self.current_edit_transaction_id
                transaction_data["updated_at"] = datetime.datetime.now().isoformat()
                
                # Fetch the original transaction to correctly revert its impact on budget
                old_transaction_for_budget_update = self.transaction_manager.get_transaction_by_id(self.current_edit_transaction_id)
                if not old_transaction_for_budget_update:
                     QMessageBox.warning(self, "Lỗi", "Không tìm thấy giao dịch gốc để cập nhật ngân sách.")
                     # Decide if to proceed or return
                
                updated_tx = self.transaction_manager.update_transaction(transaction_data)
                if updated_tx:
                    QMessageBox.information(self, "Thành công", "Đã cập nhật giao dịch.")
                    self.update_budget_on_transaction(updated_tx, old_transaction_data=old_transaction_for_budget_update)
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể cập nhật giao dịch.")
                    return # Don't proceed if update failed
            else: # Adding new transaction
                transaction_data["created_at"] = datetime.datetime.now().isoformat()
                transaction_data["updated_at"] = datetime.datetime.now().isoformat()
                new_tx = self.transaction_manager.add_transaction(transaction_data)
                QMessageBox.information(self, "Thành công", f"Đã thêm giao dịch mới: {new_tx.get('description')}.")
                self.update_budget_on_transaction(new_tx)
            
            self.load_transactions_to_table()
            self.clear_form()
            # self.transaction_added_or_updated.emit() # Moved to update_budget_on_transaction
            pulse_widget(self.transactions_table)

        except Exception as e:
            QMessageBox.critical(self, "Lỗi", f"Không thể lưu giao dịch: {str(e)}")


    def edit_selected_transaction(self):
        selected_rows = self.transactions_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        transaction_id = self.transactions_table.item(row, 0).text() # Assuming ID is in hidden column 0
        
        transaction = self.transaction_manager.get_transaction_by_id(transaction_id) # Need this method in TransactionManager

        if not transaction:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy giao dịch để sửa.")
            return

        self.current_edit_transaction_id = transaction_id
        self.description_input.setText(transaction.get("description", ""))
        self.amount_input.setText(str(transaction.get("amount", "")))
        
        # Set transaction type buttons
        if transaction.get("type") == "income":
            self.set_transaction_type_style("income")
        else:
            self.set_transaction_type_style("expense")
            
        # Set category (important: load_categories is called by set_transaction_type_style, so combo should be populated)
        category_id_to_select = transaction.get("category_id")
        if category_id_to_select:
            index = self.category_combo.findData(category_id_to_select)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else: # Category might be inactive or of different type now
                cat_obj = self.category_manager.get_category_by_id(category_id_to_select)
                if cat_obj:
                    # Add it as a temporary item, indicating it might be inactive/changed
                    self.category_combo.addItem(f"{cat_obj.get('icon','')} {cat_obj.get('name','Danh mục cũ')} (Không dùng)", category_id_to_select)
                    self.category_combo.setCurrentIndex(self.category_combo.count() - 1)
                else:
                     self.category_combo.setCurrentIndex(0) # Fallback if category not found
        else:
            self.category_combo.setCurrentIndex(0) # Fallback

        # Set date
        try:
            date_obj = datetime.datetime.fromisoformat(transaction.get("date", "").replace("Z", "+00:00"))
            self.date_edit.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
        except ValueError:
            self.date_edit.setDate(QDate.currentDate()) # Fallback

        self.add_btn.setText("Lưu thay đổi")
        self.add_btn.setIcon(QIcon.fromTheme("document-save"))
        self.description_input.setFocus()


    def delete_selected_transaction(self):
        selected_rows = self.transactions_table.selectionModel().selectedRows()
        if not selected_rows:
            return
        
        row = selected_rows[0].row()
        transaction_id = self.transactions_table.item(row, 0).text()
        description = self.transactions_table.item(row, 2).text()

        reply = QMessageBox.question(self, "Xác nhận xóa", 
                                     f"Bạn có chắc chắn muốn xóa giao dịch '{description}' không?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                transaction_to_delete = self.transaction_manager.get_transaction_by_id(transaction_id)
                if transaction_to_delete:
                    # Store details before deleting, for budget update
                    category_id = transaction_to_delete.get('category_id')
                    amount = transaction_to_delete.get('amount', 0)
                    transaction_type = transaction_to_delete.get('type')
                    tx_date_str = transaction_to_delete.get('date')
                    
                    if self.transaction_manager.delete_transaction(transaction_id):
                        QMessageBox.information(self, "Thành công", "Đã xóa giao dịch.")
                        # Update budget AFTER successful deletion
                        if transaction_type == 'expense' and category_id and tx_date_str and amount > 0:
                            try:
                                tx_date = datetime.datetime.fromisoformat(tx_date_str.replace('Z', '+00:00'))
                                year, month = tx_date.year, tx_date.month
                                self.budget_manager.revert_expense_from_budget(
                                    self.user_id, category_id, year, month, amount
                                )
                                self.transaction_added_or_updated.emit() # Emit signal after budget update
                                logging.debug(f"UserTransactionTab: Budget reverted for deleted expense {transaction_id}")
                            except Exception as e_budget:
                                logging.error(f"UserTransactionTab: Error reverting budget for deleted transaction {transaction_id}: {e_budget}")
                        
                        self.load_transactions_to_table()
                        self.clear_form() 
                    else:
                        QMessageBox.warning(self, "Lỗi", "Không thể xóa giao dịch từ dữ liệu.")
                else:
                    QMessageBox.warning(self, "Lỗi", "Không tìm thấy giao dịch để xóa.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Không thể xóa giao dịch: {str(e)}")

    def update_budget_on_transaction(self, new_transaction_data, is_delete=False, old_transaction_data=None):
        """
        Updates the budget based on a new, updated, or deleted transaction.
        This method now calls the more specific budget_manager methods.
        Note: For deletions, budget update is handled directly in delete_selected_transaction.
              This method will primarily handle add/update.
        """
        if is_delete: # Deletion is handled in delete_selected_transaction to ensure it happens after successful DB delete
            logging.debug("UserTransactionTab.update_budget_on_transaction: Called with is_delete=True. Budget update for delete is handled in delete_selected_transaction.")
            # self.transaction_added_or_updated.emit() # Signal is emitted there too
            return

        try:
            new_category_id = new_transaction_data.get('category_id')
            new_amount = new_transaction_data.get('amount', 0)
            new_type = new_transaction_data.get('type')
            new_tx_date_str = new_transaction_data.get('date')

            if not new_tx_date_str:
                logging.warning("UserTransactionTab.update_budget_on_transaction: New transaction data missing date.")
                return
            
            new_tx_date = datetime.datetime.fromisoformat(new_tx_date_str.replace('Z', '+00:00'))
            new_year, new_month = new_tx_date.year, new_tx_date.month

            budget_changed = False

            # Handling for transaction UPDATE
            if old_transaction_data:
                old_category_id = old_transaction_data.get('category_id')
                old_amount = old_transaction_data.get('amount', 0)
                old_type = old_transaction_data.get('type')
                old_tx_date_str = old_transaction_data.get('date')

                if old_tx_date_str and old_category_id and old_amount > 0:
                    old_tx_date = datetime.datetime.fromisoformat(old_tx_date_str.replace('Z', '+00:00'))
                    old_year, old_month = old_tx_date.year, old_tx_date.month
                    
                    if old_type == 'expense':
                        logging.debug(f"UserTransactionTab (Update): Reverting old expense part. Cat='{old_category_id}', Amt={old_amount}")
                        self.budget_manager.revert_expense_from_budget(
                            self.user_id, old_category_id, old_year, old_month, old_amount
                        )
                        budget_changed = True
            
            # Apply new/updated transaction part
            if new_type == 'expense' and new_category_id and new_amount > 0:
                logging.debug(f"UserTransactionTab (Add/Update): Applying new expense part. Cat='{new_category_id}', Amt={new_amount}")
                self.budget_manager.apply_expense_to_budget(
                    self.user_id, new_category_id, new_year, new_month, new_amount
                )
                budget_changed = True
            
            if budget_changed:
                self.transaction_added_or_updated.emit()
                logging.debug("UserTransactionTab.update_budget_on_transaction: Emitted transaction_added_or_updated signal.")

        except Exception as e:
            logging.error(f"UserTransactionTab: Error in update_budget_on_transaction: {e}", exc_info=True)


# Example of how to use it (for testing, not part of the class)
if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication
    import sys 
    
    # Mock managers - replace with your actual manager initializations
    class MockUserManager:
        def __init__(self):
            self.current_user_id = "user123" 
            self.users = [{"user_id": "user123", "name": "Test User"}]
        def get_user_by_id(self, user_id):
            return next((u for u in self.users if u["user_id"] == user_id), None)

    # You would need to create mock data files (transactions.json, categories.json, budgets.json)
    # or ensure your managers handle their absence gracefully for this test.
    
    # Create dummy data files if they don't exist for the mock managers to load
    mock_data_path = "./data" # Adjust if your managers expect a different path
    os.makedirs(mock_data_path, exist_ok=True)
    
    if not os.path.exists(os.path.join(mock_data_path, 'transactions.json')):
        with open(os.path.join(mock_data_path, 'transactions.json'), 'w') as f:
            json.dump([], f)
    if not os.path.exists(os.path.join(mock_data_path, 'categories.json')):
         with open(os.path.join(mock_data_path, 'categories.json'), 'w') as f:
            # Add some default categories for testing
            default_categories = [
                {"category_id": "cat_food_sys", "name": "Ăn uống", "type": "expense", "icon": "🍽️", "user_id": "system", "is_active": True},
                {"category_id": "cat_salary_sys", "name": "Lương", "type": "income", "icon": "💰", "user_id": "system", "is_active": True},
                {"category_id": "cat_ent_user", "name": "Giải trí (User)", "type": "expense", "icon": "🎮", "user_id": "user123", "is_active": True}
            ]
            json.dump(default_categories, f)

    if not os.path.exists(os.path.join(mock_data_path, 'budgets.json')):
        with open(os.path.join(mock_data_path, 'budgets.json'), 'w') as f:
            json.dump([], f)


    app = QApplication(sys.argv)
    
    # Initialize actual managers, assuming they can find their data files
    # or create them in their default locations (e.g., project_root/data/)
    # For this example, ensure your managers are configured to look in a predictable place
    # or pass specific paths if they support it.
    # The paths in the managers are relative to their own location, so this might be tricky
    # for a standalone test script like this.
    # For a real test, you'd mock the file operations or use temporary file paths.

    # For simplicity, let's assume managers will create files in a 'data' subdir of where this script runs
    # This requires managers to be adjusted or this script to be in the project root.
    try:
        # Define user_mgr before using it for initializing UserTransactionTab
        user_mgr = MockUserManager() 
        transaction_mgr = TransactionManager() # Uses default 'data/transactions.json'
        category_mgr = CategoryManager()       # Uses default 'data/categories.json'
        budget_mgr = BudgetManager()           # Uses default 'data/budgets.json'
    except Exception as e:
        print(f"Error initializing managers for test: {e}")
        print("Please ensure your data managers can correctly locate/create their data files.")
        print("This test script might need to be run from your project's root directory,")
        print("or managers need to be instantiated with explicit paths to test data files.")
        sys.exit(1)


    main_window = UserTransactionTab(user_mgr, transaction_mgr, category_mgr, None, budget_mgr, None)
    main_window.setWindowTitle("Quản lý Giao dịch - Test")
    main_window.setGeometry(100, 100, 1000, 700) # Adjusted size
    main_window.show()
    sys.exit(app.exec_())
