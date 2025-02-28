"""
Planet selector component for KP Astrology Dashboard.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QCheckBox, QGroupBox, QPushButton
)
from PyQt5.QtCore import Qt, pyqtSignal


class PlanetSelector(QGroupBox):
    """Widget for selecting planets to include in calculations."""

    # Signal emitted when selection changes
    selection_changed = pyqtSignal(list)

    def __init__(self, parent=None):
        """Initialize the planet selector."""
        super().__init__("Select Planets", parent)
        self.init_ui()

    def init_ui(self):
        """Set up the user interface."""
        main_layout = QVBoxLayout(self)

        # Create top row of checkboxes
        top_row = QHBoxLayout()

        self.sun_cb = QCheckBox("Sun")
        self.sun_cb.setChecked(True)
        self.sun_cb.stateChanged.connect(self.on_selection_changed)

        self.moon_cb = QCheckBox("Moon")
        self.moon_cb.setChecked(True)
        self.moon_cb.stateChanged.connect(self.on_selection_changed)

        self.mercury_cb = QCheckBox("Mercury")
        self.mercury_cb.setChecked(True)
        self.mercury_cb.stateChanged.connect(self.on_selection_changed)

        self.venus_cb = QCheckBox("Venus")
        self.venus_cb.setChecked(True)
        self.venus_cb.stateChanged.connect(self.on_selection_changed)

        top_row.addWidget(self.sun_cb)
        top_row.addWidget(self.moon_cb)
        top_row.addWidget(self.mercury_cb)
        top_row.addWidget(self.venus_cb)

        # Create bottom row of checkboxes
        bottom_row = QHBoxLayout()

        self.mars_cb = QCheckBox("Mars")
        self.mars_cb.setChecked(True)
        self.mars_cb.stateChanged.connect(self.on_selection_changed)

        self.jupiter_cb = QCheckBox("Jupiter")
        self.jupiter_cb.setChecked(True)
        self.jupiter_cb.stateChanged.connect(self.on_selection_changed)

        self.saturn_cb = QCheckBox("Saturn")
        self.saturn_cb.setChecked(True)
        self.saturn_cb.stateChanged.connect(self.on_selection_changed)

        self.rahu_cb = QCheckBox("Rahu")
        self.rahu_cb.setChecked(True)
        self.rahu_cb.stateChanged.connect(self.on_selection_changed)

        self.ketu_cb = QCheckBox("Ketu")
        self.ketu_cb.setChecked(True)
        self.ketu_cb.stateChanged.connect(self.on_selection_changed)

        bottom_row.addWidget(self.mars_cb)
        bottom_row.addWidget(self.jupiter_cb)
        bottom_row.addWidget(self.saturn_cb)
        bottom_row.addWidget(self.rahu_cb)
        bottom_row.addWidget(self.ketu_cb)

        # Create third row for additional planets and ascendant
        extra_row = QHBoxLayout()

        self.uranus_cb = QCheckBox("Uranus")
        self.uranus_cb.setChecked(False)
        self.uranus_cb.stateChanged.connect(self.on_selection_changed)

        self.neptune_cb = QCheckBox("Neptune")
        self.neptune_cb.setChecked(False)
        self.neptune_cb.stateChanged.connect(self.on_selection_changed)

        self.pluto_cb = QCheckBox("Pluto")
        self.pluto_cb.setChecked(False)
        self.pluto_cb.stateChanged.connect(self.on_selection_changed)

        self.ascendant_cb = QCheckBox("Ascendant")
        self.ascendant_cb.setChecked(True)
        self.ascendant_cb.stateChanged.connect(self.on_selection_changed)

        extra_row.addWidget(self.uranus_cb)
        extra_row.addWidget(self.neptune_cb)
        extra_row.addWidget(self.pluto_cb)
        extra_row.addWidget(self.ascendant_cb)
        extra_row.addStretch()

        # Create selection buttons
        buttons_row = QHBoxLayout()

        self.select_all_btn = QPushButton("Select All")
        self.select_all_btn.clicked.connect(self.select_all)

        self.select_none_btn = QPushButton("Select None")
        self.select_none_btn.clicked.connect(self.select_none)

        self.select_trad_btn = QPushButton("Traditional")
        self.select_trad_btn.clicked.connect(self.select_traditional)

        self.select_luminaries_btn = QPushButton("Luminaries")
        self.select_luminaries_btn.clicked.connect(self.select_luminaries)

        buttons_row.addWidget(self.select_all_btn)
        buttons_row.addWidget(self.select_none_btn)
        buttons_row.addWidget(self.select_trad_btn)
        buttons_row.addWidget(self.select_luminaries_btn)

        # Add rows to main layout
        main_layout.addLayout(top_row)
        main_layout.addLayout(bottom_row)
        main_layout.addLayout(extra_row)
        main_layout.addLayout(buttons_row)

    def on_selection_changed(self):
        """Handle changes to planet selection."""
        self.selection_changed.emit(self.get_selected_planets())

    def get_selected_planets(self):
        """
        Get list of selected planets.

        Returns:
            list: Names of selected planets
        """
        selected = []

        if self.sun_cb.isChecked():
            selected.append("Sun")
        if self.moon_cb.isChecked():
            selected.append("Moon")
        if self.mercury_cb.isChecked():
            selected.append("Mercury")
        if self.venus_cb.isChecked():
            selected.append("Venus")
        if self.mars_cb.isChecked():
            selected.append("Mars")
        if self.jupiter_cb.isChecked():
            selected.append("Jupiter")
        if self.saturn_cb.isChecked():
            selected.append("Saturn")
        if self.rahu_cb.isChecked():
            selected.append("Rahu")
        if self.ketu_cb.isChecked():
            selected.append("Ketu")
        if self.uranus_cb.isChecked():
            selected.append("Uranus")
        if self.neptune_cb.isChecked():
            selected.append("Neptune")
        if self.pluto_cb.isChecked():
            selected.append("Pluto")
        if self.ascendant_cb.isChecked():
            selected.append("Ascendant")

        return selected

    def select_all(self):
        """Select all planets."""
        self.sun_cb.setChecked(True)
        self.moon_cb.setChecked(True)
        self.mercury_cb.setChecked(True)
        self.venus_cb.setChecked(True)
        self.mars_cb.setChecked(True)
        self.jupiter_cb.setChecked(True)
        self.saturn_cb.setChecked(True)
        self.rahu_cb.setChecked(True)
        self.ketu_cb.setChecked(True)
        self.uranus_cb.setChecked(True)
        self.neptune_cb.setChecked(True)
        self.pluto_cb.setChecked(True)
        self.ascendant_cb.setChecked(True)

    def select_none(self):
        """Deselect all planets."""
        self.sun_cb.setChecked(False)
        self.moon_cb.setChecked(False)
        self.mercury_cb.setChecked(False)
        self.venus_cb.setChecked(False)
        self.mars_cb.setChecked(False)
        self.jupiter_cb.setChecked(False)
        self.saturn_cb.setChecked(False)
        self.rahu_cb.setChecked(False)
        self.ketu_cb.setChecked(False)
        self.uranus_cb.setChecked(False)
        self.neptune_cb.setChecked(False)
        self.pluto_cb.setChecked(False)
        self.ascendant_cb.setChecked(False)

    def select_traditional(self):
        """Select traditional planets (Sun through Saturn plus nodes)."""
        self.sun_cb.setChecked(True)
        self.moon_cb.setChecked(True)
        self.mercury_cb.setChecked(True)
        self.venus_cb.setChecked(True)
        self.mars_cb.setChecked(True)
        self.jupiter_cb.setChecked(True)
        self.saturn_cb.setChecked(True)
        self.rahu_cb.setChecked(True)
        self.ketu_cb.setChecked(True)
        self.uranus_cb.setChecked(False)
        self.neptune_cb.setChecked(False)
        self.pluto_cb.setChecked(False)
        self.ascendant_cb.setChecked(True)

    def select_luminaries(self):
        """Select just Sun, Moon, and Ascendant."""
        self.sun_cb.setChecked(True)
        self.moon_cb.setChecked(True)
        self.mercury_cb.setChecked(False)
        self.venus_cb.setChecked(False)
        self.mars_cb.setChecked(False)
        self.jupiter_cb.setChecked(False)
        self.saturn_cb.setChecked(False)
        self.rahu_cb.setChecked(False)
        self.ketu_cb.setChecked(False)
        self.uranus_cb.setChecked(False)
        self.neptune_cb.setChecked(False)
        self.pluto_cb.setChecked(False)
        self.ascendant_cb.setChecked(True)