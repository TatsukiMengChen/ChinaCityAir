#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高级图表可视化模块
实现热力图、箱线图、雷达图、交互式图表等高级可视化
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo
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

class AdvancedCharts:
    """高级图表类"""
    
    def __init__(self, output_dir: str = "charts/advanced"):
        """
        初始化高级图表类
        
        Args:
            output_dir: 图表保存目录
        """
        self.output_dir = output_dir
        
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
    
    def plot_correlation_heatmap(self, data: pd.DataFrame,
                                columns: List[str],
                                title: str = "污染物相关性热力图",
                                save_name: Optional[str] = None) -> None:
        """
        绘制相关性热力图
        
        Args:
            data: 数据DataFrame
            columns: 要分析的列名列表
            title: 图表标题
            save_name: 保存文件名
        """
        plt.figure(figsize=(10, 8))
        
        # 计算相关系数矩阵
        correlation_matrix = data[columns].corr()
        
        # 创建热力图
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool))
        sns.heatmap(correlation_matrix, mask=mask, annot=True, cmap='RdYlBu_r',
                   square=True, linewidths=0.5, cbar_kws={"shrink": .8},
                   fmt='.3f', annot_kws={'size': 10})
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"相关性热力图已保存到: {save_path}")
        
        plt.show()
    
    def plot_time_heatmap(self, data: pd.DataFrame,
                         time_column: str = 'timestamp',
                         value_column: str = 'aqi',
                         title: str = "时间-污染物热力图",
                         save_name: Optional[str] = None) -> None:
        """
        绘制时间-污染物热力图
        
        Args:
            data: 数据DataFrame
            time_column: 时间列名
            value_column: 数值列名
            title: 图表标题
            save_name: 保存文件名
        """
        # 确保时间列是datetime类型
        if data[time_column].dtype == 'object':
            data[time_column] = pd.to_datetime(data[time_column])
        
        # 提取时间特征
        data_copy = data.copy()
        data_copy['hour'] = data_copy[time_column].dt.hour
        data_copy['day'] = data_copy[time_column].dt.day
        
        # 创建透视表
        pivot_table = data_copy.pivot_table(values=value_column, 
                                           index='day', 
                                           columns='hour', 
                                           aggfunc='mean')
        
        plt.figure(figsize=(14, 8))
        sns.heatmap(pivot_table, cmap='YlOrRd', annot=False, fmt='.1f',
                   cbar_kws={'label': value_column.upper()})
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('小时', fontsize=12)
        plt.ylabel('日期', fontsize=12)
        plt.tight_layout()
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"时间热力图已保存到: {save_path}")
        
        plt.show()
    
    def plot_boxplot(self, data: pd.DataFrame,
                    columns: List[str],
                    title: str = "污染物浓度分布箱线图",
                    save_name: Optional[str] = None) -> None:
        """
        绘制箱线图
        
        Args:
            data: 数据DataFrame
            columns: 要绘制的列名列表
            title: 图表标题
            save_name: 保存文件名
        """
        plt.figure(figsize=(12, 8))
        
        # 准备数据
        plot_data = []
        labels = []
        for col in columns:
            plot_data.append(data[col].dropna())
            labels.append(col.upper())
        
        # 创建箱线图
        box_plot = plt.boxplot(plot_data, labels=labels, patch_artist=True,
                              showmeans=True, meanline=True)
        
        # 设置颜色
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                 '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        
        for patch, color in zip(box_plot['boxes'], colors):
            patch.set_facecolor(color)
            patch.set_alpha(0.7)
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.ylabel('浓度值', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"箱线图已保存到: {save_path}")
        
        plt.show()
    
    def plot_radar_chart(self, data: pd.DataFrame,
                        cities: List[str],
                        metrics: List[str],
                        title: str = "城市空气质量综合对比雷达图",
                        save_name: Optional[str] = None) -> None:
        """
        绘制雷达图
        
        Args:
            data: 数据DataFrame
            cities: 城市列表
            metrics: 指标列表
            title: 图表标题
            save_name: 保存文件名
        """
        # 筛选城市数据并计算平均值
        city_data = data[data['city'].isin(cities)]
        avg_data = city_data.groupby('city')[metrics].mean()
        
        # 数据标准化到0-1范围
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
        normalized_data = pd.DataFrame(
            scaler.fit_transform(avg_data),
            columns=avg_data.columns,
            index=avg_data.index
        )
        
        # 计算角度
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))  # 闭合图形
        
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for i, city in enumerate(cities[:5]):  # 最多显示5个城市
            if city in normalized_data.index:
                values = normalized_data.loc[city].values
                values = np.concatenate((values, [values[0]]))  # 闭合图形
                
                ax.plot(angles, values, 'o-', linewidth=2, 
                       label=city, color=colors[i % len(colors)])
                ax.fill(angles, values, alpha=0.25, color=colors[i % len(colors)])
        
        # 设置标签
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([metric.upper() for metric in metrics])
        ax.set_ylim(0, 1)
        ax.set_yticks([0.2, 0.4, 0.6, 0.8, 1.0])
        ax.set_yticklabels(['0.2', '0.4', '0.6', '0.8', '1.0'])
        ax.grid(True)
        
        plt.title(title, fontsize=16, fontweight='bold', pad=30)
        plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0))
        plt.tight_layout()
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"雷达图已保存到: {save_path}")
        
        plt.show()
    
    def plot_interactive_scatter(self, data: pd.DataFrame,
                               x_column: str,
                               y_column: str,
                               color_column: str = 'city',
                               size_column: Optional[str] = None,
                               title: str = "交互式散点图",
                               save_name: Optional[str] = None) -> None:
        """
        创建交互式散点图
        
        Args:
            data: 数据DataFrame
            x_column: x轴列名
            y_column: y轴列名
            color_column: 颜色映射列名
            size_column: 大小映射列名
            title: 图表标题
            save_name: 保存文件名
        """
        fig = px.scatter(data, x=x_column, y=y_column, 
                        color=color_column, size=size_column,
                        hover_data=['city', 'aqi', 'quality'],
                        title=title,
                        labels={x_column: x_column.upper(),
                               y_column: y_column.upper()})
        
        fig.update_layout(
            font=dict(family="Microsoft YaHei", size=12),
            title_font_size=16,
            width=800,
            height=600
        )
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            fig.write_html(save_path)
            print(f"交互式散点图已保存到: {save_path}")
        
        fig.show()
    
    def plot_interactive_time_series(self, data: pd.DataFrame,
                                   time_column: str = 'timestamp',
                                   value_columns: List[str] = ['aqi'],
                                   title: str = "交互式时间序列图",
                                   save_name: Optional[str] = None) -> None:
        """
        创建交互式时间序列图
        
        Args:
            data: 数据DataFrame
            time_column: 时间列名
            value_columns: 数值列名列表
            title: 图表标题
            save_name: 保存文件名
        """
        # 确保时间列是datetime类型
        if data[time_column].dtype == 'object':
            data[time_column] = pd.to_datetime(data[time_column])
        
        fig = go.Figure()
        
        for column in value_columns:
            fig.add_trace(go.Scatter(
                x=data[time_column],
                y=data[column],
                mode='lines+markers',
                name=column.upper(),
                line=dict(width=2),
                marker=dict(size=4)
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="时间",
            yaxis_title="数值",
            font=dict(family="Microsoft YaHei", size=12),
            title_font_size=16,
            hovermode='x unified',
            width=900,
            height=600
        )
        
        fig.update_xaxis(showgrid=True)
        fig.update_yaxis(showgrid=True)
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            fig.write_html(save_path)
            print(f"交互式时间序列图已保存到: {save_path}")
        
        fig.show()
    
    def plot_geographic_map(self, data: pd.DataFrame,
                          city_coords: Dict[str, tuple],
                          value_column: str = 'aqi',
                          title: str = "城市空气质量地理分布图",
                          save_name: Optional[str] = None) -> None:
        """
        创建地理分布地图
        
        Args:
            data: 数据DataFrame
            city_coords: 城市坐标字典 {city_name: (lat, lon)}
            value_column: 数值列名
            title: 图表标题
            save_name: 保存文件名
        """
        # 添加坐标信息
        data_with_coords = data.copy()
        data_with_coords['lat'] = data_with_coords['city'].map(
            lambda x: city_coords.get(x, (39.9, 116.4))[0])
        data_with_coords['lon'] = data_with_coords['city'].map(
            lambda x: city_coords.get(x, (39.9, 116.4))[1])
        
        # 按城市分组取平均值
        avg_data = data_with_coords.groupby('city').agg({
            value_column: 'mean',
            'lat': 'first',
            'lon': 'first',
            'quality': 'first'
        }).reset_index()
        
        fig = px.scatter_mapbox(
            avg_data,
            lat="lat",
            lon="lon",
            size=value_column,
            color=value_column,
            hover_name="city",
            hover_data={'quality': True, value_column: ':.1f'},
            color_continuous_scale="Reds",
            size_max=30,
            zoom=3,
            title=title
        )
        
        fig.update_layout(
            mapbox_style="open-street-map",
            font=dict(family="Microsoft YaHei", size=12),
            title_font_size=16,
            width=900,
            height=700
        )
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            fig.write_html(save_path)
            print(f"地理分布图已保存到: {save_path}")
        
        fig.show()
    
    def plot_pollution_dashboard(self, data: pd.DataFrame,
                               save_name: Optional[str] = None) -> None:
        """
        创建综合仪表板
        
        Args:
            data: 数据DataFrame
            save_name: 保存文件名
        """
        # 创建子图
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('AQI分布', 'PM2.5与AQI关系', '空气质量等级占比', '各污染物对比'),
            specs=[[{"type": "histogram"}, {"type": "scatter"}],
                   [{"type": "pie"}, {"type": "bar"}]]
        )
        
        # AQI分布直方图
        fig.add_trace(
            go.Histogram(x=data['aqi'], name='AQI分布', nbinsx=20),
            row=1, col=1
        )
        
        # PM2.5与AQI散点图
        fig.add_trace(
            go.Scatter(x=data['pm25'], y=data['aqi'], mode='markers',
                      name='PM2.5 vs AQI', marker=dict(opacity=0.7)),
            row=1, col=2
        )
        
        # 空气质量等级饼图
        quality_counts = data['quality'].value_counts()
        fig.add_trace(
            go.Pie(labels=quality_counts.index, values=quality_counts.values,
                   name="空气质量等级"),
            row=2, col=1
        )
        
        # 各污染物平均值柱状图
        pollutants = ['pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
        avg_values = [data[col].mean() for col in pollutants if col in data.columns]
        valid_pollutants = [col for col in pollutants if col in data.columns]
        
        fig.add_trace(
            go.Bar(x=valid_pollutants, y=avg_values, name="平均浓度"),
            row=2, col=2
        )
        
        fig.update_layout(
            title="空气质量综合仪表板",
            font=dict(family="Microsoft YaHei", size=10),
            height=800,
            showlegend=False
        )
        
        if save_name:
            save_path = os.path.join(self.output_dir, save_name)
            fig.write_html(save_path)
            print(f"综合仪表板已保存到: {save_path}")
        
        fig.show()


def main():
    """测试高级图表功能"""
    # 读取数据
    data_path = "../../data/processed/cleaned_air_quality_20250530_164153.csv"
    if os.path.exists(data_path):
        data = pd.read_csv(data_path)
        
        # 创建图表实例
        charts = AdvancedCharts("../../charts/advanced")
        
        # 测试相关性热力图
        numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
        available_columns = [col for col in numeric_columns if col in data.columns]
        
        if len(available_columns) > 1:
            charts.plot_correlation_heatmap(data, available_columns,
                                           title='污染物相关性分析',
                                           save_name='correlation_heatmap.png')
        
        # 测试箱线图
        charts.plot_boxplot(data, available_columns[:4],
                           title='主要污染物浓度分布',
                           save_name='pollutants_boxplot.png')
        
        # 测试交互式散点图
        charts.plot_interactive_scatter(data, 'pm25', 'aqi',
                                       title='PM2.5与AQI交互式分析',
                                       save_name='interactive_scatter.html')
        
        # 测试综合仪表板
        charts.plot_pollution_dashboard(data, save_name='dashboard.html')
        
        print("高级图表测试完成！")
    else:
        print(f"数据文件不存在: {data_path}")


if __name__ == "__main__":
    main()
