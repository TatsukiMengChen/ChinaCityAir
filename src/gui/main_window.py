#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主窗口模块
空气质量数据分析系统的主界面
"""

import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox, filedialog
import os
import sys
from typing import Optional

# 添加父目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from gui.data_module import DataModule
from gui.analysis_module import AnalysisModule
from gui.visualization_module import VisualizationModule
from gui.utils import configure_dpi, create_style

class MainWindow:
    """主窗口类"""
    
    def __init__(self, root: tk.Tk):
        """
        初始化主窗口
        
        Args:
            root: Tkinter根窗口
        """
        self.root = root
        self.setup_window()
        self.setup_style()
        self.create_widgets()
        
        # 初始化子模块
        self.data_module = None
        self.analysis_module = None
        self.visualization_module = None
        
    def setup_window(self):
        """设置窗口属性"""
        self.root.title("中国城市空气质量数据分析系统")
        
        # 配置高DPI支持
        configure_dpi(self.root)
        
        # 设置窗口大小和位置
        window_width = 1200
        window_height = 800
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.minsize(800, 600)
        
        # 设置窗口图标（如果有的话）
        try:
            icon_path = os.path.join(os.path.dirname(__file__), '..', '..', 'assets', 'icon.ico')
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass
    
    def setup_style(self):
        """设置界面样式"""
        self.style = create_style()
        
    def create_widgets(self):
        """创建界面组件"""
        # 创建主菜单
        self.create_menu()
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建主要内容区域
        self.create_main_content()
        
        # 创建状态栏
        self.create_status_bar()
    
    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 文件菜单
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开数据文件...", command=self.open_data_file)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.on_closing)
        
        # 数据菜单
        data_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="数据", menu=data_menu)
        data_menu.add_command(label="获取数据", command=self.show_data_module)
        data_menu.add_command(label="数据处理", command=self.show_data_module)
        
        # 分析菜单
        analysis_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="分析", menu=analysis_menu)
        analysis_menu.add_command(label="统计分析", command=self.show_analysis_module)
        analysis_menu.add_command(label="高级分析", command=self.show_analysis_module)
        
        # 可视化菜单
        visualization_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="可视化", menu=visualization_menu)
        visualization_menu.add_command(label="基础图表", command=self.show_visualization_module)
        visualization_menu.add_command(label="高级图表", command=self.show_visualization_module)
        
        # 帮助菜单
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="关于", command=self.show_about)
    
    def create_toolbar(self):
        """创建工具栏"""
        toolbar = Frame(self.root)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)
        
        # 数据相关按钮
        Button(toolbar, text="获取数据", 
                  command=self.show_data_module, width=10).pack(side=tk.LEFT, padx=2)
        Button(toolbar, text="数据分析", 
                  command=self.show_analysis_module, width=10).pack(side=tk.LEFT, padx=2)
        Button(toolbar, text="数据可视化", 
                  command=self.show_visualization_module, width=10).pack(side=tk.LEFT, padx=2)
        
        # 分隔符
        Separator(toolbar, orient='vertical').pack(side=tk.LEFT, fill=tk.Y, padx=5)
        
        # 打开文件按钮
        Button(toolbar, text="打开文件", 
                  command=self.open_data_file, width=10).pack(side=tk.LEFT, padx=2)
    
    def create_main_content(self):
        """创建主要内容区域"""
        # 创建笔记本控件（选项卡）
        self.notebook = Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 欢迎页面
        self.create_welcome_tab()
    
    def create_welcome_tab(self):
        """创建欢迎页面选项卡"""
        welcome_frame = Frame(self.notebook)
        self.notebook.add(welcome_frame, text="欢迎")
        
        # 创建欢迎内容
        main_frame = Frame(welcome_frame)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 标题
        title_label = Label(main_frame, 
                               text="中国城市空气质量数据分析系统",
                               font=('Microsoft YaHei', 16, 'bold'))
        title_label.pack(pady=20)
        
        # 功能介绍
        intro_text = """
