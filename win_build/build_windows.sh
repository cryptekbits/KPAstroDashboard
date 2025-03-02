#!/bin/bash
echo "Starting Windows build inside Docker container..."
apt-get update
apt-get install -y python3 python3-pip python3-dev build-essential git
pip3 install --upgrade pip
pip3 install pyinstaller wheel setuptools
pip3 install -r requirements.cross.txt
chmod +x handle_packages.sh
./handle_packages.sh
echo "Building Windows executable..."
python3 -m PyInstaller --name KPAstrologyDashboard-v1.0.3-win-x64 --icon resources/favicon.ico --onefile --noconfirm --hidden-import pandas --hidden-import numpy --hidden-import PyQt5 --hidden-import requests --hidden-import packaging --hidden-import geopy --hidden-import polars --hidden-import tabulate --hidden-import psutil --hidden-import ephem --hidden-import dateutil main.py
echo "Build completed!"
