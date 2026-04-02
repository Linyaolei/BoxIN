import os
import random
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMenu, 
                               QColorDialog, QInputDialog, QToolButton, QListWidget, 
                               QListWidgetItem, QAbstractItemView, QMessageBox, QListView, QPushButton, QTabWidget)
from PySide6.QtCore import Qt, QPoint, Signal, QSize, QEvent, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QPainter, QColor, QPainterPath, QAction, QCursor, QKeySequence, QShortcut
from core.config_manager import config
from core.win32_effects import apply_window_effect
from core.file_manager import open_file_safe, open_file_location, get_system_icon
from core.desktop_utils import is_color_light, get_file_stats, set_window_rounded_corners
from core.i18n import t

WIN11_MENU_QSS = """
QMenu { background-color: #2b2b2b; border: 1px solid #444; border-radius: 8px; padding: 4px; color: white; font-family: 'Microsoft YaHei UI'; font-size: 13px; }
QMenu::item { padding: 8px 32px 8px 24px; border-radius: 4px; margin: 2px; }
QMenu::item:selected { background-color: #444444; }
QMenu::separator { height: 1px; background: #555; margin: 4px 8px; }
"""

BOX_COLORS = ["#1e1e1e", "#ffffff", "#1e293b", "#142217", "#281e1d", "#2a1b24", "#16282b", "#1e1b2e", "#1c1c1c", "#2a2211", "#0f172a", "#000000"]
BOX_COLOR_NAMES = ["深邃黑", "纯净白", "苍穹蓝", "护眼绿", "暖橘色", "樱花粉", "青草翠", "高级紫", "商务灰", "落日金", "午夜蓝", "透明晶"]
PRESET_COLORS = {"红": "#e81123", "橙": "#d83b01", "金": "#d97706", "绿": "#107c10", "青": "#0891b2", "蓝": "#005fb8", "紫": "#7c3aed", "灰": "#475569"}

class BoxListWidget(QListWidget):
    def __init__(self, parent_box, tab_name="默认"):
        super().__init__()
        self.parent_box = parent_box
        self.tab_name = tab_name
        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust) 
        self.setMovement(QListView.Movement.Snap) 
        self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection) 
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.setSpacing(4)
        
        self.icon_size = 48
        self.update_icon_size(self.icon_size)
        self.apply_font_color()
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        if config.settings.get("open_mode", "double") == "single": 
            self.itemClicked.connect(self.open_item)
        else: 
            self.itemDoubleClicked.connect(self.open_item)

    def apply_font_color(self):
        is_light = is_color_light(self.parent_box.bg_color.name())
        text_color = "black" if is_light else "white"
        hover_bg = "rgba(0,0,0,20)" if is_light else "rgba(255,255,255,30)"
        selected_bg = "rgba(0,95,184,40)" if is_light else "rgba(255,255,255,60)"
        
        self.setStyleSheet(f"""
            QListWidget {{ background: transparent; border: none; outline: none; font-size: 12px; font-family: 'Microsoft YaHei UI'; }}
            QListWidget::item {{ color: {text_color}; border-radius: 5px; padding: 2px; font-size: 12px; }}
            QListWidget::item:selected {{ background: {selected_bg}; border: 1px solid rgba(128,128,128,50); }}
            QListWidget::item:hover {{ background: {hover_bg}; }}
        """)

    def update_icon_size(self, size):
        self.icon_size = size
        self.setIconSize(QSize(size, size))
        self.setGridSize(QSize(size + 40, size + 55))

    def open_item(self, item): 
        open_file_safe(item.data(Qt.UserRole))

    def add_file(self, file_path, custom_name=None):
        """【修复】：支持虚拟重命名，支持字典解析"""
        if not os.path.exists(file_path): return
        
        for i in range(self.count()):
            if self.item(i).data(Qt.UserRole) == file_path: return
            
        real_name = os.path.basename(file_path)
        display_name = custom_name if custom_name else real_name
        show_text = display_name if len(display_name) <= 8 else display_name[:7] + ".."
        
        item = QListWidgetItem(get_system_icon(file_path), show_text)
        item.setData(Qt.UserRole, file_path)
        item.setData(Qt.UserRole + 1, display_name)
        item.setToolTip(f"{display_name}\n({file_path})")
        self.addItem(item)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls(): self.add_file(url.toLocalFile())
            event.accept()
        else: super().dropEvent(event)

    def show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(WIN11_MENU_QSS)
        selected_items = self.selectedItems()
        if selected_items:
            menu.addAction("打开所在位置", lambda: open_file_location(selected_items[0].data(Qt.UserRole)))
            if len(selected_items) == 1:
                menu.addAction("✏️ " + t("Rename") + " (仅修改展示名称)", self.rename_virtual_icon)
            menu.addAction(f"移除选中的 {len(selected_items)} 个项目", self.remove_selected)
        else:
            menu.addAction(t("Clear"), self.clear)
        menu.exec(self.mapToGlobal(pos))

    def rename_virtual_icon(self):
        item = self.selectedItems()[0]
        old_name = item.data(Qt.UserRole + 1)
        new_name, ok = QInputDialog.getText(self, t("Rename"), "请输入新的展示名称:\n(此操作绝不会修改磁盘上的原文件)", text=old_name)
        if ok and new_name:
            item.setData(Qt.UserRole + 1, new_name)
            show_text = new_name if len(new_name) <= 8 else new_name[:7] + ".."
            item.setText(show_text)
            item.setToolTip(f"{new_name}\n({item.data(Qt.UserRole)})")

    def remove_selected(self):
        for item in self.selectedItems(): self.takeItem(self.row(item))

    def sort_items_custom(self, sort_by):
        items_data = []
        for i in range(self.count()):
            item = self.item(i)
            path = item.data(Qt.UserRole)
            c_name = item.data(Qt.UserRole + 1)
            size, mtime = get_file_stats(path)
            items_data.append({"name": c_name, "path": path, "ext": os.path.splitext(path)[1].lower(), "size": size, "mtime": mtime})
        if sort_by == "name": items_data.sort(key=lambda x: x["name"])
        elif sort_by == "size": items_data.sort(key=lambda x: x["size"], reverse=True)
        elif sort_by == "type": items_data.sort(key=lambda x: x["ext"])
        elif sort_by == "date": items_data.sort(key=lambda x: x["mtime"], reverse=True)
        self.clear()
        for data in items_data: self.add_file(data["path"], data["name"])

