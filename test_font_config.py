#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字体测试脚本
测试中文字体配置是否正确
"""

import sys
import os

# 添加src目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from utils.font_config import setup_chinese_font, test_chinese_display
    
    print("=" * 60)
    print("中文字体配置测试")
    print("=" * 60)
    
    # 设置字体
    print("正在配置中文字体...")
    font_success = setup_chinese_font()
    
    if font_success:
        print("\n正在生成中文测试图表...")
        test_success = test_chinese_display()
        
        if test_success:
            print("\n✓ 中文字体配置成功！")
            print("现在可以运行 python main.py 启动主程序")
        else:
            print("\n⚠ 测试图表生成失败")
    else:
        print("\n⚠ 字体配置存在问题，但程序仍可运行")
        print("图表中的中文可能显示为方框")
    
    print("=" * 60)
    
except Exception as e:
    print(f"字体测试失败: {e}")
    print("请检查utils模块是否正确安装")
