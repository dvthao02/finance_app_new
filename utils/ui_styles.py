"""
Tập hợp các styles chung cho toàn bộ ứng dụng
Sử dụng để đảm bảo tính nhất quán về giao diện và trải nghiệm người dùng
"""
from PyQt5.QtCore import Qt
from PyQt5.QtCore import QMargins
from PyQt5.QtGui import QColor
from PyQt5.QtChart import QChart, QPieSlice
from PyQt5.QtGui import QFont

class UIStyles:
    """Class chứa tất cả styles chung cho ứng dụng
    
    Các styles được định nghĩa theo thiết kế Material Design và Tailwind CSS
    để tạo giao diện hiện đại, dễ sử dụng và nhất quán
    """
    
    @staticmethod
    def get_table_style():
        """Style chung cho tất cả QTableWidget trong ứng dụng
        
        Bao gồm:
        - Màu nền và viền
        - Font chữ và kích thước
        - Hiệu ứng hover và selection
        - Style cho header
        """
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
            }
            QTableWidget::item:selected {
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
        """Style chung cho các nút thông thường
        
        Bao gồm:
        - Kích thước và padding
        - Màu sắc và viền
        - Hiệu ứng hover và pressed
        - Trạng thái disabled
        """
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
            }
            QPushButton:hover {
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
        """Style cho các nút chính (primary buttons)
        
        Sử dụng cho các hành động chính như:
        - Lưu
        - Xác nhận
        - Tiếp tục
        """
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
            }
            QPushButton:hover {
                background: #1d4ed8;
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
        """Style cho các nút nguy hiểm (danger buttons)
        
        Sử dụng cho các hành động nguy hiểm như:
        - Xóa
        - Khóa tài khoản
        - Hủy bỏ
        """
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
            }
            QPushButton:hover {
                background: #b91c1c;
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
        """Style cho các nút thành công (success buttons)
        
        Sử dụng cho các hành động tích cực như:
        - Thêm mới
        - Lưu thành công
        - Hoàn thành
        """
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
            }
            QPushButton:hover {
                background: #047857;
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
        """Style chung cho các ô nhập liệu
        
        Áp dụng cho:
        - QLineEdit
        - QComboBox
        - QDateEdit
        - QSpinBox
        """
        return """
            QLineEdit, QComboBox, QDateEdit, QSpinBox {
                font-size: 16px;
                padding: 10px 14px;
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: white;
                color: #374151;
                min-height: 18px;
            }
            QLineEdit:hover, QComboBox:hover, QDateEdit:hover, QSpinBox:hover {
                border-color: #93c5fd;
                background: #f0f9ff;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QSpinBox:focus {
                border-color: #3b82f6;
                background: #fefefe;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """
    
    @staticmethod
    def get_card_style():
        """Style cho các khung chứa (card containers)
        
        Sử dụng để tạo các khung chứa nội dung với:
        - Viền và bo góc
        - Hiệu ứng hover
        - Đổ bóng
        """
        return """
            QFrame {
                background: white;
                border-radius: 12px;
                border: 1px solid #e2e8f0;
            }
            QFrame:hover {
                border-color: #93c5fd;
                background: #fefefe;
            }
        """
    
    @staticmethod
    def get_group_box_style():
        """Style cho các khung nhóm (QGroupBox)
        
        Sử dụng để nhóm các thành phần liên quan với:
        - Tiêu đề nhóm
        - Viền và bo góc
        - Màu nền
        """
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
        """Style cho các ô tìm kiếm
        
        Bao gồm:
        - Icon tìm kiếm
        - Placeholder text
        - Hiệu ứng focus
        """
        return """
            QLineEdit {
                font-size: 16px;
                padding: 10px 14px 10px 40px;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: white;
                color: #374151;
                min-height: 18px;
            }
            QLineEdit:hover {
                border-color: #93c5fd;
                background: #f0f9ff;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background: #fefefe;
            }
            QLineEdit::placeholder {
                color: #9ca3af;
            }
        """

class TableStyleHelper:
    """Class hỗ trợ style cho bảng"""
    
    @staticmethod
    def apply_common_table_style(table):
        """Áp dụng style chung cho bảng
        
        Args:
            table: QTableWidget cần áp dụng style
        """
        table.setStyleSheet(UIStyles.get_table_style())
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(table.SelectRows)
        table.setSelectionMode(table.SingleSelection)
        table.setShowGrid(False)
        table.setCornerButtonEnabled(False)
        table.verticalHeader().setVisible(False)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setHighlightSections(False)
    
    @staticmethod
    def setup_table_selection_events(table, on_selection_changed_callback=None, on_item_clicked_callback=None):
        """Thiết lập các sự kiện cho bảng
        
        Args:
            table: QTableWidget cần thiết lập
            on_selection_changed_callback: Callback khi selection thay đổi
            on_item_clicked_callback: Callback khi item được click
        """
        if on_selection_changed_callback:
            table.itemSelectionChanged.connect(on_selection_changed_callback)
        
        def default_click_handler(item):
            if item and item.isSelected():
                table.clearSelection()
            else:
                table.selectRow(item.row())
        
        table.itemClicked.connect(on_item_clicked_callback or default_click_handler)

class ButtonStyleHelper:
    """Class hỗ trợ style cho nút"""
    
    @staticmethod
    def style_primary_button(button):
        """Áp dụng style primary cho nút
        
        Args:
            button: QPushButton cần áp dụng style
        """
        button.setStyleSheet(UIStyles.get_primary_button_style())
    
    @staticmethod
    def style_danger_button(button):
        """Áp dụng style danger cho nút
        
        Args:
            button: QPushButton cần áp dụng style
        """
        button.setStyleSheet(UIStyles.get_danger_button_style())
    
    @staticmethod
    def style_success_button(button):
        """Áp dụng style success cho nút
        
        Args:
            button: QPushButton cần áp dụng style
        """
        button.setStyleSheet(UIStyles.get_success_button_style())
    
    @staticmethod
    def style_normal_button(button):
        """Áp dụng style thông thường cho nút
        
        Args:
            button: QPushButton cần áp dụng style
        """
        button.setStyleSheet(UIStyles.get_button_style())

class ChartStyleHelper:
    """Class hỗ trợ style cho biểu đồ"""
    
    @staticmethod
    def apply_common_chart_style(chart, title=""):
        """Áp dụng style chung cho biểu đồ
        
        Args:
            chart: QChart cần áp dụng style
            title: Tiêu đề biểu đồ
        """
        chart.setTitle(title)
        chart.setTitleFont(chart.font())
        chart.setTitleBrush(QColor("#374151"))
        chart.setBackgroundVisible(False)
        chart.setMargins(QMargins(10, 10, 10, 10))
        chart.setBackgroundRoundness(8)
        chart.setPlotAreaBackgroundVisible(True)
        chart.setPlotAreaBackgroundBrush(QColor("#f8fafc"))
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        chart.legend().setFont(chart.font())
        chart.legend().setLabelColor(QColor("#374151"))
    
    @staticmethod
    def apply_pie_chart_style(pie_series, colors=None):
        """Áp dụng style cho biểu đồ tròn
        
        Args:
            pie_series: QPieSeries cần áp dụng style
            colors: Danh sách màu sắc cho các phần
        """
        if colors is None:
            colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
        
        # Tạo font mặc định
        default_font = QFont()
        default_font.setPointSize(10)
        
        for i, slice in enumerate(pie_series.slices()):
            slice.setBrush(QColor(colors[i % len(colors)]))
            slice.setLabelVisible(True)
            slice.setLabelColor(QColor("#374151"))
            slice.setLabelFont(default_font)
            # Thêm phần trăm vào label
            slice.setLabel(f"{slice.label()}: {slice.percentage()*100:.1f}%")
    
    @staticmethod
    def apply_bar_chart_style(bar_series, colors=None):
        """Áp dụng style cho biểu đồ cột
        
        Args:
            bar_series: QBarSeries cần áp dụng style
            colors: Danh sách màu sắc cho các cột
        """
        if colors is None:
            colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
        
        for i, bar_set in enumerate(bar_series.barSets()):
            bar_set.setBrush(QColor(colors[i % len(colors)]))
            bar_set.setPen(QColor(colors[i % len(colors)]))