class BaseDesktopBox(QWidget):
    box_destroyed = Signal(str) 
    box_renamed = Signal(str, str)

    def __init__(self, box_id, title, pos_x=100, pos_y=100, w=340, h=280, bg_color=None, open_settings_cb=None, is_locked=False, circle_color=None):
        super().__init__()
        self.box_id = box_id
        self.title_text = str(title)
        self.bg_color = QColor(bg_color if bg_color else config.settings.get("color_theme", "#1e1e1e"))
        self.circle_color = circle_color if circle_color else list(PRESET_COLORS.values())[random.randint(0, len(PRESET_COLORS)-1)]
        self.open_settings_cb = open_settings_cb
        self.is_locked = is_locked
        
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnBottomHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 
        self.setMouseTracking(True) 
        
        self.expanded_size = QSize(w, h)
        self.resize(self.expanded_size)
        self.move(pos_x, pos_y)
        
        self.dragging = False; self.is_rolled_up = False
        self.margin_size = 6; self.resizing = False; self.resize_dir = None

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(8, 8, 8, 8)
        self.main_layout.setSpacing(4)
        
        self.title_bar = QWidget()
        self.title_bar.setFixedHeight(28)
        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(5, 0, 0, 0)
        
        self.title_spacer = QWidget()
        self.title_spacer.setFixedSize(20, 20)
        title_layout.addWidget(self.title_spacer)
        
        self.title_label = QLabel(self.title_text)
        self.fold_btn = QToolButton(); self.fold_btn.clicked.connect(self.toggle_rollup)
        self.menu_btn = QToolButton(); self.menu_btn.setText("•••"); self.menu_btn.clicked.connect(self.show_box_menu)
        
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.fold_btn)
        title_layout.addWidget(self.menu_btn)
        self.main_layout.addWidget(self.title_bar)
        
        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(0,0,0,0)
        self.main_layout.addWidget(self.content_container)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.tabBar().setMouseTracking(True)
        self.tab_widget.tabBar().installEventFilter(self)
        self.content_layout.addWidget(self.tab_widget)
        self.lists = {} 
        
        self.circle_btn = QPushButton(self)
        self.circle_btn.setFixedSize(14, 14)
        self.circle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.circle_btn.clicked.connect(lambda: self.show_circle_menu(self.circle_btn.mapToGlobal(QPoint(0, self.circle_btn.height()))))
        self.circle_btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.circle_btn.customContextMenuRequested.connect(self.show_circle_menu)
        self.update_circle_style()
        self.circle_btn.move(14, 15) 
        
        self.update_fold_icon()
        self.apply_title_font_color()
        self.setup_shortcuts()
        
        if self.is_locked: self.apply_lock_state(animate=False)

    def update_circle_style(self):
        self.circle_btn.setStyleSheet(f"background-color: {self.circle_color}; border-radius: 7px; border: 1px solid rgba(255,255,255,0.4);")

    def show_circle_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(WIN11_MENU_QSS)
        color_menu = menu.addMenu("🎨 选择圆圈颜色 >")
        for name, hex_code in PRESET_COLORS.items(): color_menu.addAction(name, lambda h=hex_code: self.set_circle_color(h))
        color_menu.addSeparator()
        color_menu.addAction("自定义其他颜色...", self.change_circle_color_custom)
        menu.addSeparator()
        menu.addAction(t("Unlock") if self.is_locked else t("Lock"), self.toggle_lock)
        menu.exec(pos)

    def set_circle_color(self, hex_code):
        self.circle_color = hex_code; self.update_circle_style()

    def change_circle_color_custom(self):
        color = QColorDialog.getColor(QColor(self.circle_color), self, "自定义颜色")
        if color.isValid(): self.set_circle_color(color.name())

    def update_fold_icon(self):
        self.fold_btn.setText("▶" if self.is_rolled_up else "▼")

    def eventFilter(self, obj, event):
        if obj == self.tab_widget.tabBar() and event.type() == QEvent.Type.MouseMove:
            if config.settings.get("hover_switch_tab", True):
                idx = self.tab_widget.tabBar().tabAt(event.pos())
                if idx >= 0: self.tab_widget.setCurrentIndex(idx)
        return super().eventFilter(obj, event)

    def setup_shortcuts(self):
        QShortcut(QKeySequence("Ctrl+Shift+1"), self).activated.connect(lambda: self.change_icon_size(80))
        QShortcut(QKeySequence("Ctrl+Shift+2"), self).activated.connect(lambda: self.change_icon_size(64))
        QShortcut(QKeySequence("Ctrl+Shift+3"), self).activated.connect(lambda: self.change_icon_size(48))
        QShortcut(QKeySequence("Ctrl+Shift+4"), self).activated.connect(lambda: self.change_icon_size(32))

    def update_tab_position(self):
        if not hasattr(self, 'tab_widget'): return
        pos = config.settings.get("tab_position", "top")
        pos_map = {"top": QTabWidget.TabPosition.North, "bottom": QTabWidget.TabPosition.South, 
                   "left": QTabWidget.TabPosition.West, "right": QTabWidget.TabPosition.East}
        self.tab_widget.setTabPosition(pos_map.get(pos, QTabWidget.TabPosition.North))
        
        is_light = is_color_light(self.bg_color.name())
        tc = "#333" if is_light else "#ccc"
        sc = "rgba(0,0,0,30)" if is_light else "rgba(255,255,255,40)"
        sw = "black" if is_light else "white"
        
        margin_left = "30px" if self.is_locked and pos == "top" else "0px"
        self.tab_widget.setStyleSheet(f"""
            QTabWidget::pane {{ border: none; }}
            QTabBar::tab {{ background: transparent; color: {tc}; padding: 5px 15px; border-radius: 4px; }}
            QTabBar::tab:selected {{ background: {sc}; color: {sw}; font-weight: bold; }}
            QTabBar::tab:first {{ margin-left: {margin_left}; }}
        """)

    def apply_title_font_color(self):
        is_light = is_color_light(self.bg_color.name())
        tc = "black" if is_light else "white"
        btn_hover = "rgba(0,0,0,15)" if is_light else "rgba(255,255,255,40)"
        self.title_label.setStyleSheet(f"color: {tc}; font-weight: bold; font-size: 14px; font-family: 'Microsoft YaHei UI';")
        btn_qss = f"QToolButton {{ color: {tc}; background: transparent; border-radius: 4px; }} QToolButton:hover {{ background: {btn_hover}; }}"
        self.fold_btn.setStyleSheet(btn_qss); self.menu_btn.setStyleSheet(btn_qss)
        self.update_tab_position()
        for lw in self.lists.values(): lw.apply_font_color()

    def showEvent(self, event):
        self.apply_effect(); super().showEvent(event)

    def apply_effect(self):
        effect = config.settings.get("box_effect", "transparent")
        alpha = config.settings.get("theme_alpha", 180)
        apply_window_effect(self.winId(), effect, self.bg_color.name(), alpha)

    def resizeEvent(self, event):
        set_window_rounded_corners(self.winId(), 24)
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath(); path.addRoundedRect(self.rect(), 12, 12) 
        effect = config.settings.get("box_effect", "transparent")
        draw_color = QColor(self.bg_color)
        
        if effect in ["normal", "transparent"]:
            draw_color.setAlpha(config.settings.get("theme_alpha", 180) if effect == "transparent" else 255)
            painter.fillPath(path, draw_color)
        else:
            draw_color.setAlpha(15)
            painter.fillPath(path, draw_color)
        painter.setPen(QColor(255, 255, 255, 40)); painter.drawPath(path)

    def check_edge(self, pos):
        if self.is_locked or self.is_rolled_up: return None
        x, y, w, h = pos.x(), pos.y(), self.width(), self.height()
        m = self.margin_size
        if x < m and y < m: return "tl"
        if x > w - m and y > h - m: return "br"
        if x > w - m and y < m: return "tr"
        if x < m and y > h - m: return "bl"
        if x < m: return "l"
        if x > w - m: return "r"
        if y < m: return "t"
        if y > h - m: return "b"
        return None

    def update_cursor(self, edge):
        if edge in ["l", "r"]: self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif edge in ["t", "b"]: self.setCursor(Qt.CursorShape.SizeVerCursor)
        elif edge in ["tl", "br"]: self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif edge in ["tr", "bl"]: self.setCursor(Qt.CursorShape.SizeBDiagCursor)
        else: self.setCursor(Qt.CursorShape.ArrowCursor)

    def toggle_rollup(self):
        self.is_rolled_up = not self.is_rolled_up
        self.update_fold_icon()
        if self.is_rolled_up:
            self.expanded_size = self.size()
            self.content_container.setVisible(False)
            self.setFixedSize(self.expanded_size.width(), self.title_bar.height() + 16)
        else:
            self.content_container.setVisible(True)
            self.setMinimumSize(250, 150); self.setMaximumSize(16777215, 16777215) 
            self.resize(self.expanded_size)

    def enterEvent(self, event):
        if self.is_rolled_up and config.settings.get("hover_expand", True):
            self.content_container.setVisible(True)
            self.setMinimumSize(250, 150); self.setMaximumSize(16777215, 16777215)
            self.resize(self.expanded_size)
        super().enterEvent(event)

    def leaveEvent(self, event):
        if self.is_rolled_up and config.settings.get("hover_expand", True):
            if not self.rect().contains(self.mapFromGlobal(QCursor.pos())):
                self.content_container.setVisible(False)
                self.setFixedSize(self.expanded_size.width(), self.title_bar.height() + 16)
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            edge = self.check_edge(event.pos())
            if edge:
                self.resizing = True; self.resize_dir = edge; self.start_geom = self.geometry()
                self.drag_position = event.globalPosition().toPoint()
            elif not self.is_locked and self.title_bar.geometry().contains(event.pos()):
                self.dragging = True; self.drag_position = event.globalPosition().toPoint() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.resizing:
            delta = event.globalPosition().toPoint() - self.drag_position
            rect = QRect(self.start_geom)
            if "l" in self.resize_dir: rect.setLeft(rect.left() + delta.x())
            if "r" in self.resize_dir: rect.setRight(rect.right() + delta.x())
            if "t" in self.resize_dir: rect.setTop(rect.top() + delta.y())
            if "b" in self.resize_dir: rect.setBottom(rect.bottom() + delta.y())
            if rect.width() >= 250 and rect.height() >= 150:
                self.setGeometry(rect); self.expanded_size = rect.size()
            event.accept(); return
        if self.dragging:
            self.move(event.globalPosition().toPoint() - self.drag_position); event.accept()
            return
        self.update_cursor(self.check_edge(event.pos()))

    def mouseReleaseEvent(self, event):
        self.dragging = False; self.resizing = False; self.resize_dir = None
        self.setCursor(Qt.CursorShape.ArrowCursor)

    def toggle_lock(self):
        self.is_locked = not self.is_locked
        self.apply_lock_state(animate=True)
        
    def apply_lock_state(self, animate=True):
        if self.is_locked:
            self.title_bar.hide(); self.update_tab_position(); target_pos = QPoint(12, 12) 
        else:
            self.title_bar.show(); self.update_tab_position(); target_pos = QPoint(14, 15)

        if animate:
            self.anim = QPropertyAnimation(self.circle_btn, b"pos")
            self.anim.setDuration(400); self.anim.setEasingCurve(QEasingCurve.Type.OutBack) 
            self.anim.setStartValue(QPoint(14, -20) if self.is_locked else QPoint(14, 40))
            self.anim.setEndValue(target_pos); self.anim.start()
        else:
            self.circle_btn.move(target_pos)

    def show_box_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet(WIN11_MENU_QSS)
        self.build_custom_menu_items(menu) 
        
        view_menu = menu.addMenu(t("MenuView"))
        view_menu.addAction(t("ViewLargeX") + "\tCtrl+Shift+1", lambda: self.change_icon_size(80))
        view_menu.addAction(t("ViewLarge") + "\tCtrl+Shift+2", lambda: self.change_icon_size(64))
        view_menu.addAction(t("ViewMedium") + "\tCtrl+Shift+3", lambda: self.change_icon_size(48))
        view_menu.addAction(t("ViewSmall") + "\tCtrl+Shift+4", lambda: self.change_icon_size(32))
        
        sort_menu = menu.addMenu(t("MenuSort"))
        sort_menu.addAction(t("SortName"), lambda: self.sort_items("name"))
        sort_menu.addAction(t("SortSize"), lambda: self.sort_items("size"))
        sort_menu.addAction(t("SortType"), lambda: self.sort_items("type"))
        sort_menu.addAction(t("SortDate"), lambda: self.sort_items("date"))
        
        menu.addSeparator()
        menu.addAction(t("ChangeColor"), self.change_color)
        menu.addAction(t("Rename"), self.rename_box)
        menu.addAction(t("Unlock") if self.is_locked else t("Lock"), self.toggle_lock)
        
        menu.addSeparator()
        menu.addAction(t("OpenSettings"), self.open_settings_cb if self.open_settings_cb else lambda: None)
        
        if self.box_id != "main_box": 
            menu.addSeparator()
            menu.addAction(t("Disband"), self.destroy_box)
            
        menu.exec(self.menu_btn.mapToGlobal(QPoint(0, self.menu_btn.height() + 5)))

    def build_custom_menu_items(self, menu): pass
    def sort_items(self, sort_by="name"):
        current_list = self.tab_widget.currentWidget()
        if isinstance(current_list, BoxListWidget): current_list.sort_items_custom(sort_by)
    def change_icon_size(self, size):
        for lw in self.lists.values(): lw.update_icon_size(size)

    def change_color(self):
        color = QColorDialog.getColor(self.bg_color, self, "选择颜色")
        if color.isValid():
            self.bg_color = color
            self.apply_effect()
            self.apply_title_font_color()
            self.update()

    def rename_box(self, new_name=None):
        if new_name is None or isinstance(new_name, bool):
            new_name, ok = QInputDialog.getText(self, "重命名", "请输入新的盒子名称:", text=self.title_text)
            if not (ok and new_name): return
        self.title_text = new_name
        self.title_label.setText(new_name)
        self.box_renamed.emit(self.box_id, new_name)

    def destroy_box(self):
        self.box_destroyed.emit(self.box_id)
        self.close()

