#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据管理模块
包含数据获取和数据处理功能
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

from crawler.air_quality_spider import AirQualitySpider
from data_processor.data_loader import DataLoader
from data_processor.data_cleaner import DataCleaner
from data_processor.data_validator import DataValidator

class DataModule:
    """数据管理模块"""
    
    def __init__(self, parent, main_window):
        """
        初始化数据模块
        
        Args:
            parent: 父组件
            main_window: 主窗口引用
        """
        self.parent = parent
        self.main_window = main_window
        self.frame = Frame(parent)
        
        self.spider = None
        self.data_loader = DataLoader()
        self.data_cleaner = DataCleaner()
        self.data_validator = DataValidator()
        
        self.create_widgets()
    
    def create_widgets(self):
        """创建界面组件"""
        # 创建主容器
        main_container = Frame(self.frame)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # 创建选项卡
        notebook = Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # 数据获取选项卡
        self.create_crawl_tab(notebook)
        
        # 数据处理选项卡
        self.create_process_tab(notebook)
    
    def create_crawl_tab(self, parent):
        """创建数据获取选项卡"""
        crawl_frame = Frame(parent)
        parent.add(crawl_frame, text="数据获取")
        
        # 配置区域
        config_frame = LabelFrame(crawl_frame, text="爬取配置")
        config_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 数据量配置
        count_frame = Frame(config_frame)
        count_frame.pack(fill=tk.X, padx=10, pady=5)
        
        Label(count_frame, text="爬取数量:").pack(side=tk.LEFT)
        self.count_var = tk.StringVar(value="50")
        count_spinbox = Spinbox(count_frame, from_=10, to=1000,
                                   textvariable=self.count_var,
                                   width=10)
        count_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        Label(count_frame, text="(建议50-200条，避免对服务器造成压力)",
                              foreground='gray').pack(side=tk.LEFT, padx=(10, 0))
        
        # 延迟配置
        delay_frame = Frame(config_frame)
        delay_frame.pack(fill=tk.X, padx=10, pady=5)
        
        Label(delay_frame, text="请求间隔:").pack(side=tk.LEFT)
        self.delay_var = tk.StringVar(value="0.5")
        delay_spinbox = Spinbox(delay_frame, from_=0.5, to=10, increment=0.5,
                                   textvariable=self.delay_var,
                                   width=10)
        delay_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        Label(delay_frame, text="秒").pack(side=tk.LEFT, padx=(5, 0))
        
        # 操作按钮区域
        button_frame = Frame(crawl_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.start_button = Button(button_frame, text="开始爬取",
                                      command=self.start_crawling)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = Button(button_frame, text="停止爬取",
                                     command=self.stop_crawling,
                                     state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 进度条
        self.progress_var = tk.DoubleVar()
        self.progress_bar = Progressbar(button_frame,
                                          variable=self.progress_var,
                                          maximum=100)
        self.progress_bar.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(20, 0))
        
        # 日志区域
        log_frame = LabelFrame(crawl_frame, text="爬取日志")
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 创建文本框和滚动条
        log_text_frame = Frame(log_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = tk.Text(log_text_frame, height=10, width=50, wrap=tk.WORD)
        log_scrollbar = Scrollbar(log_text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_process_tab(self, parent):
        """创建数据处理选项卡"""
        process_frame = Frame(parent)
        parent.add(process_frame, text="数据处理")
        
        # 文件选择区域
        file_frame = LabelFrame(process_frame, text="数据文件")
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
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
        
        # 处理选项
        options_frame = LabelFrame(process_frame, text="处理选项")
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 缺失值处理
        missing_frame = Frame(options_frame)
        missing_frame.pack(fill=tk.X, padx=10, pady=5)
        
        Label(missing_frame, text="缺失值处理:").pack(side=tk.LEFT)
        self.missing_method_var = tk.StringVar(value="mean")
        methods = [("均值填充", "mean"), ("中位数填充", "median"), 
                  ("删除缺失值", "drop"), ("线性插值", "interpolate")]
        
        for text, value in methods:
            Radiobutton(missing_frame, text=text, variable=self.missing_method_var,
                          value=value).pack(side=tk.LEFT, padx=10)
        
        # 处理按钮
        process_button_frame = Frame(process_frame)
        process_button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.process_button = Button(process_button_frame, text="开始处理",
                                        command=self.start_processing)
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        self.save_button = Button(process_button_frame, text="保存结果",
                                     command=self.save_processed_data,
                                     state='disabled')
        self.save_button.pack(side=tk.LEFT, padx=5)
        
        # 结果显示区域
        result_frame = LabelFrame(process_frame, text="处理结果")
        result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        result_text_frame = Frame(result_frame)
        result_text_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.result_text = tk.Text(result_text_frame, height=8, width=50, wrap=tk.WORD)
        result_scrollbar = Scrollbar(result_text_frame, orient=tk.VERTICAL, command=self.result_text.yview)
        
        self.result_text.configure(yscrollcommand=result_scrollbar.set)
        self.result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        result_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def start_crawling(self):
        """开始爬取数据"""
        try:
            count = int(self.count_var.get())
            delay = float(self.delay_var.get())
            
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.progress_var.set(0)
            
            self.log_text.delete('1.0', tk.END)
            self.log_message("开始爬取空气质量数据...")
            
            # 在新线程中运行爬虫
            self.crawl_thread = threading.Thread(
                target=self._run_crawler,
                args=(count, delay),
                daemon=True
            )
            self.crawl_thread.start()
            
        except ValueError as e:
            messagebox.showerror("错误", f"参数错误: {e}")
            
    def _run_crawler(self, count, delay):
        """在线程中运行爬虫"""
        try:
            self.spider = AirQualitySpider()
            
            def progress_callback(current, total):
                progress = (current / total) * 100
                self.main_window.root.after(0, lambda: self.progress_var.set(progress))
                self.main_window.root.after(0, lambda: self.log_message(f"已爬取 {current}/{total} 条数据"))
            
            def status_callback(message):
                self.main_window.root.after(0, lambda: self.log_message(message))
            
            # 设置回调函数
            self.spider.set_progress_callback(progress_callback)
            self.spider.set_status_callback(status_callback)
            
            # 开始爬取
            filename = self.spider.crawl_data(count=count, delay=delay)
            
            if filename:
                self.main_window.root.after(0, lambda: self.log_message(f"爬取完成！数据已保存到: {filename}"))
                self.main_window.root.after(0, lambda: messagebox.showinfo("完成", f"数据爬取完成！\n保存位置: {filename}"))
            else:
                self.main_window.root.after(0, lambda: self.log_message("爬取失败！"))
                
        except Exception as e:
            self.main_window.root.after(0, lambda: self.log_message(f"爬取出错: {str(e)}"))
            self.main_window.root.after(0, lambda: messagebox.showerror("错误", f"爬取失败: {str(e)}"))
        finally:
            self.main_window.root.after(0, self._crawl_finished)
    
    def stop_crawling(self):
        """停止爬取"""
        if self.spider:
            self.spider.stop()
        self.log_message("正在停止爬取...")
    
    def _crawl_finished(self):
        """爬取完成后的清理工作"""
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_var.set(0)
    
    def log_message(self, message):
        """添加日志消息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
    
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
    
    def start_processing(self):
        """开始处理数据"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("警告", "请先选择数据文件！")
            return
        
        if not os.path.exists(file_path):
            messagebox.showerror("错误", "文件不存在！")
            return
        
        try:
            self.process_button.config(state='disabled')
            self.result_text.delete('1.0', tk.END)
            self.result_text.insert(tk.END, "正在加载数据...\n")
            
            # 加载数据
            self.data = self.data_loader.load_csv(file_path)
            self.result_text.insert(tk.END, f"数据加载完成，共 {len(self.data)} 行\n")
              # 数据清洗
            missing_method = self.missing_method_var.get()
            self.result_text.insert(tk.END, f"开始数据清洗，缺失值处理方法: {missing_method}\n")
            
            self.cleaned_data = self.data_cleaner.clean_data(self.data, missing_strategy=missing_method)
            self.result_text.insert(tk.END, f"数据清洗完成，剩余 {len(self.cleaned_data)} 行\n")
              # 显示数据质量报告
            quality_report_dict = self.data_validator.generate_quality_report(self.cleaned_data)
            self.result_text.insert(tk.END, "\n数据质量报告:\n")
            self.result_text.insert(tk.END, f"数据形状: {quality_report_dict['data_shape']}\n")
            self.result_text.insert(tk.END, f"质量分数: {quality_report_dict['quality_score']:.2f}\n")
            self.result_text.insert(tk.END, f"是否高质量: {'是' if quality_report_dict['summary']['is_high_quality'] else '否'}\n")
            self.result_text.insert(tk.END, f"问题总数: {quality_report_dict['summary']['total_issues']}\n")
            
            self.save_button.config(state='normal')
            messagebox.showinfo("完成", "数据处理完成！")
            
        except Exception as e:
            messagebox.showerror("错误", f"数据处理失败: {str(e)}")
        finally:
            self.process_button.config(state='normal')
    
    def save_processed_data(self):
        """保存处理后的数据"""
        if not hasattr(self, 'cleaned_data'):
            messagebox.showwarning("警告", "没有可保存的数据！")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="保存处理后的数据",
            defaultextension=".csv",
            filetypes=[
                ("CSV files", "*.csv"),
                ("All files", "*.*")
            ],
            initialdir=os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'processed')
        )
        
        if file_path:
            try:
                self.cleaned_data.to_csv(file_path, index=False, encoding='utf-8-sig')
                messagebox.showinfo("成功", f"数据已保存到: {file_path}")
            except Exception as e:
                messagebox.showerror("错误", f"保存失败: {str(e)}")
