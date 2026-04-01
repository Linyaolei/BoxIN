import time
import os
import copy
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton, QListWidget, QStackedWidget,
                               QHBoxLayout, QComboBox, QApplication, QSlider, QMessageBox, QFileDialog, 
                               QCheckBox, QScrollArea, QLineEdit, QFrame, QDialog, QInputDialog)
from PySide6.QtCore import Qt, QPropertyAnimation, QRect
from PySide6.QtGui import QColor, QPainter, QPainterPath

from core.config_manager import config
from core.desktop_hook import HookSignals, DesktopHookThread
from core.desktop_utils import set_desktop_icons_visible, is_hidden_or_temp_file, is_system_shortcut, get_system_theme
from core.i18n import t
from ui.box_widget import CustomDesktopBox, BoxListWidget, BOX_COLORS, BOX_COLOR_NAMES
from ui.main_box import MainDesktopBox

THEME_COLORS = {
    "default": {"dark": "#202020", "light": "#f3f3f3", "card_d": "#2b2b2b", "card_l": "#ffffff", "accent": "#005fb8"},
    "blue": {"dark": "#111827", "light": "#eef2f9", "card_d": "#1f2937", "card_l": "#ffffff", "accent": "#2563eb"},
    "green": {"dark": "#142217", "light": "#eef9f0", "card_d": "#1e3323", "card_l": "#ffffff", "accent": "#16a34a"},
    "warm": {"dark": "#281e1d", "light": "#fdf4f0", "card_d": "#3d2e2c", "card_l": "#ffffff", "accent": "#ea580c"},
    "pink": {"dark": "#2a1b24", "light": "#fdf2f8", "card_d": "#3b2633", "card_l": "#ffffff", "accent": "#db2777"},
    "cyan": {"dark": "#16282b", "light": "#ecfeff", "card_d": "#203a3e", "card_l": "#ffffff", "accent": "#0891b2"},
    "purple": {"dark": "#1e1b2e", "light": "#f5f3ff", "card_d": "#2d2844", "card_l": "#ffffff", "accent": "#7c3aed"},
    "gray": {"dark": "#1c1c1c", "light": "#f8f9fa", "card_d": "#262626", "card_l": "#ffffff", "accent": "#475569"},
    "cherry": {"dark": "#301d24", "light": "#ffe6ed", "card_d": "#422832", "card_l": "#ffffff", "accent": "#e11d48"},
    "mint": {"dark": "#162820", "light": "#eafff1", "card_d": "#203a2e", "card_l": "#ffffff", "accent": "#059669"},
    "gold": {"dark": "#2a2211", "light": "#fffbeb", "card_d": "#3b2f18", "card_l": "#ffffff", "accent": "#d97706"},
    "navy": {"dark": "#0f172a", "light": "#f1f5f9", "card_d": "#1e293b", "card_l": "#ffffff", "accent": "#3b82f6"}
}

