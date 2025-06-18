from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QComboBox, QLineEdit, QCheckBox, QSpinBox,
                            QTabWidget, QFormLayout, QGroupBox, QMessageBox,
                            QFileDialog, QProgressBar, QTextEdit, QDateEdit,
                            QGridLayout, QSpacerItem, QSizePolicy, QSlider)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap
import datetime
import json
import os
import shutil

class UserSettings(QWidget):
    """
    Tab cài đặt toàn diện cho user
    """
    settings_changed = pyqtSignal()  # Signal khi có thay đổi cài đặt
    
    def __init__(self, user_manager, wallet_manager, category_manager, settings_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.wallet_manager = wallet_manager
        self.category_manager = category_manager
        self.settings_manager = settings_manager
        self.settings = {}
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #8b5cf6);
                border-radius: 15px;
                padding: 20px;
                margin-bottom: 20px;
            }
        """)
        header_layout = QVBoxLayout()
        
        title = QLabel('⚙️ Cài đặt & Quản lý')
        title.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 24px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        subtitle = QLabel('Tùy chỉnh ứng dụng theo sở thích của bạn')
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
        
        # Main settings tabs
        self.settings_tabs = QTabWidget()
        self.settings_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #f8fafc;
                color: #6b7280;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 600;
            }
            QTabBar::tab:selected {
                background: white;
                color: #6366f1;
                border-bottom: 2px solid #6366f1;
            }
            QTabBar::tab:hover:!selected {
                background: #e2e8f0;
            }
        """)
        
        # Create tabs
        self.create_appearance_tab()
        self.create_notifications_tab()
        self.create_data_tab()
        
        layout.addWidget(self.settings_tabs)
        self.setLayout(layout)
        
        # Set background
        self.setStyleSheet("""
            QWidget {
                background-color: #f1f5f9;
            }
        """)

    def create_appearance_tab(self):
        """Tab cài đặt giao diện"""
        appearance_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Theme settings
        theme_group = QGroupBox('🎨 Giao diện')
        theme_group.setStyleSheet(self.get_group_style())
        
        theme_layout = QFormLayout()
        theme_layout.setSpacing(15)
        
        # Theme selection
        theme_label = QLabel('🌓 Chế độ màn hình:')
        theme_label.setStyleSheet("font-weight: 600; color: #374151;")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(['Sáng', 'Tối', 'Tự động theo hệ thống'])
        self.theme_combo.setStyleSheet(self.get_input_style())
        
        # Font size
        font_size_label = QLabel('📝 Kích thước chữ:')
        font_size_label.setStyleSheet("font-weight: 600; color: #374151;")
        self.font_size_slider = QSlider(Qt.Horizontal)
        self.font_size_slider.setRange(12, 20)
        self.font_size_slider.setValue(14)
        self.font_size_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 6px;
                background: #e2e8f0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: #6366f1;
                border: none;
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -6px 0;
            }
            QSlider::sub-page:horizontal {
                background: #6366f1;
                border-radius: 3px;
            }
        """)
        self.font_size_label = QLabel('14px')
        font_size_container = QHBoxLayout()
        font_size_container.addWidget(self.font_size_slider)
        font_size_container.addWidget(self.font_size_label)
        
        self.font_size_slider.valueChanged.connect(
            lambda v: self.font_size_label.setText(f'{v}px')
        )
        
        # Currency format
        currency_label = QLabel('💰 Định dạng tiền tệ:')
        currency_label.setStyleSheet("font-weight: 600; color: #374151;")
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(['VND', 'USD', 'EUR'])
        self.currency_combo.setStyleSheet(self.get_input_style())
        
        # Date format
        date_format_label = QLabel('📅 Định dạng ngày:')
        date_format_label.setStyleSheet("font-weight: 600; color: #374151;")
        self.date_format_combo = QComboBox()
        self.date_format_combo.addItems(['DD/MM/YYYY', 'MM/DD/YYYY', 'YYYY-MM-DD'])
        self.date_format_combo.setStyleSheet(self.get_input_style())
        
        theme_layout.addRow(theme_label, self.theme_combo)
        theme_layout.addRow(font_size_label, font_size_container)
        theme_layout.addRow(currency_label, self.currency_combo)
        theme_layout.addRow(date_format_label, self.date_format_combo)
        
        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)
        
        # Dashboard settings
        dashboard_group = QGroupBox('📊 Dashboard')
        dashboard_group.setStyleSheet(self.get_group_style())
        
        dashboard_layout = QFormLayout()
        dashboard_layout.setSpacing(15)
        
        # Default chart type
        chart_label = QLabel('📈 Loại biểu đồ mặc định:')
        chart_label.setStyleSheet("font-weight: 600; color: #374151;")
        self.chart_combo = QComboBox()
        self.chart_combo.addItems(['Biểu đồ cột', 'Biểu đồ tròn', 'Biểu đồ đường'])
        self.chart_combo.setStyleSheet(self.get_input_style())
        
        # Transaction limit
        limit_label = QLabel('📋 Số giao dịch hiển thị:')
        limit_label.setStyleSheet("font-weight: 600; color: #374151;")
        self.transaction_limit = QSpinBox()
        self.transaction_limit.setRange(10, 100)
        self.transaction_limit.setValue(20)
        self.transaction_limit.setSuffix(' giao dịch')
        self.transaction_limit.setStyleSheet(self.get_input_style())
        
        dashboard_layout.addRow(chart_label, self.chart_combo)
        dashboard_layout.addRow(limit_label, self.transaction_limit)
        
        dashboard_group.setLayout(dashboard_layout)
        layout.addWidget(dashboard_group)
        
        layout.addStretch()
        appearance_widget.setLayout(layout)
        self.settings_tabs.addTab(appearance_widget, '🎨 Giao diện')

    def create_notifications_tab(self):
        """Tab cài đặt thông báo"""
        notifications_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Budget notifications
        budget_group = QGroupBox('💰 Thông báo ngân sách')
        budget_group.setStyleSheet(self.get_group_style())
        
        budget_layout = QVBoxLayout()
        budget_layout.setSpacing(15)
        
        self.budget_warning_check = QCheckBox('⚠️ Cảnh báo khi vượt 80% ngân sách')
        self.budget_warning_check.setStyleSheet(self.get_checkbox_style())
        
        self.budget_exceeded_check = QCheckBox('🚨 Thông báo khi vượt ngân sách')
        self.budget_exceeded_check.setStyleSheet(self.get_checkbox_style())
        
        self.daily_summary_check = QCheckBox('📊 Tóm tắt chi tiêu hàng ngày')
        self.daily_summary_check.setStyleSheet(self.get_checkbox_style())
        
        budget_layout.addWidget(self.budget_warning_check)
        budget_layout.addWidget(self.budget_exceeded_check)
        budget_layout.addWidget(self.daily_summary_check)
        
        budget_group.setLayout(budget_layout)
        layout.addWidget(budget_group)
        
        # Reminder notifications
        reminder_group = QGroupBox('⏰ Nhắc nhở')
        reminder_group.setStyleSheet(self.get_group_style())
        
        reminder_layout = QVBoxLayout()
        reminder_layout.setSpacing(15)
        
        # Monthly report
        self.monthly_check = QCheckBox('📈 Báo cáo tháng')
        self.monthly_check.setStyleSheet(self.get_checkbox_style())
        
        # Backup reminder
        self.backup_check = QCheckBox('💾 Nhắc sao lưu dữ liệu')
        self.backup_check.setStyleSheet(self.get_checkbox_style())
        
        # Update reminder
        self.update_check = QCheckBox('🔄 Thông báo cập nhật')
        self.update_check.setStyleSheet(self.get_checkbox_style())
        
        reminder_layout.addWidget(self.monthly_check)
        reminder_layout.addWidget(self.backup_check)
        reminder_layout.addWidget(self.update_check)
        
        reminder_group.setLayout(reminder_layout)
        layout.addWidget(reminder_group)
        
        layout.addStretch()
        notifications_widget.setLayout(layout)
        self.settings_tabs.addTab(notifications_widget, '🔔 Thông báo')

    def create_data_tab(self):
        """Tab quản lý dữ liệu"""
        data_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Backup/Restore
        backup_group = QGroupBox('💾 Sao lưu & Khôi phục')
        backup_group.setStyleSheet(self.get_group_style())
        
        backup_layout = QVBoxLayout()
        backup_layout.setSpacing(15)
        
        # Backup buttons
        backup_btn = QPushButton('📤 Sao lưu dữ liệu')
        backup_btn.setStyleSheet(self.get_button_style('#10b981'))
        backup_btn.clicked.connect(self.backup_data)
        
        restore_btn = QPushButton('📥 Khôi phục dữ liệu')
        restore_btn.setStyleSheet(self.get_button_style('#3b82f6'))
        restore_btn.clicked.connect(self.restore_data)
        
        backup_layout.addWidget(backup_btn)
        backup_layout.addWidget(restore_btn)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Export/Import
        export_group = QGroupBox('📊 Xuất/Nhập dữ liệu')
        export_group.setStyleSheet(self.get_group_style())
        
        export_layout = QVBoxLayout()
        export_layout.setSpacing(15)
        
        export_csv_btn = QPushButton('📄 Xuất CSV')
        export_csv_btn.setStyleSheet(self.get_button_style('#f59e0b'))
        export_csv_btn.clicked.connect(self.export_csv)
        
        import_csv_btn = QPushButton('📄 Nhập CSV')
        import_csv_btn.setStyleSheet(self.get_button_style('#8b5cf6'))
        import_csv_btn.clicked.connect(self.import_csv)
        
        export_layout.addWidget(export_csv_btn)
        export_layout.addWidget(import_csv_btn)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        layout.addStretch()
        data_widget.setLayout(layout)
        self.settings_tabs.addTab(data_widget, '💾 Dữ liệu')

    def get_input_style(self):
        return """
            QComboBox, QSpinBox, QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 14px;
                background-color: #f8fafc;
            }
            QComboBox:focus, QSpinBox:focus, QLineEdit:focus {
                border-color: #6366f1;
                background-color: white;
            }
        """
        
    def get_group_style(self):
        return """
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #374151;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """
        
    def get_checkbox_style(self):
        return """
            QCheckBox {
                font-size: 14px;
                color: #374151;
                padding: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #d1d5db;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #6366f1;
                border-color: #6366f1;
            }
        """
        
    def get_button_style(self, color):
        return f"""
            QPushButton {{
                background: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: {color}cc;
            }}
        """
        
    def load_settings(self):
        """Load settings from file"""
        try:
            self.settings = self.settings_manager.load_settings()
                
            # Apply settings to UI
            if 'theme' in self.settings:
                index = self.theme_combo.findText(self.settings['theme'])
                if index >= 0:
                    self.theme_combo.setCurrentIndex(index)
                    
            if 'font_size' in self.settings:
                self.font_size_slider.setValue(self.settings['font_size'])
                
            if 'currency' in self.settings:
                index = self.currency_combo.findText(self.settings['currency'])
                if index >= 0:
                    self.currency_combo.setCurrentIndex(index)
                    
            if 'date_format' in self.settings:
                index = self.date_format_combo.findText(self.settings['date_format'])
                if index >= 0:
                    self.date_format_combo.setCurrentIndex(index)
                    
            if 'chart_type' in self.settings:
                index = self.chart_combo.findText(self.settings['chart_type'])
                if index >= 0:
                    self.chart_combo.setCurrentIndex(index)
                    
            if 'transaction_limit' in self.settings:
                self.transaction_limit.setValue(self.settings['transaction_limit'])
                
            # Notification settings
            self.budget_warning_check.setChecked(self.settings.get('budget_warning', True))
            self.budget_exceeded_check.setChecked(self.settings.get('budget_exceeded', True))
            self.daily_summary_check.setChecked(self.settings.get('daily_summary', False))
            self.monthly_check.setChecked(self.settings.get('monthly_report', True))
            self.backup_check.setChecked(self.settings.get('backup_reminder', True))
            self.update_check.setChecked(self.settings.get('update_notification', True))
            
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.settings = {}

    def save_settings(self):
        """Save settings to file"""
        try:
            self.settings.update({
                'theme': self.theme_combo.currentText(),
                'font_size': self.font_size_slider.value(),
                'currency': self.currency_combo.currentText(),
                'date_format': self.date_format_combo.currentText(),
                'chart_type': self.chart_combo.currentText(),
                'transaction_limit': self.transaction_limit.value(),
                'budget_warning': self.budget_warning_check.isChecked(),
                'budget_exceeded': self.budget_exceeded_check.isChecked(),
                'daily_summary': self.daily_summary_check.isChecked(),
                'monthly_report': self.monthly_check.isChecked(),
                'backup_reminder': self.backup_check.isChecked(),
                'update_notification': self.update_check.isChecked(),
                'updated_at': datetime.datetime.now().isoformat()
            })
            self.settings_manager.save_settings(self.settings)
            QMessageBox.information(self, 'Thành công', 'Đã lưu cài đặt thành công!')
            self.settings_changed.emit()
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Không thể lưu cài đặt: {str(e)}')
            
    def backup_data(self):
        """Backup data to file"""
        try:
            backup_path = QFileDialog.getSaveFileName(self, "Chọn nơi lưu backup", 
                                                    f"backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.zip", 
                                                    "ZIP Files (*.zip)")[0]
            if backup_path:
                # Implementation for backup
                QMessageBox.information(self, 'Thông báo', 'Chức năng sao lưu đang được phát triển.')
                
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Lỗi khi sao lưu: {str(e)}')
            
    def restore_data(self):
        """Restore data from backup file"""
        try:
            backup_path = QFileDialog.getOpenFileName(self, "Chọn file backup", "", "ZIP Files (*.zip)")[0]
            if backup_path:
                # Implementation for restore
                QMessageBox.information(self, 'Thông báo', 'Chức năng khôi phục đang được phát triển.')
                
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Lỗi khi khôi phục: {str(e)}')
            
    def export_csv(self):
        """Export data to CSV"""
        try:
            export_path = QFileDialog.getSaveFileName(self, "Xuất dữ liệu CSV", 
                                                    f"transactions_{datetime.datetime.now().strftime('%Y%m%d')}.csv", 
                                                    "CSV Files (*.csv)")[0]
            if export_path:
                # Implementation for CSV export
                QMessageBox.information(self, 'Thông báo', 'Chức năng xuất CSV đang được phát triển.')
                
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Lỗi khi xuất CSV: {str(e)}')
            
    def import_csv(self):
        """Import data from CSV"""
        try:
            import_path = QFileDialog.getOpenFileName(self, "Nhập dữ liệu CSV", "", "CSV Files (*.csv)")[0]
            if import_path:
                # Implementation for CSV import
                QMessageBox.information(self, 'Thông báo', 'Chức năng nhập CSV đang được phát triển.')
                
        except Exception as e:
            QMessageBox.critical(self, 'Lỗi', f'Lỗi khi nhập CSV: {str(e)}')
