from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QComboBox, QLineEdit, QDateEdit, QMessageBox, QInputDialog,
                            QTextEdit, QFrame, QGridLayout, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import QDate, Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIcon
import datetime

class UserTransactionForm(QWidget):
    """
    Form thêm/chỉnh sửa giao dịch cho user với giao diện hiện đại
    """
    transaction_added = pyqtSignal()  # Signal khi thêm giao dịch thành công
    
    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.current_transaction = None  # Để edit transaction
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        header_layout = QVBoxLayout()
        
        title = QLabel('💰 Thêm giao dịch mới')
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        subtitle = QLabel('Nhập thông tin giao dịch của bạn')
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
        
        # Form content
        form_frame = QFrame()
        form_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #e2e8f0;
                padding: 25px;
            }
        """)
        
        form_layout = QGridLayout()
        form_layout.setSpacing(20)
        
        # Style cho labels và inputs
        label_style = """
            QLabel {
                color: #374151;
                font-weight: 600;
                font-size: 14px;
                margin-bottom: 5px;
            }
        """
        
        input_style = """
            QLineEdit, QComboBox, QDateEdit {
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8fafc;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
        """
        
        # Row 0: Loại giao dịch và Số tiền
        type_label = QLabel('📊 Loại giao dịch')
        type_label.setStyleSheet(label_style)
        self.type_combo = QComboBox()
        self.type_combo.addItems(['💸 Chi tiêu', '💰 Thu nhập'])
        self.type_combo.setStyleSheet(input_style)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        
        amount_label = QLabel('💵 Số tiền')
        amount_label.setStyleSheet(label_style)
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText('VD: 50000')
        self.amount_input.setStyleSheet(input_style)
        self.amount_input.textChanged.connect(self.format_amount)
        
        form_layout.addWidget(type_label, 0, 0)
        form_layout.addWidget(self.type_combo, 1, 0)
        form_layout.addWidget(amount_label, 0, 1)
        form_layout.addWidget(self.amount_input, 1, 1)
        
        # Row 2: Danh mục
        category_label = QLabel('🏷️ Danh mục')
        category_label.setStyleSheet(label_style)
        
        category_layout = QHBoxLayout()
        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet(input_style)
        self.reload_categories()
        
        btn_add_cat = QPushButton('+ Thêm mới')
        btn_add_cat.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 12px;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        btn_add_cat.clicked.connect(self.add_category_dialog)
        
        category_layout.addWidget(self.category_combo, 3)
        category_layout.addWidget(btn_add_cat, 1)
        
        form_layout.addWidget(category_label, 2, 0, 1, 2)
        form_layout.addLayout(category_layout, 3, 0, 1, 2)
        
        # Row 4: Ngày
        date_label = QLabel('📅 Ngày giao dịch')
        date_label.setStyleSheet(label_style)
        self.date_edit = QDateEdit(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet(input_style)
        self.date_edit.setDisplayFormat('dd/MM/yyyy')
        
        form_layout.addWidget(date_label, 4, 0)
        form_layout.addWidget(self.date_edit, 5, 0)
        
        # Row 4 col 2: Wallet (nếu có)
        wallet_label = QLabel('👛 Ví/Tài khoản')
        wallet_label.setStyleSheet(label_style)
        self.wallet_combo = QComboBox()
        self.wallet_combo.addItem('💳 Ví mặc định', 'default')
        self.wallet_combo.setStyleSheet(input_style)
        
        form_layout.addWidget(wallet_label, 4, 1)
        form_layout.addWidget(self.wallet_combo, 5, 1)
        
        # Row 6: Ghi chú (full width)
        note_label = QLabel('📝 Ghi chú')
        note_label.setStyleSheet(label_style)
        self.note_input = QTextEdit()
        self.note_input.setPlaceholderText('Mô tả chi tiết về giao dịch (không bắt buộc)')
        self.note_input.setMaximumHeight(80)
        self.note_input.setStyleSheet("""
            QTextEdit {
                padding: 12px 15px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f8fafc;
            }
            QTextEdit:focus {
                border-color: #667eea;
                background-color: white;
            }
        """)
        
        form_layout.addWidget(note_label, 6, 0, 1, 2)
        form_layout.addWidget(self.note_input, 7, 0, 1, 2)
        
        form_frame.setLayout(form_layout)
        layout.addWidget(form_frame)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        btn_cancel = QPushButton('❌ Hủy')
        btn_cancel.setStyleSheet("""
            QPushButton {
                background: #6b7280;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #4b5563;
            }
        """)
        btn_cancel.clicked.connect(self.clear_form)
        
        btn_save = QPushButton('💾 Lưu giao dịch')
        btn_save.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px 30px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5a67d8, stop:1 #6b46c1);
            }
        """)
        btn_save.clicked.connect(self.save_transaction)
        
        button_layout.addStretch()
        button_layout.addWidget(btn_cancel)
        button_layout.addWidget(btn_save)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
        
        # Set window background
        self.setStyleSheet("""
            QWidget {
                background-color: #f1f5f9;
            }
        """)    
    def on_type_changed(self, text):
        """Cập nhật danh mục theo loại giao dịch"""
        self.reload_categories()
    
    def format_amount(self, text):
        """Format số tiền khi nhập"""
        # Loại bỏ tất cả ký tự không phải số
        clean_text = ''.join(filter(str.isdigit, text))
        if clean_text:
            # Format với dấu phẩy
            formatted = f"{int(clean_text):,}"
            # Cập nhật text mà không trigger signal
            self.amount_input.blockSignals(True)
            self.amount_input.setText(formatted)
            self.amount_input.blockSignals(False)
    
    def reload_categories(self):
        """Tải lại danh mục theo loại giao dịch"""
        self.category_combo.clear()
        user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
        
        # Xác định loại giao dịch hiện tại
        is_expense = self.type_combo.currentText().startswith('💸')
        tx_type = 'expense' if is_expense else 'income'
        
        # Lấy danh mục từ manager hoặc file JSON
        try:
            import json
            with open('data/categories.json', 'r', encoding='utf-8') as f:
                all_categories = json.load(f)
        except:
            all_categories = getattr(self.category_manager, 'categories', [])
        
        # Lọc danh mục theo user và loại
        categories = []
        for cat in all_categories:
            # Danh mục của user hoặc danh mục chung
            if cat.get('user_id') is None or cat.get('user_id') == user_id:
                # Lọc theo loại nếu có
                cat_type = cat.get('type', 'both')
                if cat_type == 'both' or cat_type == tx_type:
                    categories.append(cat)
        
        # Thêm icon cho từng danh mục
        category_icons = {
            'food': '🍽️', 'transport': '🚗', 'shopping': '🛒', 'health': '🏥',
            'entertainment': '🎬', 'education': '📚', 'utilities': '💡', 'rent': '🏠',
            'salary': '💰', 'business': '💼', 'investment': '📈', 'gift': '🎁',
            'other': '📦'
        }
        
        for cat in categories:
            cat_name = cat.get('name', 'Không tên')
            cat_id = cat.get('id') or cat.get('category_id')
            icon = category_icons.get(cat.get('icon', 'other'), '📦')
            
            display_name = f"{icon} {cat_name}"
            self.category_combo.addItem(display_name, cat_id)    
    def add_category_dialog(self):
        """Dialog thêm danh mục mới với giao diện đẹp"""
        dialog = QInputDialog(self)
        dialog.setWindowTitle('🏷️ Tạo danh mục mới')
        dialog.setLabelText('Nhập tên danh mục:')
        dialog.setTextValue('')
        dialog.resize(400, 150)
        
        # Style cho dialog
        dialog.setStyleSheet("""
            QInputDialog {
                background-color: white;
            }
            QLabel {
                font-size: 14px;
                color: #374151;
                font-weight: 600;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
            QPushButton {
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: 600;
            }
        """)
        
        if dialog.exec_() == QInputDialog.Accepted:
            name = dialog.textValue().strip()
            if not name:
                return
                
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            
            # Kiểm tra trùng tên
            try:
                import json
                with open('data/categories.json', 'r', encoding='utf-8') as f:
                    all_categories = json.load(f)
            except:
                all_categories = getattr(self.category_manager, 'categories', [])
            
            for c in all_categories:
                if (c.get('name', '').lower() == name.lower() and 
                    (c.get('user_id') is None or c.get('user_id') == user_id)):
                    QMessageBox.warning(self, '⚠️ Lỗi', 
                                      f'Danh mục "{name}" đã tồn tại!')
                    return
            
            # Tạo danh mục mới
            is_expense = self.type_combo.currentText().startswith('💸')
            cat_type = 'expense' if is_expense else 'income'
            
            new_cat = {
                'id': f'usercat_{user_id}_{len(all_categories)+1}',
                'name': name,
                'user_id': user_id,
                'type': cat_type,
                'icon': 'other',
                'created_at': datetime.datetime.now().isoformat()
            }
            
            # Thêm vào danh sách
            all_categories.append(new_cat)
            
            # Lưu vào file
            try:
                with open('data/categories.json', 'w', encoding='utf-8') as f:
                    json.dump(all_categories, f, ensure_ascii=False, indent=2)
                
                # Cập nhật manager nếu có
                if hasattr(self.category_manager, 'categories'):
                    self.category_manager.categories = all_categories
                if hasattr(self.category_manager, 'save'):
                    self.category_manager.save()
                    
                self.reload_categories()
                
                # Tự động chọn danh mục vừa tạo
                for i in range(self.category_combo.count()):
                    if self.category_combo.itemData(i) == new_cat['id']:
                        self.category_combo.setCurrentIndex(i)
                        break
                
                QMessageBox.information(self, '✅ Thành công', 
                                      f'Đã tạo danh mục "{name}" thành công!')
                                      
            except Exception as e:
                QMessageBox.critical(self, '❌ Lỗi', 
                                   f'Không thể lưu danh mục: {str(e)}')

    def clear_form(self):
        """Xóa form và reset về trạng thái ban đầu"""
        self.amount_input.clear()
        self.note_input.clear()
        self.date_edit.setDate(QDate.currentDate())
        self.type_combo.setCurrentIndex(0)
        self.wallet_combo.setCurrentIndex(0)
        self.reload_categories()
        
    def validate_form(self):
        """Kiểm tra tính hợp lệ của form"""
        errors = []
        
        # Kiểm tra số tiền
        amount_text = self.amount_input.text().replace(',', '').strip()
        if not amount_text:
            errors.append('Vui lòng nhập số tiền')
        else:
            try:
                amount = float(amount_text)
                if amount <= 0:
                    errors.append('Số tiền phải lớn hơn 0')
                elif amount > 999999999:
                    errors.append('Số tiền quá lớn')
            except ValueError:
                errors.append('Số tiền không hợp lệ')
        
        # Kiểm tra danh mục
        if self.category_combo.count() == 0:
            errors.append('Vui lòng chọn danh mục')
        elif not self.category_combo.currentData():
            errors.append('Danh mục không hợp lệ')
        
        # Kiểm tra ngày
        selected_date = self.date_edit.date().toPyDate()
        today = datetime.date.today()
        if selected_date > today:
            errors.append('Ngày không thể ở tương lai')
        
        return errors    
    def save_transaction(self):
        """Lưu giao dịch với validation đầy đủ"""
        # Validate form
        errors = self.validate_form()
        if errors:
            error_msg = "Vui lòng sửa các lỗi sau:\n\n" + "\n".join(f"• {error}" for error in errors)
            QMessageBox.warning(self, '⚠️ Lỗi nhập liệu', error_msg)
            return
        
        try:
            # Lấy dữ liệu từ form
            amount_text = self.amount_input.text().replace(',', '').strip()
            amount = float(amount_text)
            
            is_expense = self.type_combo.currentText().startswith('💸')
            tx_type = 'expense' if is_expense else 'income'
            
            cat_id = self.category_combo.currentData()
            date = self.date_edit.date().toString('yyyy-MM-dd')
            note = self.note_input.toPlainText().strip()
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            wallet_id = self.wallet_combo.currentData()
            
            # Tạo giao dịch mới
            import json
            
            # Đọc dữ liệu hiện tại
            try:
                with open('data/transactions.json', 'r', encoding='utf-8') as f:
                    all_transactions = json.load(f)
            except:
                all_transactions = []
            
            # Tạo ID mới
            max_id = 0
            for tx in all_transactions:
                try:
                    tx_id = tx.get('id', '')
                    if tx_id.startswith('tx_'):
                        num = int(tx_id.split('_')[-1])
                        max_id = max(max_id, num)
                except:
                    continue
            
            new_tx = {
                'id': f'tx_{user_id}_{max_id + 1}',
                'user_id': user_id,
                'type': tx_type,
                'amount': amount,
                'category_id': cat_id,
                'date': date + 'T00:00:00Z',
                'note': note,
                'wallet_id': wallet_id,
                'created_at': datetime.datetime.now().isoformat(),
                'updated_at': datetime.datetime.now().isoformat()
            }
            
            # Thêm vào danh sách
            all_transactions.append(new_tx)
            
            # Lưu vào file
            with open('data/transactions.json', 'w', encoding='utf-8') as f:
                json.dump(all_transactions, f, ensure_ascii=False, indent=2)
            
            # Cập nhật manager nếu có
            if hasattr(self.transaction_manager, 'transactions'):
                self.transaction_manager.transactions = all_transactions
            if hasattr(self.transaction_manager, 'save'):
                self.transaction_manager.save()
            
            # Hiển thị thông báo thành công
            tx_type_text = "chi tiêu" if is_expense else "thu nhập"
            success_msg = (f"✅ Đã thêm giao dịch {tx_type_text} thành công!\n\n"
                          f"💰 Số tiền: {amount:,.0f} đ\n"
                          f"📅 Ngày: {self.date_edit.date().toString('dd/MM/yyyy')}\n"
                          f"🏷️ Danh mục: {self.category_combo.currentText()}")
            
            QMessageBox.information(self, '🎉 Thành công', success_msg)
            
            # Emit signal để cập nhật UI khác
            self.transaction_added.emit()
            
            # Clear form
            self.clear_form()
            
        except Exception as e:
            QMessageBox.critical(self, '❌ Lỗi', 
                               f'Không thể lưu giao dịch:\n{str(e)}')
    
    def set_transaction_for_edit(self, transaction):
        """Thiết lập form để chỉnh sửa giao dịch"""
        self.current_transaction = transaction
        
        # Cập nhật tiêu đề
        header_title = self.findChild(QLabel)
        if header_title:
            header_title.setText('✏️ Chỉnh sửa giao dịch')
        
        # Điền dữ liệu vào form
        self.amount_input.setText(f"{transaction.get('amount', 0):,.0f}")
        
        # Chọn loại giao dịch
        if transaction.get('type') == 'expense':
            self.type_combo.setCurrentText('💸 Chi tiêu')
        else:
            self.type_combo.setCurrentText('💰 Thu nhập')
        
        # Chọn danh mục
        cat_id = transaction.get('category_id')
        for i in range(self.category_combo.count()):
            if self.category_combo.itemData(i) == cat_id:
                self.category_combo.setCurrentIndex(i)
                break
        
        # Đặt ngày
        try:
            date_str = transaction.get('date', '')
            if 'T' in date_str:
                date_str = date_str.split('T')[0]
            date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            self.date_edit.setDate(QDate(date_obj))
        except:
            pass
        
        # Ghi chú
        self.note_input.setPlainText(transaction.get('note', ''))
        
        # Cập nhật nút lưu
        save_button = self.findChildren(QPushButton)[-1]  # Nút cuối cùng
        save_button.setText('💾 Cập nhật giao dịch')
