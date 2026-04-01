import ctypes
from ctypes import c_int, Structure, POINTER, sizeof

class ACCENT_POLICY(Structure):
    _fields_ = [
        ("AccentState", c_int),
        ("AccentFlags", c_int),
        ("GradientColor", c_int),
        ("AnimationId", c_int)
    ]

class WINDOWCOMPOSITIONATTRIBDATA(Structure):
    _fields_ = [
        ("Attribute", c_int),
        ("Data", POINTER(ACCENT_POLICY)),
        ("SizeOfData", c_int)
    ]

def apply_window_effect(hwnd, effect_type="acrylic", color_hex="#1e1e1e", alpha=160):
    """
    hwnd: 窗口的 winId()
    effect_type: "normal", "transparent", "blur", "acrylic"
    """
    try:
        accent = ACCENT_POLICY()
        
        if effect_type == "normal" or effect_type == "transparent":
            accent.AccentState = 0 # 禁用底层特效，完全依靠 Qt 绘制
        elif effect_type == "blur":
            accent.AccentState = 3 # ACCENT_ENABLE_BLURBEHIND (Win10)
        elif effect_type == "acrylic":
            accent.AccentState = 4 # ACCENT_ENABLE_ACRYLICBLURBEHIND (Win10/11)

        # 解析颜色并转换为 Windows 格式 AABBGGRR
        r, g, b = int(color_hex[1:3], 16), int(color_hex[3:5], 16), int(color_hex[5:7], 16)
        accent.GradientColor = (alpha << 24) | (b << 16) | (g << 8) | r

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19 # WCA_ACCENT_POLICY
        data.Data = ctypes.pointer(accent)
        data.SizeOfData = sizeof(accent)

        ctypes.windll.user32.SetWindowCompositionAttribute(int(hwnd), ctypes.pointer(data))
    except Exception as e:
        print(f"特效加载失败: {e}")