def get_qss(theme_mode, bg_theme):
    colors = THEME_COLORS.get(bg_theme, THEME_COLORS["default"])
    pri = colors["accent"]
    if theme_mode == "dark":
        card = colors["card_d"]
        return f"""
            QWidget {{ color: #fff; font-family: 'Microsoft YaHei UI'; font-size: 13px; }}
            QListWidget {{ background: transparent; border: none; outline: none; }}
            QListWidget::item {{ height: 44px; padding-left: 18px; border-radius: 6px; margin: 2px 10px 2px 12px; color: #eee; }}
            QListWidget::item:hover {{ background-color: rgba(255,255,255,10); }}
            QListWidget::item:selected {{ background-color: rgba(255,255,255,10); font-weight: bold; }}
            QStackedWidget {{ background-color: transparent; }}
            QFrame.Card {{ background-color: {card}; border: 1px solid rgba(255,255,255,10); border-radius: 8px; }}
            QPushButton {{ background-color: rgba(255,255,255,10); border: 1px solid rgba(255,255,255,15); border-radius: 4px; padding: 6px 16px; color: #fff;}}
            QPushButton:hover {{ background-color: rgba(255,255,255,20); }}
            QPushButton#Primary {{ background-color: {pri}; color: white; border: none; }}
            QPushButton#Danger {{ background-color: transparent; color: #ff6b6b; border: 1px solid #ff6b6b; }}
            QPushButton#Danger:hover {{ background-color: #ff6b6b; color: white; }}
            QPushButton#TitleClose {{ background: transparent; border: none; color: #ccc; border-radius: 0px;}}
            QPushButton#TitleClose:hover {{ background: #e81123; color: white; }}
            
            /* 【修复】：无边框退出按钮，解决左侧截断 */
            QPushButton#ExitAppBtn {{ background: transparent; border: none; color: #ff4d4d; text-align: left; padding-left: 20px; font-weight: bold; }}
            QPushButton#ExitAppBtn:hover {{ background: rgba(255, 77, 77, 0.1); color: #ff6b6b; }}
            
            QLineEdit, QComboBox {{ background-color: rgba(0,0,0,50); border: 1px solid rgba(255,255,255,20); border-radius: 4px; padding: 6px; color: white;}}
            QScrollArea {{ border: none; background: transparent; }}
        """
    else:
        card = colors["card_l"]
        return f"""
            QWidget {{ color: #111; font-family: 'Microsoft YaHei UI'; font-size: 13px; }}
            QListWidget {{ background: transparent; border: none; outline: none; }}
            QListWidget::item {{ height: 44px; padding-left: 18px; border-radius: 6px; margin: 2px 10px 2px 12px; color: #333; }}
            QListWidget::item:hover {{ background-color: rgba(0,0,0,5); }}
            QListWidget::item:selected {{ background-color: rgba(0,0,0,5); font-weight: bold; }}
            QStackedWidget {{ background-color: transparent; }}
            QFrame.Card {{ background-color: {card}; border: 1px solid rgba(0,0,0,15); border-radius: 8px; }}
            QPushButton {{ background-color: #fdfdfd; border: 1px solid #d1d1d1; border-radius: 4px; padding: 6px 16px; color: #111;}}
            QPushButton:hover {{ background-color: #f5f5f5; }}
            QPushButton#Primary {{ background-color: {pri}; color: white; border: none; }}
            QPushButton#Danger {{ background-color: transparent; color: #d83b01; border: 1px solid #d83b01; }}
            QPushButton#Danger:hover {{ background-color: #d83b01; color: white; }}
            QPushButton#TitleClose {{ background: transparent; border: none; color: #333; border-radius: 0px;}}
            QPushButton#TitleClose:hover {{ background: #e81123; color: white; }}
            
            /* 【修复】：无边框退出按钮，解决左侧截断 */
            QPushButton#ExitAppBtn {{ background: transparent; border: none; color: #d83b01; text-align: left; padding-left: 20px; font-weight: bold; }}
            QPushButton#ExitAppBtn:hover {{ background: rgba(216, 59, 1, 0.1); color: #e81123; }}
            
            QLineEdit, QComboBox {{ background-color: #fff; border: 1px solid #ccc; border-radius: 4px; padding: 6px; color: black;}}
            QScrollArea {{ border: none; background: transparent; }}
        """

class TabManageDialog(QDialog):
    def __init__(self, box, parent=None):
        super().__init__(parent)
        self.box = box
        self.setWindowTitle(t("TabManage") + f" - {box.title_text}")
        self.resize(300, 400)
        self.setStyleSheet(parent.styleSheet()) 
        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        for cat in self.box.lists.keys():
            self.list_widget.addItem(cat)
        layout.addWidget(self.list_widget)
        
        btn_ly = QHBoxLayout()
        add_btn = QPushButton("➕")
        add_btn.clicked.connect(self.add_tab)
        rename_btn = QPushButton("✏️")
        rename_btn.clicked.connect(self.rename_tab)
        del_btn = QPushButton("➖")
        del_btn.setObjectName("Danger")
        del_btn.clicked.connect(self.del_tab)
        btn_ly.addWidget(add_btn)
        btn_ly.addWidget(rename_btn)
        btn_ly.addWidget(del_btn)
        layout.addLayout(btn_ly)
        
    def add_tab(self):
        name, ok = QInputDialog.getText(self, "New Tab", "Name:")
        if ok and name and name not in self.box.lists:
            self.list_widget.addItem(name)
            lw = BoxListWidget(self.box, name)
            self.box.lists[name] = lw
            self.box.tab_widget.addTab(lw, name)

    def rename_tab(self):
        item = self.list_widget.currentItem()
        if not item:
            return
        old_name = item.text()
        new_name, ok = QInputDialog.getText(self, "Rename", "Name:", text=old_name)
        if ok and new_name and new_name != old_name and new_name not in self.box.lists:
            item.setText(new_name)
            lw = self.box.lists.pop(old_name)
            self.box.lists[new_name] = lw
            idx = self.box.tab_widget.indexOf(lw)
            self.box.tab_widget.setTabText(idx, new_name)

    def del_tab(self):
        if self.list_widget.count() <= 1:
            return
        item = self.list_widget.currentItem()
        if not item:
            return
        name = item.text()
        self.list_widget.takeItem(self.list_widget.row(item))
        lw = self.box.lists.pop(name)
        self.box.tab_widget.removeTab(self.box.tab_widget.indexOf(lw))
        lw.deleteLater()

