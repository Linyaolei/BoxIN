import os
from core.config_manager import config

def categorize_file(file_path):
    """根据文件后缀和配置规则，返回所属分类名称"""
    rules = config.settings.get("rules", {})
    
    # 【新增功能】如果是文件夹，优先寻找规则中包含 "__dir__" (文件夹专属标识) 的分类
    if os.path.isdir(file_path):
        for category, extensions in rules.items():
            if "__dir__" in extensions or "文件夹" in extensions:
                return category
        return "文件夹" # 如果没配，默认给一个单独的标签页
        
    ext = os.path.splitext(file_path)[1].lower()
    for category, extensions in rules.items():
        if ext in extensions:
            return category

    return "未分类"