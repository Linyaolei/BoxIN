import os
from PySide6.QtWidgets import QFileIconProvider
from PySide6.QtCore import QFileInfo

def open_file_safe(file_path):
    """安全地使用系统默认程序打开文件"""
    if os.path.exists(file_path):
        os.startfile(file_path)

def open_file_location(file_path):
    """打开文件所在目录"""
    if os.path.exists(file_path):
        os.startfile(os.path.dirname(file_path))

def get_system_icon(file_path):
    """获取系统原生图标 (已修复 PySide6 兼容性)"""
    provider = QFileIconProvider()
    # 必须将其转换为 QFileInfo 对象
    return provider.icon(QFileInfo(file_path))