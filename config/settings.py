#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统配置文件
"""

import os

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 数据目录配置
DATA_DIR = os.path.join(PROJECT_ROOT, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')

# 爬虫配置
CRAWLER_CONFIG = {
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'request_delay': 1,  # 请求间隔（秒）
    'timeout': 30,       # 请求超时时间（秒）
    'max_retries': 3,    # 最大重试次数
}

# 数据源配置
DATA_SOURCES = {
    'main_url': 'https://www.aqistudy.cn/historydata/',
    'backup_urls': [
        'http://www.tianqihoubao.com/aqi/',
        'https://air.cnemc.cn:18007/',
    ]
}

# 目标城市列表（主要城市）
TARGET_CITIES = [
    '北京', '上海', '广州', '深圳', '天津', '重庆', '成都', '杭州',
    '南京', '武汉', '西安', '沈阳', '青岛', '大连', '厦门', '苏州',
    '无锡', '佛山', '东莞', '泉州', '长沙', '郑州', '石家庄', '济南',
    '哈尔滨', '长春', '太原', '合肥', '南昌', '福州', '贵阳', '昆明',
    '兰州', '西宁', '银川', '乌鲁木齐', '拉萨', '海口', '三亚', '南宁',
    '桂林', '柳州', '温州', '台州', '绍兴', '嘉兴', '湖州', '金华',
    '衢州', '丽水'
]

# 数据字段配置
DATA_FIELDS = {
    'required_fields': [
        'city',      # 城市名称
        'date',      # 日期
        'aqi',       # 空气质量指数
        'pm25',      # PM2.5浓度
        'pm10',      # PM10浓度
        'so2',       # 二氧化硫浓度
        'no2',       # 二氧化氮浓度
        'co',        # 一氧化碳浓度
        'o3',        # 臭氧浓度
        'quality'    # 空气质量等级
    ],
    'data_types': {
        'city': 'str',
        'date': 'datetime',
        'aqi': 'int',
        'pm25': 'float',
        'pm10': 'float',
        'so2': 'float',
        'no2': 'float',
        'co': 'float',
        'o3': 'float',
        'quality': 'str'
    }
}

# 数据处理配置
DATA_PROCESSING = {
    'missing_value_strategy': 'interpolation',  # 缺失值处理策略
    'outlier_detection': True,                   # 是否检测异常值
    'outlier_method': 'iqr',                    # 异常值检测方法
    'normalization': False,                      # 是否标准化
}

# 可视化配置
VISUALIZATION_CONFIG = {
    'figure_size': (12, 8),
    'dpi': 300,
    'style': 'seaborn-v0_8',
    'color_palette': 'viridis',
    'chinese_font': 'SimHei',  # 中文字体
}

# 区域划分
REGION_MAPPING = {
    '华北': ['北京', '天津', '石家庄', '太原', '呼和浩特'],
    '华东': ['上海', '南京', '杭州', '合肥', '福州', '南昌', '济南'],
    '华南': ['广州', '深圳', '南宁', '海口', '厦门'],
    '华中': ['武汉', '长沙', '郑州'],
    '西南': ['重庆', '成都', '贵阳', '昆明', '拉萨'],
    '西北': ['西安', '兰州', '西宁', '银川', '乌鲁木齐'],
    '东北': ['沈阳', '长春', '哈尔滨', '大连']
}

# 日志配置
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': os.path.join(PROJECT_ROOT, 'logs', 'app.log')
}

# GUI配置
GUI_CONFIG = {
    'window_title': '2024中国城市空气质量数据分析系统',
    'window_size': '1200x800',
    'theme': 'default'
}
