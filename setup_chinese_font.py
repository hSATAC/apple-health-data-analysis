import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

def setup_chinese_font():
    # 嘗試找到系統中的中文字體
    font_paths = [
        '/System/Library/Fonts/PingFang.ttc',
        '/System/Library/Fonts/STHeiti Light.ttc',
        '/System/Library/Fonts/STHeiti Medium.ttc',
        '/Library/Fonts/Arial Unicode.ttf',
        '/System/Library/Fonts/Helvetica.ttc'
    ]
    
    font_found = False
    for font_path in font_paths:
        if os.path.exists(font_path):
            try:
                font_prop = fm.FontProperties(fname=font_path)
                plt.rcParams['font.sans-serif'] = [font_prop.get_name()]
                plt.rcParams['axes.unicode_minus'] = False
                font_found = True
                print(f"使用字體: {font_prop.get_name()}")
                break
            except:
                continue
    
    if not font_found:
        # 如果找不到中文字體，使用英文
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        print("使用預設英文字體")
    
    return font_found