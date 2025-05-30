#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试可视化功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.data_processor.data_loader import DataLoader
from src.visualizer.basic_charts import BasicCharts
from src.visualizer.advanced_charts import AdvancedCharts

def test_visualization():
    """测试可视化功能"""
    print("开始测试可视化功能...")
    
    # 加载数据
    data_loader = DataLoader()
    
    # 查找最新的处理后数据文件
    processed_dir = 'data/processed'
    if os.path.exists(processed_dir):
        files = [f for f in os.listdir(processed_dir) if f.endswith('.csv')]
        if files:
            latest_file = max(files)
            data_file = os.path.join(processed_dir, latest_file)
            print(f"使用数据文件: {data_file}")
            
            # 加载数据
            df = data_loader.load_csv(data_file)
            if df is not None and not df.empty:
                print(f"数据加载成功，共 {len(df)} 条记录")
                
                # 创建可视化对象
                basic_charts = BasicCharts()
                advanced_charts = AdvancedCharts()
                
                # 创建输出目录
                output_dir = 'visualization_output'
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                
                print("\n开始生成基础图表...")
                
                # 测试基础图表
                try:
                    # AQI趋势图
                    if 'AQI' in df.columns and 'Date' in df.columns:
                        basic_charts.plot_aqi_trend(df, save_path=f'{output_dir}/aqi_trend.png')
                        print("✓ AQI趋势图生成成功")
                    
                    # 城市污染物对比
                    if 'City' in df.columns and 'PM2.5' in df.columns:
                        top_cities = df.groupby('City')['PM2.5'].mean().nlargest(10).index.tolist()
                        basic_charts.plot_city_pollution_comparison(df, cities=top_cities, 
                                                                  save_path=f'{output_dir}/city_comparison.png')
                        print("✓ 城市污染物对比图生成成功")
                    
                    # 空气质量等级分布
                    if 'Quality_Level' in df.columns:
                        basic_charts.plot_quality_level_distribution(df, save_path=f'{output_dir}/quality_distribution.png')
                        print("✓ 空气质量等级分布图生成成功")
                    
                    # 污染物相关性散点图
                    if 'PM2.5' in df.columns and 'PM10' in df.columns:
                        basic_charts.plot_pollutant_scatter(df, 'PM2.5', 'PM10', 
                                                           save_path=f'{output_dir}/pollutant_scatter.png')
                        print("✓ 污染物相关性散点图生成成功")
                
                except Exception as e:
                    print(f"基础图表生成出错: {e}")
                
                print("\n开始生成高级图表...")
                
                # 测试高级图表
                try:
                    # 污染物热力图
                    pollutant_cols = [col for col in ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3'] if col in df.columns]
                    if len(pollutant_cols) >= 2:
                        advanced_charts.plot_pollutant_heatmap(df[pollutant_cols], 
                                                             save_path=f'{output_dir}/pollutant_heatmap.png')
                        print("✓ 污染物热力图生成成功")
                    
                    # 城市空气质量雷达图
                    if 'City' in df.columns and len(pollutant_cols) >= 3:
                        cities = df['City'].value_counts().head(3).index.tolist()
                        advanced_charts.plot_city_radar_chart(df, cities, pollutant_cols,
                                                            save_path=f'{output_dir}/city_radar.png')
                        print("✓ 城市空气质量雷达图生成成功")
                    
                    # 污染物箱线图
                    if len(pollutant_cols) >= 1:
                        advanced_charts.plot_pollutant_boxplot(df, pollutant_cols,
                                                             save_path=f'{output_dir}/pollutant_boxplot.png')
                        print("✓ 污染物箱线图生成成功")
                
                except Exception as e:
                    print(f"高级图表生成出错: {e}")
                
                print(f"\n可视化测试完成！图表已保存到 {output_dir} 目录")
                
            else:
                print("数据文件为空或加载失败")
        else:
            print("未找到处理后的数据文件")
    else:
        print("processed 目录不存在")

if __name__ == "__main__":
    test_visualization()
