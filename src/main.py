#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2024中国城市空气质量数据分析系统
主程序入口
"""

import sys
import os
import tkinter as tk
from tkinter import messagebox

def main():
    """主程序入口"""
    try:
        # 首先设置中文字体
        try:
            from utils.font_config import setup_chinese_font
            print("正在配置中文字体...")
            font_success = setup_chinese_font()
            if font_success:
                print("✓ 中文字体配置成功")
            else:
                print("⚠ 中文字体配置警告，可能影响图表显示")
        except ImportError:
            print("⚠ 字体配置模块未找到，使用默认字体设置")
            import matplotlib.pyplot as plt
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False
        
        # 导入主窗口类
        from gui.main_window import MainWindow
        
        # 创建Tkinter根窗口
        root = tk.Tk()
        
        # 创建主窗口应用
        app = MainWindow(root)
        
        # 启动应用
        root.mainloop()
        
    except ImportError as e:
        print(f"导入模块失败: {e}")
        print("请确保所有必要的模块都已正确安装")
        sys.exit(1)
    except Exception as e:
        print(f"程序启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    print("=" * 50)
    print("2024中国城市空气质量数据分析系统")
    print("=" * 50)
    main()
