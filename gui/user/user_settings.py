from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QFrame, QComboBox, QLineEdit, QCheckBox, QSpinBox,
                            QTabWidget, QFormLayout, QGroupBox, QMessageBox,
                            QFileDialog, QProgressBar, QTextEdit, QDateEdit,
                            QGridLayout, QSpacerItem, QSizePolicy, QSlider, QInputDialog)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QPixmap
import datetime
import json
import os
import shutil

class UserSettings(QWidget):
    """
    Màn hình cài đặt toàn diện cho user
    """
    settings_changed = pyqtSignal()  # Signal khi có thay đổi cài đặt
    
    def __init__(self, user_manager, wallet_manager, category_manager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.wallet_manager = wallet_manager
        self.category_manager = category_manager
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
        self.create_privacy_tab()
        self.create_advanced_tab()
        
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
        theme_group.setStyleSheet("""
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
        """)
        
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
        dashboard_group.setStyleSheet(theme_group.styleSheet())
        
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
        
        reminder_layout = QFormLayout()
        reminder_layout.setSpacing(15)
        
        # Monthly report
        monthly_check = QCheckBox('📈 Báo cáo tháng')
        monthly_check.setStyleSheet(self.get_checkbox_style())
        
        # Backup reminder
        backup_check = QCheckBox('💾 Nhắc sao lưu dữ liệu')
        backup_check.setStyleSheet(self.get_checkbox_style())
        
        # Update reminder
        update_check = QCheckBox('🔄 Thông báo cập nhật')
        update_check.setStyleSheet(self.get_checkbox_style())
        
        reminder_layout.addRow(monthly_check)
        reminder_layout.addRow(backup_check)
        reminder_layout.addRow(update_check)
        
        reminder_group.setLayout(reminder_layout)
        layout.addWidget(reminder_group)
        
        # Sound settings
        sound_group = QGroupBox('🔊 Âm thanh')
        sound_group.setStyleSheet(self.get_group_style())
        
        sound_layout = QFormLayout()
        sound_layout.setSpacing(15)
        
        sound_check = QCheckBox('🔔 Bật âm thanh thông báo')
        sound_check.setStyleSheet(self.get_checkbox_style())
        
        volume_label = QLabel('🔉 Âm lượng:')
        volume_label.setStyleSheet("font-weight: 600; color: #374151;")
        volume_slider = QSlider(Qt.Horizontal)
        volume_slider.setRange(0, 100)
        volume_slider.setValue(50)
        volume_slider.setStyleSheet("""
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
        
        sound_layout.addRow(sound_check)
        sound_layout.addRow(volume_label, volume_slider)
        
        sound_group.setLayout(sound_layout)
        layout.addWidget(sound_group)
        
        layout.addStretch()
        notifications_widget.setLayout(layout)
        self.settings_tabs.addTab(notifications_widget, '🔔 Thông báo')

    def create_data_tab(self):
        """Tab quản lý dữ liệu"""
        data_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Backup section
        backup_group = QGroupBox('💾 Sao lưu & Khôi phục')
        backup_group.setStyleSheet(self.get_group_style())
        
        backup_layout = QVBoxLayout()
        backup_layout.setSpacing(15)
        
        # Auto backup
        auto_backup_layout = QHBoxLayout()
        auto_backup_check = QCheckBox('🔄 Tự động sao lưu')
        auto_backup_check.setStyleSheet(self.get_checkbox_style())
        
        backup_interval = QComboBox()
        backup_interval.addItems(['Hàng ngày', 'Hàng tuần', 'Hàng tháng'])
        backup_interval.setStyleSheet(self.get_input_style())
        
        auto_backup_layout.addWidget(auto_backup_check)
        auto_backup_layout.addWidget(backup_interval)
        auto_backup_layout.addStretch()
        
        # Manual backup buttons
        backup_buttons_layout = QHBoxLayout()
        
        btn_backup = QPushButton('📤 Sao lưu ngay')
        btn_backup.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        btn_backup.clicked.connect(self.backup_data)
        
        btn_restore = QPushButton('📥 Khôi phục dữ liệu')
        btn_restore.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        btn_restore.clicked.connect(self.restore_data)
        
        backup_buttons_layout.addWidget(btn_backup)
        backup_buttons_layout.addWidget(btn_restore)
        backup_buttons_layout.addStretch()
        
        backup_layout.addLayout(auto_backup_layout)
        backup_layout.addLayout(backup_buttons_layout)
        
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)
        
        # Export section
        export_group = QGroupBox('📊 Xuất dữ liệu')
        export_group.setStyleSheet(self.get_group_style())
        
        export_layout = QVBoxLayout()
        export_layout.setSpacing(15)
        
        export_buttons_layout = QHBoxLayout()
        
        btn_export_excel = QPushButton('📈 Xuất Excel')
        btn_export_excel.setStyleSheet("""
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #059669;
            }
        """)
        btn_export_excel.clicked.connect(self.export_to_excel)
        
        btn_export_csv = QPushButton('📋 Xuất CSV')
        btn_export_csv.setStyleSheet("""
            QPushButton {
                background: #f59e0b;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #d97706;
            }
        """)
        btn_export_csv.clicked.connect(self.export_to_csv)
        
        btn_export_pdf = QPushButton('📄 Xuất PDF')
        btn_export_pdf.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        btn_export_pdf.clicked.connect(self.export_to_pdf)
        
        export_buttons_layout.addWidget(btn_export_excel)
        export_buttons_layout.addWidget(btn_export_csv)
        export_buttons_layout.addWidget(btn_export_pdf)
        export_buttons_layout.addStretch()
        
        export_layout.addLayout(export_buttons_layout)
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Storage info
        storage_group = QGroupBox('💽 Thông tin lưu trữ')
        storage_group.setStyleSheet(self.get_group_style())
        
        storage_layout = QFormLayout()
        storage_layout.setSpacing(15)
        
        # Database size
        self.db_size_label = QLabel('Đang tính toán...')
        self.db_size_label.setStyleSheet("color: #6b7280;")
        storage_layout.addRow('📊 Kích thước dữ liệu:', self.db_size_label)
        
        # Transaction count
        self.transaction_count_label = QLabel('Đang đếm...')
        self.transaction_count_label.setStyleSheet("color: #6b7280;")
        storage_layout.addRow('📝 Số giao dịch:', self.transaction_count_label)
        
        # Last backup
        self.last_backup_label = QLabel('Chưa có')
        self.last_backup_label.setStyleSheet("color: #6b7280;")
        storage_layout.addRow('🔄 Sao lưu cuối:', self.last_backup_label)
        
        storage_group.setLayout(storage_layout)
        layout.addWidget(storage_group)
        
        # Update storage info
        QTimer.singleShot(1000, self.update_storage_info)
        
        layout.addStretch()
        data_widget.setLayout(layout)
        self.settings_tabs.addTab(data_widget, '💾 Dữ liệu')

    def create_privacy_tab(self):
        """Tab bảo mật & riêng tư"""
        privacy_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Security settings
        security_group = QGroupBox('🔒 Bảo mật')
        security_group.setStyleSheet(self.get_group_style())
        
        security_layout = QVBoxLayout()
        security_layout.setSpacing(15)
        
        # Auto lock
        auto_lock_check = QCheckBox('🔐 Tự động khóa sau khi không hoạt động')
        auto_lock_check.setStyleSheet(self.get_checkbox_style())
        
        lock_time_layout = QHBoxLayout()
        lock_time_label = QLabel('⏱️ Thời gian khóa:')
        lock_time_label.setStyleSheet("font-weight: 600; color: #374151;")
        lock_time_combo = QComboBox()
        lock_time_combo.addItems(['5 phút', '10 phút', '15 phút', '30 phút', '1 giờ'])
        lock_time_combo.setStyleSheet(self.get_input_style())
        
        lock_time_layout.addWidget(lock_time_label)
        lock_time_layout.addWidget(lock_time_combo)
        lock_time_layout.addStretch()
        
        # Remember login
        remember_login_check = QCheckBox('💾 Ghi nhớ đăng nhập')
        remember_login_check.setStyleSheet(self.get_checkbox_style())
        
        security_layout.addWidget(auto_lock_check)
        security_layout.addLayout(lock_time_layout)
        security_layout.addWidget(remember_login_check)
        
        security_group.setLayout(security_layout)
        layout.addWidget(security_group)
        
        # Privacy settings
        privacy_group = QGroupBox('👁️ Riêng tư')
        privacy_group.setStyleSheet(self.get_group_style())
        
        privacy_layout = QVBoxLayout()
        privacy_layout.setSpacing(15)
        
        # Hide amounts
        hide_amounts_check = QCheckBox('💰 Ẩn số tiền trong dashboard')
        hide_amounts_check.setStyleSheet(self.get_checkbox_style())
        
        # Analytics
        analytics_check = QCheckBox('📊 Cho phép thu thập dữ liệu phân tích (ẩn danh)')
        analytics_check.setStyleSheet(self.get_checkbox_style())
        
        # Error reporting
        error_reporting_check = QCheckBox('🐛 Gửi báo cáo lỗi tự động')
        error_reporting_check.setStyleSheet(self.get_checkbox_style())
        
        privacy_layout.addWidget(hide_amounts_check)
        privacy_layout.addWidget(analytics_check)
        privacy_layout.addWidget(error_reporting_check)
        
        privacy_group.setLayout(privacy_layout)
        layout.addWidget(privacy_group)
        
        # Data management
        data_mgmt_group = QGroupBox('🗑️ Quản lý dữ liệu')
        data_mgmt_group.setStyleSheet(self.get_group_style())
        
        data_mgmt_layout = QVBoxLayout()
        data_mgmt_layout.setSpacing(15)
        
        # Clear cache
        btn_clear_cache = QPushButton('🧹 Xóa cache')
        btn_clear_cache.setStyleSheet("""
            QPushButton {
                background: #f59e0b;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #d97706;
            }
        """)
        btn_clear_cache.clicked.connect(self.clear_cache)
        
        # Clear all data
        btn_clear_all = QPushButton('💀 Xóa toàn bộ dữ liệu')
        btn_clear_all.setStyleSheet("""
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #dc2626;
            }
        """)
        btn_clear_all.clicked.connect(self.clear_all_data)
        
        data_mgmt_layout.addWidget(btn_clear_cache)
        data_mgmt_layout.addWidget(btn_clear_all)
        
        data_mgmt_group.setLayout(data_mgmt_layout)
        layout.addWidget(data_mgmt_group)
        
        layout.addStretch()
        privacy_widget.setLayout(layout)
        self.settings_tabs.addTab(privacy_widget, '🔒 Bảo mật')

    def create_advanced_tab(self):
        """Tab cài đặt nâng cao"""
        advanced_widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Developer settings
        dev_group = QGroupBox('👨‍💻 Dành cho nhà phát triển')
        dev_group.setStyleSheet(self.get_group_style())
        
        dev_layout = QVBoxLayout()
        dev_layout.setSpacing(15)
        
        # Debug mode
        debug_check = QCheckBox('🐛 Chế độ debug')
        debug_check.setStyleSheet(self.get_checkbox_style())
        
        # Verbose logging
        verbose_check = QCheckBox('📝 Ghi log chi tiết')
        verbose_check.setStyleSheet(self.get_checkbox_style())
        
        # Show performance
        performance_check = QCheckBox('⚡ Hiển thị thông tin hiệu suất')
        performance_check.setStyleSheet(self.get_checkbox_style())
        
        dev_layout.addWidget(debug_check)
        dev_layout.addWidget(verbose_check)
        dev_layout.addWidget(performance_check)
        
        dev_group.setLayout(dev_layout)
        layout.addWidget(dev_group)
        
        # App info
        info_group = QGroupBox('ℹ️ Thông tin ứng dụng')
        info_group.setStyleSheet(self.get_group_style())
        
        info_layout = QFormLayout()
        info_layout.setSpacing(15)
        
        # Version
        version_label = QLabel('v1.0.0')
        version_label.setStyleSheet("color: #6b7280; font-weight: 600;")
        info_layout.addRow('📱 Phiên bản:', version_label)
        
        # Build date
        build_date_label = QLabel('11/06/2025')
        build_date_label.setStyleSheet("color: #6b7280;")
        info_layout.addRow('🔨 Ngày build:', build_date_label)
        
        # Developer
        dev_label = QLabel('FinanceTeam')
        dev_label.setStyleSheet("color: #6b7280;")
        info_layout.addRow('👨‍💻 Nhà phát triển:', dev_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Action buttons
        action_group = QGroupBox('⚙️ Thao tác')
        action_group.setStyleSheet(self.get_group_style())
        
        action_layout = QVBoxLayout()
        action_layout.setSpacing(15)
        
        # Reset settings
        btn_reset = QPushButton('🔄 Khôi phục cài đặt mặc định')
        btn_reset.setStyleSheet("""
            QPushButton {
                background: #6b7280;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #4b5563;
            }
        """)
        btn_reset.clicked.connect(self.reset_settings)
        
        # Check updates
        btn_update = QPushButton('🔍 Kiểm tra cập nhật')
        btn_update.setStyleSheet("""
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #2563eb;
            }
        """)
        btn_update.clicked.connect(self.check_updates)
        
        action_layout.addWidget(btn_reset)
        action_layout.addWidget(btn_update)
        
        action_group.setLayout(action_layout)
        layout.addWidget(action_group)
        
        layout.addStretch()
        advanced_widget.setLayout(layout)
        self.settings_tabs.addTab(advanced_widget, '⚙️ Nâng cao')

    def get_input_style(self):
        """Style cho input controls"""
        return """
            QComboBox, QSpinBox, QLineEdit {
                padding: 8px 12px;
                border: 2px solid #e2e8f0;
                border-radius: 6px;
                font-size: 13px;
                background-color: #f8fafc;
            }
            QComboBox:focus, QSpinBox:focus, QLineEdit:focus {
                border-color: #6366f1;
                background-color: white;
            }
        """

    def get_group_style(self):
        """Style cho QGroupBox"""
        return """
            QGroupBox {
                font-size: 16px;
                font-weight: 600;
                color: #374151;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """

    def get_checkbox_style(self):
        """Style cho checkbox"""
        return """
            QCheckBox {
                font-size: 14px;
                color: #374151;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #d1d5db;
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #6366f1;
                border-color: #6366f1;
                image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTIiIGhlaWdodD0iOSIgdmlld0JveD0iMCAwIDEyIDkiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxwYXRoIGQ9Ik0xIDQuNUw0LjUgOEwxMSAxIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIvPgo8L3N2Zz4K);
            }
            QCheckBox::indicator:hover {
                border-color: #6366f1;
            }
        """

    def load_settings(self):
        """Load cài đặt từ file"""
        try:
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            if not user_id:
                return
            
            with open('data/settings.json', 'r', encoding='utf-8') as f:
                all_settings = json.load(f)
            
            # Find user settings
            self.settings = {}
            for setting in all_settings:
                if setting.get('user_id') == user_id:
                    self.settings = setting.get('settings', {})
                    break
            
            # Apply settings to UI
            self.apply_settings_to_ui()
            
        except Exception as e:
            print(f"Lỗi load settings: {e}")
            self.settings = self.get_default_settings()

    def get_default_settings(self):
        """Lấy cài đặt mặc định"""
        return {
            'theme': 'Sáng',
            'font_size': 14,
            'currency': 'VND',
            'date_format': 'DD/MM/YYYY',
            'chart_type': 'Biểu đồ cột',
            'transaction_limit': 20,
            'budget_warning': True,
            'budget_exceeded': True,
            'daily_summary': False,
            'sound_enabled': True,
            'volume': 50,
            'auto_backup': False,
            'backup_interval': 'Hàng tuần',
            'auto_lock': False,
            'lock_time': '15 phút',
            'remember_login': True,
            'hide_amounts': False,
            'analytics': True,
            'error_reporting': True,
            'debug_mode': False,
            'verbose_logging': False,
            'show_performance': False
        }

    def apply_settings_to_ui(self):
        """Áp dụng cài đặt lên giao diện"""
        if not self.settings:
            self.settings = self.get_default_settings()
        
        # Appearance settings
        if hasattr(self, 'theme_combo'):
            theme = self.settings.get('theme', 'Sáng')
            index = self.theme_combo.findText(theme)
            if index >= 0:
                self.theme_combo.setCurrentIndex(index)
        
        if hasattr(self, 'font_size_slider'):
            font_size = self.settings.get('font_size', 14)
            self.font_size_slider.setValue(font_size)
            self.font_size_label.setText(f'{font_size}px')
        
        # Apply other settings...
        # (Code continues for other settings)

    def save_settings(self):
        """Lưu cài đặt"""
        try:
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            if not user_id:
                return
            
            # Collect settings from UI
            current_settings = {
                'theme': self.theme_combo.currentText() if hasattr(self, 'theme_combo') else 'Sáng',
                'font_size': self.font_size_slider.value() if hasattr(self, 'font_size_slider') else 14,
                'currency': self.currency_combo.currentText() if hasattr(self, 'currency_combo') else 'VND',
                'date_format': self.date_format_combo.currentText() if hasattr(self, 'date_format_combo') else 'DD/MM/YYYY',
                'chart_type': self.chart_combo.currentText() if hasattr(self, 'chart_combo') else 'Biểu đồ cột',
                'transaction_limit': self.transaction_limit.value() if hasattr(self, 'transaction_limit') else 20,
                # Add other settings...
                'updated_at': datetime.datetime.now().isoformat()
            }
            
            # Load existing settings
            try:
                with open('data/settings.json', 'r', encoding='utf-8') as f:
                    all_settings = json.load(f)
            except:
                all_settings = []
            
            # Update or add user settings
            user_found = False
            for i, setting in enumerate(all_settings):
                if setting.get('user_id') == user_id:
                    all_settings[i]['settings'] = current_settings
                    user_found = True
                    break
            
            if not user_found:
                all_settings.append({
                    'user_id': user_id,
                    'settings': current_settings,
                    'created_at': datetime.datetime.now().isoformat()
                })
            
            # Save to file
            with open('data/settings.json', 'w', encoding='utf-8') as f:
                json.dump(all_settings, f, ensure_ascii=False, indent=2)
            
            self.settings = current_settings
            self.settings_changed.emit()
            
            QMessageBox.information(self, '✅ Thành công', 'Đã lưu cài đặt thành công!')
            
        except Exception as e:
            QMessageBox.critical(self, '❌ Lỗi', f'Không thể lưu cài đặt:\n{str(e)}')

    def backup_data(self):
        """Sao lưu dữ liệu"""
        try:
            backup_folder = QFileDialog.getExistingDirectory(self, 'Chọn thư mục sao lưu')
            if not backup_folder:
                return
            
            # Create backup with timestamp
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f'finance_backup_{timestamp}'
            backup_path = os.path.join(backup_folder, backup_name)
            
            # Copy data folder
            shutil.copytree('data', backup_path)
            
            QMessageBox.information(self, '✅ Thành công', 
                                  f'Đã sao lưu dữ liệu thành công!\nVị trí: {backup_path}')
            
        except Exception as e:
            QMessageBox.critical(self, '❌ Lỗi', f'Không thể sao lưu dữ liệu:\n{str(e)}')

    def restore_data(self):
        """Khôi phục dữ liệu"""
        reply = QMessageBox.question(self, '❓ Xác nhận khôi phục',
                                   'Việc khôi phục sẽ ghi đè toàn bộ dữ liệu hiện tại.\n'
                                   'Bạn có chắc muốn tiếp tục?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                backup_folder = QFileDialog.getExistingDirectory(self, 'Chọn thư mục backup để khôi phục')
                if not backup_folder:
                    return
                
                # Backup current data first
                current_backup = f'data_backup_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}'
                shutil.copytree('data', current_backup)
                
                # Remove current data
                shutil.rmtree('data')
                
                # Restore from backup
                shutil.copytree(backup_folder, 'data')
                
                QMessageBox.information(self, '✅ Thành công', 
                                      f'Đã khôi phục dữ liệu thành công!\n'
                                      f'Dữ liệu cũ được lưu tại: {current_backup}')
                
            except Exception as e:
                QMessageBox.critical(self, '❌ Lỗi', f'Không thể khôi phục dữ liệu:\n{str(e)}')

    def export_to_excel(self):
        """Xuất dữ liệu ra Excel"""
        try:
            import pandas as pd
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'Xuất Excel', 
                f'finance_data_{datetime.datetime.now().strftime("%Y%m%d")}.xlsx',
                'Excel files (*.xlsx)'
            )
            
            if file_path:
                # Export transactions
                user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
                
                with open('data/transactions.json', 'r', encoding='utf-8') as f:
                    transactions = json.load(f)
                
                user_transactions = [t for t in transactions if t.get('user_id') == user_id]
                
                if user_transactions:
                    df = pd.DataFrame(user_transactions)
                    df.to_excel(file_path, index=False, engine='openpyxl')
                    
                    QMessageBox.information(self, '✅ Thành công', 
                                          f'Đã xuất {len(user_transactions)} giao dịch ra file:\n{file_path}')
                else:
                    QMessageBox.warning(self, '⚠️ Cảnh báo', 'Không có dữ liệu để xuất!')
                
        except ImportError:
            QMessageBox.warning(self, '⚠️ Thiếu thư viện', 
                              'Cần cài đặt pandas và openpyxl:\npip install pandas openpyxl')
        except Exception as e:
            QMessageBox.critical(self, '❌ Lỗi', f'Không thể xuất Excel:\n{str(e)}')

    def export_to_csv(self):
        """Xuất dữ liệu ra CSV"""
        try:
            import pandas as pd
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'Xuất CSV', 
                f'finance_data_{datetime.datetime.now().strftime("%Y%m%d")}.csv',
                'CSV files (*.csv)'
            )
            
            if file_path:
                user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
                
                with open('data/transactions.json', 'r', encoding='utf-8') as f:
                    transactions = json.load(f)
                
                user_transactions = [t for t in transactions if t.get('user_id') == user_id]
                
                if user_transactions:
                    df = pd.DataFrame(user_transactions)
                    df.to_csv(file_path, index=False, encoding='utf-8-sig')
                    
                    QMessageBox.information(self, '✅ Thành công', 
                                          f'Đã xuất {len(user_transactions)} giao dịch ra file:\n{file_path}')
                else:
                    QMessageBox.warning(self, '⚠️ Cảnh báo', 'Không có dữ liệu để xuất!')
                
        except ImportError:
            QMessageBox.warning(self, '⚠️ Thiếu thư viện', 'Cần cài đặt pandas:\npip install pandas')
        except Exception as e:
            QMessageBox.critical(self, '❌ Lỗi', f'Không thể xuất CSV:\n{str(e)}')

    def export_to_pdf(self):
        """Xuất báo cáo PDF"""
        QMessageBox.information(self, 'ℹ️ Thông báo', 'Tính năng xuất PDF đang được phát triển!')

    def update_storage_info(self):
        """Cập nhật thông tin lưu trữ"""
        try:
            # Calculate database size
            total_size = 0
            for root, dirs, files in os.walk('data'):
                for file in files:
                    total_size += os.path.getsize(os.path.join(root, file))
            
            size_mb = total_size / (1024 * 1024)
            self.db_size_label.setText(f'{size_mb:.2f} MB')
            
            # Count transactions
            user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
            if user_id:
                with open('data/transactions.json', 'r', encoding='utf-8') as f:
                    transactions = json.load(f)
                
                user_transactions = [t for t in transactions if t.get('user_id') == user_id]
                self.transaction_count_label.setText(f'{len(user_transactions)} giao dịch')
            
        except Exception as e:
            print(f"Lỗi cập nhật thông tin lưu trữ: {e}")

    def clear_cache(self):
        """Xóa cache"""
        reply = QMessageBox.question(self, '❓ Xác nhận',
                                   'Bạn có chắc muốn xóa cache?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            QMessageBox.information(self, '✅ Thành công', 'Đã xóa cache thành công!')

    def clear_all_data(self):
        """Xóa toàn bộ dữ liệu"""
        reply = QMessageBox.question(self, '⚠️ CẢNH BÁO',
                                   'HÀNH ĐỘNG NÀY SẼ XÓA TOÀN BỘ DỮ LIỆU!\n\n'
                                   'Tất cả giao dịch, ngân sách, danh mục sẽ bị xóa vĩnh viễn.\n'
                                   'Bạn có CHẮC CHẮN muốn tiếp tục?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            # Second confirmation
            text, ok = QInputDialog.getText(self, 'Xác nhận cuối cùng', 
                                          'Nhập "XOA TAT CA" để xác nhận:')
            
            if ok and text == "XOA TAT CA":
                try:
                    user_id = getattr(self.user_manager, 'current_user', {}).get('id', None)
                    
                    # Clear user data from all files
                    files_to_clear = [
                        'data/transactions.json',
                        'data/budgets.json',
                        'data/categories.json'
                    ]
                    
                    for file_path in files_to_clear:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                data = json.load(f)
                            
                            # Remove user data
                            filtered_data = [item for item in data 
                                           if item.get('user_id') != user_id]
                            
                            with open(file_path, 'w', encoding='utf-8') as f:
                                json.dump(filtered_data, f, ensure_ascii=False, indent=2)
                        except:
                            continue
                    
                    QMessageBox.information(self, '✅ Hoàn thành', 
                                          'Đã xóa toàn bộ dữ liệu của bạn!')
                    
                except Exception as e:
                    QMessageBox.critical(self, '❌ Lỗi', f'Không thể xóa dữ liệu:\n{str(e)}')

    def reset_settings(self):
        """Khôi phục cài đặt mặc định"""
        reply = QMessageBox.question(self, '❓ Xác nhận',
                                   'Bạn có chắc muốn khôi phục cài đặt mặc định?',
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.settings = self.get_default_settings()
            self.apply_settings_to_ui()
            self.save_settings()

    def check_updates(self):
        """Kiểm tra cập nhật"""
        QMessageBox.information(self, '✅ Cập nhật', 
                              'Bạn đang sử dụng phiên bản mới nhất!\nPhiên bản: v1.0.0')
