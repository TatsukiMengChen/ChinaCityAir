#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试中文字体显示
"""

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import numpy as np
import sys
import os
import platform

# 添加src路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_system_fonts():
    """测试系统可用字体"""
    print("=" * 60)
    print("系统字体检测")
    print("=" * 60)
    print(f"操作系统: {platform.system()}")
    
    # 获取所有字体
    fonts = [f.name for f in fm.fontManager.ttflist]
    chinese_fonts = []
    
    # 常见中文字体列表
    common_chinese_fonts = [
        'Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 'FangSong',
        'PingFang SC', 'STSong', 'STKaiti', 'STFangsong',
        'WenQuanYi Micro Hei', 'Noto Sans CJK SC'
    ]
    
    print("\n可用的中文字体:")
    for font in common_chinese_fonts:
        if font in fonts:
            chinese_fonts.append(font)
            print(f"✓ {font}")
        else:
            print(f"✗ {font}")
    
    return chinese_fonts

def setup_font_config():
    """设置字体配置"""
    available_fonts = test_system_fonts()
    
    if available_fonts:
        font_to_use = available_fonts[0]
        plt.rcParams['font.sans-serif'] = [font_to_use]
        print(f"\n使用字体: {font_to_use}")
    else:
        print("\n警告: 未找到中文字体，将使用默认字体")
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    
    plt.rcParams['axes.unicode_minus'] = False
    plt.rcParams['font.size'] = 12

def test_chinese_display():
    """测试中文显示"""
    print("\n" + "=" * 60)
    print("测试中文字体显示")
    print("=" * 60)
    
    try:
        # 创建测试数据
        cities = ['北京', '上海', '广州', '深圳', '杭州']
        aqi_values = [120, 85, 95, 110, 75]
        
        # 创建柱状图
        plt.figure(figsize=(10, 6))
        bars = plt.bar(cities, aqi_values, color=['#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b'])
        
        # 添加数值标签
        for bar, value in zip(bars, aqi_values):
            plt.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 2,
                    f'{value}', ha='center', va='bottom', fontweight='bold')
        
        # 设置标题和标签
        plt.title('城市空气质量指数(AQI)对比', fontsize=16, fontweight='bold', pad=20)
        plt.xlabel('城市', fontsize=12)
        plt.ylabel('AQI指数', fontsize=12)
        plt.grid(axis='y', alpha=0.3)
        
        # 保存图表
        output_file = 'test_chinese_font.png'
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ 测试图表已保存: {output_file}")
        
        # 显示图表
        plt.show()
        
        return True
        
    except Exception as e:
        print(f"✗ 中文显示测试失败: {e}")
        return False

def test_visualization_modules():
    """测试可视化模块的中文显示"""
    print("\n" + "=" * 60)
    print("测试可视化模块")
    print("=" * 60)
    
    try:
        from visualizer.basic_charts import BasicCharts
        
        # 创建测试数据
        data = pd.DataFrame({
            'city': ['北京', '上海', '广州', '深圳', '杭州'] * 2,
            'aqi': [120, 85, 95, 110, 75, 130, 90, 100, 115, 80],
            'pm25': [80, 45, 55, 70, 40, 85, 50, 60, 75, 45],
            'quality': ['轻度污染', '良', '良', '轻度污染', '良'] * 2
        })
        
        # 创建基础图表实例
        charts = BasicCharts("test_output")
        
        print("测试基础图表中文显示...")
        
        # 测试柱状图
        charts.plot_bar_chart(
            data=data,
            x_column='city',
            y_column='aqi',
            title='城市AQI对比测试',
            save_name='test_chinese_bar.png'
        )
        print("✓ 柱状图测试完成")
        
        # 测试饼图
        charts.plot_quality_distribution(
            data=data,
            title='空气质量等级分布测试',
            save_name='test_chinese_pie.png'
        )
        print("✓ 饼图测试完成")
        
        print("✓ 可视化模块中文显示测试完成")
        return True
        
    except Exception as e:
        print(f"✗ 可视化模块测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("中文字体显示测试工具")
    print("=" * 60)
    
    # 设置字体配置
    setup_font_config()
    
    # 测试基本中文显示
    basic_test = test_chinese_display()
    
    # 测试可视化模块
    module_test = test_visualization_modules()
    
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    print(f"基本中文显示: {'通过' if basic_test else '失败'}")
    print(f"可视化模块: {'通过' if module_test else '失败'}")
    
    if basic_test and module_test:
        print("\n🎉 所有中文字体显示测试通过！")
    else:
        print("\n⚠️ 部分测试失败，可能需要安装中文字体或检查字体配置")
        print("\n建议解决方案:")
        print("1. 确保系统安装了中文字体（如Microsoft YaHei）")
        print("2. 重新启动Python解释器")
        print("3. 清除matplotlib字体缓存：")
        print("   import matplotlib.font_manager as fm")
        print("   fm._rebuild()")

if __name__ == "__main__":
    main()
