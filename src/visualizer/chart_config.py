#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图表样式配置模块
统一图表样式和配色方案，实现图表保存功能
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime
import os
from typing import Optional, List, Dict, Any, Tuple

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

class ChartStyleConfig:
    """图表样式配置类"""
    
    def __init__(self):
        """初始化样式配置"""
        # 主题色彩配置
        self.color_palettes = {
            'primary': ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                       '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'],
            'air_quality': {
                '优': '#00e400',
                '良': '#ffff00', 
                '轻度污染': '#ff7e00',
                '中度污染': '#ff0000',
                '重度污染': '#8f3f97',
                '严重污染': '#7e0023'
            },
            'gradient': ['#e8f4fd', '#b3d7f7', '#7fb8f0', '#4b9ae8', '#177ce0'],
            'heat': ['#fff5f0', '#fee0d2', '#fcbba1', '#fc9272', '#fb6a4a', '#ef3b2c', '#cb181d', '#a50f15'],
            'cool': ['#f7fcfd', '#e5f5f9', '#ccece6', '#99d8c9', '#66c2a4', '#41ae76', '#238b45', '#006d2c']
        }
        
        # 字体配置
        self.fonts = {
            'title': {'family': 'Microsoft YaHei', 'size': 16, 'weight': 'bold'},
            'label': {'family': 'Microsoft YaHei', 'size': 12},
            'tick': {'family': 'Microsoft YaHei', 'size': 10},
            'legend': {'family': 'Microsoft YaHei', 'size': 10}
        }
        
        # 图形尺寸配置
        self.figure_sizes = {
            'small': (8, 6),
            'medium': (10, 8),
            'large': (12, 9),
            'wide': (14, 8),
            'square': (10, 10)
        }
        
        # DPI设置
        self.dpi = 300
        
        # 设置默认样式
        self.setup_default_style()
    
    def setup_default_style(self):
        """设置默认图表样式"""
        # 设置matplotlib样式
        plt.style.use('seaborn-v0_8-whitegrid')
        
        # 全局字体设置
        plt.rcParams.update({
            'font.sans-serif': ['Microsoft YaHei', 'SimHei'],
            'axes.unicode_minus': False,
            'figure.dpi': 100,
            'savefig.dpi': self.dpi,
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': 'gray',
            'axes.linewidth': 0.8,
            'grid.alpha': 0.3,
            'grid.linewidth': 0.5
        })
        
        # 设置seaborn样式
        sns.set_palette(self.color_palettes['primary'])
        sns.set_context("notebook", rc={"font.size": 12})
    
    def get_colors(self, palette: str = 'primary') -> List[str]:
        """
        获取颜色配置
        
        Args:
            palette: 调色板名称
            
        Returns:
            颜色列表
        """
        return self.color_palettes.get(palette, self.color_palettes['primary'])
    
    def get_quality_color(self, quality: str) -> str:
        """
        获取空气质量等级对应的颜色
        
        Args:
            quality: 空气质量等级
            
        Returns:
            颜色代码
        """
        return self.color_palettes['air_quality'].get(quality, '#cccccc')
    
    def apply_title_style(self, title: str, fontsize: int = None) -> None:
        """
        应用标题样式
        
        Args:
            title: 标题文本
            fontsize: 字体大小
        """
        size = fontsize or self.fonts['title']['size']
        plt.title(title, 
                 fontsize=size,
                 fontweight=self.fonts['title']['weight'],
                 pad=20)
    
    def apply_label_style(self, xlabel: str = None, ylabel: str = None) -> None:
        """
        应用轴标签样式
        
        Args:
            xlabel: x轴标签
            ylabel: y轴标签
        """
        if xlabel:
            plt.xlabel(xlabel, fontsize=self.fonts['label']['size'])
        if ylabel:
            plt.ylabel(ylabel, fontsize=self.fonts['label']['size'])
    
    def apply_legend_style(self, loc: str = 'best', **kwargs) -> None:
        """
        应用图例样式
        
        Args:
            loc: 图例位置
            **kwargs: 其他图例参数
        """
        default_kwargs = {
            'fontsize': self.fonts['legend']['size'],
            'frameon': True,
            'shadow': True,
            'fancybox': True,
            'framealpha': 0.9
        }
        default_kwargs.update(kwargs)
        plt.legend(loc=loc, **default_kwargs)
    
    def save_chart(self, filename: str, output_dir: str, 
                   format: str = 'png', **kwargs) -> str:
        """
        保存图表
        
        Args:
            filename: 文件名
            output_dir: 输出目录
            format: 文件格式
            **kwargs: 其他保存参数
            
        Returns:
            保存路径
        """
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 构建完整文件名
        if not filename.endswith(f'.{format}'):
            filename = f"{filename}.{format}"
        
        save_path = os.path.join(output_dir, filename)
        
        # 默认保存参数
        default_kwargs = {
            'dpi': self.dpi,
            'bbox_inches': 'tight',
            'facecolor': 'white',
            'edgecolor': 'none'
        }
        default_kwargs.update(kwargs)
        
        # 保存图表
        plt.savefig(save_path, **default_kwargs)
        
        return save_path


