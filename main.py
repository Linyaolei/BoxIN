import sys
import ctypes
import os

# 彻底屏蔽 Qt 的内部 QFont 负数警告和其他无害绘图警告
os.environ["QT_LOGGING_RULES"] = "*.debug=false;qt.qpa.*=false;qt.gui.text.*=false"

try:
    ctypes.windll.user32.SetProcessDpiAwarenessContext(-4)
except Exception: pass

from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QStyle
from PySide6.QtGui import QAction, QIcon
from ui.main_window import MainWindow

def resource_path(relative_path):
    """【绝对终极路径魔法】让图片完美兼容 PyInstaller 打包后的环境"""
    try:
        # 如果是 PyInstaller 打包后的运行环境，所有的资源会被解压到 _MEIPASS 目录
        base_path = sys._MEIPASS
    except Exception:
        # 如果是本地开发环境，就用当前文件目录
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    
    # 尝试加载内嵌的 logo.ico
    icon_path = resource_path("logo.ico")
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
    else:
        # 降级方案：找不到就用系统默认电脑图标
        app_icon = app.style().standardIcon(QStyle.StandardPixmap.SP_ComputerIcon)
        
    app.setWindowIcon(app_icon)

    main_window = MainWindow()
    main_window.show()

    # 将同一个图标应用到系统托盘
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
