import json
import os
import copy

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")

class ConfigManager:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance.init_config()
        return cls._instance

    def init_config(self):
        if not os.path.exists(CONFIG_DIR): os.makedirs(CONFIG_DIR)
        
        self.default_settings = {
            "language": "zh",            # 【新增】默认中文
            "app_theme": "system", 
            "settings_theme_color": "blue",
            "open_mode": "double",
            "box_effect": "acrylic", 
            "color_theme": "#1e1e1e",
            "theme_alpha": 180,
            "data_path": "default",
            "enable_desktop_hook": True,
            "desktop_organized": False,
            "exclude_sys_icons": True,   
            "exclude_exts": [".ini", ".tmp", ".sys", ".db"],
            "tab_position": "top",       
            "hover_expand": True,
            "hover_switch_tab": True,     
            "rules": {
                "文档": [".doc", ".docx", ".pdf", ".txt", ".xlsx", ".csv", ".pptx"],
                "图片": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],
                "应用": [".exe", ".lnk"]
            }
        }
        self.settings = self.load_json(SETTINGS_FILE, copy.deepcopy(self.default_settings))
        self.data_path = CONFIG_DIR if self.settings["data_path"] == "default" else self.settings["data_path"]
        self.data_file = os.path.join(self.data_path, "data.json")
        self.default_data = {"main_box": {"title": "主盒子", "x": 100, "y": 100, "tabs": {"文档": [], "图片": [], "应用": [], "未分类": []}}, "custom_boxes": []}
        self.data = self.load_json(self.data_file, copy.deepcopy(self.default_data))

    def load_json(self, file_path, default_data):
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    file_data = json.load(f)
                    for k, v in file_data.items(): default_data[k] = v
            except: pass
        return default_data

    def save_all(self):
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f: json.dump(self.settings, f, ensure_ascii=False, indent=4)
        if not os.path.exists(self.data_path): os.makedirs(self.data_path)
        with open(self.data_file, "w", encoding="utf-8") as f: json.dump(self.data, f, ensure_ascii=False, indent=4)

config = ConfigManager()