from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, QMessageBox, QHeaderView, QInputDialog
from PyQt5.QtCore import Qt

class UserCategoryTab(QWidget):
    """
    Tab quản lý danh mục chi tiêu cho user: thêm, sửa, xoá danh mục cá nhân.
    """
    def __init__(self, category_manager, user_id, reload_callback=None, parent=None):
        super().__init__(parent)
        self.category_manager = category_manager
        self.user_id = user_id
        self.reload_callback = reload_callback  # callback để reload category ở các tab khác
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        title = QLabel('Quản lý danh mục của bạn')
        title.setStyleSheet('font-size:18px; font-weight:bold;')
        layout.addWidget(title)

        # Bảng danh mục
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Tên danh mục', 'Sửa', 'Xoá'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

        # Thêm mới danh mục
        add_layout = QHBoxLayout()
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText('Nhập tên danh mục mới...')
        btn_add = QPushButton('Thêm danh mục')
        btn_add.clicked.connect(self.add_category)
        add_layout.addWidget(self.input_name)
        add_layout.addWidget(btn_add)
        layout.addLayout(add_layout)

        self.setLayout(layout)
        self.reload_table()

    def reload_table(self):
        # Lấy danh mục hệ thống + user
        categories = [c for c in getattr(self.category_manager, 'categories', []) if c.get('user_id') is None or c.get('user_id') == self.user_id]
        self.table.setRowCount(len(categories))
        for i, cat in enumerate(categories):
            self.table.setItem(i, 0, QTableWidgetItem(cat.get('name', 'Không tên')))
            # Sửa
            btn_edit = QPushButton('Sửa')
            btn_edit.clicked.connect(lambda _, row=i: self.edit_category(row))
            self.table.setCellWidget(i, 1, btn_edit)
            # Xoá
            btn_del = QPushButton('Xoá')
            btn_del.clicked.connect(lambda _, row=i: self.delete_category(row))
            # Chỉ cho xoá nếu là category của user
            if cat.get('user_id') == self.user_id:
                self.table.setCellWidget(i, 2, btn_del)
            else:
                self.table.setCellWidget(i, 2, QLabel('(Hệ thống)'))
        self.table.resizeRowsToContents()

    def add_category(self):
        name = self.input_name.text().strip()
        if not name:
            QMessageBox.warning(self, 'Lỗi', 'Tên danh mục không được để trống!')
            return
        # Check trùng tên
        for c in self.category_manager.categories:
            if c.get('name', '').lower() == name.lower() and (c.get('user_id') is None or c.get('user_id') == self.user_id):
                QMessageBox.warning(self, 'Lỗi', 'Danh mục đã tồn tại!')
                return
        # Thêm mới
        new_cat = {
            'id': f'usercat_{self.user_id}_{len(self.category_manager.categories)+1}',
            'name': name,
            'user_id': self.user_id
        }
        self.category_manager.categories.append(new_cat)
        if hasattr(self.category_manager, 'save'):
            self.category_manager.save()
        self.input_name.clear()
        self.reload_table()
        if self.reload_callback:
            self.reload_callback()

    def edit_category(self, row):
        cat = [c for c in self.category_manager.categories if c.get('user_id') is None or c.get('user_id') == self.user_id][row]
        if cat.get('user_id') != self.user_id:
            QMessageBox.information(self, 'Thông báo', 'Không thể sửa danh mục hệ thống!')
            return
        new_name, ok = QInputDialog.getText(self, 'Sửa danh mục', 'Tên mới:', text=cat.get('name', ''))
        if ok and new_name.strip():
            cat['name'] = new_name.strip()
            if hasattr(self.category_manager, 'save'):
                self.category_manager.save()
            self.reload_table()
            if self.reload_callback:
                self.reload_callback()

    def delete_category(self, row):
        cat = [c for c in self.category_manager.categories if c.get('user_id') is None or c.get('user_id') == self.user_id][row]
        if cat.get('user_id') != self.user_id:
            QMessageBox.information(self, 'Thông báo', 'Không thể xoá danh mục hệ thống!')
            return
        # Kiểm tra có giao dịch liên quan không
        if hasattr(self.category_manager, 'transaction_manager'):
            txs = self.category_manager.transaction_manager.get_transactions_by_category(cat['id'])
            if txs:
                QMessageBox.warning(self, 'Lỗi', 'Không thể xoá danh mục đã có giao dịch!')
                return
        # Xoá
        self.category_manager.categories.remove(cat)
        if hasattr(self.category_manager, 'save'):
            self.category_manager.save()
        self.reload_table()
        if self.reload_callback:
            self.reload_callback()
