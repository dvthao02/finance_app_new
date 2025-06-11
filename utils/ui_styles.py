"""
Tập hợp các styles chung cho toàn bộ ứng dụng
Sử dụng để đảm bảo tính nhất quán về giao diện
"""
from PyQt5.QtCore import Qt

class UIStyles:
    """Class chứa tất cả styles chung cho ứng dụng"""
    
    @staticmethod
    def get_table_style():
        """Style chung cho tất cả QTableWidget trong ứng dụng"""
        return """
            QTableWidget {
                gridline-color: #e2e8f0;
                background-color: white;
                font-size: 16px;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                selection-background-color: #3b82f6;
                selection-color: white;
                alternate-background-color: #f8fafc;
            }
            QTableWidget::item {
                padding: 14px 12px;
                border-bottom: 1px solid #f1f5f9;
                border-right: 1px solid #f1f5f9;
                color: #374151;
            }            QTableWidget::item:selected {
                background-color: #3b82f6 !important;
                color: white !important;
                border: none !important;
                font-weight: 500 !important;
            }
            QTableWidget::item:selected:!active {
                background-color: #3b82f6 !important;
                color: white !important;
                border: none !important;
                font-weight: 500 !important;
            }
            QTableWidget::item:selected:active {
                background-color: #3b82f6 !important;
                color: white !important;
                border: none !important;
                font-weight: 500 !important;
            }
            QTableWidget::item:hover:!selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            QTableWidget::item:alternate {
                background-color: #f8fafc;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                    stop: 0 #f8fafc, stop: 1 #e2e8f0);
                padding: 14px 12px;
                border: none;
                border-bottom: 2px solid #3b82f6;
                border-right: 1px solid #e2e8f0;
                font-weight: 600;
                font-size: 16px;
                color: #374151;
                text-align: left;
            }
            QHeaderView::section:first {
                border-left: none;
            }
            QHeaderView::section:last {
                border-right: none;
            }
        """
    
    @staticmethod
    def get_button_style():
        """Style chung cho buttons"""
        return """
            QPushButton {
                font-size: 16px;
                font-weight: 500;
                padding: 10px 18px;
                border-radius: 6px;
                border: 1px solid #e2e8f0;
                background: white;
                color: #374151;
                min-height: 22px;
            }            QPushButton:hover {
                background: #e0e7ff;
                border-color: #a5b4fc;
                color: #3730a3;
            }
            QPushButton:pressed {
                background: #f3f4f6;
            }
            QPushButton:disabled {
                background: #f8fafc;
                color: #9ca3af;
                border-color: #e5e7eb;
            }
        """
    
    @staticmethod
    def get_primary_button_style():
        """Style cho primary buttons"""
        return """
            QPushButton {
                background: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 16px;
                min-height: 20px;
            }            QPushButton:hover {
                background: #1d4ed8;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
            }
            QPushButton:pressed {
                background: #1d4ed8;
            }
            QPushButton:disabled {
                background: #9ca3af;
            }
        """
    
    @staticmethod
    def get_danger_button_style():
        """Style cho danger buttons (xóa, khóa, v.v.)"""
        return """
            QPushButton {
                background: #ef4444;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 16px;
                min-height: 20px;
            }            QPushButton:hover {
                background: #b91c1c;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
            }
            QPushButton:pressed {
                background: #b91c1c;
            }
            QPushButton:disabled {
                background: #9ca3af;
            }
        """
    
    @staticmethod
    def get_success_button_style():
        """Style cho success buttons (thêm, lưu, v.v.)"""
        return """
            QPushButton {
                background: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-weight: 600;
                font-size: 16px;
                min-height: 20px;
            }            QPushButton:hover {
                background: #047857;
                transform: translateY(-1px);
                box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
            }
            QPushButton:pressed {
                background: #047857;
            }
            QPushButton:disabled {
                background: #9ca3af;
            }
        """
    
    @staticmethod
    def get_input_style():
        """Style chung cho input controls"""
        return """
            QLineEdit, QComboBox, QDateEdit, QSpinBox {
                font-size: 16px;
                padding: 10px 14px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
                color: #374151;
                min-height: 18px;            }
            QLineEdit:hover, QComboBox:hover, QDateEdit:hover, QSpinBox:hover {
                border-color: #93c5fd;
                background: #f0f9ff;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
                border-color: #3b82f6;
                background: #fefefe;
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """
    
    @staticmethod
    def get_card_style():
        """Style cho card containers"""
        return """
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }            QFrame:hover {
                border-color: #93c5fd;
                background: #fefefe;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
                transform: translateY(-2px);
            }
        """
    
    @staticmethod
    def get_group_box_style():
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
    
    @staticmethod
    def get_search_box_style():
        """Style cho search boxes"""
        return """
            QLineEdit {
                background: #f8fafc;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 0 12px;
                font-size: 16px;
                color: #374151;
                min-height: 18px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: white;
            }            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """
    
    @staticmethod
    def get_common_style():
        """Style chung cho toàn bộ ứng dụng"""
        return """
            QWidget {
                font-family: 'Segoe UI', Arial, sans-serif;
                background-color: #f8fafc;
                color: #374151;
            }
            QMainWindow {
                background-color: #f8fafc;
            }
            QTabWidget::pane {
                border: 1px solid #e2e8f0;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #f1f5f9;
                color: #6b7280;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-size: 14px;
                font-weight: 500;
            }
            QTabBar::tab:selected {
                background: white;
                color: #3b82f6;
                border-bottom: 2px solid #3b82f6;
            }            QTabBar::tab:hover {
                background: #dbeafe;
                color: #1e40af;
                border-bottom: 2px solid #93c5fd;
            }
        """

class TableStyleHelper:
    """Helper class để áp dụng styling chung cho tables"""
    
    @staticmethod
    def apply_common_table_style(table):
        """Áp dụng styling chung cho QTableWidget"""        # Apply CSS styling
        table.setStyleSheet(UIStyles.get_table_style())
        
        # Common table settings
        table.setEditTriggers(table.NoEditTriggers)
        table.setSelectionBehavior(table.SelectRows)
        table.setSelectionMode(table.SingleSelection)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        
        # Enable better selection handling
        table.setFocusPolicy(Qt.StrongFocus)
    
    @staticmethod
    def setup_table_selection_events(table, on_selection_changed_callback=None, on_item_clicked_callback=None):
        """Setup các event handlers cho table selection"""
        if on_selection_changed_callback:
            table.itemSelectionChanged.connect(on_selection_changed_callback)
        
        if on_item_clicked_callback:
            table.itemClicked.connect(on_item_clicked_callback)
        else:
            # Default click handler để đảm bảo selection works
            def default_click_handler(item):
                if item:
                    table.selectRow(item.row())
            table.itemClicked.connect(default_click_handler)

class ButtonStyleHelper:
    """Helper class để áp dụng styling cho buttons"""
    
    @staticmethod
    def style_primary_button(button):
        """Style button thành primary button"""
        button.setStyleSheet(UIStyles.get_primary_button_style())
    
    @staticmethod
    def style_danger_button(button):
        """Style button thành danger button"""
        button.setStyleSheet(UIStyles.get_danger_button_style())
    
    @staticmethod
    def style_success_button(button):
        """Style button thành success button"""
        button.setStyleSheet(UIStyles.get_success_button_style())
    
    @staticmethod
    def style_normal_button(button):
        """Style button thành normal button"""
        button.setStyleSheet(UIStyles.get_button_style())
