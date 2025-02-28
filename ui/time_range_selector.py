"""
Time range selector component for KP Astrology Dashboard.
Provides UI for selecting start and end dates/times for calculations.
"""
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QTimeEdit, QGroupBox, QRadioButton, QButtonGroup,
    QComboBox
)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal


class TimeRangeSelector(QGroupBox):
    """Widget for selecting a time range for calculations."""

    # Signal emitted when time range changes
    range_changed = pyqtSignal(datetime, datetime)

    def __init__(self, parent=None):
        """Initialize the time range selector."""
        super().__init__("Time Range Selection", parent)
        self.init_ui()

    def init_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)

        # Range type selection
        range_type_layout = QHBoxLayout()
        self.range_type_group = QButtonGroup(self)

        self.custom_range_rb = QRadioButton("Custom Range")
        self.custom_range_rb.setChecked(True)
        self.custom_range_rb.toggled.connect(self.on_range_type_changed)
        self.range_type_group.addButton(self.custom_range_rb)

        self.preset_range_rb = QRadioButton("Preset Range")
        self.preset_range_rb.toggled.connect(self.on_range_type_changed)
        self.range_type_group.addButton(self.preset_range_rb)

        range_type_layout.addWidget(self.custom_range_rb)
        range_type_layout.addWidget(self.preset_range_rb)
        range_type_layout.addStretch()

        # Custom range selection
        self.custom_range_widget = QWidget()
        custom_range_layout = QVBoxLayout(self.custom_range_widget)

        # Start date/time
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel("Start:"))

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.dateChanged.connect(self.on_range_changed)
        start_layout.addWidget(self.start_date_edit)

        self.start_time_edit = QTimeEdit()
        self.start_time_edit.setDisplayFormat("hh:mm")
        self.start_time_edit.setTime(QTime(0, 0))
        self.start_time_edit.timeChanged.connect(self.on_range_changed)
        start_layout.addWidget(self.start_time_edit)

        custom_range_layout.addLayout(start_layout)

        # End date/time
        end_layout = QHBoxLayout()
        end_layout.addWidget(QLabel("End:"))

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.dateChanged.connect(self.on_range_changed)
        end_layout.addWidget(self.end_date_edit)

        self.end_time_edit = QTimeEdit()
        self.end_time_edit.setDisplayFormat("hh:mm")
        self.end_time_edit.setTime(QTime(23, 59))
        self.end_time_edit.timeChanged.connect(self.on_range_changed)
        end_layout.addWidget(self.end_time_edit)

        custom_range_layout.addLayout(end_layout)

        # Quick selection buttons
        quick_buttons_layout = QHBoxLayout()

        today_btn = QPushButton("Today")
        today_btn.clicked.connect(self.set_today)
        quick_buttons_layout.addWidget(today_btn)

        tomorrow_btn = QPushButton("Tomorrow")
        tomorrow_btn.clicked.connect(self.set_tomorrow)
        quick_buttons_layout.addWidget(tomorrow_btn)

        week_btn = QPushButton("This Week")
        week_btn.clicked.connect(self.set_this_week)
        quick_buttons_layout.addWidget(week_btn)

        month_btn = QPushButton("This Month")
        month_btn.clicked.connect(self.set_this_month)
        quick_buttons_layout.addWidget(month_btn)

        custom_range_layout.addLayout(quick_buttons_layout)

        # Preset range selection
        self.preset_range_widget = QWidget()
        preset_range_layout = QVBoxLayout(self.preset_range_widget)

        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("Preset:"))

        self.preset_combo = QComboBox()
        self.preset_combo.addItems([
            "Today", "Tomorrow", "Next 3 Days",
            "Next Week", "Next Month",
            "Past 3 Days", "Past Week", "Past Month",
            "Custom Days Range"
        ])
        self.preset_combo.currentIndexChanged.connect(self.on_preset_changed)
        preset_layout.addWidget(self.preset_combo)

        preset_range_layout.addLayout(preset_layout)

        # Custom days range
        custom_days_layout = QHBoxLayout()

        custom_days_layout.addWidget(QLabel("Past Days:"))
        self.past_days_combo = QComboBox()
        self.past_days_combo.addItems(["0", "1", "3", "7", "14", "30", "60", "90"])
        self.past_days_combo.setCurrentIndex(3)  # Default to 7 days
        self.past_days_combo.currentIndexChanged.connect(self.on_range_changed)
        custom_days_layout.addWidget(self.past_days_combo)

        custom_days_layout.addWidget(QLabel("Future Days:"))
        self.future_days_combo = QComboBox()
        self.future_days_combo.addItems(["0", "1", "3", "7", "14", "30", "60", "90"])
        self.future_days_combo.setCurrentIndex(4)  # Default to 14 days
        self.future_days_combo.currentIndexChanged.connect(self.on_range_changed)
        custom_days_layout.addWidget(self.future_days_combo)

        preset_range_layout.addLayout(custom_days_layout)

        # Add widgets to main layout
        main_layout.addLayout(range_type_layout)
        main_layout.addWidget(self.custom_range_widget)
        main_layout.addWidget(self.preset_range_widget)

        # Set initial visibility
        self.preset_range_widget.setVisible(False)

        # Initial range calculation
        self.on_range_changed()

    def on_range_type_changed(self):
        """Handle change in range type selection."""
        is_custom = self.custom_range_rb.isChecked()

        self.custom_range_widget.setVisible(is_custom)
        self.preset_range_widget.setVisible(not is_custom)

        self.on_range_changed()

    def on_preset_changed(self):
        """Handle change in preset selection."""
        preset = self.preset_combo.currentText()

        if preset == "Today":
            self.set_today()
        elif preset == "Tomorrow":
            self.set_tomorrow()
        elif preset == "Next 3 Days":
            self.set_next_days(3)
        elif preset == "Next Week":
            self.set_next_days(7)
        elif preset == "Next Month":
            self.set_next_days(30)
        elif preset == "Past 3 Days":
            self.set_past_days(3)
        elif preset == "Past Week":
            self.set_past_days(7)
        elif preset == "Past Month":
            self.set_past_days(30)
        # For "Custom Days Range" we just use the past/future day combos

        self.on_range_changed()

    def on_range_changed(self):
        """Update and emit the new time range."""
        start_time, end_time = self.get_time_range()
        self.range_changed.emit(start_time, end_time)

    def get_time_range(self) -> tuple:
        """
        Get the currently selected time range.

        Returns:
            Tuple of (start_datetime, end_datetime)
        """
        if self.custom_range_rb.isChecked():
            # Get values from custom range controls
            start_date = self.start_date_edit.date()
            start_time = self.start_time_edit.time()

            end_date = self.end_date_edit.date()
            end_time = self.end_time_edit.time()

            # Create datetime objects
            start_dt = datetime(
                start_date.year(), start_date.month(), start_date.day(),
                start_time.hour(), start_time.minute()
            )

            end_dt = datetime(
                end_date.year(), end_date.month(), end_date.day(),
                end_time.hour(), end_time.minute()
            )
        else:
            # Use preset range
            now = datetime.now()
            today = datetime(now.year, now.month, now.day)

            if self.preset_combo.currentText() == "Custom Days Range":
                # Get days from combos
                past_days = int(self.past_days_combo.currentText())
                future_days = int(self.future_days_combo.currentText())

                start_dt = today - timedelta(days=past_days)
                end_dt = today + timedelta(days=future_days, hours=23, minutes=59)
            else:
                # This won't be reached as we handle presets in on_preset_changed()
                # but keeping it as a fallback
                start_dt = today
                end_dt = today + timedelta(hours=23, minutes=59)

        return start_dt, end_dt

    def set_today(self):
        """Set range to today."""
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)

        if self.custom_range_rb.isChecked():
            self.start_date_edit.setDate(QDate(today.year, today.month, today.day))
            self.start_time_edit.setTime(QTime(0, 0))

            self.end_date_edit.setDate(QDate(today.year, today.month, today.day))
            self.end_time_edit.setTime(QTime(23, 59))
        else:
            # Set past and future days to 0
            self.past_days_combo.setCurrentText("0")
            self.future_days_combo.setCurrentText("0")

    def set_tomorrow(self):
        """Set range to tomorrow."""
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        tomorrow = today + timedelta(days=1)

        if self.custom_range_rb.isChecked():
            self.start_date_edit.setDate(QDate(tomorrow.year, tomorrow.month, tomorrow.day))
            self.start_time_edit.setTime(QTime(0, 0))

            self.end_date_edit.setDate(QDate(tomorrow.year, tomorrow.month, tomorrow.day))
            self.end_time_edit.setTime(QTime(23, 59))
        else:
            # Set past days to 0 and future days to 1
            self.past_days_combo.setCurrentText("0")
            self.future_days_combo.setCurrentText("1")

    def set_this_week(self):
        """Set range to current week."""
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)

        # Calculate days until end of week (assuming Sunday is end of week)
        days_to_end = 6 - today.weekday()
        if days_to_end < 0:
            days_to_end += 7

        week_end = today + timedelta(days=days_to_end)

        if self.custom_range_rb.isChecked():
            self.start_date_edit.setDate(QDate(today.year, today.month, today.day))
            self.start_time_edit.setTime(QTime(0, 0))

            self.end_date_edit.setDate(QDate(week_end.year, week_end.month, week_end.day))
            self.end_time_edit.setTime(QTime(23, 59))
        else:
            # Use preset "Next Week"
            self.preset_combo.setCurrentText("Next Week")

    def set_this_month(self):
        """Set range to current month."""
        now = datetime.now()
        month_start = datetime(now.year, now.month, 1)

        # Calculate last day of month
        if now.month == 12:
            next_month = datetime(now.year + 1, 1, 1)
        else:
            next_month = datetime(now.year, now.month + 1, 1)

        month_end = next_month - timedelta(days=1)

        if self.custom_range_rb.isChecked():
            self.start_date_edit.setDate(QDate(month_start.year, month_start.month, month_start.day))
            self.start_time_edit.setTime(QTime(0, 0))

            self.end_date_edit.setDate(QDate(month_end.year, month_end.month, month_end.day))
            self.end_time_edit.setTime(QTime(23, 59))
        else:
            # Use preset "Next Month"
            self.preset_combo.setCurrentText("Next Month")

    def set_next_days(self, days):
        """
        Set range to specified number of future days.

        Args:
            days: Number of days in the future
        """
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        end_day = today + timedelta(days=days - 1)  # -1 because we include today

        if self.custom_range_rb.isChecked():
            self.start_date_edit.setDate(QDate(today.year, today.month, today.day))
            self.start_time_edit.setTime(QTime(0, 0))

            self.end_date_edit.setDate(QDate(end_day.year, end_day.month, end_day.day))
            self.end_time_edit.setTime(QTime(23, 59))
        else:
            # Set past days to 0 and future days to the specified value
            self.past_days_combo.setCurrentText("0")
            if str(days) in [self.future_days_combo.itemText(i) for i in range(self.future_days_combo.count())]:
                self.future_days_combo.setCurrentText(str(days))
            else:
                # Find closest value
                values = [int(self.future_days_combo.itemText(i)) for i in range(self.future_days_combo.count())]
                closest = min(values, key=lambda x: abs(x - days))
                self.future_days_combo.setCurrentText(str(closest))

    def set_past_days(self, days):
        """
        Set range to specified number of past days.

        Args:
            days: Number of days in the past
        """
        now = datetime.now()
        today = datetime(now.year, now.month, now.day)
        start_day = today - timedelta(days=days)

        if self.custom_range_rb.isChecked():
            self.start_date_edit.setDate(QDate(start_day.year, start_day.month, start_day.day))
            self.start_time_edit.setTime(QTime(0, 0))

            self.end_date_edit.setDate(QDate(today.year, today.month, today.day))
            self.end_time_edit.setTime(QTime(23, 59))
        else:
            # Set past days to the specified value and future days to 0
            if str(days) in [self.past_days_combo.itemText(i) for i in range(self.past_days_combo.count())]:
                self.past_days_combo.setCurrentText(str(days))
            else:
                # Find closest value
                values = [int(self.past_days_combo.itemText(i)) for i in range(self.past_days_combo.count())]
                closest = min(values, key=lambda x: abs(x - days))
                self.past_days_combo.setCurrentText(str(closest))
            self.future_days_combo.setCurrentText("0")