class AnimatedSidebar(QWidget):
    def __init__(self, parent_window):
        super().__init__()
        self.parent_window = parent_window
        self.setFixedWidth(200)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 10, 0, 10)
        
        self.list_widget = QListWidget()
        self.list_widget.addItems([t("Home"), t("Appearance"), t("BoxRules"), t("DesktopHook"), t("SystemAdv")])
        self.list_widget.setCurrentRow(0)
        self.layout.addWidget(self.list_widget)
        
        self.indicator = QWidget(self.list_widget)
        self.indicator.setFixedSize(3, 18)
        self.indicator.setStyleSheet(f"background-color: {self.get_accent_color()}; border-radius: 1.5px;")
        self.indicator.move(14, 14) 
        
        self.anim = QPropertyAnimation(self.indicator, b"geometry")
        self.anim.setDuration(200)
        self.list_widget.currentRowChanged.connect(self.animate_indicator)
        
        self.layout.addStretch()
        
        # 【修复】使用无边框 QSS ID 修复退出按钮
        exit_btn = QPushButton(t("ExitApp"))
        exit_btn.setObjectName("ExitAppBtn")
        exit_btn.setMinimumHeight(44)
        exit_btn.clicked.connect(self.parent_window.save_and_exit)
        self.layout.addWidget(exit_btn)
        
    def get_accent_color(self):
        c = config.settings.get("panel_bg_theme", "default")
        return THEME_COLORS.get(c, THEME_COLORS["default"])["accent"]

    def animate_indicator(self, row):
        item_rect = self.list_widget.visualItemRect(self.list_widget.item(row))
        target_y = item_rect.y() + (item_rect.height() - 18) // 2
        self.anim.setEndValue(QRect(14, target_y, 3, 18))
        self.indicator.setStyleSheet(f"background-color: {self.get_accent_color()}; border-radius: 1.5px;")
        self.anim.start()
        self.parent_window.pages.setCurrentIndex(row)

