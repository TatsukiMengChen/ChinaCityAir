#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
2024中国城市空气质量数据分析系统 - 主程序入口
作者: AI Assistant
日期: 2024年
"""

import sys
import os

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

if __name__ == "__main__":
    try:
        # 导入并运行主程序
        from src.main import main
        main()
    except ImportError as e:
        print("=" * 50)
        print("2024中国城市空气质量数据分析系统")
        print("=" * 50)
        print(f"导入模块失败: {e}")
        print("请确保所有必要的模块都已正确安装")
        print("=" * 50)
    except Exception as e:
        print("=" * 50)
        print("程序运行出错:")
        print(f"错误信息: {e}")
        print("=" * 50)
