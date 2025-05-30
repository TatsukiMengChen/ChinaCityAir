#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据可视化模块
提供各种图表生成功能
"""

import tkinter as tk
from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox, filedialog
import os
import sys
import threading
from datetime import datetime

# 添加父目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_processor.data_loader import DataLoader
from visualizer.basic_charts import BasicCharts
from visualizer.advanced_charts import AdvancedCharts

class VisualizationModule:
    """数据可视化模块"""
    
    def __init__(self, parent, main_window):
        """
        初始化可视化模块
        
        Args:
            parent: 父组件
            main_window: 主窗口引用
        """
        self.parent = parent
        self.main_window = main_window
        self.frame = Frame(parent)
        
        self.data_loader = DataLoader()
        self.basic_charts = BasicCharts()
        self.advanced_charts = AdvancedCharts()
        
        self.data = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主容器
        main_container = Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 文件选择区域
        file_frame = LabelFrame(main_container, text="数据文件")
        file_frame.pack(fill=tk.X, pady=(0, 10))
        
        file_select_frame = Frame(file_frame)
        file_select_frame.pack(fill=tk.X, padx=10, pady=5)
        
        Label(file_select_frame, text="选择数据文件:").pack(side=tk.LEFT)
        
        self.file_path_var = tk.StringVar()
        self.file_path_entry = Entry(file_select_frame, textvariable=self.file_path_var,
                                       state='readonly', width=50)
        self.file_path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        browse_button = Button(file_select_frame, text="浏览",
                                 command=self.browse_data_file)
        browse_button.pack(side=tk.RIGHT)
        
        load_button = Button(file_select_frame, text="加载数据",
                               command=self.load_data)
        load_button.pack(side=tk.RIGHT, padx=(0, 5))
        
        # 创建选项卡
        notebook = Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 基础图表选项卡
        self.create_basic_charts_tab(notebook)
        
        # 高级图表选项卡
        self.create_advanced_charts_tab(notebook)
    
    def create_basic_charts_tab(self, parent):
        """创建基础图表选项卡"""
        basic_frame = Frame(parent)
        parent.add(basic_frame, text="基础图表")
        
        # 图表选择区域
        chart_frame = LabelFrame(basic_frame, text="图表类型")
        chart_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 创建图表按钮网格
        button_frame = Frame(chart_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 第一行按钮
        row1 = Frame(button_frame)
        row1.pack(fill=tk.X, pady=2)
        
        Button(row1, text="AQI对比柱状图", 
               command=lambda: self.generate_chart('aqi_comparison'),
               width=20).pack(side=tk.LEFT, padx=5)
        Button(row1, text="PM2.5对比柱状图", 
               command=lambda: self.generate_chart('pm25_comparison'),
               width=20).pack(side=tk.LEFT, padx=5)
        Button(row1, text="空气质量分布饼图", 
               command=lambda: self.generate_chart('quality_pie'),
               width=20).pack(side=tk.LEFT, padx=5)
        
        # 第二行按钮
        row2 = Frame(button_frame)
        row2.pack(fill=tk.X, pady=2)
        
        Button(row2, text="污染物散点图", 
               command=lambda: self.generate_chart('pollutant_scatter'),
               width=20).pack(side=tk.LEFT, padx=5)
        Button(row2, text="时间趋势折线图", 
               command=lambda: self.generate_chart('time_trend'),
               width=20).pack(side=tk.LEFT, padx=5)
        Button(row2, text="污染物箱线图", 
               command=lambda: self.generate_chart('pollutant_box'),
               width=20).pack(side=tk.LEFT, padx=5)
        
        # 参数设置
        param_frame = LabelFrame(basic_frame, text="图表参数")
        param_frame.pack(fill=tk.X, padx=10, pady=5)
        
        param_grid = Frame(param_frame)
        param_grid.pack(fill=tk.X, padx=10, pady=5)
        
        # 城市数量
        Label(param_grid, text="显示城市数量:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.city_count_var = tk.StringVar(value="20")
        city_spinbox = Spinbox(param_grid, from_=5, to=100, textvariable=self.city_count_var, width=10)
        city_spinbox.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 图表尺寸
        Label(param_grid, text="图表宽度:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.width_var = tk.StringVar(value="12")
        width_spinbox = Spinbox(param_grid, from_=8, to=20, textvariable=self.width_var, width=10)
        width_spinbox.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        Label(param_grid, text="图表高度:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.height_var = tk.StringVar(value="8")
        height_spinbox = Spinbox(param_grid, from_=6, to=16, textvariable=self.height_var, width=10)
        height_spinbox.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 保存格式
        Label(param_grid, text="保存格式:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        self.format_var = tk.StringVar(value="png")
        format_combo = Combobox(param_grid, textvariable=self.format_var,
                                  values=["png", "jpg", "pdf", "svg"],
                                  state="readonly", width=10)
        format_combo.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)
        
        # 状态显示区域
        status_frame = LabelFrame(basic_frame, text="生成状态")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        status_text_frame = Frame(status_frame)
        status_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.basic_status_text = tk.Text(status_text_frame, height=8, wrap=tk.WORD)
        basic_scrollbar = Scrollbar(status_text_frame, orient=tk.VERTICAL, command=self.basic_status_text.yview)
        
        self.basic_status_text.configure(yscrollcommand=basic_scrollbar.set)
        self.basic_status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        basic_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_advanced_charts_tab(self, parent):
        """创建高级图表选项卡"""
        advanced_frame = Frame(parent)
        parent.add(advanced_frame, text="高级图表")
        
        # 图表选择区域
        chart_frame = LabelFrame(advanced_frame, text="高级图表类型")
        chart_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 创建图表按钮网格
        button_frame = Frame(chart_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # 第一行按钮
        row1 = Frame(button_frame)
        row1.pack(fill=tk.X, pady=2)
        
        Button(row1, text="相关性热力图", 
               command=lambda: self.generate_advanced_chart('correlation_heatmap'),
               width=20).pack(side=tk.LEFT, padx=5)
        Button(row1, text="城市雷达图", 
               command=lambda: self.generate_advanced_chart('city_radar'),
               width=20).pack(side=tk.LEFT, padx=5)
        Button(row1, text="地理热力图", 
               command=lambda: self.generate_advanced_chart('geo_heatmap'),
               width=20).pack(side=tk.LEFT, padx=5)
        
        # 第二行按钮
        row2 = Frame(button_frame)
        row2.pack(fill=tk.X, pady=2)
        
        Button(row2, text="3D散点图", 
               command=lambda: self.generate_advanced_chart('3d_scatter'),
               width=20).pack(side=tk.LEFT, padx=5)
        Button(row2, text="交互式图表", 
               command=lambda: self.generate_advanced_chart('interactive'),
               width=20).pack(side=tk.LEFT, padx=5)
        Button(row2, text="综合仪表盘", 
               command=lambda: self.generate_advanced_chart('dashboard'),
               width=20).pack(side=tk.LEFT, padx=5)
        
        # 高级参数设置
        param_frame = LabelFrame(advanced_frame, text="高级参数")
        param_frame.pack(fill=tk.X, padx=10, pady=5)
        
        param_grid = Frame(param_frame)
        param_grid.pack(fill=tk.X, padx=10, pady=5)
        
        # 分析深度
        Label(param_grid, text="分析深度:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.depth_var = tk.StringVar(value="standard")
        depth_combo = Combobox(param_grid, textvariable=self.depth_var,
                                 values=["basic", "standard", "detailed"],
                                 state="readonly", width=15)
        depth_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 图表主题
        Label(param_grid, text="图表主题:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
        self.theme_var = tk.StringVar(value="default")
        theme_combo = Combobox(param_grid, textvariable=self.theme_var,
                                 values=["default", "seaborn", "ggplot", "classic"],
                                 state="readonly", width=15)
        theme_combo.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
        
        # 颜色方案
        Label(param_grid, text="颜色方案:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.color_var = tk.StringVar(value="viridis")
        color_combo = Combobox(param_grid, textvariable=self.color_var,
                                 values=["viridis", "plasma", "coolwarm", "rainbow"],
                                 state="readonly", width=15)
        color_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        
        # 交互性
        self.interactive_var = tk.BooleanVar(value=True)
        Checkbutton(param_grid, text="启用交互功能", 
                      variable=self.interactive_var).grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
        
        # 状态显示区域
        status_frame = LabelFrame(advanced_frame, text="生成状态")
        status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        status_text_frame = Frame(status_frame)
        status_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.advanced_status_text = tk.Text(status_text_frame, height=8, wrap=tk.WORD)
        advanced_scrollbar = Scrollbar(status_text_frame, orient=tk.VERTICAL, command=self.advanced_status_text.yview)
        
        self.advanced_status_text.configure(yscrollcommand=advanced_scrollbar.set)
        self.advanced_status_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        advanced_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def browse_data_file(self):
        """浏览数据文件"""
        file_path = filedialog.askopenfilename(
            title="选择数据文件",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ],
            initialdir=os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        )
        
        if file_path:
            self.file_path_var.set(file_path)
    
    def load_data(self):
        """加载数据"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("警告", "请先选择数据文件！")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在！")
            return
        
        try:
            self.data = self.data_loader.load_csv(file_path)
            self.main_window.update_status(f"数据加载完成，共 {len(self.data)} 行")
            messagebox.showinfo("成功", f"数据加载完成！\n共 {len(self.data)} 行数据")
        except Exception as e:
            messagebox.showerror("错误", f"数据加载失败: {str(e)}")
    
    def generate_chart(self, chart_type):
        """生成基础图表"""
        if self.data is None:
            messagebox.showwarning("警告", "请先加载数据！")
            return
        
        try:
            self.log_basic_status(f"开始生成 {chart_type} 图表...")
            
            # 获取参数
            city_count = int(self.city_count_var.get())
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            format_type = self.format_var.get()
              # 根据图表类型生成
            if chart_type == 'aqi_comparison':
                # 使用柱状图显示城市AQI对比
                save_name = f"city_aqi_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
                self.basic_charts.plot_bar_chart(
                    self.data, 'city', 'aqi', 
                    title=f'城市AQI对比 (前{city_count}名)', 
                    top_n=city_count, save_name=save_name)
                filepath = os.path.join(self.basic_charts.output_dir, save_name)
                
            elif chart_type == 'pm25_comparison':
                # 使用柱状图显示城市PM2.5对比
                save_name = f"city_pm25_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
                self.basic_charts.plot_bar_chart(
                    self.data, 'city', 'pm25', 
                    title=f'城市PM2.5对比 (前{city_count}名)', 
                    top_n=city_count, save_name=save_name)
                filepath = os.path.join(self.basic_charts.output_dir, save_name)
                
            elif chart_type == 'quality_pie':
                # 使用饼图显示空气质量分布
                save_name = f"quality_distribution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
                self.basic_charts.plot_quality_distribution(
                    self.data, title='空气质量等级分布', save_name=save_name)
                filepath = os.path.join(self.basic_charts.output_dir, save_name)
                
            elif chart_type == 'pollutant_scatter':
                # 使用散点图显示污染物相关性
                save_name = f"pm25_aqi_scatter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
                self.basic_charts.plot_scatter(
                    self.data, 'pm25', 'aqi', 
                    title='PM2.5与AQI相关性分析', 
                    color_column='city', save_name=save_name)
                filepath = os.path.join(self.basic_charts.output_dir, save_name)
                
            elif chart_type == 'time_trend':
                # 使用时间序列图显示趋势
                if 'timestamp' in self.data.columns:
                    save_name = f"time_trend_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
                    self.basic_charts.plot_time_series(
                        self.data, ['aqi', 'pm25'], 
                        title='空气质量时间序列分析', save_name=save_name)
                    filepath = os.path.join(self.basic_charts.output_dir, save_name)
                else:
                    raise ValueError("数据中缺少时间列，无法生成时间序列图")
                
            elif chart_type == 'pollutant_box':
                # 使用多城市对比图代替箱线图
                cities = self.data['city'].unique()[:10]  # 取前10个城市
                save_name = f"multi_city_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{format_type}"
                self.basic_charts.plot_multi_city_comparison(
                    self.data, cities.tolist(), 
                    pollutant='aqi', title='多城市AQI对比', save_name=save_name)
                filepath = os.path.join(self.basic_charts.output_dir, save_name)
            
            else:
                raise ValueError(f"未知的图表类型: {chart_type}")
            
            if filepath:
                self.log_basic_status(f"图表生成完成: {filepath}")
                messagebox.showinfo("成功", f"图表已生成并保存到:\n{filepath}")
            else:
                self.log_basic_status("图表生成失败")
                
        except Exception as e:
            error_msg = f"生成图表失败: {str(e)}"
            self.log_basic_status(error_msg)
            messagebox.showerror("错误", error_msg)
    
    def generate_advanced_chart(self, chart_type):
        """生成高级图表"""
        if self.data is None:
            messagebox.showwarning("警告", "请先加载数据！")
            return
        
        try:
            self.log_advanced_status(f"开始生成 {chart_type} 高级图表...")
            
            # 获取参数
            depth = self.depth_var.get()
            theme = self.theme_var.get()
            color_scheme = self.color_var.get()
            interactive = self.interactive_var.get()
              # 根据图表类型生成
            if chart_type == 'correlation_heatmap':
                # 使用相关性热力图
                numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
                available_columns = [col for col in numeric_columns if col in self.data.columns]
                save_name = f"correlation_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.advanced_charts.plot_correlation_heatmap(
                    data=self.data, 
                    columns=available_columns, 
                    title='污染物相关性热力图', 
                    save_name=save_name)
                filepath = os.path.join(self.advanced_charts.output_dir, save_name)
                
            elif chart_type == 'city_radar':
                # 使用雷达图
                cities = self.data['city'].unique()[:5]  # 取前5个城市
                metrics = ['aqi', 'pm25', 'pm10']
                available_metrics = [col for col in metrics if col in self.data.columns]
                save_name = f"city_radar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.advanced_charts.plot_radar_chart(
                    data=self.data, 
                    cities=cities.tolist(), 
                    metrics=available_metrics, 
                    title='城市空气质量雷达图', 
                    save_name=save_name)
                filepath = os.path.join(self.advanced_charts.output_dir, save_name)
                
            elif chart_type == 'geo_heatmap':
                # 使用时间热力图代替地理热力图
                if 'timestamp' in self.data.columns:
                    save_name = f"time_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                    self.advanced_charts.plot_time_heatmap(
                        data=self.data, 
                        time_column='timestamp', 
                        value_column='aqi', 
                        title='时间-AQI热力图', 
                        save_name=save_name)
                    filepath = os.path.join(self.advanced_charts.output_dir, save_name)
                else:
                    raise ValueError("数据中缺少时间列，无法生成时间热力图")
                
            elif chart_type == '3d_scatter':
                # 使用交互式散点图代替3D散点图
                save_name = f"interactive_scatter_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                self.advanced_charts.plot_interactive_scatter(
                    data=self.data, 
                    x_column='pm25', 
                    y_column='aqi', 
                    color_column='city', 
                    title='PM2.5与AQI交互式散点图', 
                    save_name=save_name)
                filepath = os.path.join(self.advanced_charts.output_dir, save_name)
                
            elif chart_type == 'interactive':
                # 使用交互式时间序列图
                if 'timestamp' in self.data.columns:
                    save_name = f"interactive_time_series_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                    self.advanced_charts.plot_interactive_time_series(
                        data=self.data, 
                        time_column='timestamp', 
                        value_columns=['aqi', 'pm25'], 
                        title='交互式时间序列图', 
                        save_name=save_name)
                    filepath = os.path.join(self.advanced_charts.output_dir, save_name)
                else:
                    raise ValueError("数据中缺少时间列，无法生成交互式时间序列图")
                
            elif chart_type == 'dashboard':
                # 使用综合仪表板
                save_name = f"pollution_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
                self.advanced_charts.plot_pollution_dashboard(
                    data=self.data, 
                    save_name=save_name)
                filepath = os.path.join(self.advanced_charts.output_dir, save_name)
            
            else:
                raise ValueError(f"未知的高级图表类型: {chart_type}")
            
            if filepath:
                self.log_advanced_status(f"高级图表生成完成: {filepath}")
                messagebox.showinfo("成功", f"高级图表已生成并保存到:\n{filepath}")
            else:
                self.log_advanced_status("高级图表生成失败")
                
        except Exception as e:
            error_msg = f"生成高级图表失败: {str(e)}"
            self.log_advanced_status(error_msg)
            messagebox.showerror("错误", error_msg)
    
    def log_basic_status(self, message):
        """记录基础图表状态"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.basic_status_text.insert(tk.END, log_entry)
        self.basic_status_text.see(tk.END)
        self.main_window.root.update_idletasks()
    
    def log_advanced_status(self, message):
        """记录高级图表状态"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.advanced_status_text.insert(tk.END, log_entry)
        self.advanced_status_text.see(tk.END)
        self.main_window.root.update_idletasks()