class ChartManager:
    """图表管理器"""
    
    def __init__(self, output_base_dir: str = "charts"):
        """
        初始化图表管理器
        
        Args:
            output_base_dir: 基础输出目录
        """
        self.output_base_dir = output_base_dir
        self.style_config = ChartStyleConfig()
        
        # 创建子目录
        self.subdirs = {
            'basic': os.path.join(output_base_dir, 'basic'),
            'advanced': os.path.join(output_base_dir, 'advanced'),
            'interactive': os.path.join(output_base_dir, 'interactive'),
            'reports': os.path.join(output_base_dir, 'reports')
        }
        
        for subdir in self.subdirs.values():
            os.makedirs(subdir, exist_ok=True)
    
    def create_styled_figure(self, size: str = 'medium') -> Tuple[plt.Figure, plt.Axes]:
        """
        创建带样式的图形
        
        Args:
            size: 图形尺寸
            
        Returns:
            图形和轴对象
        """
        figsize = self.style_config.figure_sizes.get(size, (10, 8))
        fig, ax = plt.subplots(figsize=figsize)
        
        # 应用样式
        ax.grid(True, alpha=0.3)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        return fig, ax
    
    def save_current_chart(self, filename: str, category: str = 'basic', 
                          format: str = 'png') -> str:
        """
        保存当前图表
        
        Args:
            filename: 文件名
            category: 图表类别
            format: 文件格式
            
        Returns:
            保存路径
        """
        output_dir = self.subdirs.get(category, self.subdirs['basic'])
        return self.style_config.save_chart(filename, output_dir, format)
    
    def generate_chart_summary(self) -> Dict[str, Any]:
        """
        生成图表汇总信息
        
        Returns:
            汇总信息字典
        """
        summary = {
            'total_charts': 0,
            'categories': {},
            'formats': {},
            'creation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        for category, subdir in self.subdirs.items():
            if os.path.exists(subdir):
                files = os.listdir(subdir)
                chart_files = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.svg', '.pdf', '.html'))]
                
                summary['categories'][category] = len(chart_files)
                summary['total_charts'] += len(chart_files)
                
                # 统计文件格式
                for file in chart_files:
                    ext = file.split('.')[-1].lower()
                    summary['formats'][ext] = summary['formats'].get(ext, 0) + 1
        
        return summary
    
    def create_summary_report(self, save_path: Optional[str] = None) -> str:
        """
        创建图表汇总报告
        
        Args:
            save_path: 报告保存路径
            
        Returns:
            报告内容
        """
        summary = self.generate_chart_summary()
        
        report = f"""
# 图表生成汇总报告

## 基本信息
- 生成时间: {summary['creation_time']}
- 图表总数: {summary['total_charts']}

## 分类统计
"""
        
        for category, count in summary['categories'].items():
            report += f"- {category}: {count} 个图表\n"
        
        report += "\n## 格式统计\n"
        for format_type, count in summary['formats'].items():
            report += f"- {format_type.upper()}: {count} 个文件\n"
        
        report += f"""
## 目录结构
- 基础图表: {self.subdirs['basic']}
- 高级图表: {self.subdirs['advanced']}  
- 交互式图表: {self.subdirs['interactive']}
- 报告图表: {self.subdirs['reports']}

## 图表说明
1. 基础图表包含折线图、柱状图、饼图、散点图等
2. 高级图表包含热力图、箱线图、雷达图等
3. 交互式图表使用Plotly生成，支持缩放、筛选等操作
4. 所有图表均使用统一的样式配置和配色方案

生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}
"""
        
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"汇总报告已保存到: {save_path}")
        
        return report


def main():
    """测试图表样式和管理功能"""
    # 创建图表管理器
    manager = ChartManager("../../charts")
    
    # 测试样式配置
    style = manager.style_config
    
    # 创建测试图表
    fig, ax = manager.create_styled_figure('medium')
    
    # 生成测试数据
    x = np.linspace(0, 10, 100)
    y1 = np.sin(x)
    y2 = np.cos(x)
    
    # 绘制图表
    colors = style.get_colors('primary')
    ax.plot(x, y1, color=colors[0], linewidth=2, label='sin(x)')
    ax.plot(x, y2, color=colors[1], linewidth=2, label='cos(x)')
    
    # 应用样式
    style.apply_title_style('测试图表样式')
    style.apply_label_style('X轴', 'Y轴') 
    style.apply_legend_style()
    
    # 保存图表
    save_path = manager.save_current_chart('test_style', 'basic')
    print(f"测试图表已保存到: {save_path}")
    
    plt.show()
    
    # 生成汇总报告
    report_path = os.path.join(manager.subdirs['reports'], 'chart_summary.md')
    manager.create_summary_report(report_path)
    
    print("图表样式配置测试完成！")


if __name__ == "__main__":
    main()
