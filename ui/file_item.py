import os
from PySide6.QtWidgets import QToolButton, QMenu
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QAction
from core.config_manager import config
from core.file_manager import open_file_safe, open_file_location, get_system_icon

class FileItemWidget(QToolButton):
    def __init__(self, file_path):
        super().__init__()
        self.file_path = file_path
        self.setFixedSize(70, 80)
        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setStyleSheet("""
            QToolButton { border: none; border-radius: 5px; background: transparent; color: white; font-size: 12px; }
            QToolButton:hover { background: rgba(255, 255, 255, 50); }
        """)
        
        self.setIcon(get_system_icon(self.file_path))
        self.setIconSize(QRect(0, 0, 48, 48).size())
        
        name = os.path.basename(file_path)
        if len(name) > 8: name = name[:7] + ".."
        self.setText(name)

        if config.settings.get("open_mode") == "single":
            self.clicked.connect(self.open_target)
        else:
            self.doubleClicked = self.open_target
            
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def mouseDoubleClickEvent(self, event):
        if config.settings.get("open_mode") == "double" and event.button() == Qt.LeftButton:
            self.open_target()
        super().mouseDoubleClickEvent(event)

    def open_target(self):
        open_file_safe(self.file_path)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        open_dir_action = QAction("打开所在位置", self)
        open_dir_action.triggered.connect(lambda: open_file_location(self.file_path))
        remove_action = QAction("从盒子移除", self)
        remove_action.triggered.connect(self.deleteLater)
        
        menu.addAction(open_dir_action)
        menu.addAction(remove_action)
        menu.exec(self.mapToGlobal(pos))