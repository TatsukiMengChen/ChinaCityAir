#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体配置模块
用于解决matplotlib中文显示问题
"""

import matplotlib.pyplot as plt
import matplotlib
import os
import sys
import warnings

def setup_chinese_font():
    """设置中文字体显示（修正版，兼容新版matplotlib）"""
    import matplotlib.pyplot as plt
    import sys
    import warnings
    # 只忽略所有警告，不引用cbook
    warnings.filterwarnings('ignore')
    try:
        if sys.platform.startswith('win'):
            chinese_fonts = [
                'Microsoft YaHei', 'SimHei', 'KaiTi', 'SimSun', 'FangSong'
            ]
        elif sys.platform.startswith('darwin'):
            chinese_fonts = [
                'PingFang SC', 'Hiragino Sans GB', 'STHeiti', 'Arial Unicode MS'
            ]
        else:
            chinese_fonts = [
                'WenQuanYi Micro Hei', 'Noto Sans CJK SC', 'Source Han Sans CN', 'DejaVu Sans'
            ]
        font_set = False
        for font_name in chinese_fonts:
            try:
                plt.rcParams['font.sans-serif'] = [font_name] + plt.rcParams['font.sans-serif']
                plt.rcParams['axes.unicode_minus'] = False
                font_set = True
                print(f"✓ 成功设置中文字体: {font_name}")
                break
            except Exception:
                continue
        if not font_set:
            print("⚠ 警告: 无法找到合适的中文字体，使用默认配置")
            plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.dpi'] = 100
        plt.rcParams['savefig.dpi'] = 300
        plt.rcParams['figure.figsize'] = [12, 8]
        plt.rcParams['font.size'] = 10
        return font_set
    except Exception as e:
        print(f"✗ 字体配置失败: {e}")
        return False

def get_chinese_font_name():
    """获取当前设置的中文字体名称"""
    try:
        return plt.rcParams['font.sans-serif'][0]
    except:
        return "default"

def test_chinese_display():
    """测试中文显示效果"""
    try:
        import matplotlib.pyplot as plt
        import numpy as np
        
        # 创建测试图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 测试1：简单文本
        ax1.text(0.5, 0.5, '这是中文测试\n空气质量分析\nAir Quality Analysis', 
                fontsize=14, ha='center', va='center',
                bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
        ax1.set_title('中文字体测试', fontsize=16, fontweight='bold')
        ax1.set_xlim(0, 1)
        ax1.set_ylim(0, 1)
        ax1.grid(True, alpha=0.3)
        
        # 测试2：图表标签
        cities = ['北京', '上海', '广州', '深圳', '杭州']
        values = [85, 92, 78, 88, 75]
        
        bars = ax2.bar(cities, values, color=['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57'])
        ax2.set_title('城市空气质量指数对比', fontsize=16, fontweight='bold')
        ax2.set_xlabel('城市', fontsize=12)
        ax2.set_ylabel('AQI数值', fontsize=12)
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 添加数值标签
        for bar, value in zip(bars, values):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    str(value), ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        
        # 保存测试图片
        test_file = 'test_chinese_font.png'
        plt.savefig(test_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"✓ 中文显示测试完成，测试图片已保存: {test_file}")
        return True
        
    except Exception as e:
        print(f"✗ 中文显示测试失败: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("字体配置测试")
    print("=" * 50)
    
    # 设置字体
    font_success = setup_chinese_font()
    
    # 测试显示
    if font_success:
        test_chinese_display()
    
    print("=" * 50)