本系统提供以下功能：

📊 数据获取：从权威网站爬取最新的空气质量数据
🔧 数据处理：清洗和预处理原始数据
📈 数据分析：进行统计分析和趋势分析
📉 数据可视化：生成各种图表和报告

使用指南：
1. 点击"获取数据"开始爬取空气质量数据
2. 选择"数据分析"查看统计结果
3. 使用"数据可视化"生成图表
4. 或者直接打开已有的数据文件进行分析
        """
        
        intro_label = Label(main_frame, text=intro_text, 
                               font=('Microsoft YaHei', 10),
                               justify=tk.LEFT)
        intro_label.pack(pady=10, anchor=tk.W)
        
        # 快速操作按钮
        button_frame = Frame(main_frame)
        button_frame.pack(pady=20)
        
        Button(button_frame, text="开始获取数据", 
                  command=self.show_data_module).pack(side=tk.LEFT, padx=10)
        Button(button_frame, text="打开数据文件", 
                  command=self.open_data_file).pack(side=tk.LEFT, padx=10)
    
    def create_status_bar(self):
        """创建状态栏"""
        self.status_bar = Frame(self.root)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = Label(self.status_bar, text="就绪")
        self.status_label.pack(side=tk.LEFT, padx=5, pady=2)
        
        # 进度条（可选）
        self.progress_var = tk.DoubleVar()
        self.progress_bar = Progressbar(self.status_bar, 
                                           variable=self.progress_var,
                                           length=200)
        self.progress_bar.pack(side=tk.RIGHT, padx=5, pady=2)
    
    def show_data_module(self):
        """显示数据模块"""
        if self.data_module is None:
            self.data_module = DataModule(self.notebook, self)
        
        # 检查选项卡是否已存在
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == "数据管理":
                self.notebook.select(i)
                return
        
        self.notebook.add(self.data_module.frame, text="数据管理")
        self.notebook.select(self.data_module.frame)
    
    def show_analysis_module(self):
        """显示分析模块"""
        if self.analysis_module is None:
            self.analysis_module = AnalysisModule(self.notebook, self)
        
        # 检查选项卡是否已存在
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == "数据分析":
                self.notebook.select(i)
                return
        
        self.notebook.add(self.analysis_module.frame, text="数据分析")
        self.notebook.select(self.analysis_module.frame)
    
    def show_visualization_module(self):
        """显示可视化模块"""
        if self.visualization_module is None:
            self.visualization_module = VisualizationModule(self.notebook, self)
        
        # 检查选项卡是否已存在
        for i in range(self.notebook.index("end")):
            if self.notebook.tab(i, "text") == "数据可视化":
                self.notebook.select(i)
                return
        
        self.notebook.add(self.visualization_module.frame, text="数据可视化")
        self.notebook.select(self.visualization_module.frame)
    
    def open_data_file(self):
        """打开数据文件"""
        file_path = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ],
            initialdir=os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        )
        
        if file_path:
            self.update_status(f"已选择文件: {os.path.basename(file_path)}")
            # 这里可以添加加载数据的逻辑
            messagebox.showinfo("提示", f"已选择数据文件：\n{file_path}")
    
    def show_about(self):
        """显示关于对话框"""
        about_text = """
中国城市空气质量数据分析系统

版本：1.0.0
开发者：MengChen
开发时间：2024年

功能特点：
• 数据爬取和处理
• 统计分析
• 数据可视化
• 友好的用户界面

技术栈：
• Python 3.x
• Tkinter GUI
• Pandas 数据处理
• Matplotlib 可视化
        """
        messagebox.showinfo("关于", about_text)
    
    def update_status(self, message: str):
        """更新状态栏"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def update_progress(self, value: float):
        """更新进度条"""
        self.progress_var.set(value)
        self.root.update_idletasks()
    
    def on_closing(self):
        """窗口关闭事件"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MainWindow(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