class Win11TitleBar(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setFixedHeight(35)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 0, 0)
        self.title_label = QLabel(t("Settings"))
        self.title_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.title_label)
        layout.addStretch()
        self.close_btn = QPushButton("✕")
        self.close_btn.setFixedSize(45, 35)
        self.close_btn.clicked.connect(self.parent.hide_and_save)
        layout.addWidget(self.close_btn)
        self.dragging = False
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.drag_pos = event.globalPosition().toPoint() - self.parent.pos()
    def mouseMoveEvent(self, event):
        if self.dragging:
            self.parent.move(event.globalPosition().toPoint() - self.drag_pos)
    def mouseReleaseEvent(self, event):
        self.dragging = False

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Window)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground) 
        self.resize(850, 620)
        
        self.boxes = {} 
        self.boxes_visible = True
        self.hook_thread = None
        self.manually_hidden_boxes = set()
        
        self.setup_ui()
        self.apply_theme() 
        self.load_all_boxes()
        self.apply_hook_setting()

    def showEvent(self, event):
        # 【修复：真正的屏幕居中】使用可用几何体并在首次显示时移动
        super().showEvent(event)
        try:
            screen_geo = self.screen().availableGeometry()
            x = screen_geo.x() + (screen_geo.width() - self.width()) // 2
            y = screen_geo.y() + (screen_geo.height() - self.height()) // 2
            self.move(x, y)
        except: pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 8, 8)
        tm = config.settings.get("app_theme", "system")
        if tm == "system": tm = get_system_theme()
        bg_theme = config.settings.get("panel_bg_theme", "default")
        
        bg_color = QColor(THEME_COLORS.get(bg_theme, THEME_COLORS["default"])["dark" if tm == "dark" else "light"])
        painter.fillPath(path, bg_color)
        painter.setPen(QColor("#444" if tm == "dark" else "#ccc"))
        painter.drawPath(path)

    def apply_theme(self):
        tm = config.settings.get("app_theme", "system")
        if tm == "system": tm = get_system_theme()
        bg_theme = config.settings.get("panel_bg_theme", "default")
        self.setStyleSheet(get_qss(tm, bg_theme))
        if hasattr(self, 'title_bar'): self.title_bar.close_btn.setObjectName("TitleClose")
        if hasattr(self, 'sidebar'): self.sidebar.animate_indicator(self.pages.currentIndex())
        self.update()

    def create_card(self, parent_layout):
        card = QFrame()
        card.setProperty("class", "Card")
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(10)
        parent_layout.addWidget(card)
        return layout

    def setup_ui(self):
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)
        self.title_bar = Win11TitleBar(self)
        root_layout.addWidget(self.title_bar)

        main_layout = QHBoxLayout()
        root_layout.addLayout(main_layout)

        self.pages = QStackedWidget()
        self.sidebar = AnimatedSidebar(self)
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages)

        # 0: 主页
        home_page = QWidget()
        h_ly = QVBoxLayout(home_page)
        h_ly.setContentsMargins(20, 20, 30, 20)
        h_ly.addWidget(QLabel(t("GuideTitle")))
        card1 = self.create_card(h_ly)
        card1.addWidget(QLabel(t("GuideText")))
        card2 = self.create_card(h_ly)
        card2.addWidget(QLabel(t("LicenseTitle") + "<br>" + t("LicenseText")))
        h_ly.addStretch()
        self.pages.addWidget(home_page)

        # 1: 外观
        ui_page = QWidget()
        ui_layout = QVBoxLayout(ui_page)
        ui_layout.setContentsMargins(20, 20, 30, 20)
        ui_layout.addWidget(QLabel(f"<h1 style='font-size:24px; font-weight:normal;'>{t('Appearance')}</h1>"))
        
        app_card = self.create_card(ui_layout)
        ly = QHBoxLayout()
        ly.addWidget(QLabel(t("ThemeMode")))
        self.app_theme_combo = QComboBox()
        self.app_theme_combo.addItems([t("System"), t("Light"), t("Dark")])
        self.app_theme_combo.setCurrentIndex({"system": 0, "light": 1, "dark": 2}.get(config.settings.get("app_theme", "system"), 0))
        self.app_theme_combo.currentIndexChanged.connect(lambda idx: self.update_setting("app_theme", ["system", "light", "dark"][idx], self.apply_theme))
        ly.addWidget(self.app_theme_combo)
        app_card.addLayout(ly)
        
        ly_color = QHBoxLayout()
        ly_color.addWidget(QLabel(t("GlobalColor")))
        self.set_color_combo = QComboBox()
        self.set_color_combo.addItems(["Default", "Blue", "Green", "Warm", "Pink", "Cyan", "Purple", "Gray", "Cherry", "Mint", "Gold", "Navy"])
        color_keys = ["default", "blue", "green", "warm", "pink", "cyan", "purple", "gray", "cherry", "mint", "gold", "navy"]
        self.set_color_combo.setCurrentIndex(color_keys.index(config.settings.get("panel_bg_theme", "default")))
        self.set_color_combo.currentIndexChanged.connect(lambda idx: self.update_setting("panel_bg_theme", color_keys[idx], self.apply_theme))
        ly_color.addWidget(self.set_color_combo)
        app_card.addLayout(ly_color)

        box_card = self.create_card(ui_layout)
        ly2 = QHBoxLayout()
        ly2.addWidget(QLabel(t("BoxMaterial")))
        self.effect_combo = QComboBox()
        self.effect_combo.addItems([t("Normal"), t("Transparent"), t("Blur"), t("Acrylic")])
        self.effect_combo.setCurrentIndex({"normal":0,"transparent":1,"blur":2,"acrylic":3}.get(config.settings.get("box_effect", "transparent"), 1))
        self.effect_combo.currentIndexChanged.connect(lambda idx: self.update_setting("box_effect", ["normal", "transparent", "blur", "acrylic"][idx], self.refresh_all_boxes))
        ly2.addWidget(self.effect_combo)
        box_card.addLayout(ly2)
        
        ly3 = QHBoxLayout()
        ly3.addWidget(QLabel(t("BoxColor")))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(BOX_COLOR_NAMES)
        try:
            self.theme_combo.setCurrentIndex(BOX_COLORS.index(config.settings.get("color_theme", "#1e1e1e")))
        except:
            self.theme_combo.setCurrentIndex(0)
        self.theme_combo.currentIndexChanged.connect(self.change_box_color)
        ly3.addWidget(self.theme_combo)
        box_card.addLayout(ly3)

        ly4 = QHBoxLayout()
        ly4.addWidget(QLabel(t("BoxOpacity")))
        self.alpha_slider = QSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(0, 255)
        self.alpha_slider.setValue(config.settings.get("theme_alpha", 180))
        self.alpha_slider.valueChanged.connect(lambda val: self.update_setting("theme_alpha", val, self.refresh_all_boxes))
        ly4.addWidget(self.alpha_slider)
        box_card.addLayout(ly4)

        tab_card = self.create_card(ui_layout)
        ly_tab = QHBoxLayout()
        ly_tab.addWidget(QLabel(t("TabPosition")))
        self.tab_pos_combo = QComboBox()
        self.tab_pos_combo.addItems([t("Top"), t("Bottom"), t("Left"), t("Right")])
        self.tab_pos_combo.setCurrentIndex({"top":0,"bottom":1,"left":2,"right":3}.get(config.settings.get("tab_position", "top"), 0))
        self.tab_pos_combo.currentIndexChanged.connect(lambda idx: self.update_setting("tab_position", ["top", "bottom", "left", "right"][idx], self.update_all_tabs_pos))
        ly_tab.addWidget(self.tab_pos_combo)
        tab_card.addLayout(ly_tab)
        
        ui_layout.addStretch()
        self.pages.addWidget(ui_page)

        # 2: 规则管理
        box_page = QWidget()
        box_layout = QVBoxLayout(box_page)
        box_layout.setContentsMargins(20, 20, 30, 20)
        box_layout.addWidget(QLabel(f"<h1 style='font-size:24px; font-weight:normal;'>{t('BoxRules')}</h1>"))
        
        m_card = self.create_card(box_layout)
        btn_ly = QHBoxLayout()
        btn_ly.addWidget(QLabel(t("BoxList")))
        add_box_btn = QPushButton(t("NewBox"))
        add_box_btn.clicked.connect(lambda: self.create_custom_box("Custom Box"))
        btn_ly.addWidget(add_box_btn)
        m_card.addLayout(btn_ly)
        
        self.box_list_ui = QVBoxLayout()
        m_card.addLayout(self.box_list_ui)
        self.refresh_box_management_ui()

        r_card = self.create_card(box_layout)
        top_rule_ly = QHBoxLayout()
        top_rule_ly.addWidget(QLabel(t("RuleTitle")))
        apply_rule_btn = QPushButton(t("ApplyRule"))
        apply_rule_btn.setObjectName("Primary")
        apply_rule_btn.clicked.connect(self.apply_rules_and_refresh)
        add_rule_btn = QPushButton(t("AddRule"))
        add_rule_btn.clicked.connect(lambda: self.add_rule_row("", ""))
        top_rule_ly.addWidget(add_rule_btn)
        top_rule_ly.addWidget(apply_rule_btn)
        r_card.addLayout(top_rule_ly)

        self.rule_scroll = QScrollArea()
        self.rule_scroll.setWidgetResizable(True)
        self.rule_container = QWidget()
        self.rule_form_layout = QVBoxLayout(self.rule_container)
        self.rule_form_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.rule_rows = []
        for cat, exts in config.settings.get("rules", {}).items():
            self.add_rule_row(cat, ", ".join(exts))
        self.rule_scroll.setWidget(self.rule_container)
        r_card.addWidget(self.rule_scroll)
        self.pages.addWidget(box_page)

        # 3: 桌面接管
        org_page = QWidget()
        org_layout = QVBoxLayout(org_page)
        org_layout.setContentsMargins(20, 20, 30, 20)
        org_layout.addWidget(QLabel(f"<h1 style='font-size:24px; font-weight:normal;'>{t('DesktopHook')}</h1>"))
        
        o_card = self.create_card(org_layout)
        o_card.addWidget(QLabel(t("HookTitle")))
        self.exclude_cb = QCheckBox(t("ExcludeSys"))
        self.exclude_cb.setChecked(config.settings.get("exclude_sys_icons", True))
        self.exclude_cb.stateChanged.connect(lambda state: self.update_setting("exclude_sys_icons", state == 2))
        o_card.addWidget(self.exclude_cb)
        
        ex_ly = QHBoxLayout()
        ex_ly.addWidget(QLabel(t("ExcludeExt")))
        self.exclude_exts_input = QLineEdit(", ".join(config.settings.get("exclude_exts", [])))
        self.exclude_exts_input.textChanged.connect(self.save_exclude_exts)
        ex_ly.addWidget(self.exclude_exts_input)
        o_card.addLayout(ex_ly)
        
        org_btn = QPushButton(t("OrgBtn"))
        org_btn.setObjectName("Primary")
        org_btn.setMinimumHeight(40)
        org_btn.clicked.connect(self.organize_desktop)
        o_card.addWidget(org_btn)
        
        restore_btn = QPushButton(t("RestoreBtn"))
        restore_btn.setMinimumHeight(40)
        restore_btn.clicked.connect(self.restore_desktop)
        o_card.addWidget(restore_btn)
        org_layout.addStretch()
        self.pages.addWidget(org_page)

        # 4: 系统偏好
        sys_page = QWidget()
        sys_layout = QVBoxLayout(sys_page)
        sys_layout.setContentsMargins(20, 20, 30, 20)
        sys_layout.addWidget(QLabel(f"<h1 style='font-size:24px; font-weight:normal;'>{t('SystemAdv')}</h1>"))
        
        s_card = self.create_card(sys_layout)
        
        lang_ly = QHBoxLayout()
        lang_ly.addWidget(QLabel("Language / 语言:"))
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(["简体中文 (zh_CN)", "English (en_US)", "日本語 (ja_JP)"])
        self.lang_combo.setCurrentIndex({"zh": 0, "en": 1, "ja": 2}.get(config.settings.get("language", "zh"), 0))
        self.lang_combo.currentIndexChanged.connect(self.change_language)
        lang_ly.addWidget(self.lang_combo)
        s_card.addLayout(lang_ly)
        
        self.hook_cb = QCheckBox(t("HookEnable"))
        self.hook_cb.setChecked(config.settings.get("enable_desktop_hook", True))
        self.hook_cb.stateChanged.connect(self.toggle_hook)
        s_card.addWidget(self.hook_cb)
        
        self.hover_cb = QCheckBox(t("HoverExpand"))
        self.hover_cb.setChecked(config.settings.get("hover_expand", True))
        self.hover_cb.stateChanged.connect(lambda state: self.update_setting("hover_expand", state == 2))
        s_card.addWidget(self.hover_cb)
        
        self.hover_tab_cb = QCheckBox(t("HoverTab"))
        self.hover_tab_cb.setChecked(config.settings.get("hover_switch_tab", True))
        self.hover_tab_cb.stateChanged.connect(lambda state: self.update_setting("hover_switch_tab", state == 2))
        s_card.addWidget(self.hover_tab_cb)
        
        path_ly = QHBoxLayout()
        path_ly.addWidget(QLabel(t("DataPath")))
        path_ly.addWidget(QLabel(config.settings.get("data_path", "default")))
        change_path_btn = QPushButton(t("ChangePath"))
        change_path_btn.clicked.connect(self.change_data_path)
        path_ly.addWidget(change_path_btn)
        s_card.addLayout(path_ly)
        
        sys_layout.addStretch()
        danger_card = self.create_card(sys_layout)
        reset_btn = QPushButton(t("Reset"))
        reset_btn.setObjectName("Danger")
        reset_btn.clicked.connect(self.reset_to_default_settings)
        danger_card.addWidget(reset_btn)
        self.pages.addWidget(sys_page)

    # ================= 业务逻辑区 =================
    def change_language(self, idx):
        lang = ["zh", "en", "ja"][idx]
        config.settings["language"] = lang
        config.save_all()
        QMessageBox.information(self, "Language Changed", "Please restart the application to apply the new language.\n请重新启动软件以应用新语言。")

    def update_all_tabs_pos(self):
        for box in self.boxes.values():
            if hasattr(box, 'update_tab_position'): box.update_tab_position()

    def update_setting(self, key, value, callback=None):
        config.settings[key] = value
        config.save_all()
        if callback: callback()

    def save_exclude_exts(self):
        self.update_setting("exclude_exts", [e.strip() for e in self.exclude_exts_input.text().split(",") if e.strip().startswith(".")])

    def reset_to_default_settings(self):
        if QMessageBox.question(self, "Warning", "Reset to default?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
            config.settings = copy.deepcopy(config.default_settings)
            config.save_all()
            QApplication.quit()

    def refresh_box_management_ui(self):
        while self.box_list_ui.count():
            item = self.box_list_ui.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        for box_id, box in self.boxes.items():
            row = QWidget()
            ly = QHBoxLayout(row)
            ly.setContentsMargins(0, 0, 0, 0)
            ly.addWidget(QLabel(f"🗂️ {box.title_text}" if box_id != "main_box" else f"⭐ {box.title_text}"))
            ly.addStretch()
            
            if box_id != "main_box":
                tab_btn = QPushButton(t("TabManage"))
                tab_btn.clicked.connect(lambda _, b=box: TabManageDialog(b, self).exec())
                ly.addWidget(tab_btn)
            
            toggle_btn = QPushButton(t("Hidden") if box_id in self.manually_hidden_boxes else t("Shown"))
            toggle_btn.clicked.connect(lambda _, b=box, btn=toggle_btn: self.toggle_single_box(b, btn))
            ly.addWidget(toggle_btn)
            
            rename_btn = QPushButton(t("Rename"))
            rename_btn.clicked.connect(lambda _, b=box: b.rename_box(None))
            ly.addWidget(rename_btn)
            
            if box_id != "main_box":
                del_btn = QPushButton(t("Disband"))
                del_btn.clicked.connect(lambda _, b=box: b.destroy_box())
                ly.addWidget(del_btn)
            self.box_list_ui.addWidget(row)

    def toggle_single_box(self, box, btn):
        if box.isVisible():
            box.hide()
            self.manually_hidden_boxes.add(box.box_id)
            btn.setText(t("Hidden"))
        else:
            box.show()
            self.manually_hidden_boxes.discard(box.box_id)
            btn.setText(t("Shown"))

    def add_rule_row(self, cat_name, exts):
        row_widget = QWidget()
        row_layout = QHBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 5, 0, 5)
        cat_input = QLineEdit(str(cat_name))
        cat_input.setPlaceholderText(t("CatName"))
        cat_input.setFixedWidth(80)
        ext_input = QLineEdit(str(exts))
        ext_input.setPlaceholderText(t("ExtName"))
        del_btn = QPushButton(t("Del"))
        del_btn.setFixedWidth(60)
        del_btn.clicked.connect(lambda: self.remove_rule_row(row_widget))
        cat_input.textChanged.connect(self.auto_save_rules)
        ext_input.textChanged.connect(self.auto_save_rules)
        row_layout.addWidget(cat_input)
        row_layout.addWidget(ext_input)
        row_layout.addWidget(del_btn)
        self.rule_form_layout.addWidget(row_widget)
        self.rule_rows.append((row_widget, cat_input, ext_input))
        self.auto_save_rules()

    def remove_rule_row(self, row_widget):
        self.rule_rows = [row for row in self.rule_rows if row[0] != row_widget]
        row_widget.deleteLater()
        self.auto_save_rules()

    def auto_save_rules(self):
        new_rules = {}
        for _, cat_input, ext_input in self.rule_rows:
            cat = cat_input.text().strip()
            if cat:
                exts = [e.strip() for e in ext_input.text().split(",") if e.strip()]
                new_rules[cat] = exts
        config.settings["rules"] = new_rules
        config.save_all()

    def apply_rules_and_refresh(self):
        self.main_box.refresh_by_new_rules()

    def organize_desktop(self):
        desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        public_desktop = os.path.join(os.environ.get("PUBLIC", "C:\\Users\\Public"), "Desktop")
        files_to_map = []
        exclude_exts = config.settings.get("exclude_exts", [])
        for d in [desktop_dir, public_desktop]:
            if os.path.exists(d):
                for f in os.listdir(d):
                    full_path = os.path.join(d, f)
                    if not is_hidden_or_temp_file(full_path):
                        if config.settings.get("exclude_sys_icons", True) and is_system_shortcut(full_path): continue
                        if os.path.splitext(full_path)[1].lower() in exclude_exts: continue
                        files_to_map.append(full_path)
        self.main_box.bulk_add_files(files_to_map)
        set_desktop_icons_visible(False)
        self.update_setting("desktop_organized", True)

    def restore_desktop(self):
        for lw in self.main_box.lists.values(): lw.clear()
        self.main_box.mapped_files.clear()
        set_desktop_icons_visible(True)
        self.update_setting("desktop_organized", False)

    def change_box_color(self, idx):
        config.settings["color_theme"] = BOX_COLORS[idx]
        for box in self.boxes.values(): 
            box.bg_color = QColor(BOX_COLORS[idx])
            box.apply_title_font_color()
        self.refresh_all_boxes()

    def refresh_all_boxes(self):
        for box in self.boxes.values():
            box.apply_effect()
            box.update()

    def change_data_path(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Change Path")
        if dir_path: config.settings["data_path"] = dir_path

    def toggle_hook(self, state):
        config.settings["enable_desktop_hook"] = (state == 2)
        self.apply_hook_setting()

    def apply_hook_setting(self):
        if config.settings.get("enable_desktop_hook", True):
            if not self.hook_thread:
                self.hook_signals = HookSignals()
                self.hook_signals.toggle_boxes.connect(self.toggle_boxes_visibility)
                self.hook_thread = DesktopHookThread(self.hook_signals)
                self.hook_thread.start()
        else:
            if self.hook_thread:
                self.hook_thread.stop_listener()
                self.hook_thread = None

    def load_all_boxes(self):
        self.main_box = MainDesktopBox(config.data.get("main_box", {}), self.organize_desktop, self.restore_desktop, self.showNormal)
        if "main_box" not in self.manually_hidden_boxes:
            self.main_box.show()
        self.boxes["main_box"] = self.main_box
        for box_data in config.data.get("custom_boxes", []):
            self.create_custom_box_from_data(box_data)

    def create_custom_box(self, title):
        self.create_custom_box_from_data({"id": f"box_{int(time.time())}", "title": title, "x": 200, "y": 200, "color": config.settings.get("color_theme", "#1e1e1e"), "files": []})

    def create_custom_box_from_data(self, data):
        box = CustomDesktopBox(data, self.showNormal)
        box.box_destroyed.connect(self.handle_box_destroyed)
        box.box_renamed.connect(lambda _, __: self.refresh_box_management_ui())
        if data["id"] not in self.manually_hidden_boxes:
            box.show()
        self.boxes[data["id"]] = box
        self.refresh_box_management_ui()

    def handle_box_destroyed(self, box_id):
        self.boxes.pop(box_id, None)
        self.refresh_box_management_ui()

    def toggle_boxes_visibility(self):
        self.boxes_visible = not self.boxes_visible
        for box_id, box in self.boxes.items():
            if self.boxes_visible:
                if box_id not in self.manually_hidden_boxes: box.show()
            else: box.hide()
        set_desktop_icons_visible(self.boxes_visible and not config.settings.get("desktop_organized", False))

    def save_data_state(self):
        config.data["main_box"] = self.main_box.get_state()
        config.data["custom_boxes"] = [box.get_state() for id, box in self.boxes.items() if id != "main_box"]
        config.save_all()

    def hide_and_save(self):
        self.save_data_state()
        self.hide()

    def save_and_exit(self):
        self.save_data_state()
        if self.hook_thread: self.hook_thread.stop_listener()
        set_desktop_icons_visible(True)
        QApplication.quit()