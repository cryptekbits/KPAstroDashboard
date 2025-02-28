"""
Date and time selection panel for KP Astrology Dashboard.
"""
from datetime import datetime
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QDateEdit, QTimeEdit, QCheckBox, QGroupBox, QRadioButton,
    QButtonGroup
)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal


class DateTimePanel(QGroupBox):
    """Panel for selecting date and time."""

    # Signal emitted when date/time selection changes
    datetime_changed = pyqtSignal(datetime)

    def __init__(self, parent=None):
        """Initialize the date time panel."""
        super().__init__("Date & Time Selection", parent)
        self.init_ui()

    def init_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)

        # Current datetime object for reference
        current_dt = datetime.now()

        # Date selection
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDate(QDate(current_dt.year, current_dt.month, current_dt.day))
        self.date_picker.dateChanged.connect(self.on_datetime_changed)

        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_picker)

        # Quick date buttons
        quick_date_layout = QHBoxLayout()

        today_btn = QPushButton("Today")
        today_btn.clicked.connect(self.set_today)

        yesterday_btn = QPushButton("Yesterday")
        yesterday_btn.clicked.connect(self.set_yesterday)

        tomorrow_btn = QPushButton("Tomorrow")
        tomorrow_btn.clicked.connect(self.set_tomorrow)

        quick_date_layout.addWidget(today_btn)
        quick_date_layout.addWidget(yesterday_btn)
        quick_date_layout.addWidget(tomorrow_btn)

        # Time selection
        time_layout = QHBoxLayout()
        time_label = QLabel("Time:")
        self.time_picker = QTimeEdit()
        self.time_picker.setDisplayFormat("hh:mm:ss AP")
        self.time_picker.setTime(QTime(current_dt.hour, current_dt.minute, current_dt.second))
        self.time_picker.timeChanged.connect(self.on_datetime_changed)

        time_layout.addWidget(time_label)
        time_layout.addWidget(self.time_picker)

        # Quick time buttons
        quick_time_layout = QHBoxLayout()

        now_btn = QPushButton("Current Time")
        now_btn.clicked.connect(self.set_current_time)

        noon_btn = QPushButton("Noon (12:00 PM)")
        noon_btn.clicked.connect(self.set_noon)

        midnight_btn = QPushButton("Midnight (12:00 AM)")
        midnight_btn.clicked.connect(self.set_midnight)

        sunrise_btn = QPushButton("Sunrise (~6:00 AM)")
        sunrise_btn.clicked.connect(self.set_sunrise)

        sunset_btn = QPushButton("Sunset (~6:00 PM)")
        sunset_btn.clicked.connect(self.set_sunset)

        quick_time_layout.addWidget(now_btn)
        quick_time_layout.addWidget(noon_btn)
        quick_time_layout.addWidget(midnight_btn)
        quick_time_layout.addWidget(sunrise_btn)
        quick_time_layout.addWidget(sunset_btn)

        # Use current time checkbox
        current_time_layout = QHBoxLayout()
        self.use_current_time_cb = QCheckBox("Use Current Time")
        self.use_current_time_cb.stateChanged.connect(self.toggle_current_time)

        current_time_layout.addWidget(self.use_current_time_cb)
        current_time_layout.addStretch()

        # Time format selection
        time_format_group = QGroupBox("Time Format")
        time_format_layout = QHBoxLayout(time_format_group)

        self.time_format_group = QButtonGroup(self)

        self.local_time_rb = QRadioButton("Local Time")
        self.local_time_rb.setChecked(True)

        self.sidereal_time_rb = QRadioButton("Sidereal Time")

        self.time_format_group.addButton(self.local_time_rb)
        self.time_format_group.addButton(self.sidereal_time_rb)

        time_format_layout.addWidget(self.local_time_rb)
        time_format_layout.addWidget(self.sidereal_time_rb)

        # Add all layouts to main layout
        main_layout.addLayout(date_layout)
        main_layout.addLayout(quick_date_layout)
        main_layout.addLayout(time_layout)
        main_layout.addLayout(quick_time_layout)
        main_layout.addLayout(current_time_layout)
        main_layout.addWidget(time_format_group)

        # Set up timer for current time updates if needed
        self.current_time_timer = None
        if self.use_current_time_cb.isChecked():
            self.toggle_current_time(Qt.Checked)

    def set_today(self):
        """Set the date to today."""
        today = QDate.currentDate()
        self.date_picker.setDate(today)

    def set_yesterday(self):
        """Set the date to yesterday."""
        yesterday = QDate.currentDate().addDays(-1)
        self.date_picker.setDate(yesterday)

    def set_tomorrow(self):
        """Set the date to tomorrow."""
        tomorrow = QDate.currentDate().addDays(1)
        self.date_picker.setDate(tomorrow)

    def set_current_time(self):
        """Set the time to current time."""
        current_time = QTime.currentTime()
        self.time_picker.setTime(current_time)

    def set_noon(self):
        """Set the time to noon (12:00 PM)."""
        self.time_picker.setTime(QTime(12, 0, 0))

    def set_midnight(self):
        """Set the time to midnight (12:00 AM)."""
        self.time_picker.setTime(QTime(0, 0, 0))

    def set_sunrise(self):
        """Set the time to approximate sunrise (6:00 AM)."""
        self.time_picker.setTime(QTime(6, 0, 0))

    def set_sunset(self):
        """Set the time to approximate sunset (6:00 PM)."""
        self.time_picker.setTime(QTime(18, 0, 0))

    def get_selected_datetime(self):
        """
        Get the currently selected date and time as a datetime object.

        Returns:
            datetime: The selected date and time
        """
        # If using current time, return current datetime
        if self.use_current_time_cb.isChecked():
            return datetime.now()

        # Get selected date
        qdate = self.date_picker.date()

        # Get selected time
        qtime = self.time_picker.time()

        # Combine into datetime
        return datetime(
            qdate.year(),
            qdate.month(),
            qdate.day(),
            qtime.hour(),
            qtime.minute(),
            qtime.second()
        )

    def on_datetime_changed(self):
        """Handle date or time changes."""
        # Only emit the signal if not using current time
        if not self.use_current_time_cb.isChecked():
            self.datetime_changed.emit(self.get_selected_datetime())

    def toggle_current_time(self, state):
        """
        Toggle using current time vs selected time.

        Args:
            state: CheckBox state (Qt.Checked or Qt.Unchecked)
        """
        if state == Qt.Checked:
            # Disable date and time pickers
            self.date_picker.setEnabled(False)
            self.time_picker.setEnabled(False)

            # Create timer to update current time if not already created
            if not self.current_time_timer:
                from PyQt5.QtCore import QTimer
                self.current_time_timer = QTimer(self)
                self.current_time_timer.timeout.connect(self.update_current_time_display)
                self.current_time_timer.start(1000)  # Update every second

            # Update display immediately
            self.update_current_time_display()

            # Emit signal with current time
            self.datetime_changed.emit(datetime.now())
        else:
            # Enable date and time pickers
            self.date_picker.setEnabled(True)
            self.time_picker.setEnabled(True)

            # Stop timer if running
            if self.current_time_timer:
                self.current_time_timer.stop()

            # Emit signal with selected time
            self.datetime_changed.emit(self.get_selected_datetime())

    def update_current_time_display(self):
        """Update the display to show current time."""
        current_dt = datetime.now()
        current_date = QDate(current_dt.year, current_dt.month, current_dt.day)
        current_time = QTime(current_dt.hour, current_dt.minute, current_dt.second)

        # Update display (but do not trigger signals)
        self.date_picker.blockSignals(True)
        self.time_picker.blockSignals(True)

        self.date_picker.setDate(current_date)
        self.time_picker.setTime(current_time)

        self.date_picker.blockSignals(False)
        self.time_picker.blockSignals(False)