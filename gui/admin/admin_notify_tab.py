from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit, QComboBox, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox

class AdminNotifyTab(QWidget):
    def __init__(self, notification_manager, parent=None):
        super().__init__(parent)
        self.notification_manager = notification_manager
        self.init_ui()
        self.load_notifications_table()

    def init_ui(self):
        layout = QVBoxLayout(self)
        self.notify_title = QLineEdit(); self.notify_title.setPlaceholderText("Tiêu đề thông báo")
        self.notify_content = QTextEdit(); self.notify_content.setPlaceholderText("Nội dung thông báo")
        self.notify_type = QComboBox(); self.notify_type.addItems(["Tin tức", "Cảnh báo", "Bảo trì"])
        send_btn = QPushButton("Gửi thông báo")
        send_btn.clicked.connect(self.send_notification)
        layout.addWidget(self.notify_title)
        layout.addWidget(self.notify_content)
        layout.addWidget(self.notify_type)
        layout.addWidget(send_btn)
        self.notify_table = QTableWidget(0, 6)
        self.notify_table.setHorizontalHeaderLabels([
            "Tiêu đề", "Nội dung", "Loại", "Ngày gửi", "Ưu tiên", "Trạng thái"
        ])
        self.notify_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.notify_table.horizontalHeader().setStretchLastSection(True)
        self.notify_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.notify_table)
        btn_layout = QHBoxLayout()
        self.btn_view_notify = QPushButton("Xem chi tiết")
        self.btn_mark_read = QPushButton("Đánh dấu đã đọc")
        self.btn_delete_notify = QPushButton("Xóa thông báo")        
        btn_layout.addWidget(self.btn_view_notify)
        btn_layout.addWidget(self.btn_mark_read)
        btn_layout.addWidget(self.btn_delete_notify)
        layout.addLayout(btn_layout)
        
        # Kết nối các nút với các hàm
        self.btn_view_notify.clicked.connect(self.view_notification_detail)
        self.btn_mark_read.clicked.connect(self.mark_notification_read)
        self.btn_delete_notify.clicked.connect(self.delete_notification)
        self.notify_title.returnPressed.connect(self.send_notification)

    def load_notifications_table(self, current_user_id=None):
        notifications = self.notification_manager.get_all_notifications()
        filtered = []
        for n in notifications:
            if not n.get('user_id') or (current_user_id and n.get('user_id') == current_user_id):
                filtered.append(n)
        self.notify_table.setRowCount(0)
        for n in filtered:
            row = self.notify_table.rowCount()
            self.notify_table.insertRow(row)
            title = n.get('title', '')
            content = n.get('message', n.get('content', ''))
            notify_type = n.get('type', '')
            created_at = n.get('created_at', '')
            created_at_fmt = self.format_datetime(created_at)
            priority = n.get('priority', '')
            is_read = n.get('is_read', False)
            status = 'Đã đọc' if is_read else 'Chưa đọc'
            self.notify_table.setItem(row, 0, QTableWidgetItem(title))
            self.notify_table.setItem(row, 1, QTableWidgetItem(content))
            self.notify_table.setItem(row, 2, QTableWidgetItem(notify_type))
            self.notify_table.setItem(row, 3, QTableWidgetItem(created_at_fmt))
            self.notify_table.setItem(row, 4, QTableWidgetItem(priority))
            self.notify_table.setItem(row, 5, QTableWidgetItem(status))

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

    def clear_form(self):
        """Clear all input fields"""
        self.notify_title.clear()
        self.notify_content.clear()
        self.notify_type.setCurrentIndex(0)

    def send_notification(self):
        title = self.notify_title.text().strip()
        content = self.notify_content.toPlainText().strip()
        notify_type = self.notify_type.currentText()
        if not title or not content:
            QMessageBox.warning(self, 'Thiếu thông tin', 'Vui lòng nhập tiêu đề và nội dung!')
            return
        
        try:
            self.notification_manager.add_notification(title, content, notify_type)
            QMessageBox.information(self, 'Thành công', 'Đã gửi thông báo!')
            self.load_notifications_table()
            self.clear_form()  # Clear form after successful addition
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Không thể gửi thông báo: {str(e)}')

    def view_notification_detail(self):
        selected_row = self.notify_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn thông báo cần xem")
            return
            
        title = self.notify_table.item(selected_row, 0).text()
        content = self.notify_table.item(selected_row, 1).text()
        notify_type = self.notify_table.item(selected_row, 2).text()
        created_at = self.notify_table.item(selected_row, 3).text()
        priority = self.notify_table.item(selected_row, 4).text()
        status = self.notify_table.item(selected_row, 5).text()
        
        detail_text = f"""
Tiêu đề: {title}
Loại: {notify_type}
Ngày gửi: {created_at}
Ưu tiên: {priority}
Trạng thái: {status}

Nội dung:
{content}
        """
        
        QMessageBox.information(self, "Chi tiết thông báo", detail_text.strip())

    def mark_notification_read(self):
        selected_row = self.notify_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn thông báo cần đánh dấu")
            return
            
        title = self.notify_table.item(selected_row, 0).text()
          # Tìm notification trong danh sách
        notifications = self.notification_manager.get_all_notifications()
        notification_to_update = None
        for notification in notifications:
            if notification.get('title') == title:
                notification_to_update = notification
                break
                
        if notification_to_update:
            # Sử dụng method update_notification có sẵn
            success = self.notification_manager.update_notification(
                notification_to_update.get('id') or notification_to_update.get('notification_id'),
                is_read=True
            )
            
            if success:
                QMessageBox.information(self, "Thành công", "Đã đánh dấu thông báo là đã đọc!")
                self.load_notifications_table()
            else:
                QMessageBox.warning(self, "Lỗi", "Không thể đánh dấu thông báo!")
        else:
            QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông báo!")

    def delete_notification(self):
        selected_row = self.notify_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Cảnh báo", "Vui lòng chọn thông báo cần xóa")
            return
            
        title = self.notify_table.item(selected_row, 0).text()
        
        reply = QMessageBox.question(self, "Xác nhận xóa", 
                                   f"Bạn có chắc chắn muốn xóa thông báo '{title}'?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Tìm notification để xóa
            notifications = self.notification_manager.get_all_notifications()
            notification_to_delete = None
            for n in notifications:
                if n.get('title') == title:
                    notification_to_delete = n
                    break
            
            if notification_to_delete:
                # Sử dụng method delete_notification có sẵn
                success = self.notification_manager.delete_notification(
                    notification_to_delete.get('id') or notification_to_delete.get('notification_id')
                )
                
                if success:
                    QMessageBox.information(self, "Thành công", "Đã xóa thông báo!")
                    self.load_notifications_table()
                else:
                    QMessageBox.warning(self, "Lỗi", "Không thể xóa thông báo!")
            else:
                QMessageBox.warning(self, "Lỗi", "Không tìm thấy thông báo!")
