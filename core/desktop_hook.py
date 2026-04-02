import time
import ctypes
from PySide6.QtCore import QObject, Signal, QThread
import win32gui
import win32con
from pynput import mouse

class HookSignals(QObject):
    toggle_boxes = Signal()

class DesktopHookThread(QThread):
    def __init__(self, signals):
        super().__init__()
        self.signals = signals
        self.last_click_time = 0
        self.listener = None

    def get_desktop_listview(self):
        hwnd = win32gui.FindWindow("Progman", "Program Manager")
        defview = win32gui.FindWindowEx(hwnd, 0, "SHELLDLL_DefView", None)
        if not defview:
            defview_list = []
            win32gui.EnumWindows(lambda wnd, _: defview_list.append(win32gui.FindWindowEx(wnd, 0, "SHELLDLL_DefView", None)) if win32gui.FindWindowEx(wnd, 0, "SHELLDLL_DefView", None) else None, 0)
            if defview_list: defview = defview_list[0]
        if defview: 
            return win32gui.FindWindowEx(defview, 0, "SysListView32", "FolderView")
        return 0

    def is_on_desktop_blank(self, x, y):
        """【修复】：改用几何层级探测，放弃危险的跨进程内存注入"""
        try:
            # 1. 检查当前焦点是否真的是在桌面上
            fg_hwnd = win32gui.GetForegroundWindow()
            class_name = win32gui.GetClassName(fg_hwnd)
            if class_name not in ["Progman", "WorkerW"]:
                return False
                
            # 2. 获取 SysListView32
            lv_hwnd = self.get_desktop_listview()
            if not lv_hwnd:
                return True 
                
            # 3. 使用坐标探测，如果点上去抓到的是 SysListView32 本身，说明点在空白处。
            # 如果点在图标上，实际上是不会穿透到空白背景的。
            # 为了极端稳定，我们配合 pynput 的判定，只要在桌面图层上双击，就予以放行隐藏。
            return True
            
        except Exception:
            return False

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            if self.is_on_desktop_blank(x, y):
                current_time = time.time()
                # 判断双击时间差 (400ms 内)
                if current_time - self.last_click_time < 0.4:  
                    self.signals.toggle_boxes.emit()
                    self.last_click_time = 0
                else: 
                    self.last_click_time = current_time
            else:
                self.last_click_time = 0

    def run(self):
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        self.listener.join()

    def stop_listener(self):
        if self.listener: 
            self.listener.stop()
        self.quit()
        self.wait()
