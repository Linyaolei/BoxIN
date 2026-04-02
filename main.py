import sys
import ctypes
import os

os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false;qt.gui.text.*=false"

try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
except Exception: pass

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle
from PySide6.QtGui import QAction, QIcon
from ui.main_window import MainWindow
from core.desktop_utils import get_resource_path

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 【修复 1】：使用 get_resource_path 绝对路径加载打包后的图标
    icon_path = get_resource_path("logo.ico")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
    else:
        app_icon = app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        
    app.setWindowIcon(app_icon)

    main_window = MainWindow()
    main_window.show()

    tray_icon = QSystemTrayIcon(app_icon, app)
    
    tray_menu = QMenu()
    show_action = QAction("打开设置中心", app)
    show_action.triggered.connect(main_window.showNormal)
    tray_menu.addAction(show_action)
    
    toggle_action = QAction("显示/隐藏所有盒子", app)
    toggle_action.triggered.connect(main_window.toggle_boxes_visibility)
    tray_menu.addAction(toggle_action)
    
    tray_menu.addSeparator()
    quit_action = QAction("退出程序", app)
    quit_action.triggered.connect(main_window.save_and_exit)
    tray_menu.addAction(quit_action)

    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()

    def on_tray_activated(reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            main_window.showNormal()
            
    tray_icon.activated.connect(on_tray_activated)
    app.aboutToQuit.connect(main_window.hook_thread.stop_listener)

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
