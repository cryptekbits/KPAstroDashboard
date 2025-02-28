"""
Progress dialog for displaying calculation progress.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QProgressBar,
    QPushButton, QHBoxLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal


class ProgressDialog(QDialog):
    """Dialog for displaying calculation progress."""

    # Signal emitted when cancel button is clicked
    cancelled = pyqtSignal()

    def __init__(self, title="Processing", message="Please wait...", parent=None):
        """
        Initialize the progress dialog.

        Args:
            title: Dialog title
            message: Initial message
            parent: Parent widget
        """
        super().__init__(parent)

        # Set dialog properties
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setModal(True)

        # Create layout
        layout = QVBoxLayout(self)

        # Message label
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.message_label.setWordWrap(True)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setFormat("%p% (%v/%m)")

        # Buttons
        buttons_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.on_cancel)

        buttons_layout.addStretch()
        buttons_layout.addWidget(self.cancel_button)

        # Add widgets to layout
        layout.addWidget(self.message_label)
        layout.addWidget(self.progress_bar)
        layout.addSpacing(10)
        layout.addLayout(buttons_layout)

    def update_progress(self, value, message=None):
        """
        Update progress bar and message.

        Args:
            value: Progress value (0-100)
            message: Optional new message
        """
        self.progress_bar.setValue(value)

        if message:
            self.message_label.setText(message)

        # Auto-close at 100%
        if value >= 100:
            self.accept()

    def on_cancel(self):
        """Handle cancel button click."""
        self.cancelled.emit()
        self.reject()