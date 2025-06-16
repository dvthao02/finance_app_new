"""
Animated Widgets Utilities
===========================

Module chứa các widget có hiệu ứng animation để tăng trải nghiệm người dùng.
Các widget này có thể được sử dụng trong bất kỳ phần nào của ứng dụng.

Các widget chính:
- AnimatedNumberLabel: Label hiển thị số với hiệu ứng đếm
- AnimatedStatCard: Thẻ thống kê với animation
- SlideInWidget: Widget trượt vào từ bên trái
- FadeInWidget: Widget với hiệu ứng fade in
- StaggeredAnimationGroup: Nhóm animation chạy lần lượt

Cách sử dụng:
    from utils.animated_widgets import AnimatedNumberLabel, AnimatedStatCard
    
    # Tạo label số có animation
    label = AnimatedNumberLabel()
    label.set_target_value(1000000)  # Sẽ đếm từ 0 lên 1,000,000
    
    # Tạo stat card
    card = AnimatedStatCard("Thu nhập", 500000, "Tháng này", "#10b981", "📈")
"""

from PyQt5.QtWidgets import QLabel, QFrame, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect, QEasingCurve, QTimer, pyqtSignal, QSequentialAnimationGroup
from PyQt5.QtGui import QFont, QColor, QPalette
import random

class AnimatedNumberLabel(QLabel):
    """Label hiển thị số tiền với hiệu ứng đếm"""
    
    animation_finished = pyqtSignal()
    
    def __init__(self, target_value=0, prefix="", suffix=" đ", duration=1500, parent=None):
        super().__init__(parent)
        self.target_value = target_value
        self.current_value = 0
        self.prefix = prefix
        self.suffix = suffix
        self.duration = duration
        
        # Timer cho animation
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_display)
        self.animation_steps = 60  # 60 frames for smooth animation
        self.current_step = 0
        
    def set_target_value(self, value):
        """Đặt giá trị đích và bắt đầu animation"""
        self.target_value = float(value)
        self.current_step = 0
        
        # Tính toán increment cho mỗi bước
        self.increment = (self.target_value - self.current_value) / self.animation_steps
        
        # Bắt đầu animation
        self.timer.start(self.duration // self.animation_steps)
        
    def update_display(self):
        """Cập nhật hiển thị trong quá trình animation"""
        if self.current_step < self.animation_steps:
            self.current_value += self.increment
            self.current_step += 1
            
            # Hiển thị giá trị hiện tại
            display_value = int(self.current_value)
            self.setText(f"{self.prefix}{display_value:,}{self.suffix}")
        else:
            # Animation hoàn thành
            self.current_value = self.target_value
            display_value = int(self.target_value)
            self.setText(f"{self.prefix}{display_value:,}{self.suffix}")
            self.timer.stop()
            self.animation_finished.emit()

class AnimatedStatCard(QFrame):
    """Thẻ thống kê với hiệu ứng animation"""
    
    def __init__(self, title, value, subtitle, color, trend_icon, parent=None):
        super().__init__(parent)
        self.color = color
        self.init_ui(title, subtitle, color, trend_icon)
        self.set_value(value)
        
    def init_ui(self, title, subtitle, color, trend_icon):
        self.setStyleSheet("""
            QFrame {
                background: white;
                border-radius: 12px;
                border: none;
            }
        """)
        self.setFixedHeight(110)  # Giảm chiều cao xuống một chút
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 12, 15, 12)  # Giảm contentMargins
        layout.setSpacing(5)  # Giảm spacing
        
        # Header với title và trend
        header_layout = QHBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setFont(QFont('Segoe UI', 12))
        self.title_label.setStyleSheet('color: #64748b;')
        header_layout.addWidget(self.title_label)
        
        header_layout.addStretch()
        
        self.trend_label = QLabel(trend_icon)
        self.trend_label.setFont(QFont('Segoe UI', 14))
        self.trend_label.setStyleSheet(f'color: {color};')
        header_layout.addWidget(self.trend_label)
        
        layout.addLayout(header_layout)
        
        # Animated value
        self.value_label = AnimatedNumberLabel()
        self.value_label.setFont(QFont('Segoe UI', 18, QFont.Bold))
        self.value_label.setStyleSheet(f'color: {color};')
        layout.addWidget(self.value_label)
        
        # Subtitle
        self.subtitle_label = QLabel(subtitle)
        self.subtitle_label.setFont(QFont('Segoe UI', 10))
        self.subtitle_label.setStyleSheet('color: #94a3b8;')
        layout.addWidget(self.subtitle_label)
        
    def set_value(self, value):
        """Đặt giá trị và bắt đầu animation"""
        # Parse value nếu là string có format tiền tệ
        if isinstance(value, str):
            # Remove currency symbols and commas
            clean_value = value.replace('đ', '').replace(',', '').replace('.', '').strip()
            try:
                numeric_value = float(clean_value)
            except ValueError:
                numeric_value = 0
        else:
            numeric_value = float(value)
            
        self.value_label.set_target_value(numeric_value)
        
    def update_subtitle(self, new_subtitle):
        """Cập nhật subtitle"""
        self.subtitle_label.setText(new_subtitle)
        
    def update_trend(self, new_trend_icon):
        """Cập nhật trend icon"""
        self.trend_label.setText(new_trend_icon)

