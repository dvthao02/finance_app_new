from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QPainter, QColor, QBrush, QPen
import math

class FloatingActionButton(QPushButton):
    """Nút floating action button với hiệu ứng"""
    
    def __init__(self, icon_text="＋", parent=None):
        super().__init__(icon_text, parent)
        self.setFixedSize(56, 56)
        self.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 28px;
                font-size: 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #5a6fd8, stop:1 #6a3d8c);
                transform: scale(1.1);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                    stop:0 #4c5bc4, stop:1 #5a3077);
                transform: scale(0.95);
            }
        """)
        
        # Shadow effect (simplified)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
    def paintEvent(self, event):
        # Draw shadow
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Shadow
        shadow_rect = self.rect().adjusted(2, 2, -2, -2)
        painter.fillRect(shadow_rect, QColor(0, 0, 0, 30))
        
        super().paintEvent(event)

class QuickActionItem(QFrame):
    """Item trong menu quick actions"""
    
    clicked = pyqtSignal()
    
    def __init__(self, icon, text, color="#3b82f6", parent=None):
        super().__init__(parent)
        self.color = color
        self.init_ui(icon, text)
        
    def init_ui(self, icon, text):
        self.setFixedSize(200, 50)
        self.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #e2e8f0;
                border-radius: 25px;
                margin: 2px;
            }}
            QFrame:hover {{
                background: #f8fafc;
                border-color: {self.color};
                transform: translateX(5px);
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont('Segoe UI', 16))
        icon_label.setStyleSheet(f"color: {self.color};")
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        # Text
        text_label = QLabel(text)
        text_label.setFont(QFont('Segoe UI', 12))
        text_label.setStyleSheet("color: #1e293b;")
        layout.addWidget(text_label)
        
        layout.addStretch()
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class QuickActionsMenu(QWidget):
    """Menu quick actions"""
    
    add_income_clicked = pyqtSignal()
    add_expense_clicked = pyqtSignal() 
    view_report_clicked = pyqtSignal()
    view_budget_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.init_ui()
        self.is_visible = False
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Items
        items_data = [
            ("💰", "Thêm thu nhập", "#10b981", self.add_income_clicked),
            ("💸", "Thêm chi tiêu", "#ef4444", self.add_expense_clicked),
            ("📊", "Xem báo cáo", "#3b82f6", self.view_report_clicked),
            ("🎯", "Quản lý ngân sách", "#8b5cf6", self.view_budget_clicked),
        ]
        
        self.items = []
        for icon, text, color, signal in items_data:
            item = QuickActionItem(icon, text, color)
            item.clicked.connect(signal.emit)
            layout.addWidget(item)
            self.items.append(item)
            
        # Initially hide all items
        for item in self.items:
            item.hide()
            
    def show_menu(self, position):
        """Hiển thị menu tại vị trí chỉ định"""
        if self.is_visible:
            self.hide_menu()
            return
            
        # Position menu above the FAB
        menu_height = len(self.items) * 58  # 50 + 8 spacing
        self.setGeometry(position.x() - 100, position.y() - menu_height - 10, 
                        200, menu_height)
        
        self.show()
        self.is_visible = True
        
        # Animate items appearing
        for i, item in enumerate(self.items):
            QTimer.singleShot(i * 100, lambda item=item: self.show_item(item))
            
    def show_item(self, item):
        """Hiển thị một item với animation"""
        item.show()
        
        # Slide animation
        original_pos = item.pos()
        start_pos = original_pos + QRect(50, 0, 0, 0).topLeft()
        item.move(start_pos)
        
        animation = QPropertyAnimation(item, b"pos")
        animation.setDuration(300)
        animation.setEasingCurve(QEasingCurve.OutBack)
        animation.setStartValue(start_pos)
        animation.setEndValue(original_pos)
        animation.start()
        
    def hide_menu(self):
        """Ẩn menu"""
        if not self.is_visible:
            return
            
        for item in self.items:
            item.hide()
            
        self.hide()
        self.is_visible = False

class QuickActionsWidget(QWidget):
    """Widget chứa floating action button và menu"""
    
    add_income_requested = pyqtSignal()
    add_expense_requested = pyqtSignal()
    view_report_requested = pyqtSignal()
    view_budget_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        # Create floating action button
        self.fab = FloatingActionButton("＋", self)
        self.fab.clicked.connect(self.toggle_menu)
        
        # Create menu
        self.menu = QuickActionsMenu(self.parent())
        
        # Connect menu signals
        self.menu.add_income_clicked.connect(self.on_add_income)
        self.menu.add_expense_clicked.connect(self.on_add_expense)
        self.menu.view_report_clicked.connect(self.on_view_report)
        self.menu.view_budget_clicked.connect(self.on_view_budget)
        
    def position_fab(self, parent_rect):
        """Đặt vị trí FAB ở góc dưới phải"""
        fab_x = parent_rect.width() - self.fab.width() - 30
        fab_y = parent_rect.height() - self.fab.height() - 30
        self.fab.move(fab_x, fab_y)
        
    def toggle_menu(self):
        """Toggle hiển thị/ẩn menu"""
        fab_global_pos = self.fab.mapToGlobal(self.fab.rect().center())
        fab_parent_pos = self.parent().mapFromGlobal(fab_global_pos)
        self.menu.show_menu(fab_parent_pos)
        
    def on_add_income(self):
        """Xử lý thêm thu nhập"""
        self.menu.hide_menu()
        self.add_income_requested.emit()
        
    def on_add_expense(self):
        """Xử lý thêm chi tiêu"""
        self.menu.hide_menu()
        self.add_expense_requested.emit()
        
    def on_view_report(self):
        """Xử lý xem báo cáo"""
        self.menu.hide_menu()
        self.view_report_requested.emit()
        
    def on_view_budget(self):
        """Xử lý quản lý ngân sách"""
        self.menu.hide_menu()
        self.view_budget_requested.emit()

def add_quick_actions_to_widget(parent_widget):
    """Thêm quick actions vào widget cha"""
    quick_actions = QuickActionsWidget(parent_widget)
    
    def update_fab_position():
        quick_actions.position_fab(parent_widget.rect())
        
    # Position FAB initially
    QTimer.singleShot(100, update_fab_position)
    
    # Update position when parent resizes
    original_resize = parent_widget.resizeEvent
    def new_resize(event):
        original_resize(event)
        update_fab_position()
    parent_widget.resizeEvent = new_resize
    
    return quick_actions
