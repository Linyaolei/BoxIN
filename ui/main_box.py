import os
from PySide6.QtWidgets import QWidget, QVBoxLayout, QTabWidget, QMenu
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QPoint, QFileSystemWatcher, QEvent
from core.config_manager import config
from core.rule_engine import categorize_file
from core.desktop_utils import is_hidden_or_temp_file, is_system_shortcut, is_color_light
from ui.box_widget import BaseDesktopBox, BoxListWidget, WIN11_MENU_QSS

class MainDesktopBox(BaseDesktopBox):
    def __init__(self, box_data, organize_callback, restore_callback, open_settings_cb):
        super().__init__("main_box", box_data.get("title", "主盒子"), box_data.get("x", 100), box_data.get("y", 100), box_data.get("w", 340), box_data.get("h", 280), open_settings_cb=open_settings_cb, is_locked=box_data.get("is_locked", False), circle_color=box_data.get("circle_color"))
        
        self.organize_callback = organize_callback 
        self.restore_callback = restore_callback
        self.tabs_data = box_data.get("tabs", {})
        self.mapped_files = set()
        self.load_tabs()
        
        self.desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        self.watcher = QFileSystemWatcher([self.desktop_dir])
        self.watcher.directoryChanged.connect(self.on_desktop_changed)

    def on_desktop_changed(self, path):
        if not config.settings.get("desktop_organized", False): return
        exclude_exts = config.settings.get("exclude_exts", [])
        
        for f in os.listdir(self.desktop_dir):
            full_path = os.path.join(self.desktop_dir, f)
            if full_path not in self.mapped_files and not is_hidden_or_temp_file(full_path):
                if config.settings.get("exclude_sys_icons", True) and is_system_shortcut(full_path): continue
                if os.path.splitext(full_path)[1].lower() in exclude_exts: continue
                self.bulk_add_files([full_path])

    def build_custom_menu_items(self, menu):
        menu.addAction("🚀 一键整理并接管桌面", self.organize_callback)
        menu.addAction("↩️ 停止整理还原桌面", self.restore_callback)
        menu.addSeparator()

    def load_tabs(self):
        all_categories = list(config.settings.get("rules", {}).keys()) + ["文件夹", "未分类"]
        to_remove = []
        for cat in self.lists.keys():
            if cat not in all_categories: to_remove.append(cat)
        for cat in to_remove:
            idx = self.tab_widget.indexOf(self.lists[cat])
            if idx >= 0: self.tab_widget.removeTab(idx)
            del self.lists[cat]
            
        for cat in all_categories:
            if cat not in self.tabs_data: self.tabs_data[cat] = []
            if cat not in self.lists:
                list_widget = BoxListWidget(self, cat)
                self.lists[cat] = list_widget
                self.tab_widget.addTab(list_widget, cat)
                
            for f in self.tabs_data[cat]:
                self.lists[cat].add_file(f)
                self.mapped_files.add(f)
        self.setAcceptDrops(True)

    def refresh_by_new_rules(self):
        all_existing_files = list(self.mapped_files)
        for lw in self.lists.values(): lw.clear()
        self.mapped_files.clear()
        self.tabs_data.clear()
        self.load_tabs()
        self.bulk_add_files(all_existing_files)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                self.bulk_add_files([url.toLocalFile()])
            event.accept()

    def bulk_add_files(self, file_paths):
        for file_path in file_paths:
            cat = categorize_file(file_path)
            if cat in self.lists: 
                self.lists[cat].add_file(file_path)
                self.mapped_files.add(file_path)

    def get_state(self):
        saved_tabs = {}
        for cat, lw in self.lists.items():
            valid_files = []
            for i in range(lw.count()):
                path = lw.item(i).data(Qt.UserRole)
                if os.path.exists(path): valid_files.append(path)
            saved_tabs[cat] = valid_files
        return {"title": self.title_text, "x": self.x(), "y": self.y(), "w": self.width(), "h": self.height(), "circle_color": self.circle_color, "is_locked": self.is_locked, "tabs": saved_tabs}