class SlideInWidget(QFrame):
    """Widget có hiệu ứng slide in từ bên trái"""
    
    def __init__(self, content_widget, parent=None):
        super().__init__(parent)
        self.content_widget = content_widget
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content_widget)
        
        # Ẩn ban đầu ở bên trái
        self.setGeometry(-self.width(), 0, self.width(), self.height())
        
    def slide_in(self, duration=800):
        """Hiệu ứng slide in"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(duration)
        self.animation.setEasingCurve(QEasingCurve.OutCubic)
        
        # Vị trí cuối
        end_rect = QRect(0, 0, self.width(), self.height())
        self.animation.setEndValue(end_rect)
        
        self.animation.start()

class FadeInWidget(QFrame):
    """Widget có hiệu ứng fade in"""
    
    def __init__(self, content_widget, parent=None):
        super().__init__(parent)
        self.content_widget = content_widget
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.content_widget)
        
        # Trong suốt ban đầu
        self.setStyleSheet("background: transparent;")
        
    def fade_in(self, duration=1000):
        """Hiệu ứng fade in"""
        self.setStyleSheet("background: white;")

class StaggeredAnimationGroup:
    """Nhóm animation chạy lần lượt với delay"""
    
    def __init__(self, widgets, delay=200):
        self.widgets = widgets
        self.delay = delay
        self.current_index = 0
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.animate_next)
        
    def start_animations(self):
        """Bắt đầu animation cho tất cả widgets"""
        self.current_index = 0
        if self.widgets:
            self.animate_next()
            
    def animate_next(self):
        """Animate widget tiếp theo"""
        if self.current_index < len(self.widgets):
            widget = self.widgets[self.current_index]
            
            # Trigger animation based on widget type
            if hasattr(widget, 'set_value'):
                # For AnimatedStatCard
                value = getattr(widget, '_target_value', 0)
                widget.set_value(value)
            elif hasattr(widget, 'slide_in'):
                widget.slide_in()
            elif hasattr(widget, 'fade_in'):
                widget.fade_in()
                
            self.current_index += 1
            
            # Schedule next animation
            if self.current_index < len(self.widgets):
                self.timer.singleShot(self.delay, self.animate_next)
        else:
            self.timer.stop()

def create_loading_dots_animation(label):
    """Tạo hiệu ứng loading dots cho label"""
    dots = ["", ".", "..", "..."]
    current_dot = 0
    
    def update_dots():
        nonlocal current_dot
        base_text = label.text().rstrip('.')
        label.setText(base_text + dots[current_dot])
        current_dot = (current_dot + 1) % len(dots)
    
    timer = QTimer()
    timer.timeout.connect(update_dots)
    timer.start(500)  # Update every 500ms
    
    return timer

def shake_widget(widget, duration=300):
    """Hiệu ứng lắc widget"""
    original_pos = widget.pos()
    
    animation = QPropertyAnimation(widget, b"pos")
    animation.setDuration(duration)
    animation.setLoopCount(3)
    
    # Tạo hiệu ứng lắc
    shake_distance = 5
    animation.setKeyValueAt(0, original_pos)
    animation.setKeyValueAt(0.25, original_pos + QRect(shake_distance, 0, 0, 0).topLeft())
    animation.setKeyValueAt(0.75, original_pos + QRect(-shake_distance, 0, 0, 0).topLeft())
    animation.setKeyValueAt(1, original_pos)
    
    animation.start()
    return animation

def pulse_widget(widget, color="#3b82f6", duration=1000):
    """Hiệu ứng pulse cho widget"""
    original_style = widget.styleSheet()
    
    def pulse_in():
        widget.setStyleSheet(f"""
            {original_style}
            border: 2px solid {color};
            background-color: rgba(59, 130, 246, 0.1);
        """)
        
    def pulse_out():
        widget.setStyleSheet(original_style)
    
    # Tạo sequence animation
    timer1 = QTimer()
    timer2 = QTimer()
    
    timer1.singleShot(0, pulse_in)
    timer2.singleShot(duration // 2, pulse_out)
    
    return timer1, timer2
