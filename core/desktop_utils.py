import win32gui
import win32con
import win32api
import os
import winreg
import re

def get_desktop_listview():
    hwnd = win32gui.FindWindow("Progman", "Program Manager")
    defview = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
    if not defview:
        defview_list = []
        win32gui.EnumWindows(lambda wnd, _: defview_list.append(win32gui.FindWindowEx(wnd, 0, "SHELLDLL_DefView", None)) if win32gui.FindWindowEx(wnd, 0, "SHELLDLL_DefView", None) else None, 0)
        if defview_list: defview = defview_list[0]
    if defview: return win32gui.FindWindowEx(defview, 0, "SysListView32", "FolderView")
    return 0

def set_desktop_icons_visible(visible):
    lv = get_desktop_listview()
    if lv: win32gui.ShowWindow(lv, win32con.SW_SHOW if visible else win32con.SW_HIDE)

def is_hidden_or_temp_file(filepath):
    """【修复】：增强临时文件过滤，防止杀毒软件占位符被吸入"""
    name = os.path.basename(filepath)
    
    # 1. 过滤标准临时文件前缀和系统配置文件
    if name.startswith("~$") or name.lower() == "desktop.ini": return True
    
    # 2. 过滤类似 ZZZZZ3573229001.doc 的杀软或同步盘缓存文件
    if re.match(r"^Z{3,}\d+\.[a-zA-Z0-9]+$", name, re.IGNORECASE): return True
    
    # 3. 过滤纯数字或全大写字母组合且被标记为隐藏的文件
    try:
        attrs = win32api.GetFileAttributes(filepath)
        return bool(attrs & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM))
    except: return False

def is_system_shortcut(filepath):
    name = os.path.basename(filepath).lower()
    return name in ["此电脑", "回收站", "网络", "控制面板"] or "::{20D04FE0" in filepath

def get_system_theme():
    try:
        registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
        key = winreg.OpenKey(registry, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize")
        value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        return "light" if value == 1 else "dark"
    except: return "light"

def is_color_light(hex_color):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6: return False
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return ((0.299 * r + 0.587 * g + 0.114 * b) / 255) > 0.65

def get_file_stats(filepath):
    try:
        stat = os.stat(filepath)
        return stat.st_size, stat.st_mtime
    except: return 0, 0
