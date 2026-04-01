import time
from PySide6.QtCore import QObject, Signal, QThread
import win32gui
from pynput import mouse

class HookSignals(QObject):
    toggle_boxes = Signal()

class DesktopHookThread(QThread):
    def __init__(self, signals):
        super().__init__()
        self.signals = signals
        self.last_click_time = 0
        self.listener = None

    def is_desktop_window(self):
        try:
            hwnd = win32gui.GetForegroundWindow()
            return win32gui.GetClassName(hwnd) in ["Progman", "WorkerW"]
        except: 
            return False

    def on_click(self, x, y, button, pressed):
        if pressed and button == mouse.Button.left:
            if self.is_desktop_window():
                current_time = time.time()
                if current_time - self.last_click_time < 0.4:  
                    self.signals.toggle_boxes.emit()
                    self.last_click_time = 0
                else: 
                    self.last_click_time = current_time

    def run(self):
        self.listener = mouse.Listener(on_click=self.on_click)
        self.listener.start()
        self.listener.join()

    def stop_listener(self):
        if self.listener: 
            self.listener.stop()
        self.quit()
        self.wait()