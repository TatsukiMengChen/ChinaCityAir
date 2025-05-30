#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的可视化测试脚本
"""

import matplotlib.pyplot as plt
import pandas as pd
import os
import sys

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei']
plt.rcParams['axes.unicode_minus'] = False

def test_simple_charts():
    """测试简单图表生成"""
    print("开始简单可视化测试...")
    
    # 创建输出目录
    output_dir = "visualization_output"
    os.makedirs(output_dir, exist_ok=True)
    
    # 读取数据
    data_file = "data/processed/cleaned_air_quality_20250530_164153.csv"
    if not os.path.exists(data_file):
        print(f"数据文件不存在: {data_file}")
        return
    
    try:
        data = pd.read_csv(data_file)
        print(f"数据加载成功，形状: {data.shape}")
        print(f"列名: {list(data.columns)}")
        print("数据预览:")
        print(data.head())
        
        # 1. 创建简单柱状图 - AQI对比
        plt.figure(figsize=(10, 6))
        plt.bar(data['city'], data['aqi'], color=['#1f77b4', '#ff7f0e', '#2ca02c'])
        plt.title('各城市AQI对比', fontsize=14, fontweight='bold')
        plt.xlabel('城市')
        plt.ylabel('AQI值')
        plt.xticks(rotation=45)
        
        # 添加数值标签
        for i, v in enumerate(data['aqi']):
            plt.text(i, v + 1, str(v), ha='center', va='bottom')
        
        plt.tight_layout()
        chart1_path = os.path.join(output_dir, 'city_aqi_comparison.png')
        plt.savefig(chart1_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ AQI对比图已保存: {chart1_path}")
        
        # 2. 创建PM2.5对比图
        plt.figure(figsize=(10, 6))
        plt.bar(data['city'], data['pm25'], color=['#d62728', '#9467bd', '#8c564b'])
        plt.title('各城市PM2.5浓度对比', fontsize=14, fontweight='bold')
        plt.xlabel('城市')
        plt.ylabel('PM2.5浓度 (μg/m³)')
        plt.xticks(rotation=45)
        
        # 添加数值标签
        for i, v in enumerate(data['pm25']):
            plt.text(i, v + 1, str(v), ha='center', va='bottom')
        
        plt.tight_layout()
        chart2_path = os.path.join(output_dir, 'city_pm25_comparison.png')
        plt.savefig(chart2_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ PM2.5对比图已保存: {chart2_path}")
        
        # 3. 创建空气质量等级饼图
        quality_counts = data['quality'].value_counts()
        plt.figure(figsize=(8, 8))
        colors = ['#00e400', '#ffff00', '#ff7e00'][:len(quality_counts)]
        
        wedges, texts, autotexts = plt.pie(quality_counts.values, 
                                          labels=quality_counts.index,
                                          autopct='%1.1f%%',
                                          colors=colors,
                                          startangle=90)
        
        plt.title('空气质量等级分布', fontsize=14, fontweight='bold')
        
        chart3_path = os.path.join(output_dir, 'quality_distribution.png')
        plt.savefig(chart3_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ 空气质量分布图已保存: {chart3_path}")
        
        # 4. 创建多污染物雷达图
        import numpy as np
        
        # 选择一个城市的数据作为示例
        city_data = data.iloc[0]
        pollutants = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'o3']
        values = [city_data[p] for p in pollutants]
        
        # 归一化数据到0-1范围以便在雷达图中显示
        max_values = [200, 150, 250, 50, 100, 200]  # 各污染物的最大参考值
        normalized_values = [v/max_v for v, max_v in zip(values, max_values)]
        
        # 创建雷达图
        angles = np.linspace(0, 2 * np.pi, len(pollutants), endpoint=False).tolist()
        normalized_values += normalized_values[:1]  # 闭合图形
        angles += angles[:1]
        
        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(projection='polar'))
        ax.plot(angles, normalized_values, 'o-', linewidth=2, color='#1f77b4')
        ax.fill(angles, normalized_values, alpha=0.25, color='#1f77b4')
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels([p.upper() for p in pollutants])
        ax.set_ylim(0, 1)
        ax.set_title(f'{city_data["city"]} 空气质量雷达图', fontsize=14, fontweight='bold', pad=20)
        ax.grid(True)
        
        chart4_path = os.path.join(output_dir, 'radar_chart.png')
        plt.savefig(chart4_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ 雷达图已保存: {chart4_path}")
        
        # 5. 创建污染物相关性散点图
        plt.figure(figsize=(10, 6))
        plt.scatter(data['pm25'], data['aqi'], s=100, alpha=0.7, c=['#1f77b4', '#ff7f0e', '#2ca02c'])
        
        # 添加城市标签
        for i, city in enumerate(data['city']):
            plt.annotate(city, (data['pm25'].iloc[i], data['aqi'].iloc[i]), 
                        xytext=(5, 5), textcoords='offset points')
        
        plt.title('PM2.5与AQI相关性分析', fontsize=14, fontweight='bold')
        plt.xlabel('PM2.5浓度 (μg/m³)')
        plt.ylabel('AQI值')
        plt.grid(True, alpha=0.3)
        
        chart5_path = os.path.join(output_dir, 'pm25_aqi_scatter.png')
        plt.savefig(chart5_path, dpi=300, bbox_inches='tight')
        plt.close()
        print(f"✓ 散点图已保存: {chart5_path}")
        
        print(f"\n✅ 所有图表生成完成！请查看 {output_dir} 目录")
        
        # 列出生成的文件
        print("\n生成的图表文件:")
        for file in os.listdir(output_dir):
            if file.endswith('.png'):
                print(f"  - {file}")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_charts()
