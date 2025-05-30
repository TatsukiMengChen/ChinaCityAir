#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础图表可视化模块
实现折线图、柱状图、饼图、散点图等基础图表
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys
from typing import Optional, List, Dict, Any

# 添加父目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# 导入字体配置
try:
    from utils.font_config import setup_chinese_font
    # 设置中文字体
    setup_chinese_font()
except ImportError:
    # 备用字体设置
    plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
    plt.rcParams['axes.unicode_minus'] = False

class BasicCharts:
    """基础图表类"""
    
    def __init__(self, output_dir: str = "charts"):
        """
        初始化基础图表类
        
        Args:
            output_dir: 图表保存目录
        """
        self.output_dir = output_dir
        self.colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                      '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置图表样式
        sns.set_style("whitegrid")
        plt.style.use('seaborn-v0_8')
        
        # 确保中文字体设置
        try:
            setup_chinese_font()
        except:
            plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
            plt.rcParams['axes.unicode_minus'] = False
    
    def plot_time_series(self, data: pd.DataFrame, 
                        columns: List[str],
                        time_column: str = 'timestamp',
                        title: str = "空气质量时间序列图",
                        save_name: Optional[str] = None) -> None:
        """
        绘制时间序列折线图
        
        Args:
            data: 数据DataFrame
            columns: 要绘制的列名列表
            time_column: 时间列名
            title: 图表标题
            save_name: 保存文件名
        """
        plt.figure(figsize=(12, 8))
        
        # 确保时间列是datetime类型
        if data[time_column].dtype == 'object':
            data[time_column] = pd.to_datetime(data[time_column])
        
        # 绘制多条线
        for i, column in enumerate(columns):
            plt.plot(data[time_column], data[column], 
                    label=column, color=self.colors[i % len(self.colors)],
                    linewidth=2, marker='o', markersize=4)
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('时间', fontsize=12)
        plt.ylabel('浓度值', fontsize=12)
        plt.legend(loc='upper right', frameon=True, shadow=True)
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"时间序列图已保存到: {save_path}")
        
        plt.show()
    
    def plot_bar_chart(self, data: pd.DataFrame,
                      x_column: str,
                      y_column: str,
                      title: str = "柱状图",
                      top_n: int = 20,
                      save_name: Optional[str] = None) -> None:
        """
        绘制柱状图
        
        Args:
            data: 数据DataFrame
            x_column: x轴列名
            y_column: y轴列名
            title: 图表标题
            top_n: 显示前N个数据
            save_name: 保存文件名
        """
        plt.figure(figsize=(14, 8))
        
        # 排序并取前N个
        sorted_data = data.nlargest(top_n, y_column)
        
        bars = plt.bar(range(len(sorted_data)), sorted_data[y_column], 
                      color=self.colors[0], alpha=0.8, edgecolor='black', linewidth=0.5)
        
        # 添加数值标签
        for i, bar in enumerate(bars):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=10)
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.xlabel(x_column, fontsize=12)
        plt.ylabel(y_column, fontsize=12)
        plt.xticks(range(len(sorted_data)), sorted_data[x_column], rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"柱状图已保存到: {save_path}")
        
        plt.show()
    
    def plot_pie_chart(self, data: pd.DataFrame,
                      value_column: str,
                      label_column: str,
                      title: str = "饼图",
                      save_name: Optional[str] = None) -> None:
        """
        绘制饼图
        
        Args:
            data: 数据DataFrame
            value_column: 数值列名
            label_column: 标签列名
            title: 图表标题
            save_name: 保存文件名
        """
        plt.figure(figsize=(10, 8))
        
        # 准备数据
        sizes = data[value_column].values
        labels = data[label_column].values
        
        # 绘制饼图
        wedges, texts, autotexts = plt.pie(sizes, labels=labels, autopct='%1.1f%%',
                                          colors=self.colors, startangle=90,
                                          explode=[0.05] * len(sizes))
        
        # 美化文本
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.axis('equal')
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"饼图已保存到: {save_path}")
        
        plt.show()
    
    def plot_scatter(self, data: pd.DataFrame,
                    x_column: str,
                    y_column: str,
                    title: str = "散点图",
                    color_column: Optional[str] = None,
                    save_name: Optional[str] = None) -> None:
        """
        绘制散点图
        
        Args:
            data: 数据DataFrame
            x_column: x轴列名
            y_column: y轴列名
            title: 图表标题
            color_column: 颜色映射列名
            save_name: 保存文件名
        """
        plt.figure(figsize=(10, 8))
        
        if color_column and color_column in data.columns:
            # 如果颜色列是文本类型，创建颜色映射
            if data[color_column].dtype == 'object':
                unique_values = data[color_column].unique()
                color_map = {val: self.colors[i % len(self.colors)] for i, val in enumerate(unique_values)}
                colors = [color_map[val] for val in data[color_column]]
                scatter = plt.scatter(data[x_column], data[y_column], 
                                    c=colors, alpha=0.7, s=50, 
                                    edgecolors='black', linewidth=0.5)
                
                # 创建图例
                from matplotlib.patches import Patch
                legend_elements = [Patch(facecolor=color_map[val], label=val) for val in unique_values]
                plt.legend(handles=legend_elements, title=color_column, loc='upper right')
            else:
                # 数值类型，使用colormap
                scatter = plt.scatter(data[x_column], data[y_column], 
                                    c=data[color_column], cmap='viridis',
                                    alpha=0.7, s=50, edgecolors='black', linewidth=0.5)
                plt.colorbar(scatter, label=color_column)
        else:
            plt.scatter(data[x_column], data[y_column], 
                       color=self.colors[0], alpha=0.7, s=50,
                       edgecolors='black', linewidth=0.5)
        
        # 添加趋势线
        z = np.polyfit(data[x_column], data[y_column], 1)
        p = np.poly1d(z)
        plt.plot(data[x_column], p(data[x_column]), "r--", alpha=0.8, linewidth=2)
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.xlabel(x_column, fontsize=12)
        plt.ylabel(y_column, fontsize=12)
        plt.grid(True, alpha=0.3)
        
        # 添加相关系数
        correlation = data[x_column].corr(data[y_column])
        plt.text(0.05, 0.95, f'相关系数: {correlation:.3f}', 
                transform=plt.gca().transAxes, fontsize=12,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        
        plt.tight_layout()
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"散点图已保存到: {save_path}")
        
        plt.show()
    
    def plot_multi_city_comparison(self, data: pd.DataFrame,
                                  cities: List[str],
                                  pollutant: str = 'aqi',
                                  title: str = "多城市污染物对比",
                                  save_name: Optional[str] = None) -> None:
        """
        绘制多城市污染物对比图
        
        Args:
            data: 数据DataFrame
            cities: 城市列表
            pollutant: 污染物名称
            title: 图表标题
            save_name: 保存文件名
        """
        plt.figure(figsize=(12, 8))
        
        # 筛选指定城市的数据
        city_data = data[data['city'].isin(cities)]
        
        # 按城市分组计算平均值
        avg_data = city_data.groupby('city')[pollutant].mean().reset_index()
        avg_data = avg_data.sort_values(pollutant, ascending=False)
        
        bars = plt.bar(avg_data['city'], avg_data[pollutant], 
                      color=self.colors[:len(avg_data)], alpha=0.8,
                      edgecolor='black', linewidth=0.5)
        
        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=10)
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('城市', fontsize=12)
        plt.ylabel(f'{pollutant.upper()} 平均值', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"多城市对比图已保存到: {save_path}")
        
        plt.show()
    
    def plot_quality_distribution(self, data: pd.DataFrame,
                                 title: str = "空气质量等级分布",
                                 save_name: Optional[str] = None) -> None:
        """
        绘制空气质量等级分布饼图
        
        Args:
            data: 数据DataFrame
            title: 图表标题
            save_name: 保存文件名
        """
        plt.figure(figsize=(10, 8))
        
        # 统计各质量等级的数量
        quality_counts = data['quality'].value_counts()
        
        # 定义质量等级对应的颜色
        quality_colors = {
            '优': '#00e400',
            '良': '#ffff00',
            '轻度污染': '#ff7e00',
            '中度污染': '#ff0000',
            '重度污染': '#8f3f97',
            '严重污染': '#7e0023'
        }
        
        colors = [quality_colors.get(quality, self.colors[i % len(self.colors)]) 
                 for i, quality in enumerate(quality_counts.index)]
        
        wedges, texts, autotexts = plt.pie(quality_counts.values, 
                                          labels=quality_counts.index,
                                          autopct='%1.1f%%',
                                          colors=colors,
                                          startangle=90,
                                          explode=[0.05] * len(quality_counts))
        
        # 美化文本
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(11)
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.axis('equal')
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"空气质量分布图已保存到: {save_path}")
        
        plt.show()


def main():
    """测试基础图表功能"""
    # 读取数据
    data_path = "../../data/processed/cleaned_air_quality_20250530_164153.csv"
    if os.path.exists(data_path):
        data = pd.read_csv(data_path)
        
        # 创建图表实例
        charts = BasicCharts("../../charts/basic")
        
        # 测试柱状图
        charts.plot_bar_chart(data, 'city', 'aqi', 
                             title='各城市AQI排名', 
                             save_name='city_aqi_ranking.png')
        
        # 测试散点图
        charts.plot_scatter(data, 'pm25', 'aqi', 
                           title='PM2.5与AQI相关性分析',
                           save_name='pm25_aqi_correlation.png')
        
        # 测试空气质量分布图
        charts.plot_quality_distribution(data, 
                                        title='空气质量等级分布',
                                        save_name='quality_distribution.png')
        
        print("基础图表测试完成！")
    else:
        print(f"数据文件不存在: {data_path}")


if __name__ == "__main__":
    main()
