"""
Message panel for displaying informational messages in the KP Astrology Dashboard.
"""
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon


class MessagePanel(QFrame):
    """Panel for displaying informational messages."""

    def __init__(self, message="", icon_path=None, parent=None):
        """
        Initialize the message panel.

        Args:
            message: Message text to display
            icon_path: Path to optional icon
            parent: Parent widget
        """
        super().__init__(parent)

        # Set frame style
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        self.setStyleSheet("background-color: #f0f0f0; border-radius: 5px;")

        # Create layout
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Add icon if provided
        if icon_path:
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(icon_path).pixmap(64, 64))
            icon_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(icon_label)

        # Add message label
        self.message_label = QLabel(message)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setFont(QFont("Arial", 12))

        layout.addWidget(self.message_label)

    def set_message(self, message):
        """
        Update the displayed message.

        Args:
            message: New message text
        """
        self.message_label.setText(message)

    def set_info_style(self):
        """Set style for informational messages."""
        self.setStyleSheet("background-color: #e6f7ff; border: 1px solid #91d5ff; border-radius: 5px;")

    def set_warning_style(self):
        """Set style for warning messages."""
        self.setStyleSheet("background-color: #fff7e6; border: 1px solid #ffd591; border-radius: 5px;")

    def set_error_style(self):
        """Set style for error messages."""
        self.setStyleSheet("background-color: #fff1f0; border: 1px solid #ffa39e; border-radius: 5px;")

    def set_success_style(self):
        """Set style for success messages."""
        self.setStyleSheet("background-color: #f6ffed; border: 1px solid #b7eb8f; border-radius: 5px;")