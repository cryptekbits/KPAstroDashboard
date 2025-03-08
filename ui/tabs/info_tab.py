"""
Info tab for the KP Astrology application.
"""

import os
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QGroupBox, QScrollArea, QGridLayout)
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QFont, QPixmap

class InfoTab:
    """Info tab for the KP Astrology application."""

    def __init__(self, parent):
        """
        Initialize info tab.
        
        Parameters:
        -----------
        parent : QWidget
            Parent widget to attach the tab to
        """
        self.parent = parent

    def setup_tab(self):
        """
        Set up the info tab.
        
        Returns:
        --------
        QWidget
            The info tab widget
        """
        # Create the info tab
        info_tab = QWidget()
        
        # Create a scroll area for the info content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        info_widget = QWidget()
        scroll_area.setWidget(info_widget)
        
        # Set the scroll area as the info tab's layout
        info_tab_layout = QVBoxLayout(info_tab)
        info_tab_layout.addWidget(scroll_area)

        info_layout = QVBoxLayout(info_widget)
        
        # Add logo if available
        self.add_logo_section(info_layout)
        
        # Application information
        self.add_app_info_section(info_layout)
        
        # Repository information
        self.add_repo_section(info_layout)
        
        # Author information
        self.add_author_section(info_layout)
        
        # License information
        self.add_license_section(info_layout)
        
        return info_tab
    
    def add_logo_section(self, layout):
        """Add logo section to the layout."""
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                              'resources', 'logo.png')
        
        if os.path.exists(logo_path):
            logo_label = QLabel()
            pixmap = QPixmap(logo_path)
            # Scale the pixmap while maintaining aspect ratio
            pixmap = pixmap.scaledToWidth(400, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
    
    def add_app_info_section(self, layout):
        """Add application information section to the layout."""
        # Import version information here to ensure we get the latest values
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from version import VERSION, VERSION_NAME, BUILD_DATE
        
        app_group = QGroupBox("Application Information")
        app_layout = QGridLayout()
        app_group.setLayout(app_layout)
        
        # Application name with larger font
        name_label = QLabel("KP Astrology Dashboard")
        font = name_label.font()
        font.setPointSize(14)
        font.setBold(True)
        name_label.setFont(font)
        name_label.setAlignment(Qt.AlignCenter)
        app_layout.addWidget(name_label, 0, 0, 1, 2)
        
        # Version information
        app_layout.addWidget(QLabel("Version:"), 1, 0)
        app_layout.addWidget(QLabel(f"{VERSION} ({VERSION_NAME})"), 1, 1)
        
        # Build date
        app_layout.addWidget(QLabel("Build Date:"), 2, 0)
        app_layout.addWidget(QLabel(BUILD_DATE), 2, 1)
        
        layout.addWidget(app_group)
    
    def add_repo_section(self, layout):
        """Add repository information section to the layout."""
        # Import repository information
        import sys
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        from version import GITHUB_REPO_OWNER, GITHUB_REPO_NAME
        
        repo_group = QGroupBox("Repository Information")
        repo_layout = QGridLayout()
        repo_group.setLayout(repo_layout)
        
        # Create repository URL
        repo_url = f"https://github.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}"
        
        # Add clickable link
        repo_layout.addWidget(QLabel("GitHub Repository:"), 0, 0)
        link_label = QLabel(f"<a href='{repo_url}'>{repo_url}</a>")
        link_label.setOpenExternalLinks(True)
        repo_layout.addWidget(link_label, 0, 1)
        
        layout.addWidget(repo_group)
    
    def add_author_section(self, layout):
        """Add author information section to the layout."""
        author_group = QGroupBox("Author Information")
        author_layout = QGridLayout()
        author_group.setLayout(author_layout)
        
        # Author name
        author_layout.addWidget(QLabel("Author:"), 0, 0)
        author_layout.addWidget(QLabel("Manan Ramnani"), 0, 1)
        
        # Email with clickable link
        email = "ramnani.manan@gmail.com"
        author_layout.addWidget(QLabel("Email:"), 1, 0)
        email_label = QLabel(f"<a href='mailto:{email}'>{email}</a>")
        email_label.setOpenExternalLinks(True)
        author_layout.addWidget(email_label, 1, 1)
        
        layout.addWidget(author_group)
    
    def add_license_section(self, layout):
        """Add license information section to the layout."""
        license_group = QGroupBox("License Information")
        license_layout = QVBoxLayout()
        license_group.setLayout(license_layout)
        
        # Copyright notice
        copyright_label = QLabel("© 2023-2025 Manan Ramnani. All rights reserved.")
        copyright_label.setAlignment(Qt.AlignCenter)
        license_layout.addWidget(copyright_label)
        
        # License details
        license_text = """
        This software is proprietary and confidential.
        Unauthorized copying, distribution, modification, public display, 
        or public performance of this software is strictly prohibited.
        """
        license_label = QLabel(license_text)
        license_label.setWordWrap(True)
        license_label.setAlignment(Qt.AlignCenter)
        license_layout.addWidget(license_label)
        
        layout.addWidget(license_group) 