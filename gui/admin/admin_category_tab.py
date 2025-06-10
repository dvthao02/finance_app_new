from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QTextEdit, 
                           QPushButton, QLabel, QTableWidget, QTableWidgetItem, QHeaderView, 
                           QColorDialog, QFileDialog, QMessageBox, QDialog, QFormLayout, 
                           QDialogButtonBox)
from PyQt5.QtGui import QIcon, QPixmap
import os

class AdminCategoryTab(QWidget):
    def __init__(self, category_manager, parent=None):
        super().__init__(parent)
        self.category_manager = category_manager
        self.init_ui()
        self.load_categories_table()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.category_table = QTableWidget(0, 8)
        self.category_table.setHorizontalHeaderLabels([
            "Icon", "Tên danh mục", "Loại", "Màu sắc", "Mô tả", "Trạng thái", "Ngày tạo", "Người tạo"
        ])
        self.category_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.category_table.horizontalHeader().setStretchLastSection(True)
        self.category_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.category_table)
        btn_layout = QHBoxLayout()
        self.btn_add_cat = QPushButton("Thêm danh mục")
        self.btn_edit_cat = QPushButton("Sửa danh mục")
        self.btn_del_cat = QPushButton("Xóa danh mục")
        btn_layout.addWidget(self.btn_add_cat)
        btn_layout.addWidget(self.btn_edit_cat)
        btn_layout.addWidget(self.btn_del_cat)
        layout.addLayout(btn_layout)
        self.btn_add_cat.clicked.connect(self.add_category_dialog)
        self.btn_edit_cat.clicked.connect(self.edit_category_dialog)
        self.btn_del_cat.clicked.connect(self.delete_category)

    def load_categories_table(self):
        categories = self.category_manager.load_categories()
        self.category_table.setRowCount(0)
        for cat in categories:
            if cat.get('user_id', 'system') == 'system':
                row = self.category_table.rowCount()
                self.category_table.insertRow(row)
                icon = cat.get('icon', '')
                icon_item = QTableWidgetItem()
                if os.path.isfile(icon):
                    pixmap = QPixmap(icon)
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(32, 32)
                        icon_item.setIcon(QIcon(pixmap))
                else:
                    icon_item.setText(icon)
                self.category_table.setItem(row, 0, icon_item)
                self.category_table.setItem(row, 1, QTableWidgetItem(cat.get('name', '')))
                self.category_table.setItem(row, 2, QTableWidgetItem('Chi' if cat.get('type')=='expense' else 'Thu'))
                self.category_table.setItem(row, 3, QTableWidgetItem(cat.get('color', '')))
                self.category_table.setItem(row, 4, QTableWidgetItem(cat.get('description', '')))
                self.category_table.setItem(row, 5, QTableWidgetItem('Hoạt động' if cat.get('is_active', True) else 'Ẩn'))
                self.category_table.setItem(row, 6, QTableWidgetItem(cat.get('created_at', '')))
                self.category_table.setItem(row, 7, QTableWidgetItem('Hệ thống'))    
    def add_category_dialog(self):
        from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QTextEdit, QDialogButtonBox, QColorDialog, QPushButton, QHBoxLayout, QFileDialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Thêm danh mục mới")
        dialog.setFixedSize(400, 300)
        
        layout = QFormLayout(dialog)
        
        name_input = QLineEdit()
        layout.addRow("Tên danh mục:", name_input)
        
        type_combo = QComboBox()
        type_combo.addItems(["expense", "income"])
        layout.addRow("Loại:", type_combo)
        
        # Color picker
        color_layout = QHBoxLayout()
        self.selected_color = "#FF5722"
        color_button = QPushButton("Chọn màu")
        color_display = QLabel()
        color_display.setFixedSize(30, 30)
        color_display.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #ccc;")
        
        def pick_color():
            color = QColorDialog.getColor()
            if color.isValid():
                self.selected_color = color.name()
                color_display.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #ccc;")
        
        color_button.clicked.connect(pick_color)
        color_layout.addWidget(color_button)
        color_layout.addWidget(color_display)
        layout.addRow("Màu sắc:", color_layout)
        
        # Icon picker
        icon_layout = QHBoxLayout()
        self.selected_icon = ""
        icon_button = QPushButton("Chọn icon")
        icon_label = QLabel("Chưa chọn")
        
        def pick_icon():
            file_path, _ = QFileDialog.getOpenFileName(dialog, "Chọn icon", "", "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)")
            if file_path:
                self.selected_icon = file_path
                icon_label.setText(os.path.basename(file_path))
        
        icon_button.clicked.connect(pick_icon)
        icon_layout.addWidget(icon_button)
        icon_layout.addWidget(icon_label)
        layout.addRow("Icon:", icon_layout)
        
        desc_input = QTextEdit()
        desc_input.setMaximumHeight(60)
        layout.addRow("Mô tả:", desc_input)
        
        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên danh mục")
                return
                
            try:
                result = self.category_manager.create_category(
                    user_id='system',
                    name=name,
                    category_type=type_combo.currentText(),
                    icon=self.selected_icon,
                    color=self.selected_color,
                    description=desc_input.toPlainText().strip(),
                    is_active=True                )
                
                if result:
                    QMessageBox.information(self, "Thành công", "Đã thêm danh mục thành công!")
                    self.refresh_table_with_loading()
                    # Clear selections for next use
                    self.selected_icon = ""
                    self.selected_color = "#FF5722"
                    dialog.accept()  # Close dialog after success
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể thêm danh mục")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi thêm danh mục: {str(e)}")

    def edit_category_dialog(self):
        selected_row = self.category_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn danh mục cần sửa")
            return
            
        category_name = self.category_table.item(selected_row, 1).text()
        categories = self.category_manager.load_categories()
        category = None
        for cat in categories:
            if cat.get('name') == category_name and cat.get('user_id') == 'system':
                category = cat
                break
                
        if not category:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy danh mục")
            return
            
        from PyQt5.QtWidgets import QDialog, QFormLayout, QLineEdit, QComboBox, QTextEdit, QDialogButtonBox, QColorDialog, QPushButton, QHBoxLayout, QFileDialog
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Sửa danh mục")
        dialog.setFixedSize(400, 300)
        
        layout = QFormLayout(dialog)
        
        name_input = QLineEdit(category.get('name', ''))
        layout.addRow("Tên danh mục:", name_input)
        
        type_combo = QComboBox()
        type_combo.addItems(["expense", "income"])
        current_type = category.get('type', 'expense')
        type_combo.setCurrentText(current_type)
        layout.addRow("Loại:", type_combo)
        
        # Color picker
        color_layout = QHBoxLayout()
        self.selected_color = category.get('color', '#FF5722')
        color_button = QPushButton("Chọn màu")
        color_display = QLabel()
        color_display.setFixedSize(30, 30)
        color_display.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #ccc;")
        
        def pick_color():
            color = QColorDialog.getColor()
            if color.isValid():
                self.selected_color = color.name()
                color_display.setStyleSheet(f"background-color: {self.selected_color}; border: 1px solid #ccc;")
        
        color_button.clicked.connect(pick_color)
        color_layout.addWidget(color_button)
        color_layout.addWidget(color_display)
        layout.addRow("Màu sắc:", color_layout)
        
        # Icon picker
        icon_layout = QHBoxLayout()
        self.selected_icon = category.get('icon', '')
        icon_button = QPushButton("Chọn icon")
        icon_label = QLabel(os.path.basename(self.selected_icon) if self.selected_icon else "Chưa chọn")
        
        def pick_icon():
            file_path, _ = QFileDialog.getOpenFileName(dialog, "Chọn icon", "", "Image Files (*.png *.jpg *.jpeg *.gif *.bmp)")
            if file_path:
                self.selected_icon = file_path
                icon_label.setText(os.path.basename(file_path))
        
        icon_button.clicked.connect(pick_icon)
        icon_layout.addWidget(icon_button)
        icon_layout.addWidget(icon_label)
        layout.addRow("Icon:", icon_layout)
        
        desc_input = QTextEdit()
        desc_input.setPlainText(category.get('description', ''))
        desc_input.setMaximumHeight(60)
        layout.addRow("Mô tả:", desc_input)
          # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addRow(buttons)
        
        if dialog.exec_() == QDialog.Accepted:
            name = name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Lỗi", "Vui lòng nhập tên danh mục")
                return
                
            try:
                result = self.category_manager.update_category(
                    category.get('category_id'),
                    'system',  # current_user_id
                    True,      # is_admin
                    name=name,
                    category_type=type_combo.currentText(),
                    color=self.selected_color,
                    icon=self.selected_icon,
                    description=desc_input.toPlainText().strip(),                    is_active=True                )
                
                if result:
                    QMessageBox.information(self, "Thành công", "Đã cập nhật danh mục thành công!")
                    self.refresh_table_with_loading()
                    dialog.accept()  # Close dialog after success
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể cập nhật danh mục")
            except Exception as e:
                QMessageBox.critical(self, "Lỗi", f"Lỗi khi cập nhật danh mục: {str(e)}")

    def delete_category(self):
        selected_row = self.category_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn danh mục cần xóa")
            return
            
        category_name = self.category_table.item(selected_row, 1).text()
        reply = QMessageBox.question(self, "Xác nhận xóa", 
                                   f"Bạn có chắc chắn muốn xóa danh mục '{category_name}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            categories = self.category_manager.load_categories()
            category = None
            for cat in categories:
                if cat.get('name') == category_name and cat.get('user_id') == 'system':
                    category = cat
                    break
                    
            if category:
                try:
                    # Use the category_id to delete
                    self.category_manager.delete_category(
                        category.get('category_id'),
                        'system',  # current_user_id
                        True       # is_admin           
                    )
                    
                    if result:
                        QMessageBox.information(self, "Thành công", "Đã xóa danh mục thành công!")
                        self.refresh_table_with_loading()
                    else:
                        QMessageBox.warning(self, "Lỗi", "Không thể xóa danh mục")
                except Exception as e:
                    QMessageBox.critical(self, "Lỗi", f"Lỗi khi xóa danh mục: {str(e)}")
            else:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy danh mục")
                
    def refresh_table_with_loading(self):
        """Refresh table with loading indicator"""
        # Show loading message
        self.category_table.setRowCount(1)
        loading_item = QTableWidgetItem("Đang tải dữ liệu...")
        loading_item.setTextAlignment(4)  # Center alignment
        self.category_table.setItem(0, 1, loading_item)
        
        # Process events to show loading message
        from PyQt5.QtCore import QCoreApplication
        QCoreApplication.processEvents()
        
        # Load actual data
        self.load_categories_table()
