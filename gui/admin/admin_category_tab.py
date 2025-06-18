from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QFrame, QComboBox, QMessageBox,
                            QTableWidget, QTableWidgetItem, QGroupBox, QHeaderView, QScrollArea,
                            QSizePolicy, QSpacerItem, QAbstractItemView, QColorDialog, QTextEdit)
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QBrush
from PyQt5.QtCore import Qt, QSize
from data_manager.category_manager import CategoryManager
from utils.icon_list import CATEGORY_ICONS, CATEGORY_COLORS
import os

class AdminCategoryTab(QWidget):
    def __init__(self, category_manager, parent=None):
        super().__init__(parent)
        self.category_manager = category_manager
        self.current_edit_category_id = None  # ID của danh mục đang chỉnh sửa
        self.init_ui()
        self.load_categories_to_table()
        
    def init_ui(self):
        tab_layout = QVBoxLayout(self)
        tab_layout.setContentsMargins(0,0,0,0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        scroll_content_widget = QWidget()
        main_layout = QVBoxLayout(scroll_content_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(15)

        # --- Header Section ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(5, 5, 5, 5)
        title_label = QLabel("Quản lý Danh mục (Admin)")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(title_label)
        header_layout.addStretch(1)
        header_widget.setStyleSheet("""
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #3b5998, stop:1 #2c4380);
            border-radius: 6px;
            padding: 8px 12px;
            margin-bottom: 10px;
        """)
        main_layout.addWidget(header_widget)

        # --- Form and Table Layout ---
        content_layout = QHBoxLayout()

        # --- Category Form Group ---
        form_group = QGroupBox("Thêm/Sửa Danh mục")
        form_group.setFixedWidth(400)
        form_group_layout = QVBoxLayout(form_group)
        form_group_layout.setSpacing(15)

        # Tên danh mục
        name_label = QLabel("Tên danh mục:")
        name_label.setFont(QFont('Segoe UI', 10, QFont.Medium))
        form_group_layout.addWidget(name_label)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("VD: Ăn uống")
        self.name_input.setFont(QFont('Segoe UI', 10))
        self.name_input.setStyleSheet(self.get_line_edit_style())
        form_group_layout.addWidget(self.name_input)

        # Loại danh mục
        type_label = QLabel("Loại danh mục:")
        type_label.setFont(QFont('Segoe UI', 10, QFont.Medium))
        form_group_layout.addWidget(type_label)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Chi tiêu", "Thu nhập"])
        self.type_combo.setFont(QFont('Segoe UI', 10))
        self.type_combo.setStyleSheet(self.get_combo_box_style())
        form_group_layout.addWidget(self.type_combo)
          # Icon (chỉ ComboBox)
        icon_label = QLabel("Biểu tượng:")
        icon_label.setFont(QFont('Segoe UI', 10, QFont.Medium))
        form_group_layout.addWidget(icon_label)
        self.icon_combo = QComboBox()
        self.icon_combo.setFont(QFont('Segoe UI Emoji', 16))
        self.icon_combo.setMinimumHeight(40)
        for icon in CATEGORY_ICONS:
            self.icon_combo.addItem(icon)
        self.icon_combo.setStyleSheet("""
            QComboBox { 
                border: 1px solid #d1d5db; 
                border-radius: 8px; 
                padding: 5px 15px; 
                background: #f9fafb; 
                min-width: 200px; 
                font-size: 16pt;
            }
            QComboBox:focus { 
                border-color: #3b82f6; 
                background: white; 
            }
            QComboBox::drop-down { 
                subcontrol-origin: padding; 
                subcontrol-position: top right; 
                width: 35px; 
                border-left-width: 1px; 
                border-left-color: #d1d5db; 
                border-left-style: solid; 
                border-top-right-radius: 8px; 
                border-bottom-right-radius: 8px; 
            }
            QComboBox QAbstractItemView { 
                border: 1px solid #d1d5db; 
                background: white;
                selection-background-color: #dbeafe; 
                color: #1e3a8a; 
                padding: 8px; 
                font-size: 16pt; 
            }
            QComboBox::item { 
                min-height: 30px; 
                padding: 5px; 
            }
        """)
        form_group_layout.addWidget(self.icon_combo)
        
        # Màu sắc danh mục
        color_label = QLabel("Màu sắc:")
        color_label.setFont(QFont('Segoe UI', 10, QFont.Medium))
        form_group_layout.addWidget(color_label)
        
        # Layout cho chọn màu
        color_select_layout = QHBoxLayout()
        
        # Hiển thị màu đã chọn
        self.color_preview = QFrame()
        self.color_preview.setFixedSize(40, 40)
        self.color_preview.setFrameShape(QFrame.Box)
        self.color_preview.setFrameShadow(QFrame.Raised)
        self.color_preview.setStyleSheet("background-color: #34a853; border-radius: 5px;")
        color_select_layout.addWidget(self.color_preview)
        
        # Hiển thị mã màu
        self.color_value = QLineEdit("#34a853")
        self.color_value.setReadOnly(True)
        self.color_value.setStyleSheet(self.get_line_edit_style())
        color_select_layout.addWidget(self.color_value)
        
        # Nút chọn màu
        self.color_button = QPushButton("Chọn màu")
        self.color_button.clicked.connect(self.choose_color)
        self.color_button.setStyleSheet("""
            QPushButton {
                background-color: #64748b;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #475569;
            }
        """)
        color_select_layout.addWidget(self.color_button)
        
        form_group_layout.addLayout(color_select_layout)
        
        # Mô tả (thêm trường này cho admin)
        desc_label = QLabel("Mô tả (tùy chọn):")
        desc_label.setFont(QFont('Segoe UI', 10, QFont.Medium))
        form_group_layout.addWidget(desc_label)
        self.desc_input = QTextEdit()
        self.desc_input.setMaximumHeight(80)
        self.desc_input.setStyleSheet("""
            QTextEdit { 
                border: 1px solid #d1d5db; 
                border-radius: 8px; 
                padding: 8px; 
                background: #f9fafb; 
                font-size: 10pt;
            }
            QTextEdit:focus { 
                border-color: #3b82f6; 
                background: white; 
            }
        """)
        form_group_layout.addWidget(self.desc_input)
        
        # Kết nối sự kiện thay đổi loại danh mục với hàm cập nhật màu sắc
        self.type_combo.currentIndexChanged.connect(self.update_default_color)

        form_group_layout.addStretch()

        # Action Buttons for Form
        form_buttons_layout = QHBoxLayout()
        self.add_btn = QPushButton(QIcon.fromTheme("list-add"), "Thêm mới")
        self.add_btn.setStyleSheet(self.get_action_button_style("add"))
        self.add_btn.clicked.connect(self.add_or_update_category)
        form_buttons_layout.addWidget(self.add_btn)

        self.clear_btn = QPushButton(QIcon.fromTheme("edit-clear"), "Làm mới")
        self.clear_btn.setStyleSheet(self.get_action_button_style("clear"))
        self.clear_btn.clicked.connect(self.clear_form)
        form_buttons_layout.addWidget(self.clear_btn)
        form_group_layout.addLayout(form_buttons_layout)

        content_layout.addWidget(form_group)        # --- Categories Table Group ---
        table_group = QGroupBox("Danh sách Danh mục")
        table_group_layout = QVBoxLayout(table_group)
        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(6)
        # Đổi thứ tự cột: Icon trước, tên sau
        self.categories_table.setHorizontalHeaderLabels(["ID", "Icon", "Tên", "Loại", "Người tạo", "Thao tác"])
        
        # Set font cho header để hiển thị đúng
        header_font = QFont('Segoe UI', 10, QFont.Bold)
        self.categories_table.horizontalHeader().setFont(header_font)
        self.categories_table.verticalHeader().setVisible(False)
        self.categories_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.categories_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.categories_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.categories_table.setShowGrid(True)
        # Tăng chiều cao mặc định của các hàng để emoji hiển thị đẹp
        self.categories_table.verticalHeader().setDefaultSectionSize(50)
        self.categories_table.setStyleSheet("""
            QTableWidget { 
                border: 1px solid #e2e8f0; 
                border-radius: 8px; 
                font-size: 10pt; 
                background-color: white; 
            }
            QHeaderView::section { 
                background-color: #f1f5f9; 
                padding: 8px; 
                border: none; 
                font-weight: bold; 
            }
            QTableWidget::item { 
                padding: 8px; 
                border-bottom: 1px solid #f1f5f9; 
            }
            QTableWidget::item:selected { 
                background-color: #dbeafe; 
                color: #1e40af; 
            }        """)
        
        header = self.categories_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID (ẩn)
        header.setSectionResizeMode(1, QHeaderView.Fixed)  # Icon
        header.setSectionResizeMode(2, QHeaderView.Stretch)  # Tên
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Loại
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Người tạo
        header.setSectionResizeMode(5, QHeaderView.Fixed)  # Thao tác
        self.categories_table.hideColumn(0) # Hide ID column        # Cố định kích thước cột icon và thao tác để hiển thị đẹp
        self.categories_table.setColumnWidth(1, 80)  # Tăng chiều rộng cột icon
        self.categories_table.setColumnWidth(5, 180)  # Đủ rộng cho 2 nút
        
        table_group_layout.addWidget(self.categories_table)
        content_layout.addWidget(table_group)
        main_layout.addLayout(content_layout)
        scroll_content_widget.setLayout(main_layout)
        scroll_area.setWidget(scroll_content_widget)
        tab_layout.addWidget(scroll_area)
        self.setLayout(tab_layout)
        self.clear_form()

    def refresh_table(self):
        """Tải lại dữ liệu vào bảng"""
        self.load_categories_to_table()

    def get_line_edit_style(self):
        return """QLineEdit { 
            border: 1px solid #d1d5db; 
            border-radius: 8px; 
            padding: 8px 12px; 
            background: #f9fafb; 
            font-size: 10pt;
        }
        QLineEdit:focus { 
            border-color: #3b82f6; 
            background: white; 
        }
        """
        
    def get_combo_box_style(self):
        return """
            QComboBox { border: 1px solid #d1d5db; border-radius: 8px; padding: 8px 12px; background: #f9fafb; min-width: 150px; font-size: 10pt;}
            QComboBox:focus { border-color: #3b82f6; background: white; }
            QComboBox::drop-down { subcontrol-origin: padding; subcontrol-position: top right; width: 25px; border-left-width: 1px; border-left-color: #d1d5db; border-left-style: solid; border-top-right-radius: 8px; border-bottom-right-radius: 8px; }
            QComboBox QAbstractItemView { border: 1px solid #d1d5db; background: white; selection-background-color: #dbeafe; color: #1e3a8a; padding: 4px; }
        """
        
    def get_action_button_style(self, type):
        base_style = "QPushButton { border-radius: 6px; padding: 5px 8px; font-size: 9pt; font-weight: bold; }"
        if type == "add":
            return base_style + "QPushButton { background-color: #22c55e; color: white; border: 1px solid #16a34a;} QPushButton:hover { background-color: #16a34a; }"
        elif type == "edit":
            return base_style + "QPushButton { background-color: #f97316; color: white; border: 1px solid #ea580c;} QPushButton:hover { background-color: #ea580c; } QPushButton:disabled { background-color: #fdba74; border-color: #fed7aa; color: #f9fafb;}"
        elif type == "delete":
            return base_style + "QPushButton { background-color: #ef4444; color: white; border: 1px solid #dc2626;} QPushButton:hover { background-color: #dc2626; } QPushButton:disabled { background-color: #fca5a5; border-color: #fecaca; color: #f9fafb;}"
        elif type == "clear":
            return base_style + "QPushButton { background-color: #64748b; color: white; border: 1px solid #475569;} QPushButton:hover { background-color: #475569; }"
        return base_style

    def load_categories_to_table(self):
        self.categories_table.setRowCount(0)
        # Trong trang admin, hiển thị tất cả các danh mục từ mọi người dùng
        # Lấy trực tiếp tất cả các danh mục từ thuộc tính categories
        categories = self.category_manager.categories
        for row, cat in enumerate(categories):
            self.categories_table.insertRow(row)
            self.categories_table.setItem(row, 0, QTableWidgetItem(cat.get('category_id', '')))
            # Icon hiển thị trước (cột 1)
            icon = cat.get('icon', '🔖')  
            icon_item = QTableWidgetItem(icon)
            icon_item.setFont(QFont('Segoe UI Emoji', 24)) 
            icon_item.setTextAlignment(Qt.AlignCenter)
            # Sử dụng màu cho icon nếu có
            color = cat.get('color', '#FFFFFF')
            icon_item.setBackground(QBrush(QColor(color)))
            self.categories_table.setItem(row, 1, icon_item)
            
            # Tên (cột 2)
            self.categories_table.setItem(row, 2, QTableWidgetItem(cat.get('name', '')))
            
            # Loại (cột 3)
            type_display = "Thu nhập" if cat.get('type') == 'income' else "Chi tiêu"
            self.categories_table.setItem(row, 3, QTableWidgetItem(type_display))

            # Người tạo (cột 4)
            user_id = cat.get('user_id')
            user_display = "Hệ thống" if user_id == 'system' else f"Người dùng (ID: {user_id})"
            self.categories_table.setItem(row, 4, QTableWidgetItem(user_display))
            # Thao tác (cột 5)
            action_layout = QHBoxLayout()
            action_layout.setContentsMargins(0, 0, 0, 0)
            action_layout.setSpacing(5)  # Giảm khoảng cách giữa 2 nút
            
            # Admin có thể sửa và xóa tất cả các danh mục
            btn_edit = QPushButton("Sửa")
            btn_edit.setFixedWidth(70)  # Cố định chiều rộng nút
            btn_edit.setStyleSheet(self.get_action_button_style("edit"))
            btn_edit.clicked.connect(lambda _, row=row: self.edit_category(row))
            action_layout.addWidget(btn_edit)
            
            btn_del = QPushButton("Xóa")
            btn_del.setFixedWidth(70)  # Cố định chiều rộng nút
            btn_del.setStyleSheet(self.get_action_button_style("delete"))
            btn_del.clicked.connect(lambda _, row=row: self.delete_category(row))
            action_layout.addWidget(btn_del)
                
            action_widget = QWidget()
            action_widget.setLayout(action_layout)
            self.categories_table.setCellWidget(row, 5, action_widget)
                  # Đảm bảo các hàng đủ cao để hiển thị icon lớn
        self.categories_table.resizeRowsToContents()
        # Đảm bảo cột icon có chiều rộng cố định
        self.categories_table.setColumnWidth(1, 80)  # Tăng chiều rộng cột icon
        
    def clear_form(self):
        self.current_edit_category_id = None
        self.name_input.clear()
        self.icon_combo.setCurrentIndex(0)
        self.type_combo.setCurrentIndex(0)
        self.color_value.setText("#34a853")
        self.color_preview.setStyleSheet("background-color: #34a853; border-radius: 5px;")
        self.desc_input.clear()
        self.add_btn.setText("Thêm mới")
        self.add_btn.setIcon(QIcon.fromTheme("list-add"))
        self.name_input.setFocus()
        self.categories_table.clearSelection()

    def add_or_update_category(self):
        name = self.name_input.text().strip()
        icon = self.icon_combo.currentText().strip() or "📝"
        type_str = self.type_combo.currentText()
        category_type = 'expense' if type_str == "Chi tiêu" else 'income'
        color = self.color_value.text().strip() or "#34a853"
        description = self.desc_input.toPlainText().strip()
        
        if not name:
            QMessageBox.warning(self, "Lỗi", "Tên danh mục không được để trống!")
            return
            
        try:
            if self.current_edit_category_id:
                # Sửa danh mục - Admin có quyền sửa cả danh mục hệ thống
                updated = self.category_manager.update_category(
                    self.current_edit_category_id, 
                    'system',  # Admin sử dụng ID 'system'
                    True,      # is_admin=True
                    name=name, 
                    type=category_type, 
                    icon=icon, 
                    color=color,
                    description=description
                )
                if updated:
                    QMessageBox.information(self, "Thành công", "Đã cập nhật danh mục!")
                else:
                    QMessageBox.information(self, "Không có thay đổi", "Không có thông tin nào được cập nhật.")
            else:
                # Thêm mới - Admin tạo danh mục hệ thống
                self.category_manager.create_category(
                    user_id='system',
                    name=name, 
                    category_type=category_type, 
                    icon=icon, 
                    color=color,
                    description=description
                )
                QMessageBox.information(self, "Thành công", "Đã thêm danh mục hệ thống mới!")
                
            self.load_categories_to_table()
            self.clear_form()
        except Exception as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            
    def edit_category(self, row):
        cat_id = self.categories_table.item(row, 0).text()
        cat = self.category_manager.get_category_by_id(cat_id)
        if not cat:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy danh mục để sửa.")
            return
            
        self.current_edit_category_id = cat_id
        self.name_input.setText(cat.get('name', ''))
          
        # Cập nhật icon
        icon = cat.get('icon', '')
        icon_idx = 0
        if icon in CATEGORY_ICONS:
            icon_idx = CATEGORY_ICONS.index(icon)
        self.icon_combo.setCurrentIndex(icon_idx)
          
        # Cập nhật loại danh mục
        idx = 0 if cat.get('type') == 'expense' else 1
        self.type_combo.setCurrentIndex(idx)
        
        # Cập nhật màu sắc
        color = cat.get('color', '#34a853')
        self.update_color_preview(color)
        
        # Cập nhật mô tả
        self.desc_input.setPlainText(cat.get('description', ''))
        
        self.add_btn.setText("Lưu thay đổi")
        self.add_btn.setIcon(QIcon.fromTheme("document-save"))
        self.name_input.setFocus()

    def delete_category(self, row):
        cat_id = self.categories_table.item(row, 0).text()
        cat = self.category_manager.get_category_by_id(cat_id)
        if not cat:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy danh mục để xóa.")
            return
            
        # Cảnh báo nếu đây là danh mục hệ thống
        warning_msg = ""
        if cat.get('user_id') == 'system':
            warning_msg = "\n\nĐây là danh mục hệ thống. Xóa có thể ảnh hưởng đến hoạt động của ứng dụng!"
            
        reply = QMessageBox.question(
            self, 
            "Xác nhận xóa", 
            f"Bạn có chắc muốn xóa danh mục '{cat.get('name')}'?{warning_msg}", 
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # Admin có quyền xóa mọi danh mục
                self.category_manager.delete_category(cat_id, 'system', True)
                QMessageBox.information(self, "Thành công", "Đã xóa danh mục!")
                self.load_categories_to_table()
                self.clear_form()
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", str(e))

    def choose_color(self):
        """Hiện dialog chọn màu và cập nhật màu đã chọn"""
        # Lấy màu hiện tại từ preview
        current_color = QColor(self.color_value.text())
        
        # Hiển thị ColorDialog
        color = QColorDialog.getColor(current_color, self, "Chọn màu cho danh mục")
        
        # Nếu màu hợp lệ và người dùng không bấm Cancel
        if color.isValid():
            color_hex = color.name()
            self.update_color_preview(color_hex)
            
    def update_color_preview(self, color_hex):
        """Cập nhật màu hiển thị và giá trị màu"""
        self.color_preview.setStyleSheet(f"background-color: {color_hex}; border-radius: 5px;")
        self.color_value.setText(color_hex)
        
    def update_default_color(self):
        """Cập nhật màu mặc định dựa trên loại danh mục"""
        category_type = 'expense' if self.type_combo.currentText() == "Chi tiêu" else 'income'
        # Chọn màu đầu tiên từ danh sách màu tương ứng
        if category_type in CATEGORY_COLORS and len(CATEGORY_COLORS[category_type]) > 0:
            default_color = CATEGORY_COLORS[category_type][0]
            self.update_color_preview(default_color)

    def format_datetime(self, dt_str):
        from datetime import datetime
        try:
            if not dt_str:
                return ''
            if 'T' in dt_str:
                dt = datetime.fromisoformat(dt_str.split('.')[0])
            else:
                dt = datetime.strptime(dt_str, "%Y-%m-%d")
            return dt.strftime("%d-%m-%Y %H:%M:%S")
        except Exception:
            return dt_str
