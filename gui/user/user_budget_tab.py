# Copy nội dung từ user_budget.py sang user_budget_tab.py
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                            QLineEdit, QFrame, QComboBox, QMessageBox, QTableWidget,
                            QTableWidgetItem, QHeaderView, QAbstractItemView, QProgressBar,
                            QDateEdit, QDialog, QFormLayout, QDialogButtonBox, QSplitter)
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette
from PyQt5.QtCore import Qt, pyqtSignal, QDate
import datetime
import json
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import logging # Added for logging errors

class EditBudgetDialog(QDialog):
    def __init__(self, budget_data, category_manager, current_user_id, parent=None): # Added current_user_id
        super().__init__(parent)
        self.setWindowTitle("Sửa Ngân sách")
        self.setMinimumWidth(400)
        self.setStyleSheet("QDialog { background-color: #ffffff; border: 1px solid #cccccc; }")

        self.category_manager = category_manager
        self.budget_data = budget_data
        self.current_user_id = current_user_id # Store current_user_id

        layout = QFormLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        self.category_combo = QComboBox()
        self.category_combo.setFont(QFont('Segoe UI', 11))
        self.category_combo.setStyleSheet("QComboBox { padding: 5px; border: 1px solid #cccccc; border-radius: 3px; }")
        self.load_categories() # Call after current_user_id is set

        # Pre-select category if editing
        if budget_data and 'category_id' in budget_data:
            cat_id_to_select = budget_data['category_id']
            index = self.category_combo.findData(cat_id_to_select)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            # If not found by ID (e.g. category was deleted/changed), try by name as a fallback
            elif budget_data and 'category' in budget_data:
                 # Find by text might be less reliable if names are not unique or change
                 # but can be a fallback.
                 for i in range(self.category_combo.count()):
                     if self.category_combo.itemText(i).endswith(budget_data['category']): # Assuming name is at the end after icon
                         self.category_combo.setCurrentIndex(i)
                         break
        elif budget_data and 'category' in budget_data: # Fallback to name if id not present (legacy)
             self.category_combo.setCurrentText(budget_data['category'])


        layout.addRow("Danh mục:", self.category_combo)

        self.limit_input = QLineEdit()
        self.limit_input.setFont(QFont('Segoe UI', 11))
        self.limit_input.setStyleSheet("QLineEdit { padding: 5px; border: 1px solid #cccccc; border-radius: 3px; }")
        if budget_data and 'limit' in budget_data:
            self.limit_input.setText(str(budget_data['limit']))
        layout.addRow("Giới hạn:", self.limit_input)
        
        self.month_year_edit = QDateEdit()
        self.month_year_edit.setFont(QFont('Segoe UI', 11))
        self.month_year_edit.setStyleSheet("QDateEdit { padding: 5px; border: 1px solid #cccccc; border-radius: 3px; }")
        self.month_year_edit.setCalendarPopup(True)
        self.month_year_edit.setDisplayFormat("MM/yyyy")
        if budget_data and 'month' in budget_data and 'year' in budget_data:
            self.month_year_edit.setDate(QDate(budget_data['year'], budget_data['month'], 1))
        else:
            self.month_year_edit.setDate(QDate.currentDate())
        layout.addRow("Tháng/Năm:", self.month_year_edit)

        self.note_input = QLineEdit()
        self.note_input.setFont(QFont('Segoe UI', 11))
        self.note_input.setStyleSheet("QLineEdit { padding: 5px; border: 1px solid #cccccc; border-radius: 3px; }")
        if budget_data and 'note' in budget_data:
            self.note_input.setText(budget_data['note'])
        layout.addRow("Ghi chú:", self.note_input)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        self.buttons.setStyleSheet("QPushButton { padding: 5px 15px; background-color: #007bff; color: white; border-radius: 3px; }")
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def load_categories(self):
        self.category_combo.clear()
        try:
            # Use self.current_user_id passed to __init__
            # Ensure get_user_categories returns a list of dicts with 'category_id' and 'name'
            categories = self.category_manager.get_all_categories(user_id=self.current_user_id, category_type='expense') # MODIFIED HERE
            if categories:
                for category in sorted(categories, key=lambda x: x.get('name', '')): # Sort for better UX
                    # Ensure 'category_id' is used for data, 'name' (with icon) for display
                    display_name = f"{category.get('icon','')} {category.get('name', 'N/A')}".strip()
                    self.category_combo.addItem(display_name, category.get('category_id')) 
            else:
                self.category_combo.addItem("Không có danh mục chi tiêu", None) # Add None as data for placeholder
        except Exception as e:
            logging.error(f"EditBudgetDialog: Error loading categories: {e}")
            self.category_combo.addItem("Lỗi tải danh mục", None) # Add None as data for error

    def get_data(self):
        limit_text = self.limit_input.text().replace(',', '').replace('.', '')
        try:
            limit = float(limit_text)
        except ValueError:
            QMessageBox.warning(self, "Lỗi", "Số tiền giới hạn không hợp lệ.")
            return None

        if limit <= 0:
            QMessageBox.warning(self, "Lỗi", "Số tiền giới hạn phải lớn hơn 0.")
            return None
            
        selected_date = self.month_year_edit.date()
        
        # Get category_id from combo box data
        selected_category_id = self.category_combo.currentData()
        # Get the displayed text, which might include an icon
        raw_category_text = self.category_combo.currentText()

        # Attempt to derive name if icon is present (simple split, might need refinement)
        # This is mainly for the "category" field in budget_data, 'category_id' is primary
        parts = raw_category_text.split(" ", 1)
        selected_category_name = parts[1] if len(parts) > 1 else raw_category_text


        if selected_category_id is None and selected_category_name != "Không có danh mục chi tiêu" and selected_category_name != "Lỗi tải danh mục":
            QMessageBox.warning(self, "Lỗi Danh Mục", f"Danh mục '{selected_category_name}' không có ID hợp lệ.")
            return None

        return {
            "id": self.budget_data.get('id') if self.budget_data else None,
            "category": selected_category_name, # Store the cleaned name
            "category_id": selected_category_id, # This is the important part
            "limit": limit,
            "month": selected_date.month(),
            "year": selected_date.year(),
            "note": self.note_input.text().strip(),
        }

