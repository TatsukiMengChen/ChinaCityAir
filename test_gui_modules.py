#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GUI模块接口测试脚本
验证所有修复的GUI模块是否正常工作
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime

# 添加项目根目录到路径
project_root = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, project_root)

def create_sample_data():
    """创建示例数据用于测试"""
    data = {
        'city': ['北京', '上海', '广州', '深圳', '杭州'] * 20,
        'aqi': np.random.randint(30, 200, 100),
        'pm25': np.random.randint(20, 150, 100),
        'pm10': np.random.randint(30, 200, 100),
        'so2': np.random.randint(5, 80, 100),
        'no2': np.random.randint(10, 120, 100),
        'co': np.random.uniform(0.3, 3.0, 100),
        'o3': np.random.randint(20, 250, 100),
        'quality': ['良'] * 100,
        'timestamp': pd.date_range('2024-01-01', periods=100, freq='H')
    }
    
    df = pd.DataFrame(data)
    
    # 根据AQI设置正确的质量等级
    def get_quality(aqi):
        if aqi <= 50:
            return '优'
        elif aqi <= 100:
            return '良'
        elif aqi <= 150:
            return '轻度污染'
        elif aqi <= 200:
            return '中度污染'
        elif aqi <= 300:
            return '重度污染'
        else:
            return '严重污染'
    
    df['quality'] = df['aqi'].apply(get_quality)
    
    return df

