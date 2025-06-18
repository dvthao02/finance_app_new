import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTableWidget, 
    QTableWidgetItem, QGroupBox, QDateEdit, QSizePolicy, QSpacerItem, QToolTip, QMessageBox,
    QHeaderView, QScrollArea, QProgressBar # Added QProgressBar
)
from PyQt5.QtCore import Qt, QDate, QMargins, QPointF, QLineF
from PyQt5.QtGui import QFont, QPainter, QColor, QCursor, QPalette # Added QPalette, Added QCursor
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

class HoverableBudgetListItemWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)
        self.original_palette = self.palette()
        self.hover_palette = QPalette(self.original_palette) # QPalette is now defined
        self.hover_palette.setColor(QPalette.Window, QColor("#e9ecef")) # Light gray for hover

    def enterEvent(self, event):
        self.setPalette(self.hover_palette)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setPalette(self.original_palette)
        super().leaveEvent(event)

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
        self.charts_group = QGroupBox("Biểu đồ và Ngân sách tháng này") # Adjusted title
        charts_group_layout = QVBoxLayout() 
        chart_layout_h = QHBoxLayout() 

        # New Budget Overview List Section - Initialized here but added to chart_layout_h
        self.budget_overview_list_group = QGroupBox("Ngân sách tháng này")
        self.budget_overview_list_group.setStyleSheet("QGroupBox { font-weight: bold; }")
        self.budget_overview_list_layout = QVBoxLayout()
        self.budget_overview_list_group.setLayout(self.budget_overview_list_layout)
        self.budget_overview_list_group.setMinimumHeight(300) # Give it some initial height
        self.budget_overview_list_group.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)

        # Add Budget Overview List to the left side of the horizontal chart layout
        chart_layout_h.addWidget(self.budget_overview_list_group, 1) # Assign stretch factor 1
        
        # Tạo biểu đồ tròn cho chi tiêu (remains on the right)
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
        chart_layout_h.addWidget(self.spending_chart_view, 1) # Assign stretch factor 1

        charts_group_layout.addLayout(chart_layout_h) 
        self.charts_group.setLayout(charts_group_layout)
        main_layout.addWidget(self.charts_group)

        # Remove the old placement of budget_overview_list_group from main_layout if it was there
        # (It was added directly to main_layout in previous versions, ensure it's not added twice)
        # The new placement is inside chart_layout_h

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
                logging.warning("UserOverviewTab: User ID, TransactionManager, or CategoryManager not available for dashboard update.")
                self.balance_card.set_value(0); self.expense_card.set_value(0); self.saving_card.set_value(0)
                self.tx_table.setRowCount(0)
                if hasattr(self, 'spending_series'): self.spending_series.clear()
                return
            
            logging.debug(f"UserOverviewTab: Starting dashboard update for user {self.user_id}. Filter: {current_filter_text}")
            start_date, end_date = self.get_filter_dates()
            logging.debug(f"UserOverviewTab: Date range for transactions: Start={start_date}, End={end_date}")
            transactions = self.transaction_manager.get_transactions_in_range(start_date, end_date, self.user_id)
            logging.debug(f"UserOverviewTab: Found {len(transactions)} transactions in range.")
            
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

            # --- REMOVE OLD BUDGET BAR CHART LOGIC ---
            # if self.budget_manager:
            #     # self.budget_chart.removeAllSeries() # This was the source of the error
            #     # for axis in self.budget_chart.axes(): self.budget_chart.removeAxis(axis)
            #     
            #     logging.info(f"UserOverviewTab: Updating budget chart for user {self.user_id}. Filter: {self.filter_combo.currentText()}")
            #     all_user_budgets = self.budget_manager.get_budgets_by_user(self.user_id)
            #     logging.info(f"UserOverviewTab: Raw budgets from budget_manager for user {self.user_id} ({len(all_user_budgets)} items): {all_user_budgets}")
            #
            #     budgets_for_period = []
            #     current_display_month = None
            #     current_display_year = None
            #
            #     if current_filter_text == "Tháng này":
            #         today = datetime.date.today()
            #         current_display_month = today.month
            #         current_display_year = today.year
            #         logging.debug(f"UserOverviewTab: Filter is 'Tháng này'. Target year={current_display_year}, month={current_display_month} for budgets.")
            #     else:
            #         logging.debug(f"UserOverviewTab: Filter is '{current_filter_text}'. Budget chart will show all user budgets with limit > 0.")
            #
            #     for budget_item in all_user_budgets:
            #         budget_cat_id = budget_item.get('category_id')
            #         budget_limit = budget_item.get('limit', 0)
            #         try:
            #             b_month = int(budget_item.get('month'))
            #             b_year = int(budget_item.get('year'))
            #         except (ValueError, TypeError):
            #             logging.warning(f"UserOverviewTab: Budget item has invalid month/year: {budget_item}. Skipping.")
            #             continue
            #
            #         logging.debug(f"UserOverviewTab: Checking budget: ID={budget_item.get('id')}, CatID='{budget_cat_id}', M={b_month}(type:{type(b_month)}), Y={b_year}(type:{type(b_year)}), Limit={budget_limit}, current_amount={budget_item.get('current_amount')}")
            #
            #         if budget_limit > 0:
            #             if current_display_year and current_display_month: 
            #                 if b_year == current_display_year and b_month == current_display_month:
            #                     budgets_for_period.append(budget_item)
            #             else: 
            #                 budgets_for_period.append(budget_item)
            #     
            #     logging.info(f"UserOverviewTab: Filtered budgets_for_period before charting ({len(budgets_for_period)} items): {budgets_for_period}")
            #     
            #     # Clear previous chart data for tooltips - These attributes are removed
            #     # self.chart_category_names = []
            #     # self.chart_budget_values = []
            #     # self.chart_spent_values = []
            #
            #     # ... (Logic for populating self.chart_category_names etc. and updating self.budget_chart) ...
            #     # This entire block for self.budget_chart is now removed.
            #
            #     # if self.chart_category_names: 
            #     #    ... (add series to self.budget_chart) ...
            #     # else:
            #     #    # Determine the correct "no data" message 
            #     #    if not budgets_for_period: 
            #     #        self.budget_chart.setTitle("Ngân sách và chi tiêu (Không có dữ liệu ngân sách cho kỳ này)")
            #     #    else: 
            #     #        self.budget_chart.setTitle("Ngân sách và chi tiêu (Không có dữ liệu hợp lệ để vẽ biểu đồ)")
            # --- END REMOVE OLD BUDGET BAR CHART LOGIC ---
            
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
                # Update legend items based on current slices
                legend_markers = self.spending_chart.legend().markers(self.spending_series)
                for i, s_slice in enumerate(self.spending_series.slices()):
                    if i < len(legend_markers):
                        cat_name = s_slice.property("category_name_prop")
                        if cat_name:
                             legend_markers[i].setLabel(cat_name)
            
            # ---- Update Budget Overview List ----
            # Clear previous budget list items
            while self.budget_overview_list_layout.count():
                child = self.budget_overview_list_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()

            if self.budget_manager and self.user_id and self.category_manager:
                today = datetime.date.today()
                current_month_budgets = self.budget_manager.get_budgets_by_month(today.year, today.month, self.user_id)
                
                logging.debug(f"UserOverviewTab: Found {len(current_month_budgets)} budgets for current month ({today.month}/{today.year}) for overview list.")
                
                if not current_month_budgets:
                    no_budget_label = QLabel("Không có ngân sách nào được thiết lập cho tháng này.")
                    no_budget_label.setAlignment(Qt.AlignCenter)
                    no_budget_label.setStyleSheet("padding: 10px; color: grey;")
                    self.budget_overview_list_layout.addWidget(no_budget_label)
                else:
                    for budget in current_month_budgets:
                        category_id = budget.get('category_id')
                        category_name = "N/A"
                        if category_id:
                            cat_obj = self.category_manager.get_category_by_id(category_id)
                            if cat_obj:
                                category_name = cat_obj.get('name', 'N/A')
                        
                        limit = budget.get('limit', 0)
                        # current_amount now represents the REMAINING balance
                        remaining = budget.get('current_amount', 0)  # remaining balance
                        spent = limit - remaining  # spent = limit - remaining
                        
                        # Ensure spent is not negative (in case of data inconsistency)
                        spent = max(0, spent)
                        
                        percentage = 0
                        if limit > 0:
                            percentage = int((spent / limit) * 100)
                        percentage = min(max(percentage, 0), 100) # Clamp

                        item_widget = HoverableBudgetListItemWidget() # MODIFIED HERE
                        item_layout = QHBoxLayout(item_widget)
                        item_layout.setContentsMargins(8, 5, 8, 5) # Adjusted margins for a bit more padding

                        name_label = QLabel(f"{category_name}")
                        name_label.setMinimumWidth(100) 
                        name_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
                        name_label.setStyleSheet("background-color: transparent;") # Ensure label bg is transparent

                        progress_bar = QProgressBar()
                        progress_bar.setValue(percentage)
                        progress_bar.setFormat(f"{percentage}%")
                        progress_bar.setFixedHeight(18) # Slightly smaller height
                        progress_bar.setStyleSheet("background-color: transparent;") # Ensure progressbar bg is transparent within item_widget

                        progress_bar_style_sheet = (
                            "QProgressBar {"
                            "    border: 1px solid #cccccc;"
                            "    border-radius: 5px;"
                            "    text-align: center;"
                            "    height: 18px;"
                            "    background-color: #f0f0f0;"
                            "    /* Lighter background for the bar track */"
                            "}"
                            "QProgressBar::chunk {"
                            "    background-color: %s;"
                            "    border-radius: 4px;"
                            "}"
                        )
                        chunk_color = "#10b981" # Default Green
                        if percentage >= 90:
                            chunk_color = "#ef4444" # Red
                        elif percentage >= 75:
                            chunk_color = "#f97316" # Orange
                        progress_bar.setStyleSheet(progress_bar_style_sheet % chunk_color)

                        item_layout.addWidget(name_label)
                        item_layout.addWidget(progress_bar, 1) 

                        tooltip_text = (f"<b>{category_name}</b><br>"
                                        f"Giới hạn: {limit:,.0f} đ<br>"
                                        f"Đã chi: {spent:,.0f} đ<br>"
                                        f"Còn lại: {remaining:,.0f} đ<br>"
                                        f"Tiến độ: {percentage}%")
                        item_widget.setToolTip(tooltip_text)
                        
                        self.budget_overview_list_layout.addWidget(item_widget)
                    
                    self.budget_overview_list_layout.addStretch(1) 
            else:
                if not self.budget_manager: logging.warning("UserOverviewTab: BudgetManager not available for budget overview list.")
                if not self.user_id: logging.warning("UserOverviewTab: User ID not available for budget overview list.")
                if not self.category_manager: logging.warning("UserOverviewTab: CategoryManager not available for budget overview list.")
                
                unavailable_label = QLabel("Không thể tải danh sách ngân sách.")
                unavailable_label.setAlignment(Qt.AlignCenter)
                unavailable_label.setStyleSheet("padding: 10px; color: grey;")
                self.budget_overview_list_layout.addWidget(unavailable_label)
            # ---- End of Budget Overview List Update ----

            # Refresh chart views
            self.spending_chart_view.repaint()

        except Exception as e:
            logging.error(f"UserOverviewTab: Lỗi cập nhật dashboard: {e}", exc_info=True)
            # Optionally, display a user-friendly error message in the UI
            # error_dialog = QMessageBox(self)
            # error_dialog.setIcon(QMessageBox.Warning)
            # error_dialog.setText(f"Không thể tải dữ liệu tổng quan: {e}")
            # error_dialog.setWindowTitle("Lỗi")
            # error_dialog.exec_()

    def on_slice_hovered(self, slice, state):
        """Handle pie chart slice hover events"""
        if state:  # Hovering over a slice
            try:
                category_name = slice.property("category_name_prop")
                category_value = slice.property("category_value_prop")
                category_percentage = slice.property("category_percentage_prop")
                
                if category_name and category_value is not None:
                    tooltip_text = (
                        f"<b>{category_name}</b><br>"
                        f"Số tiền: {category_value:,.0f} đ<br>"
                        f"Tỷ lệ: {category_percentage:.1f}%"
                    )
                    QToolTip.showText(QCursor.pos(), tooltip_text)
            except Exception as e:
                logging.error(f"Error in on_slice_hovered: {e}")

    def handle_add_income(self):
        """Handle add income quick action"""
        # This should be connected to the main window's add income functionality
        pass

    def handle_add_expense(self):
        """Handle add expense quick action"""
        # This should be connected to the main window's add expense functionality
        pass

    def handle_view_report(self):
        """Handle view report quick action"""
        # This should be connected to the main window's view report functionality
        pass

    def handle_view_budget(self):
        """Handle view budget quick action"""
        # This should be connected to the main window's view budget functionality
        pass

    def update_budget_overview_list(self):
        # Clear existing items
        for i in reversed(range(self.budget_overview_list_layout.count())):
            widget_item = self.budget_overview_list_layout.itemAt(i)
            if widget_item:
                widget = widget_item.widget()
                if widget is not None:
                    widget.deleteLater()

        if not self.budget_manager or not self.user_id:
            no_data_label = QLabel("Không có dữ liệu ngân sách.")
            self.budget_overview_list_layout.addWidget(no_data_label)
            return

        today = datetime.date.today()
        current_month_budgets = self.budget_manager.get_budgets_by_month_year(self.user_id, today.month, today.year)
        
        if not current_month_budgets:
            no_data_label = QLabel("Không có ngân sách nào cho tháng này.")
            self.budget_overview_list_layout.addWidget(no_data_label)
            return

        for budget_item_data in current_month_budgets:
            category_id = budget_item_data.get("category_id")
            category_name = self.category_manager.get_category_name(category_id) if category_id else "Chưa phân loại"
            limit = budget_item_data.get("limit", 0)
            current_amount_spent = abs(budget_item_data.get("current_amount", 0)) # abs() to ensure positive
            remaining = limit - current_amount_spent
            progress_percentage = (current_amount_spent / limit * 100) if limit > 0 else 0
            
            item_widget = HoverableBudgetListItemWidget() # Use the hoverable widget
            item_layout = QVBoxLayout(item_widget)
            item_layout.setContentsMargins(8, 5, 8, 5) # Add some padding

            name_label = QLabel(f"<b>{category_name}</b>")
            item_layout.addWidget(name_label)

            progress_bar = QProgressBar()
            progress_bar.setValue(int(progress_percentage))
            progress_bar.setTextVisible(False) # Hide default text
            progress_bar.setFixedHeight(12) # Make it a bit slimmer
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #cccccc;
                    border-radius: 5px;
                    background-color: #f0f0f0; /* Lighter background for the bar track */
                    text-align: center;
                }}
                QProgressBar::chunk {{
                    background-color: {'#66bb6a' if progress_percentage <= 70 else ('#ffa726' if progress_percentage <= 100 else '#ef5350')};
                    border-radius: 4px;
                }}
            """)
            item_layout.addWidget(progress_bar)

            details_label = QLabel(f"Đã chi: {current_amount_spent:,.0f}đ / {limit:,.0f}đ")
            details_label.setStyleSheet("font-size: 9pt; color: #555;")
            item_layout.addWidget(details_label)
            
            item_widget.setToolTip(
                f"<b>{category_name}</b><br>"
                f"Ngân sách: {limit:,.0f}đ<br>"
                f"Đã chi: {current_amount_spent:,.0f}đ ({progress_percentage:.1f}%)<br>"
                f"Còn lại: {remaining:,.0f}đ"
            )
            self.budget_overview_list_layout.addWidget(item_widget)

        self.budget_overview_list_layout.addStretch(1) # Push items to the top
