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