def test_analysis_module():
    """测试分析模块接口"""
    print("=" * 60)
    print("测试分析模块接口")
    print("=" * 60)
    
    try:
        from src.analyzer.statistical_analyzer import StatisticalAnalyzer
        from src.analyzer.advanced_analyzer import AdvancedAnalyzer
        
        # 创建示例数据
        df = create_sample_data()
        
        # 测试统计分析器
        stat_analyzer = StatisticalAnalyzer()
        stat_analyzer.data = df
        print("测试统计分析器方法:")
        
        # 测试基本统计
        stat_analyzer.data = df
        basic_stats = stat_analyzer.descriptive_statistics()
        print(f"✓ descriptive_statistics() - 返回字典，包含 {len(basic_stats)} 个统计量")
          # 测试质量分布
        stat_analyzer.data = df
        quality_dist = stat_analyzer.quality_distribution()
        print(f"✓ quality_distribution() - 返回字典，包含 {len(quality_dist)} 个质量等级")
        
        # 测试城市排名
        city_ranking = stat_analyzer.air_quality_ranking(top_n=10)
        print(f"✓ air_quality_ranking() - 返回DataFrame，形状: {city_ranking.shape}")
        
        # 测试污染物相关性
        correlation = stat_analyzer.correlation_analysis()
        print(f"✓ correlation_analysis() - 返回相关性矩阵，形状: {correlation.shape}")
        
        # 测试高级分析器
        advanced_analyzer = AdvancedAnalyzer()
        advanced_analyzer.data = df
        
        print("\n测试高级分析器方法:")
        
        # 测试地区分析
        regional_analysis = advanced_analyzer.regional_analysis()
        print(f"✓ regional_analysis() - 返回字典，包含 {len(regional_analysis)} 个项目")
        
        # 测试季节分析
        seasonal_analysis = advanced_analyzer.seasonal_analysis()
        print(f"✓ seasonal_analysis() - 返回字典，包含 {len(seasonal_analysis)} 个项目")
        
        # 测试城市排名
        top_cities = advanced_analyzer.top_cities_analysis()
        print(f"✓ top_cities_analysis() - 返回字典，包含 {len(top_cities)} 个项目")
        
        print("\n分析模块接口测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 分析模块接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_visualization_module():
    """测试可视化模块接口"""
    print("\n" + "=" * 60)
    print("测试可视化模块接口")
    print("=" * 60)
    
    try:
        from src.visualizer.basic_charts import BasicCharts
        from src.visualizer.advanced_charts import AdvancedCharts
        
        # 创建示例数据
        df = create_sample_data()
        
        # 测试基础图表
        basic_charts = BasicCharts()
        basic_charts.data = df
        
        print("测试基础图表方法:")
          # 创建输出目录
        output_dir = os.path.join(project_root, 'test_output')
        os.makedirs(output_dir, exist_ok=True)
        
        # 测试柱状图
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bar_chart_path = os.path.join(output_dir, f'bar_chart_{timestamp}.png')
        basic_charts.plot_bar_chart(
            data=df,
            x_column='city',
            y_column='aqi',
            title='城市AQI对比',
            save_name=f'bar_chart_{timestamp}.png'
        )
        print(f"✓ plot_bar_chart() - 已保存到: {bar_chart_path}")
        
        # 测试时间序列图（如果有时间列的话）
        if 'timestamp' in df.columns:
            line_chart_path = os.path.join(output_dir, f'time_series_{timestamp}.png')
            basic_charts.plot_time_series(
                data=df,
                columns=['aqi'],
                time_column='timestamp',
                title='AQI时间趋势',
                save_name=f'time_series_{timestamp}.png'
            )
            print(f"✓ plot_time_series() - 已保存到: {line_chart_path}")
        else:
            print("× 测试数据没有时间列，跳过时间序列图测试")
          # 测试空气质量分布饼图
        pie_chart_path = os.path.join(output_dir, f'quality_pie_{timestamp}.png')
        basic_charts.plot_quality_distribution(
            data=df,
            title='空气质量等级分布',
            save_name=f'quality_pie_{timestamp}.png'
        )
        print(f"✓ plot_quality_distribution() - 已保存到: {pie_chart_path}")
          # 测试高级图表
        advanced_charts = AdvancedCharts()
        
        print("\n测试高级图表方法:")
        
        # 测试相关性热力图
        numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
        available_columns = [col for col in numeric_columns if col in df.columns]
        heatmap_path = os.path.join(output_dir, f'heatmap_{timestamp}.png')
        advanced_charts.plot_correlation_heatmap(
            data=df,
            columns=available_columns,
            title='污染物相关性热力图',
            save_name=f'heatmap_{timestamp}.png'
        )
        print(f"✓ plot_correlation_heatmap() - 已保存到: {heatmap_path}")
        
        # 测试交互式散点图
        scatter_path = os.path.join(output_dir, f'scatter_{timestamp}.html')
        advanced_charts.plot_interactive_scatter(
            data=df,
            x_column='pm25',
            y_column='aqi',
            color_column='city',
            title='PM2.5与AQI交互式散点图',
            save_name=f'scatter_{timestamp}.html'
        )
        print(f"✓ plot_interactive_scatter() - 已保存到: {scatter_path}")
        
        # 测试雷达图
        cities = df['city'].unique()[:3]  # 取前3个城市
        metrics = ['aqi', 'pm25', 'pm10']
        available_metrics = [col for col in metrics if col in df.columns]
        radar_path = os.path.join(output_dir, f'radar_{timestamp}.png')
        advanced_charts.plot_radar_chart(
            data=df,
            cities=cities.tolist(),
            metrics=available_metrics,
            title='城市空气质量雷达图',
            save_name=f'radar_{timestamp}.png'
        )
        print(f"✓ plot_radar_chart() - 已保存到: {radar_path}")
        
        print("\n可视化模块接口测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 可视化模块接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_module():
    """测试数据处理模块接口"""
    print("\n" + "=" * 60)
    print("测试数据处理模块接口")
    print("=" * 60)
    
    try:
        from src.data_processor.data_cleaner import DataCleaner
        from src.data_processor.data_validator import DataValidator
        
        # 创建示例数据
        df = create_sample_data()
        
        # 测试数据清洗器
        data_cleaner = DataCleaner()
        
        print("测试数据清洗器方法:")
        
        # 测试数据清洗
        cleaned_data = data_cleaner.clean_data(df, missing_strategy='median')
        print(f"✓ clean_data() - 输入形状: {df.shape}, 输出形状: {cleaned_data.shape}")
        
        # 测试数据验证器
        data_validator = DataValidator()
        
        print("\n测试数据验证器方法:")
        
        # 测试质量报告生成
        quality_report = data_validator.generate_quality_report(cleaned_data)
        print(f"✓ generate_quality_report() - 返回报告，质量分数: {quality_report['quality_score']:.2f}")
        print(f"  数据形状: {quality_report['data_shape']}")
        print(f"  是否高质量: {'是' if quality_report['summary']['is_high_quality'] else '否'}")
        print(f"  问题总数: {quality_report['summary']['total_issues']}")
        
        print("\n数据处理模块接口测试通过！")
        return True
        
    except Exception as e:
        print(f"✗ 数据处理模块接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("开始GUI模块接口测试...")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # 测试各个模块
    test_results.append(("分析模块", test_analysis_module()))
    test_results.append(("可视化模块", test_visualization_module()))
    test_results.append(("数据处理模块", test_data_module()))
    
    # 输出测试结果总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    all_passed = True
    for module_name, result in test_results:
        status = "通过" if result else "失败"
        print(f"{module_name}: {status}")
        if not result:
            all_passed = False
    
    print(f"\n总体测试结果: {'全部通过' if all_passed else '存在失败'}")
    
    if all_passed:
        print("\n🎉 所有GUI模块接口修复成功！")
        print("现在可以运行完整的GUI应用程序了。")
    else:
        print("\n⚠️ 部分模块仍存在问题，需要进一步修复。")
    
    return all_passed

if __name__ == "__main__":
    main()
