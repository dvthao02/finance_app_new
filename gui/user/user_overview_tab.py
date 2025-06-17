import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QGroupBox, QDateEdit, QSizePolicy, QSpacerItem, QToolTip, QMessageBox,
    QHeaderView, QScrollArea # Added QScrollArea
)
from PyQt5.QtCore import Qt, QDate, QMargins, QPointF, QLineF
from PyQt5.QtGui import QFont, QPainter, QColor
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QPieSeries, QPieSlice, QBarCategoryAxis, QValueAxis, QLegend
import datetime
import logging

# Placeholder imports for data managers (replace with actual imports in your project)
from data_manager.transaction_manager import TransactionManager
from data_manager.budget_manager import BudgetManager
from data_manager.category_manager import CategoryManager
from utils.animated_widgets import AnimatedStatCard
from utils.quick_actions import add_quick_actions_to_widget
from utils.ui_styles import TableStyleHelper, ChartStyleHelper

OTHER_CATEGORY_THRESHOLD_PERCENT = 3.0 # Categories below this % go into "Khác"

class UserOverviewTab(QWidget):
    def __init__(self, user_manager, transaction_manager, category_manager, wallet_manager=None, budget_manager=None, notification_manager=None, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
        self.wallet_manager = wallet_manager
        self.budget_manager = budget_manager
        self.notification_manager = notification_manager
        
        self.user_id = None
        self.user_name = "Khách" 

        if hasattr(self.user_manager, 'current_user_id') and self.user_manager.current_user_id:
            self.user_id = self.user_manager.current_user_id
            current_user_details = self.user_manager.get_user_by_id(self.user_id)
            if current_user_details:
                self.user_name = current_user_details.get("name", "Người dùng")
            else:
                self.user_name = "Người dùng" 
                logging.warning(f"UserOverviewTab: Không tìm thấy chi tiết người dùng cho user_id {self.user_id}, nhưng user_id đã được đặt.")
        else:
            logging.warning("UserOverviewTab: user_manager.current_user_id không tìm thấy hoặc là None.")
            
        print(f"DEBUG: UserOverviewTab initialized with user_id={self.user_id}, user_name={self.user_name}")
        self.init_ui()
        self.update_dashboard()

    def init_ui(self):
        # Overall layout for the UserOverviewTab, containing the scroll area
        tab_layout = QVBoxLayout(self)
        tab_layout.setContentsMargins(0,0,0,0) # Remove margins for the tab's own layout

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }") # Optional: style scroll area

        # This widget will contain all the original content and be scrollable
        scroll_content_widget = QWidget()
        # Use a slightly different background for the content if needed, or keep transparent
        # scroll_content_widget.setStyleSheet("background: #f9f9f9;") 
        
        main_layout = QVBoxLayout(scroll_content_widget) # Original main_layout, now on this new widget
        main_layout.setContentsMargins(10, 10, 10, 10) # Add some padding inside the scrollable area
        
        # Quick Actions (remains at the top for now)
        self.quick_actions = add_quick_actions_to_widget(scroll_content_widget) 
        self.quick_actions.add_income_requested.connect(self.handle_add_income)
        self.quick_actions.add_expense_requested.connect(self.handle_add_expense)
        self.quick_actions.view_report_requested.connect(self.handle_view_report)
        self.quick_actions.view_budget_requested.connect(self.handle_view_budget)
        main_layout.addWidget(self.quick_actions)
        
        # --- New Header Section ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget) # Apply layout directly to header_widget
        header_layout.setContentsMargins(5, 5, 5, 5) # Margins for content within the header

        page_title_text = "Tổng quan chi tiêu"

        title_label = QLabel(page_title_text)
        title_label.setStyleSheet("""/* Styles for title_label */
            font-size: 16px; /* Adjusted for potentially smaller header */
            font-weight: bold; 
            color: white; /* Changed to white */
            padding: 0px; /* Remove individual padding, rely on header_widget padding */
            background-color: transparent; /* Ensure no conflicting background */
            border: none; /* Ensure no conflicting border */
        """)
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(title_label)

        header_layout.addStretch(1) # Push date to the right

        date_label = QLabel(f"{datetime.datetime.now():%A, %d/%m/%Y}")
        date_label.setStyleSheet("""/* Styles for date_label */
            font-size: 12px; /* Adjusted for potentially smaller header */
            color: white; /* Changed to white */
            padding: 0px; /* Remove individual padding */
            background-color: transparent; /* Ensure no conflicting background */
            border: none; /* Ensure no conflicting border */
        """)
        date_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header_layout.addWidget(date_label)

        header_widget.setStyleSheet("""/* Styles for header_widget */
            background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #5DADE2, stop:1 #3498DB);
            border-radius: 6px; /* Slightly smaller radius */
            padding: 8px 12px; /* Vertical padding 8px, Horizontal 12px - controls height */
            margin-bottom: 10px; 
            /* border-bottom: 1px solid #e0e0e0; /* Removed */
        """)
        main_layout.addWidget(header_widget)
       
        
        # Filter group
        filter_group = QGroupBox("Lọc theo:")
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "Tháng này", "3 tháng gần nhất", "6 tháng gần nhất", "1 năm gần nhất", "Tất cả", "Tùy chọn"
        ])
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)
        filter_layout.addWidget(self.filter_combo)
        self.custom_start = QDateEdit(calendarPopup=True)
        self.custom_end = QDateEdit(calendarPopup=True)
        self.custom_start.setDisplayFormat("dd/MM/yyyy")
        self.custom_end.setDisplayFormat("dd/MM/yyyy")
        self.custom_start.setDate(QDate.currentDate())
        self.custom_end.setDate(QDate.currentDate())
        self.custom_start.hide()
        self.custom_end.hide()
        filter_layout.addWidget(self.custom_start)
        filter_layout.addWidget(QLabel("-"))
        filter_layout.addWidget(self.custom_end)
        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)
        self.custom_start.dateChanged.connect(self.update_dashboard)
        self.custom_end.dateChanged.connect(self.update_dashboard)
        
        # Animated Info boxes
        info_layout = QHBoxLayout()
        filter_text = self.filter_combo.currentText()
        subtitle_period = "Tùy chọn" if filter_text == "Tùy chọn" else filter_text.lower()

        self.balance_card = AnimatedStatCard("Số dư", 0, f"Trong {subtitle_period}", "#10b981", "💰")
        self.expense_card = AnimatedStatCard("Chi tiêu", 0, f"Trong {subtitle_period}", "#ef4444", "💸")
        self.saving_card = AnimatedStatCard("Tiết kiệm", 0, f"Trong {subtitle_period}", "#3b82f6", "💎")
        for card in [self.balance_card, self.expense_card, self.saving_card]:
            info_layout.addWidget(card)
        main_layout.addLayout(info_layout)
        
        # Charts for budgets and spending by category
        self.charts_group = QGroupBox("Biểu đồ thống kê")
        charts_group_layout = QVBoxLayout() 
        chart_layout_h = QHBoxLayout() 

        # Tạo biểu đồ cột cho ngân sách
        self.budget_chart = QChart()
        self.budget_chart.setTitle("Ngân sách và chi tiêu")
        self.budget_chart.legend().setVisible(True)
        self.budget_chart.legend().setAlignment(Qt.AlignBottom)
        
        self.budget_chart_view = QChartView(self.budget_chart)
        self.budget_chart_view.setRenderHint(QPainter.Antialiasing)
        self.budget_chart_view.setMinimumHeight(300) # Keep reasonable height
        self.budget_chart_view.setMouseTracking(True)
        chart_layout_h.addWidget(self.budget_chart_view)
        
        # Tạo biểu đồ tròn cho chi tiêu
        self.spending_chart = QChart()
        self.spending_chart.setTitle("Chi tiêu theo danh mục")
        self.spending_chart.legend().setVisible(True)
        self.spending_chart.legend().setAlignment(Qt.AlignRight) # Legend on the right
        self.spending_chart.legend().setMarkerShape(QLegend.MarkerShapeCircle) 
        self.spending_chart.legend().setFont(QFont("Arial", 9)) 
        
        self.spending_series = QPieSeries()
        self.spending_series.setHoleSize(0.35) 
        self.spending_chart.addSeries(self.spending_series)
        
        self.spending_chart_view = QChartView(self.spending_chart)
        self.spending_chart_view.setRenderHint(QPainter.Antialiasing)
        self.spending_chart_view.setMinimumHeight(350) 
        self.spending_chart_view.setMouseTracking(True)
        chart_layout_h.addWidget(self.spending_chart_view)

        charts_group_layout.addLayout(chart_layout_h) 
        self.charts_group.setLayout(charts_group_layout)
        main_layout.addWidget(self.charts_group) 

        # Recent transactions table - moved to the bottom
        self.recent_transactions_group = QGroupBox("Giao dịch gần đây (15 mục mới nhất)")
        recent_transactions_layout = QVBoxLayout()
        self.tx_table = QTableWidget(0, 4)
        self.tx_table.setHorizontalHeaderLabels(["Ngày", "Danh mục", "Số tiền", "Ghi chú"])
        
        for i in range(3): # First 3 columns
             self.tx_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Interactive)
        self.tx_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch) # Last column (Ghi chú) stretches

        TableStyleHelper.apply_common_table_style(self.tx_table)
        self.tx_table.setMinimumHeight(200) # Adjusted height for better fit with scroll area
        self.tx_table.setMaximumHeight(400) 
        self.tx_table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tx_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        recent_transactions_layout.addWidget(self.tx_table)
        self.recent_transactions_group.setLayout(recent_transactions_layout)
        main_layout.addWidget(self.recent_transactions_group) 
        
        main_layout.addStretch(1) # Add stretch to push content up if space available

        scroll_content_widget.setLayout(main_layout)
        scroll_area.setWidget(scroll_content_widget)
        tab_layout.addWidget(scroll_area)
        # self.setLayout(tab_layout) # Implicitly set

    def on_filter_changed(self):
        if self.filter_combo.currentText() == "Tùy chọn":
            self.custom_start.show()
            self.custom_end.show()
        else:
            self.custom_start.hide()
            self.custom_end.hide()
        self.update_dashboard()
        filter_text = self.filter_combo.currentText()
        subtitle_period = "Tùy chọn" if filter_text == "Tùy chọn" else filter_text.lower()
        
        self.balance_card.update_subtitle(f"Trong {subtitle_period}")
        self.expense_card.update_subtitle(f"Trong {subtitle_period}")
        self.saving_card.update_subtitle(f"Trong {subtitle_period}")

    def get_filter_dates(self):
        today = datetime.date.today()
        filter_text = self.filter_combo.currentText()
        start, end = None, None

        if filter_text == "Tháng này":
            start = today.replace(day=1)
            end = today # Data up to and including today
        elif filter_text == "3 tháng gần nhất":
            start = today - datetime.timedelta(days=90); end = today
        elif filter_text == "6 tháng gần nhất":
            start = today - datetime.timedelta(days=180); end = today
        elif filter_text == "1 năm gần nhất":
            start = today - datetime.timedelta(days=365); end = today
        elif filter_text == "Tất cả":
            return None, None
        elif filter_text == "Tùy chọn":
            start = self.custom_start.date().toPyDate()
            end = self.custom_end.date().toPyDate()
        
        start_dt = datetime.datetime.combine(start, datetime.time.min) if start else None
        end_dt = datetime.datetime.combine(end, datetime.time.max) if end else None
        return start_dt, end_dt

    def update_dashboard(self):
        try:
            current_filter_text = self.filter_combo.currentText()
            subtitle_period = "Tùy chọn" if current_filter_text == "Tùy chọn" else current_filter_text.lower()
            self.balance_card.update_subtitle(f"Trong {subtitle_period}")
            self.expense_card.update_subtitle(f"Trong {subtitle_period}")
            self.saving_card.update_subtitle(f"Trong {subtitle_period}")

            if not self.user_id or not self.transaction_manager or not self.category_manager:
                logging.warning("User ID, TransactionManager, or CategoryManager not available.")
                self.balance_card.set_value(0); self.expense_card.set_value(0); self.saving_card.set_value(0)
                self.tx_table.setRowCount(0)
                if hasattr(self, 'budget_chart'): self.budget_chart.removeAllSeries()
                if hasattr(self, 'spending_series'): self.spending_series.clear()
                return
            
            start_date, end_date = self.get_filter_dates()
            transactions = self.transaction_manager.get_transactions_in_range(start_date, end_date, self.user_id)
            
            total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
            total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
            self.balance_card.set_value(total_income - total_expense)
            self.expense_card.set_value(total_expense)
            self.saving_card.set_value(total_income - total_expense)

            all_user_transactions = self.transaction_manager.get_transactions_by_user(self.user_id)
            self.tx_table.setRowCount(0) 
            recent_transactions_to_display = sorted(all_user_transactions, key=lambda x: x["date"], reverse=True)[:15]
            self.recent_transactions_group.setTitle(f"Giao dịch gần đây ({len(recent_transactions_to_display)} mục mới nhất)")

            for t in recent_transactions_to_display:
                row = self.tx_table.rowCount()
                self.tx_table.insertRow(row)
                try:
                    date_obj = datetime.datetime.fromisoformat(t["date"].replace('Z', '+00:00'))
                    display_date = date_obj.strftime("%d/%m/%Y")
                except: display_date = str(t.get("date", ""))
                self.tx_table.setItem(row, 0, QTableWidgetItem(display_date))
                
                category_id = t.get("category_id", "")
                category_name = self.category_manager.get_category_name(category_id) if category_id else "Khác"
                self.tx_table.setItem(row, 1, QTableWidgetItem(category_name))
                
                amount_item = QTableWidgetItem(f"{t['amount']:,} đ")
                amount_item.setForeground(QColor('#ef4444' if t.get('type') == 'expense' else '#10b981'))
                self.tx_table.setItem(row, 2, amount_item)
                self.tx_table.setItem(row, 3, QTableWidgetItem(t.get("note", "")))
            self.tx_table.resizeColumnsToContents()

            if self.budget_manager:
                self.budget_chart.removeAllSeries()
                for axis in self.budget_chart.axes(): self.budget_chart.removeAxis(axis)
                
                category_totals_for_budget = {}
                for t in transactions:
                    if t.get("type") == "expense" and t.get("category_id"):
                        category_totals_for_budget[t["category_id"]] = category_totals_for_budget.get(t["category_id"], 0) + t["amount"]

                budgets = self.budget_manager.get_budgets_by_user(self.user_id)
                budget_series = QBarSeries()
                categories_for_chart, budget_values, spent_values = [], [], []
                
                for budget in budgets:
                    if budget.get("amount", 0) > 0:
                        category_id = budget["category_id"]
                        category_name = self.category_manager.get_category_name(category_id) or "Không xác định"
                        total_budget = budget["amount"]
                        total_spent = category_totals_for_budget.get(category_id, 0)
                        
                        categories_for_chart.append(category_name)
                        budget_values.append(total_budget)
                        spent_values.append(total_spent)
                        
                        if total_spent > total_budget and self.notification_manager:
                            self.notification_manager.add_notification(
                                title="Cảnh báo ngân sách",
                                content=f"Danh mục '{category_name}' đã vượt ngân sách!\\nNgân sách: {total_budget:,} đ\\nĐã chi tiêu: {total_spent:,} đ",
                                notify_type="budget", user_id=self.user_id
                            )
                
                if categories_for_chart:
                    budget_set = QBarSet("Ngân sách")
                    spent_set = QBarSet("Đã chi tiêu")
                    budget_set.append(budget_values)
                    spent_set.append(spent_values)
                    
                    budget_set.setColor(QColor("#10b981"))
                    spent_set.setColor(QColor("#ef4444"))
                    
                    budget_series.append(budget_set)
                    budget_series.append(spent_set)
                    budget_series.setLabelsVisible(False)
                    budget_series.setLabelsPosition(QBarSeries.LabelsInsideEnd)
                    budget_series.setLabelsFormat("%.0f đ")  # Corrected format for bar labels

                    budget_series.hovered.connect(self.on_bar_hovered)
                    self.budget_chart.addSeries(budget_series)
                
                    axisX = QBarCategoryAxis(); axisX.append(categories_for_chart); axisX.setTitleText("Danh mục")
                    self.budget_chart.setAxisX(axisX, budget_series)
                    
                    axisY = QValueAxis(); axisY.setTitleText("Số tiền (đ)")
                    max_val = 0
                    if budget_values or spent_values:
                         max_val = max(max(budget_values if budget_values else [0]), max(spent_values if spent_values else [0]))
                    axisY.setRange(0, max_val * 1.1 if max_val > 0 else 100)
                    axisY.setLabelFormat("%{value:,.0f}")
                    self.budget_chart.setAxisY(axisY, budget_series)
                    
                    font = QFont("Arial", 10)
                    self.budget_chart.setFont(font); self.budget_chart.legend().setFont(font)
                    if self.budget_chart.axisX(): self.budget_chart.axisX().setLabelsFont(font)
                    if self.budget_chart.axisY(): self.budget_chart.axisY().setLabelsFont(font)
                else:
                    self.budget_chart.setTitle("Ngân sách và chi tiêu (Không có dữ liệu)")
            
            # Update Spending Pie Chart
            self.spending_series.clear()
            category_spending_raw = {}
            for t in transactions:
                if t.get("type") == "expense":
                    category_id = t.get("category_id", "")
                    category_name = self.category_manager.get_category_name(category_id) or "Khác"
                    category_spending_raw[category_name] = category_spending_raw.get(category_name, 0) + t["amount"]
            
            total_spending_for_pie = sum(category_spending_raw.values())
            
            # Group small categories into "Khác"
            processed_category_spending = {}
            other_total_value = 0
            if total_spending_for_pie > 0: # Avoid division by zero if no spending
                for category, total in category_spending_raw.items():
                    percentage = (total / total_spending_for_pie) * 100
                    if percentage < OTHER_CATEGORY_THRESHOLD_PERCENT:
                        other_total_value += total
                    else:
                        processed_category_spending[category] = total
                if other_total_value > 0:
                    processed_category_spending["Khác"] = processed_category_spending.get("Khác", 0) + other_total_value

            # Sort processed categories for display
            sorted_category_spending = sorted(processed_category_spending.items(), key=lambda item: item[1], reverse=True)

            if self.spending_chart.legend().markers():
                for marker in self.spending_chart.legend().markers():
                    try: marker.clicked.disconnect()
                    except TypeError: pass
            
            for category_name, total_value in sorted_category_spending:
                if total_value > 0:
                    percentage = (total_value / total_spending_for_pie) * 100 if total_spending_for_pie > 0 else 0
                    
                    slice = self.spending_series.append(category_name, total_value) # category_name for legend
                    # slice.setLabel(f\"{percentage:.1f}%\") # DEFER setting final label text
                    
                    slice.setLabelVisible(True) # Initial visibility

                    slice.setProperty("category_name_prop", category_name) 
                    slice.setProperty("category_value_prop", total_value)
                    slice.setProperty("category_percentage_prop", percentage)
            
            if not self.spending_series.slices():
                self.spending_chart.setTitle("Chi tiêu theo danh mục (Không có dữ liệu)")
            else:
                self.spending_chart.setTitle("Chi tiêu theo danh mục")

            try: 
                self.spending_series.hovered.disconnect(self.on_slice_hovered)
            except TypeError: pass
            self.spending_series.hovered.connect(self.on_slice_hovered)
            
            ChartStyleHelper.apply_pie_chart_style(self.spending_series)

            # Iterate AFTER style helper to set final labels and ensure properties
            for s_slice in self.spending_series.slices(): # Renamed loop variable to avoid conflict
                perc = s_slice.property("category_percentage_prop")
                if perc is not None:
                    s_slice.setLabel(f"{perc:.1f}%")
                
                s_slice.setLabelVisible(True) # Ensure label is visible
                s_slice.setLabelColor(QColor("#FFFFFF")) # Ensure label color
                s_slice.setLabelFont(QFont("Arial", 8, QFont.Bold)) # Ensure label font

            # Explicitly set legend labels to category names
            if self.spending_chart.legend().isVisible() and self.spending_series.count() > 0:
                legend_markers = self.spending_chart.legend().markers(self.spending_series)
                pie_slices = self.spending_series.slices()

                if len(legend_markers) == len(pie_slices):
                    for i in range(len(legend_markers)):
                        marker = legend_markers[i]
                        current_slice = pie_slices[i]
                        
                        category_name_for_legend = current_slice.property("category_name_prop")
                        if category_name_for_legend is not None:
                            marker.setLabel(str(category_name_for_legend))
                        else:
                            logging.warning(f"Missing 'category_name_prop' for slice: {current_slice.label()} in pie chart legend.")
                else:
                    logging.warning(
                        f"Pie chart legend update: Mismatch between number of slices ({len(pie_slices)}) "
                        f"and legend markers ({len(legend_markers)}). Legend labels might not be updated correctly."
                    )
            
        except Exception as e:
            logging.error(f"Lỗi khi cập nhật dashboard: {str(e)}")
            import traceback; traceback.print_exc()
            QMessageBox.critical(self, "Lỗi", f"Không thể cập nhật dashboard: {str(e)}")

    def on_bar_hovered(self, status, index, barset):
        try:
            if not barset: QToolTip.hideText(); return

            if status:
                axis_x = self.budget_chart.axisX()
                if not axis_x or not hasattr(axis_x, 'categories') or not axis_x.categories():
                    QToolTip.hideText(); return
                
                categories_list = axis_x.categories()
                if index >= len(categories_list) or index >= barset.count():
                    QToolTip.hideText(); return
                
                category_name = categories_list[index]
                current_bar_value = barset.at(index)
                other_bar_set_label = "Đã chi tiêu" if barset.label() == "Ngân sách" else "Ngân sách"
                other_bar_value = 0

                for series_item in self.budget_chart.series():
                    if isinstance(series_item, QBarSeries):
                        for bs in series_item.barSets():
                            if bs.label() == other_bar_set_label and index < bs.count():
                                other_bar_value = bs.at(index); break
                        if other_bar_value != 0 or (barset.label() == "Đã chi tiêu" and other_bar_set_label == "Ngân sách"): 
                            break 
                
                tip = f"<b>{category_name}</b><br/>"
                if barset.label() == "Ngân sách":
                    tip += f"Ngân sách: {current_bar_value:,.0f} đ<br/>Đã chi tiêu: {other_bar_value:,.0f} đ"
                else:
                    tip += f"Ngân sách: {other_bar_value:,.0f} đ<br/>Đã chi tiêu: {current_bar_value:,.0f} đ"
                
                QToolTip.showText(self.cursor().pos(), tip, self.budget_chart_view)
            else:
                QToolTip.hideText()
        except Exception as e:
            logging.error(f"Lỗi trong on_bar_hovered: {e}")
            import traceback; traceback.print_exc()
            QToolTip.hideText()

    def on_slice_hovered(self, slice, state):
        try:
            if state:
                category_name = slice.property("category_name_prop")
                value = slice.property("category_value_prop")
                percentage = slice.property("category_percentage_prop")
                
                if category_name is None or value is None or percentage is None: 
                    QToolTip.hideText() 
                    return

                tooltip_text = f"<b>{category_name}</b><br/>{value:,.0f} đ ({percentage:.1f}%)"
                QToolTip.showText(self.cursor().pos(), tooltip_text, self.spending_chart_view)
            else:
                QToolTip.hideText()
        except Exception as e:
            logging.error(f"Lỗi trong on_slice_hovered: {e}")
            QToolTip.hideText()

    def _parse_date(self, date_str):
        try: return datetime.datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
        except: return None

    def handle_add_income(self): print("[QuickAction] Thêm thu nhập")
    def handle_add_expense(self): print("[QuickAction] Thêm chi tiêu")
    def handle_view_report(self): print("[QuickAction] Xem báo cáo")
    def handle_view_budget(self): print("[QuickAction] Xem ngân sách")