class CustomDesktopBox(BaseDesktopBox):
    def __init__(self, box_data, open_settings_cb):
        super().__init__(box_data["id"], box_data["title"], box_data["x"], box_data["y"], box_data.get("w", 340), box_data.get("h", 280), box_data.get("color"), open_settings_cb, box_data.get("is_locked", False), box_data.get("circle_color"))
        self.tabs_data = box_data.get("tabs", {"默认": []})
        
        # 【核心修复】：解析旧存档纯字符串列表，以及新存档字典结构
        if "files" in box_data: self.tabs_data = {"默认": box_data["files"]}
            
        for cat, files in self.tabs_data.items():
            self.add_tab_page(cat, files)
        self.setAcceptDrops(True)

    def add_tab_page(self, tab_name, files=[]):
        if tab_name in self.lists: return
        lw = BoxListWidget(self, tab_name)
        self.lists[tab_name] = lw
        self.tab_widget.addTab(lw, tab_name)
        
        # 【核心修复】：向下兼容旧的纯字符串数组
        for f in files: 
            if isinstance(f, dict):
                lw.add_file(f.get("path"), f.get("name"))
            else:
                lw.add_file(f)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls(): event.accept()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            current_list = self.tab_widget.currentWidget()
            if isinstance(current_list, BoxListWidget):
                for url in event.mimeData().urls():
                    current_list.add_file(url.toLocalFile())
            event.accept()

    def get_state(self):
        saved_tabs = {}
        for cat, lw in self.lists.items():
            valid_files = []
            for i in range(lw.count()):
                item = lw.item(i)
                path = item.data(Qt.UserRole)
                c_name = item.data(Qt.UserRole + 1)
                if os.path.exists(path): 
                    valid_files.append({"path": path, "name": c_name})
            saved_tabs[cat] = valid_files
            
        return {"id": self.box_id, "title": self.title_text, "x": self.x(), "y": self.y(), "w": self.width(), "h": self.height(), "color": self.bg_color.name(), "circle_color": self.circle_color, "is_locked": self.is_locked, "tabs": saved_tabs}
