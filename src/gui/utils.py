#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI工具模块
提供DPI配置、样式设置等工具函数
"""

import tkinter as tk
from tkinter import ttk
import os
import sys

def configure_dpi(root: tk.Tk):
    """
    配置高DPI支持
    
    Args:
        root: Tkinter根窗口
    """
    try:
        # Windows系统DPI感知设置
        if sys.platform.startswith('win'):
            import ctypes
            # 调用api设置成由应用程序缩放
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
            # 调用api获得当前的缩放因子
            ScaleFactor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
            # 设置缩放因子
            root.tk.call('tk', 'scaling', ScaleFactor/75)
            
    except Exception as e:
        print(f"DPI配置警告: {e}")

def create_style() -> ttk.Style:
    """
    创建和配置ttk样式，使用Windows 11默认样式
    
    Returns:
        配置好的ttk.Style对象
    """
    style = ttk.Style()
    
    # 获取可用主题并选择最合适的Windows原生主题
    available_themes = style.theme_names()
    print(f"可用主题: {available_themes}")
    
    # 优先使用Windows原生主题，按优先级选择
    # if 'winnative' in available_themes:
    #     style.theme_use('winnative')
    # elif 'xpnative' in available_themes:
    #     style.theme_use('xpnative')
    # elif 'vista' in available_themes:
    #     style.theme_use('vista')
    # elif 'clam' in available_themes:
    #     style.theme_use('clam')
    # else:
    #     style.theme_use('default')
    style.theme_use('xpnative')
    
    print(f"使用主题: {style.theme_use()}")
    
    return style

def create_scrollable_frame(parent, width=None, height=None) -> tuple:
    """
    创建可滚动的框架
    
    Args:
        parent: 父组件
        width: 框架宽度
        height: 框架高度
        
    Returns:
        (canvas, scrollable_frame) 元组
    """
    # 创建画布和滚动条
    canvas = tk.Canvas(parent, highlightthickness=0)
    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    if width:
        canvas.config(width=width)
    if height:
        canvas.config(height=height)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # 绑定鼠标滚轮事件
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind("<MouseWheel>", _on_mousewheel)
    
    # 布局
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    return canvas, scrollable_frame

def center_window(window, width, height):
    """
    将窗口居中显示
    
    Args:
        window: 窗口对象
        width: 窗口宽度
        height: 窗口高度
    """
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    window.geometry(f"{width}x{height}+{x}+{y}")

def validate_number_input(char):
    """
    验证数字输入
    
    Args:
        char: 输入的字符
        
    Returns:
        bool: 是否为有效输入
    """
    return char.isdigit() or char == "." or char == ""

def create_labeled_entry(parent, label_text, entry_var=None, width=20) -> tuple:
    """
    创建带标签的输入框
    
    Args:
        parent: 父组件
        label_text: 标签文本
        entry_var: 关联的变量
        width: 输入框宽度
        
    Returns:
        (label, entry) 元组
    """
    frame = ttk.Frame(parent)
    
    label = ttk.Label(frame, text=label_text)
    label.pack(side=tk.LEFT, padx=(0, 10))
    
    if entry_var is None:
        entry_var = tk.StringVar()
    
    entry = ttk.Entry(frame, textvariable=entry_var, width=width)
    entry.pack(side=tk.LEFT)
    
    return frame, label, entry, entry_var

def show_loading_dialog(parent, title="处理中", message="请稍候..."):
    """
    显示加载对话框
    
    Args:
        parent: 父窗口
        title: 对话框标题
        message: 显示消息
        
    Returns:
        对话框窗口对象
    """
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry("300x100")
    dialog.resizable(False, False)
    dialog.transient(parent)
    dialog.grab_set()
    
    center_window(dialog, 300, 100)
    
    # 消息标签
    msg_label = ttk.Label(dialog, text=message, font=('Microsoft YaHei', 10))
    msg_label.pack(pady=20)
    
    # 进度条
    progress = ttk.Progressbar(dialog, mode='indeterminate')
    progress.pack(pady=10, padx=20, fill=tk.X)
    progress.start()
    
    dialog.progress = progress
    return dialog

def close_loading_dialog(dialog):
    """
    关闭加载对话框
    
    Args:
        dialog: 对话框窗口对象
    """
    if dialog and dialog.winfo_exists():
        dialog.progress.stop()
        dialog.destroy()

class ToolTip:
    """工具提示类"""
    
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        
        # 绑定事件
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        """鼠标进入事件"""
        if self.tooltip_window:
            return
        
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 20
        y += self.widget.winfo_rooty() + 20
        
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        
        label = ttk.Label(self.tooltip_window, text=self.text,
                         background="lightyellow", relief="solid",
                         borderwidth=1, font=('Microsoft YaHei', 8))
        label.pack()
    
    def on_leave(self, event=None):
        """鼠标离开事件"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
