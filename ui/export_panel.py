"""
Export panel for KP Astrology Dashboard.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGroupBox, QCheckBox, QComboBox, QFileDialog,
    QLineEdit, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal


class ExportPanel(QWidget):
    """Panel for export options and controls."""

    # Signal emitted when export is requested
    export_requested = pyqtSignal(dict)

    def __init__(self, parent=None):
        """Initialize the export panel."""
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Export Options")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 14pt; font-weight: bold;")

        # File options
        file_group = QGroupBox("File Options")
        file_layout = QGridLayout(file_group)

        file_layout.addWidget(QLabel("Export Format:"), 0, 0)

        self.format_combo = QComboBox()
        self.format_combo.addItems(["Excel (.xlsx)", "CSV (.csv)", "HTML (.html)"])
        file_layout.addWidget(self.format_combo, 0, 1)

        file_layout.addWidget(QLabel("File Name:"), 1, 0)

        self.filename_layout = QHBoxLayout()
        self.filename_edit = QLineEdit("KP_Astrology_Report")
        self.filename_layout.addWidget(self.filename_edit)

        self.browse_button = QPushButton("Browse...")
        self.browse_button.clicked.connect(self.browse_save_location)
        self.filename_layout.addWidget(self.browse_button)

        file_layout.addLayout(self.filename_layout, 1, 1)

        # Content options
        content_group = QGroupBox("Content to Export")
        content_layout = QVBoxLayout(content_group)

        self.planets_cb = QCheckBox("Planet Positions")
        self.planets_cb.setChecked(True)

        self.houses_cb = QCheckBox("House Data")
        self.houses_cb.setChecked(True)

        self.aspects_cb = QCheckBox("Aspects")
        self.aspects_cb.setChecked(True)

        self.hora_cb = QCheckBox("Hora Timings")
        self.hora_cb.setChecked(True)

        self.transits_cb = QCheckBox("Planet Transits")
        self.transits_cb.setChecked(True)

        self.yogas_cb = QCheckBox("Yogas")
        self.yogas_cb.setChecked(True)

        content_layout.addWidget(self.planets_cb)
        content_layout.addWidget(self.houses_cb)
        content_layout.addWidget(self.aspects_cb)
        content_layout.addWidget(self.hora_cb)
        content_layout.addWidget(self.transits_cb)
        content_layout.addWidget(self.yogas_cb)

        # Format options
        format_group = QGroupBox("Formatting Options")
        format_layout = QVBoxLayout(format_group)

        self.highlight_cb = QCheckBox("Highlight Current Time")
        self.highlight_cb.setChecked(True)

        self.color_cb = QCheckBox("Use Color Coding")
        self.color_cb.setChecked(True)

        self.autofilter_cb = QCheckBox("Include AutoFilter")
        self.autofilter_cb.setChecked(True)

        self.separate_sheets_cb = QCheckBox("Use Separate Sheets")
        self.separate_sheets_cb.setChecked(True)

        format_layout.addWidget(self.highlight_cb)
        format_layout.addWidget(self.color_cb)
        format_layout.addWidget(self.autofilter_cb)
        format_layout.addWidget(self.separate_sheets_cb)

        # Export button
        self.export_button = QPushButton("Export")
        self.export_button.setStyleSheet("font-size: 12pt; padding: 8px;")
        self.export_button.clicked.connect(self.request_export)

        # Add widgets to main layout
        main_layout.addWidget(title_label)
        main_layout.addWidget(file_group)
        main_layout.addWidget(content_group)
        main_layout.addWidget(format_group)
        main_layout.addStretch()
        main_layout.addWidget(self.export_button)

    def browse_save_location(self):
        """Open file dialog to select save location."""
        # Get current format extension
        format_text = self.format_combo.currentText()
        if "Excel" in format_text:
            extension = "xlsx"
            filter_text = "Excel Files (*.xlsx)"
        elif "CSV" in format_text:
            extension = "csv"
            filter_text = "CSV Files (*.csv)"
        else:
            extension = "html"
            filter_text = "HTML Files (*.html)"

        # Get current filename
        current_filename = self.filename_edit.text()
        if not current_filename.endswith(f".{extension}"):
            current_filename = f"{current_filename}.{extension}"

        # Open save dialog
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Export As",
            current_filename,
            filter_text
        )

        if file_path:
            # Update filename field (without extension)
            if f".{extension}" in file_path:
                base_filename = file_path[:-len(f".{extension}")]
                self.filename_edit.setText(base_filename)
            else:
                self.filename_edit.setText(file_path)

    def request_export(self):
        """Emit signal with export options."""
        # Collect all options
        options = {
            "format": self.format_combo.currentText().split(" ")[0].lower(),
            "filename": self.filename_edit.text(),
            "content": {
                "planets": self.planets_cb.isChecked(),
                "houses": self.houses_cb.isChecked(),
                "aspects": self.aspects_cb.isChecked(),
                "hora": self.hora_cb.isChecked(),
                "transits": self.transits_cb.isChecked(),
                "yogas": self.yogas_cb.isChecked()
            },
            "formatting": {
                "highlight_current": self.highlight_cb.isChecked(),
                "color_coding": self.color_cb.isChecked(),
                "autofilter": self.autofilter_cb.isChecked(),
                "separate_sheets": self.separate_sheets_cb.isChecked()
            }
        }

        # Emit signal
        self.export_requested.emit(options)