class UserBudgetTab(QWidget):
    budget_changed = pyqtSignal() # Signal when a budget is added, updated, or deleted

    def __init__(self, current_user_id, user_manager, transaction_manager, category_manager, wallet_manager, budget_manager, notification_manager, parent=None): # Added current_user_id
        super().__init__(parent)
        self.current_user_id = current_user_id # Assign directly
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager # Store wallet_manager
        self.budget_manager = budget_manager
        self.notification_manager = notification_manager

        self.budgets_data = [] # To store loaded budget data
        self.current_edit_budget_id = None # To store ID of budget being edited

        self._init_ui()
        self.load_budgets_and_categories()


    def _init_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        splitter = QSplitter(Qt.Horizontal)

        # Left side: Form and Chart
        left_panel = QFrame()
        left_panel.setFixedWidth(400) # Adjust as needed
        left_panel.setStyleSheet("background-color: #f8fafc; border-radius: 8px;")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(15, 15, 15, 15)
        left_layout.setSpacing(15)

        # Form Title
        form_title_label = QLabel("Quản lý Ngân sách")
        form_title_label.setFont(QFont('Segoe UI', 16, QFont.Bold))
        form_title_label.setStyleSheet("color: #1e293b;")
        left_layout.addWidget(form_title_label)
        
        # Form fields
        self.budget_form_frame = QFrame() # Using a frame for better styling if needed
        form_layout = QFormLayout(self.budget_form_frame)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignLeft)

        self.category_combo = QComboBox()
        self.category_combo.setFont(QFont('Segoe UI', 11))
        # self.category_combo.setStyleSheet(UIStyles.get_combo_box_style()) # Replaced
        self.category_combo.setStyleSheet("QComboBox { padding: 5px; border: 1px solid #cccccc; border-radius: 3px; }")
        form_layout.addRow("Danh mục:", self.category_combo)

        self.limit_input = QLineEdit()
        self.limit_input.setPlaceholderText("VD: 5000000")
        self.limit_input.setFont(QFont('Segoe UI', 11))
        # self.limit_input.setStyleSheet(UIStyles.get_line_edit_style()) # Replaced
        self.limit_input.setStyleSheet("QLineEdit { padding: 5px; border: 1px solid #cccccc; border-radius: 3px; }")
        form_layout.addRow("Giới hạn (VNĐ):", self.limit_input)

        self.month_year_edit = QDateEdit(QDate.currentDate())
        self.month_year_edit.setFont(QFont('Segoe UI', 11))
        # self.month_year_edit.setStyleSheet(UIStyles.get_date_edit_style()) # Replaced
        self.month_year_edit.setStyleSheet("QDateEdit { padding: 5px; border: 1px solid #cccccc; border-radius: 3px; }")
        self.month_year_edit.setCalendarPopup(True)
        self.month_year_edit.setDisplayFormat("MM/yyyy")
        form_layout.addRow("Tháng/Năm:", self.month_year_edit)
        
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Ghi chú (tùy chọn)")
        self.note_input.setFont(QFont('Segoe UI', 11))
        # self.note_input.setStyleSheet(UIStyles.get_line_edit_style()) # Replaced
        self.note_input.setStyleSheet("QLineEdit { padding: 5px; border: 1px solid #cccccc; border-radius: 3px; }")
        form_layout.addRow("Ghi chú:", self.note_input)

        left_layout.addWidget(self.budget_form_frame)

        # Action Buttons (Add, Clear/Reset)
        form_buttons_layout = QHBoxLayout()
        self.add_budget_button = QPushButton("Thêm Ngân sách")
        self.add_budget_button.setFont(QFont('Segoe UI', 11, QFont.Bold))
        # self.add_budget_button.setStyleSheet(ButtonStyleHelper.get_add_button_style()) # Replaced
        self.add_budget_button.setStyleSheet("QPushButton { background-color: #28a745; color: white; padding: 8px; border-radius: 4px; }")
        self.add_budget_button.setIcon(QIcon("assets/income_icon.png")) # Placeholder, updated path
        self.add_budget_button.clicked.connect(self.save_budget_entry)
        form_buttons_layout.addWidget(self.add_budget_button)

        self.clear_form_button = QPushButton("Làm mới Form")
        self.clear_form_button.setFont(QFont('Segoe UI', 11))
        # self.clear_form_button.setStyleSheet(ButtonStyleHelper.get_clear_button_style()) # Replaced
        self.clear_form_button.setStyleSheet("QPushButton { background-color: #ffc107; color: black; padding: 8px; border-radius: 4px; }")
        self.clear_form_button.setIcon(QIcon("assets/unread_icon.png")) # Placeholder, updated path
        self.clear_form_button.clicked.connect(self.clear_budget_form)
        form_buttons_layout.addWidget(self.clear_form_button)
        left_layout.addLayout(form_buttons_layout)
        
        left_layout.addStretch(1) # Pushes chart down or form up

        # Budget Chart
        chart_title_label = QLabel("Biểu đồ Ngân sách")
        chart_title_label.setFont(QFont('Segoe UI', 14, QFont.Bold))
        chart_title_label.setStyleSheet("color: #334155; margin-top: 15px;")
        left_layout.addWidget(chart_title_label)

        self.figure = Figure(figsize=(5, 4), dpi=100) # Adjust size as needed
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("border-radius: 6px;")
        left_layout.addWidget(self.canvas)
        
        left_layout.addStretch(2) # More stretch at the bottom

        splitter.addWidget(left_panel)

        # Right side: Budget Table
        right_panel = QFrame()
        right_panel.setStyleSheet("background-color: white; border-radius: 8px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)

        table_title_label = QLabel("Danh sách Ngân sách")
        table_title_label.setFont(QFont('Segoe UI', 16, QFont.Bold))
        table_title_label.setStyleSheet("color: #1e293b;")
        right_layout.addWidget(table_title_label)

        self.budget_table = QTableWidget()
        self.budget_table.setFont(QFont('Segoe UI', 10))
        self.budget_table.setColumnCount(6) # ID, Category, Limit, Spent, Remaining, Progress
        self.budget_table.setHorizontalHeaderLabels(["ID", "Danh mục", "Giới hạn", "Đã chi", "Còn lại", "Tiến độ"])
        # TableStyleHelper.apply_table_style(self.budget_table) # Replaced
        self.budget_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #e0e0e0;
                gridline-color: #f0f0f0;
                font-size: 10pt;
            }
            QHeaderView::section {
                background-color: #f7f7f7;
                padding: 6px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 6px;
            }
            QTableWidget::item:selected {
                background-color: #d0e4f8;
                color: black;
            }
        """)
        self.budget_table.verticalHeader().setVisible(False)
        self.budget_table.horizontalHeader().setStretchLastSection(True)
        self.budget_table.setAlternatingRowColors(True)

        self.budget_table.setColumnHidden(0, True) # Hide ID column
        self.budget_table.setColumnWidth(1, 180) # Category
        self.budget_table.setColumnWidth(2, 120) # Limit
        self.budget_table.setColumnWidth(3, 120) # Spent
        self.budget_table.setColumnWidth(4, 120) # Remaining
        self.budget_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch) # Progress
        self.budget_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.budget_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.budget_table.doubleClicked.connect(self.handle_table_double_click) # For editing
        right_layout.addWidget(self.budget_table)

        # Table Action Buttons (Edit, Delete, Refresh)
        table_actions_layout = QHBoxLayout()
        table_actions_layout.addStretch()

        self.edit_budget_button = QPushButton("Sửa")
        self.edit_budget_button.setFont(QFont('Segoe UI', 10, QFont.Bold))
        # self.edit_budget_button.setStyleSheet(ButtonStyleHelper.get_edit_button_style()) # Replaced
        self.edit_budget_button.setStyleSheet("QPushButton { background-color: #17a2b8; color: white; padding: 6px; border-radius: 4px; }")
        self.edit_budget_button.setIcon(QIcon("assets/expense_icon.png")) # Placeholder, updated path
        self.edit_budget_button.clicked.connect(self.edit_selected_budget)
        table_actions_layout.addWidget(self.edit_budget_button)

        self.delete_budget_button = QPushButton("Xóa")
        self.delete_budget_button.setFont(QFont('Segoe UI', 10, QFont.Bold))
        # self.delete_budget_button.setStyleSheet(ButtonStyleHelper.get_delete_button_style()) # Replaced
        self.delete_budget_button.setStyleSheet("QPushButton { background-color: #dc3545; color: white; padding: 6px; border-radius: 4px; }")
        self.delete_budget_button.setIcon(QIcon("assets/notifications_icon.png")) # Placeholder, updated path
        self.delete_budget_button.clicked.connect(self.delete_selected_budget)
        table_actions_layout.addWidget(self.delete_budget_button)
        
        self.refresh_button = QPushButton("Tải lại")
        self.refresh_button.setFont(QFont('Segoe UI', 10, QFont.Bold))
        # self.refresh_button.setStyleSheet(ButtonStyleHelper.get_refresh_button_style()) # Replaced
        self.refresh_button.setStyleSheet("QPushButton { background-color: #6c757d; color: white; padding: 6px; border-radius: 4px; }")
        self.refresh_button.setIcon(QIcon("assets/users_icon.png")) # Placeholder, updated path
        self.refresh_button.clicked.connect(self.load_budgets_and_categories)
        table_actions_layout.addWidget(self.refresh_button)

        right_layout.addLayout(table_actions_layout)
        splitter.addWidget(right_panel)
        
        splitter.setSizes([400, 600]) # Initial sizes for left and right panels
        main_layout.addWidget(splitter)

    def load_budgets_and_categories(self):
        # Use self.current_user_id directly as it's passed in __init__
        if not self.current_user_id:
            # print("UserBudgetTab: No current_user_id. Cannot load data.")
            self.budget_table.setRowCount(0) # Clear table
            self.category_combo.clear()
            self.update_budget_chart([]) # Clear chart
            return

        # self.current_user_id is already set from __init__
        # No need to get it from user_manager.current_user

        # Load categories for the form
        self.category_combo.clear()
        try:
            # Get expense categories for the current user
            # Ensure this method returns categories with 'category_id', 'name', and 'icon'
            categories = self.category_manager.get_all_categories(user_id=self.current_user_id, category_type='expense') # MODIFIED HERE
            if categories:
                for category in sorted(categories, key=lambda x: x.get('name', '')): # Sort for better UX
                    display_name = f"{category.get('icon','')} {category.get('name', 'N/A')}".strip()
                    self.category_combo.addItem(display_name, category.get('category_id'))
            else:
                self.category_combo.addItem("Không có danh mục chi tiêu", None)
        except Exception as e:
            logging.error(f"UserBudgetTab: Error loading categories for form: {e}") # Use logging
            self.category_combo.addItem("Lỗi tải danh mục", None)

        # Load budgets for the table
        try:
            # For simplicity, let's load budgets for the current month by default.
            # Could add a month/year selector for the table later.
            now = datetime.datetime.now()
            self.budgets_data = self.budget_manager.get_budgets_by_month(now.year, now.month, self.current_user_id)
            self.populate_budget_table()
            self.update_budget_chart(self.budgets_data)
        except Exception as e:
            logging.error(f"UserBudgetTab: Error loading budgets: {e}") # Use logging
            QMessageBox.critical(self, "Lỗi", f"Không thể tải danh sách ngân sách: {e}")
            self.budgets_data = []
            self.populate_budget_table() # Will show empty table
            self.update_budget_chart([])


    def populate_budget_table(self):
        self.budget_table.setRowCount(0)
        if not self.budgets_data:
            return

        # No longer need to manually sum transactions here for "spent" amount,
        # as budget_item['current_amount'] will be used directly.

        for row, budget in enumerate(self.budgets_data):
            self.budget_table.insertRow(row)
            
            budget_id = budget.get('id', '')            # Attempt to get category name from category_id for more robustness
            category_id = budget.get('category_id')
            category_name = budget.get('category', 'N/A') # Fallback to stored name
            if category_id:
                cat_obj = self.category_manager.get_category_by_id(category_id)
                if cat_obj:
                    category_name = cat_obj.get('name', category_name)
            
            limit = budget.get('limit', 0)
            
            # current_amount now represents the REMAINING balance
            remaining = budget.get('current_amount', 0)  # remaining balance
            spent = limit - remaining  # spent = limit - remaining
            
            # Ensure spent is not negative (in case of data inconsistency)
            spent = max(0, spent)

            self.budget_table.setItem(row, 0, QTableWidgetItem(str(budget_id)))
            self.budget_table.setItem(row, 1, QTableWidgetItem(category_name))
            
            limit_item = QTableWidgetItem(f"{limit:,.0f} đ")
            limit_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.budget_table.setItem(row, 2, limit_item)

            # Display spent as a positive number
            spent_item = QTableWidgetItem(f"{spent:,.0f} đ") # MODIFIED HERE: spent is already abs()
            spent_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.budget_table.setItem(row, 3, spent_item)

            remaining_item = QTableWidgetItem(f"{remaining:,.0f} đ")
            remaining_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            if remaining < 0:
                remaining_item.setForeground(QColor("red"))
            else:
                remaining_item.setForeground(QColor("green"))
            self.budget_table.setItem(row, 4, remaining_item)            # Progress Bar
            progress_bar = QProgressBar()
            progress_bar.setMinimum(0)
            progress_bar.setMaximum(100)
            # Calculate percentage based on spent amount
            percentage = int((spent / limit) * 100) if limit > 0 else 0
            percentage = min(max(percentage, 0), 100) # Clamp về 100% nếu vượt
            progress_bar.setValue(percentage)
            
            progress_bar_style_sheet = """
                QProgressBar {
                    border: 1px solid #e5e7eb;
                    border-radius: 5px;
                    text-align: center;
                    height: 20px;
                }
                QProgressBar::chunk {
                    background-color: %s;
                    border-radius: 4px;
                }
            """
            if percentage >= 90:
                progress_bar.setStyleSheet(progress_bar_style_sheet % "#ef4444") # Red
            elif percentage >= 75:
                progress_bar.setStyleSheet(progress_bar_style_sheet % "#f97316") # Orange
            else:
                progress_bar.setStyleSheet(progress_bar_style_sheet % "#10b981") # Green
            self.budget_table.setCellWidget(row, 5, progress_bar)
            
            self.budget_table.item(row, 0).setData(Qt.UserRole, budget)


    def clear_budget_form(self):
        self.category_combo.setCurrentIndex(0) if self.category_combo.count() > 0 else None
        self.limit_input.clear()
        self.month_year_edit.setDate(QDate.currentDate())
        self.note_input.clear()
        self.current_edit_budget_id = None # Reset edit state
        self.add_budget_button.setText("Thêm Ngân sách")


    def save_budget_entry(self):
        if not self.current_user_id:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông tin người dùng.")
            return

        raw_category_text = self.category_combo.currentText()
        category_id = self.category_combo.currentData() # Get category_id from combobox data

        # Attempt to derive name if icon is present
        parts = raw_category_text.split(" ", 1)
        category_name = parts[1] if len(parts) > 1 else raw_category_text


        # CRITICAL FIX: Check if category_id is None
        if category_id is None:
            QMessageBox.warning(self, "Lỗi Danh Mục", 
                                f"Không tìm thấy ID cho danh mục '{category_name}'.\\n"
                                "Vui lòng đảm bảo danh mục được chọn có ID hợp lệ.\\n"
                                "Nếu đây là danh mục mới, hãy thử làm mới hoặc kiểm tra lại phần quản lý danh mục.")
            logging.error(f"UserBudgetTab: Attempted to save budget for category '{category_name}' which has a None category_id.")
            return

        limit_text = self.limit_input.text().strip().replace(',', '').replace('.', '')
        note = self.note_input.text().strip()
        selected_date = self.month_year_edit.date()
        month = selected_date.month()
        year = selected_date.year()

        if not category_name or self.category_combo.currentIndex() == -1:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng chọn một danh mục.")
            return
        if not limit_text:
            QMessageBox.warning(self, "Thiếu thông tin", "Vui lòng nhập số tiền giới hạn.")
            return

        try:
            limit = float(limit_text)
            if limit <= 0:
                QMessageBox.warning(self, "Không hợp lệ", "Số tiền giới hạn phải lớn hơn 0.")
                return
        except ValueError:
            QMessageBox.warning(self, "Không hợp lệ", "Số tiền giới hạn không đúng định dạng.")
            return

        budget_data = {
            "user_id": self.current_user_id,
            "category": category_name, # Save the cleaned name
            "category_id": category_id, # Ensure category_id is saved
            "limit": limit,
            "month": month,
            "year": year,
            "note": note,
            "created_at": datetime.datetime.now().isoformat(), 
            "updated_at": datetime.datetime.now().isoformat(),
            "current_amount": 0 # Initialize current_amount spent for new budgets
        }
        
        try:
            if self.current_edit_budget_id: # Editing existing budget
                success = self.budget_manager.update_budget(self.current_edit_budget_id, budget_data)
                operation = "cập nhật"
            else: # Adding new budget
                # Use add_or_update_budget to handle potential duplicates for same cat/month/year
                result_budget = self.budget_manager.add_or_update_budget(budget_data)
                success = bool(result_budget)
                operation = "thêm"
            
            if success:
                QMessageBox.information(self, "Thành công", f"Đã {operation} ngân sách thành công!")
                self.clear_budget_form()
                self.load_budgets_and_categories() # Reload table and chart
                self.budget_changed.emit()
            else:
                QMessageBox.warning(self, "Lỗi", f"Không thể {operation} ngân sách. Có thể ngân sách cho danh mục và tháng này đã tồn tại (nếu thêm mới) hoặc có lỗi xảy ra.")
        except Exception as e:
            QMessageBox.critical(self, "Lỗi hệ thống", f"Lỗi khi {operation} ngân sách: {e}")
            print(f"Error saving budget: {e}")


    def handle_table_double_click(self, index):
        self.edit_selected_budget()

    def edit_selected_budget(self):
        selected_rows = self.budget_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn một ngân sách từ bảng để sửa.")
            return
        
        selected_row = selected_rows[0].row()
        budget_item_data = self.budget_table.item(selected_row, 0).data(Qt.UserRole)

        if not budget_item_data or not isinstance(budget_item_data, dict):
            QMessageBox.warning(self, "Lỗi", "Không thể lấy dữ liệu ngân sách để sửa.")
            return

        # Pass current_user_id to the dialog
        dialog = EditBudgetDialog(budget_item_data, self.category_manager, self.current_user_id, self)
        if dialog.exec_():
            updated_data = dialog.get_data()
            if updated_data:
                try:
                    # Ensure user_id is maintained if not part of dialog.get_data()
                    if 'user_id' not in updated_data and 'user_id' in budget_item_data:
                         updated_data['user_id'] = budget_item_data['user_id']
                    
                    # Ensure 'current_amount' is preserved if not part of dialog data (it shouldn't be)
                    if 'current_amount' not in updated_data and 'current_amount' in budget_item_data:
                        updated_data['current_amount'] = budget_item_data['current_amount']
                    
                    updated_data['updated_at'] = datetime.datetime.now().isoformat()

                    # Crucial check for category_id from dialog
                    if updated_data.get("category_id") is None:
                         QMessageBox.warning(self, "Lỗi", "Không thể cập nhật ngân sách do thiếu ID danh mục từ form sửa.")
                         logging.error("UserBudgetTab.edit_selected_budget: category_id is None after EditBudgetDialog.")
                         return

                    success = self.budget_manager.update_budget(updated_data['id'], updated_data)
                    if success:
                        QMessageBox.information(self, "Thành công", "Đã cập nhật ngân sách.")
                        self.load_budgets_and_categories()
                        self.budget_changed.emit()
                    else:
                        QMessageBox.warning(self, "Lỗi", "Không thể cập nhật ngân sách. Kiểm tra xem có ID ngân sách hợp lệ không.")
                except Exception as e:
                    QMessageBox.critical(self, "Lỗi hệ thống", f"Lỗi khi cập nhật ngân sách: {e}")
                    print(f"Error updating budget from dialog: {e}")


    def delete_selected_budget(self):
        selected_rows = self.budget_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.information(self, "Thông báo", "Vui lòng chọn một ngân sách từ bảng để xóa.")
            return

        selected_row = selected_rows[0].row()
        budget_id_item = self.budget_table.item(selected_row, 0) # ID is in column 0
        budget_category_item = self.budget_table.item(selected_row, 1) # Category name for message

        if not budget_id_item or not budget_category_item:
            QMessageBox.warning(self, "Lỗi", "Không thể xác định ngân sách để xóa.")
            return
        
        budget_id = budget_id_item.text()
        budget_category = budget_category_item.text()

        reply = QMessageBox.question(self, "Xác nhận Xóa",
                                     f"Bạn có chắc chắn muốn xóa ngân sách cho danh mục '{budget_category}' không?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            try:
                success = self.budget_manager.delete_budget(budget_id)
                if success:
                    QMessageBox.information(self, "Thành công", f"Đã xóa ngân sách cho '{budget_category}'.")
                    self.load_budgets_and_categories() # Reload table and chart
                    self.budget_changed.emit()
                else:
                    QMessageBox.warning(self, "Lỗi", f"Không thể xóa ngân sách cho '{budget_category}'. Ngân sách không tồn tại.")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi hệ thống", f"Lỗi khi xóa ngân sách: {e}")
                print(f"Error deleting budget: {e}")

    def update_budget_chart(self, budgets_for_chart=None):
        self.figure.clear()
        if budgets_for_chart is None: # Use self.budgets_data if no specific data passed
            budgets_for_chart = self.budgets_data

        if not budgets_for_chart:
            # Display a message if no data
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "Không có dữ liệu ngân sách để hiển thị", 
                    horizontalalignment='center', verticalalignment='center', 
                    fontsize=12, color='gray')
            ax.axis('off') # Hide axes
            self.canvas.draw()
            return

        # Prepare data for chart (e.g., spending vs. limit for each category)
        categories = [b.get('category', 'N/A') for b in budgets_for_chart]
        limits = [b.get('limit', 0) for b in budgets_for_chart]
        # Đã chi = limit - current_amount (có thể lớn hơn limit nếu chi vượt)
        spent_amounts = [max(0, b.get('limit', 0) - b.get('current_amount', 0)) for b in budgets_for_chart]

        # Get current month and year for chart title
        now = datetime.datetime.now() # ADDED THIS LINE

        ax = self.figure.add_subplot(111)
        
        # Create bar chart
        x = range(len(categories))
        bar_width = 0.35
        
        rects1 = ax.bar(x, limits, bar_width, label='Giới hạn', color='#60a5fa') # blue-400
        rects2 = ax.bar([p + bar_width for p in x], spent_amounts, bar_width, label='Đã chi', color='#f87171') # red-400

        ax.set_ylabel('Số tiền (VNĐ)')
        ax.set_title(f'Ngân sách Tháng {now.month}/{now.year}', fontsize=12, fontweight='bold')
        ax.set_xticks([p + bar_width / 2 for p in x])
        ax.set_xticklabels(categories, rotation=45, ha="right")
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.7)

        # Add value labels on top of bars
        def autolabel(rects):
            for rect in rects:
                height = rect.get_height()
                ax.annotate(f'{height:,.0f}',
                            xy=(rect.get_x() + rect.get_width() / 2, height),
                            xytext=(0, 3),  # 3 points vertical offset
                            textcoords="offset points",
                            ha='center', va='bottom', fontsize=8)
        autolabel(rects1)
        autolabel(rects2)

        self.figure.tight_layout() # Adjust layout to prevent labels from overlapping
        self.canvas.draw()

    def set_current_user_id(self, user_id):
        """Allow external update of user_id, e.g., from dashboard."""
        self.current_user_id = user_id
        # print(f"UserBudgetTab: current_user_id set to {user_id}")
        self.load_budgets_and_categories() # Reload data for the new user

# Example of QColorConstants if not available (usually part of PyQt5.QtGui)
class QColorConstants:
    Red = QColor("red")
    Green = QColor("green")
