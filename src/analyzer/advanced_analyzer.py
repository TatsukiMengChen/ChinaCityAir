# -*- coding: utf-8 -*-
"""
高级分析模块
用于对空气质量数据进行高级分析，包括区域分析、时间序列分析等
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import sys
import os
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_processor.data_loader import DataLoader

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class AdvancedAnalyzer:
    """高级分析器"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.data = None
        
        # 区域划分
        self.regions = {
            '华北': ['北京', '天津', '石家庄', '太原', '呼和浩特', '保定', '唐山', '邯郸', '秦皇岛', '张家口'],
            '华东': ['上海', '南京', '杭州', '合肥', '福州', '南昌', '济南', '苏州', '无锡', '宁波', '温州', '嘉兴'],
            '华南': ['广州', '深圳', '南宁', '海口', '珠海', '佛山', '东莞', '中山', '江门', '湛江'],
            '华中': ['武汉', '长沙', '郑州', '南阳', '洛阳', '开封', '新乡', '平顶山'],
            '西南': ['重庆', '成都', '贵阳', '昆明', '拉萨', '绵阳', '泸州', '德阳', '遵义'],
            '西北': ['西安', '兰州', '西宁', '银川', '乌鲁木齐', '宝鸡', '咸阳', '渭南'],
            '东北': ['沈阳', '长春', '哈尔滨', '大连', '鞍山', '抚顺', '吉林', '齐齐哈尔']
        }
        
    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """加载数据"""
        try:
            if file_path:
                self.data = self.data_loader.load_csv(file_path)
            else:
                self.data = self.data_loader.load_latest_data()
            if self.data is not None:
                logger.info(f"成功加载数据，形状：{self.data.shape}")
                # 转换时间戳列为datetime类型
                if 'timestamp' in self.data.columns:
                    self.data['timestamp'] = pd.to_datetime(self.data['timestamp'])
            return self.data
        except Exception as e:
            logger.error(f"加载数据失败：{e}")
            return None
    
    def regional_analysis(self) -> Dict:
        """区域分析"""
        if self.data is None:
            logger.error("请先加载数据")
            return {}
        
        logger.info("开始区域分析...")
        
        regional_stats = {}
        
        try:
            for region, cities in self.regions.items():
                # 筛选该区域的城市
                region_data = self.data[self.data['city'].isin(cities)]
                
                if not region_data.empty:
                    numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
                    available_columns = [col for col in numeric_columns if col in region_data.columns]
                    
                    regional_stats[region] = {}
                    for col in available_columns:
                        col_data = pd.to_numeric(region_data[col], errors='coerce')
                        regional_stats[region][col] = {
                            '均值': float(np.mean(col_data.dropna())),
                            '中位数': float(np.median(col_data.dropna())),
                            '最小值': float(np.min(col_data.dropna())),
                            '最大值': float(np.max(col_data.dropna())),
                            '标准差': float(np.std(col_data.dropna())),
                            '城市数量': len(region_data['city'].unique())
                        }
                    
                    # 空气质量等级分布
                    if 'quality' in region_data.columns:
                        quality_dist = region_data['quality'].value_counts(normalize=True) * 100
                        regional_stats[region]['空气质量分布'] = quality_dist.to_dict()
                    
                else:
                    regional_stats[region] = {'说明': '该区域暂无数据'}
            
            logger.info(f"完成 {len(regional_stats)} 个区域的分析")
            return regional_stats
            
        except Exception as e:
            logger.error(f"区域分析失败：{e}")
            return {}
    
    def pollutant_distribution_analysis(self) -> Dict:
        """污染物分布特征分析"""
        if self.data is None:
            logger.error("请先加载数据")
            return {}
        
        logger.info("开始污染物分布特征分析...")
        
        try:
            numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
            available_columns = [col for col in numeric_columns if col in self.data.columns]
            
            distribution_stats = {}
            
            for col in available_columns:
                col_data = pd.to_numeric(self.data[col], errors='coerce').dropna()
                
                # 基本统计信息
                distribution_stats[col] = {
                    '基本统计': {
                        '均值': float(np.mean(col_data)),
                        '中位数': float(np.median(col_data)),
                        '标准差': float(np.std(col_data)),
                        '偏度': float(col_data.skew()),  # 偏度
                        '峰度': float(col_data.kurtosis()),  # 峰度
                    },
                    '分位数': {
                        '10%': float(np.percentile(col_data, 10)),
                        '25%': float(np.percentile(col_data, 25)),
                        '50%': float(np.percentile(col_data, 50)),
                        '75%': float(np.percentile(col_data, 75)),
                        '90%': float(np.percentile(col_data, 90)),
                        '95%': float(np.percentile(col_data, 95)),
                        '99%': float(np.percentile(col_data, 99)),
                    }
                }
                
                # 根据不同污染物设置标准
                if col == 'aqi':
                    # AQI等级划分
                    levels = {
                        '优': (0, 50),
                        '良': (51, 100),
                        '轻度污染': (101, 150),
                        '中度污染': (151, 200),
                        '重度污染': (201, 300),
                        '严重污染': (301, float('inf'))
                    }
                elif col == 'pm25':
                    # PM2.5标准 (μg/m³)
                    levels = {
                        '优': (0, 35),
                        '良': (36, 75),
                        '轻度污染': (76, 115),
                        '中度污染': (116, 150),
                        '重度污染': (151, 250),
                        '严重污染': (251, float('inf'))
                    }
                elif col == 'pm10':
                    # PM10标准 (μg/m³)
                    levels = {
                        '优': (0, 50),
                        '良': (51, 150),
                        '轻度污染': (151, 250),
                        '中度污染': (251, 350),
                        '重度污染': (351, 420),
                        '严重污染': (421, float('inf'))
                    }
                else:
                    levels = None
                
                if levels:
                    level_distribution = {}
                    for level, (min_val, max_val) in levels.items():
                        count = len(col_data[(col_data >= min_val) & (col_data <= max_val)])
                        percentage = count / len(col_data) * 100
                        level_distribution[level] = {
                            '数量': count,
                            '比例': round(percentage, 2)
                        }
                    distribution_stats[col]['等级分布'] = level_distribution
            
            logger.info(f"完成 {len(distribution_stats)} 个污染物的分布分析")
            return distribution_stats
            
        except Exception as e:
            logger.error(f"污染物分布分析失败：{e}")
            return {}
    
    def seasonal_analysis(self) -> Dict:
        """季节性分析"""
        if self.data is None:
            logger.error("请先加载数据")
            return {}
        
        logger.info("开始季节性分析...")
        
        try:
            if 'timestamp' not in self.data.columns:
                logger.warning("数据中缺少时间信息，无法进行季节性分析")
                return {}
            
            # 添加季节信息
            data_with_season = self.data.copy()
            data_with_season['month'] = data_with_season['timestamp'].dt.month
            
            # 定义季节
            def get_season(month):
                if month in [3, 4, 5]:
                    return '春季'
                elif month in [6, 7, 8]:
                    return '夏季'
                elif month in [9, 10, 11]:
                    return '秋季'
                else:
                    return '冬季'
            
            data_with_season['season'] = data_with_season['month'].apply(get_season)
            
            numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
            available_columns = [col for col in numeric_columns if col in data_with_season.columns]
            
            seasonal_stats = {}
            
            for season in ['春季', '夏季', '秋季', '冬季']:
                season_data = data_with_season[data_with_season['season'] == season]
                
                if not season_data.empty:
                    seasonal_stats[season] = {}
                    for col in available_columns:
                        col_data = pd.to_numeric(season_data[col], errors='coerce').dropna()
                        if not col_data.empty:
                            seasonal_stats[season][col] = {
                                '均值': float(np.mean(col_data)),
                                '中位数': float(np.median(col_data)),
                                '标准差': float(np.std(col_data)),
                                '数据量': len(col_data)
                            }
                else:
                    seasonal_stats[season] = {'说明': '该季节暂无数据'}
            
            logger.info(f"完成季节性分析")
            return seasonal_stats
            
        except Exception as e:
            logger.error(f"季节性分析失败：{e}")
            return {}
    
    def top_cities_analysis(self, metric: str = 'aqi', top_n: int = 50) -> Dict:
        """前50城市专项分析"""
        if self.data is None:
            logger.error("请先加载数据")
            return {}
        
        logger.info(f"开始前{top_n}城市专项分析...")
        
        try:
            if metric not in self.data.columns:
                logger.error(f"指标 {metric} 不存在于数据中")
                return {}
            
            # 按城市分组，计算平均值
            city_data = self.data.groupby('city').agg({
                'aqi': 'mean',
                'pm25': 'mean',
                'pm10': 'mean',
                'so2': 'mean',
                'no2': 'mean',
                'co': 'mean',
                'o3': 'mean'
            }).round(2)
            
            # 排序获取前N名
            if metric == 'aqi':
                # AQI越低越好
                top_cities = city_data.sort_values(metric, ascending=True).head(top_n)
            else:
                top_cities = city_data.sort_values(metric, ascending=False).head(top_n)
            
            analysis_result = {
                '城市排名': top_cities.to_dict('index'),
                '统计摘要': {
                    '最佳城市': top_cities.index[0],
                    '最佳值': float(top_cities.iloc[0][metric]),
                    '平均值': float(top_cities[metric].mean()),
                    '标准差': float(top_cities[metric].std()),
                    '分析城市数': len(top_cities)
                }
            }
            
            # 按区域分组分析
            region_analysis = {}
            for region, cities in self.regions.items():
                region_cities = top_cities[top_cities.index.isin(cities)]
                if not region_cities.empty:
                    region_analysis[region] = {
                        '城市数': len(region_cities),
                        f'平均{metric}': float(region_cities[metric].mean()),
                        '城市列表': region_cities.index.tolist()
                    }
            
            analysis_result['区域分布'] = region_analysis
            
            logger.info(f"完成前{top_n}城市专项分析")
            return analysis_result
            
        except Exception as e:
            logger.error(f"前{top_n}城市分析失败：{e}")
            return {}
    
    def generate_advanced_report(self, output_file: Optional[str] = None) -> str:
        """生成高级分析报告"""
        if self.data is None:
            logger.error("请先加载数据")
            return ""
        
        logger.info("生成高级分析报告...")
        
        report = []
        report.append("="*60)
        report.append("空气质量数据高级分析报告")
        report.append("="*60)
        report.append(f"分析时间：{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"数据形状：{self.data.shape}")
        report.append("")
        
        # 区域分析
        report.append("1. 区域空气质量分析")
        report.append("-"*40)
        regional = self.regional_analysis()
        for region, stats in regional.items():
            report.append(f"\n{region}:")
            if '说明' in stats:
                report.append(f"  {stats['说明']}")
            else:
                for indicator, values in stats.items():
                    if indicator != '空气质量分布' and isinstance(values, dict) and '均值' in values:
                        report.append(f"  {indicator}: 均值={values['均值']:.2f}, 城市数={values['城市数量']}")
        
        # 污染物分布分析
        report.append("\n\n2. 污染物分布特征分析")
        report.append("-"*40)
        pollutant_dist = self.pollutant_distribution_analysis()
        for pollutant, stats in pollutant_dist.items():
            report.append(f"\n{pollutant.upper()}:")
            if '基本统计' in stats:
                basic_stats = stats['基本统计']
                report.append(f"  均值: {basic_stats['均值']:.2f}")
                report.append(f"  标准差: {basic_stats['标准差']:.2f}")
                report.append(f"  偏度: {basic_stats['偏度']:.3f}")
        
        # 前50城市分析
        report.append("\n\n3. 前50城市分析（按AQI排序）")
        report.append("-"*40)
        top_cities = self.top_cities_analysis(top_n=min(50, len(self.data['city'].unique())))
        if '统计摘要' in top_cities:
            summary = top_cities['统计摘要']
            report.append(f"最佳城市: {summary['最佳城市']} (AQI: {summary['最佳值']:.2f})")
            report.append(f"平均AQI: {summary['平均值']:.2f}")
            report.append(f"分析城市数: {summary['分析城市数']}")
        
        if '区域分布' in top_cities:
            report.append("\n区域分布:")
            for region, info in top_cities['区域分布'].items():
                report.append(f"  {region}: {info['城市数']}个城市, 平均AQI: {info['平均aqi']:.2f}")
        
        report_text = "\n".join(report)
        
        # 保存报告
        if output_file is None:
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"advanced_analysis_report_{timestamp}.txt"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"高级分析报告已保存到：{output_file}")
        except Exception as e:
            logger.error(f"保存报告失败：{e}")
        
        return report_text

def main():
    """主函数，用于测试"""
    analyzer = AdvancedAnalyzer()
    
    # 加载数据
    data = analyzer.load_data()
    if data is None:
        print("数据加载失败")
        return
    
    print("="*50)
    print("高级分析模块测试")
    print("="*50)
    
    # 区域分析
    print("\n1. 区域分析:")
    regional = analyzer.regional_analysis()
    for region, stats in regional.items():
        print(f"\n{region}:")
        if '说明' in stats:
            print(f"  {stats['说明']}")
        else:
            for indicator, values in stats.items():
                if indicator != '空气质量分布' and isinstance(values, dict) and '均值' in values:
                    print(f"  {indicator}: 均值={values['均值']:.2f}")
    
    # 污染物分布分析
    print("\n2. 污染物分布分析:")
    pollutant_dist = analyzer.pollutant_distribution_analysis()
    for pollutant, stats in pollutant_dist.items():
        print(f"\n{pollutant.upper()}:")
        if '基本统计' in stats:
            basic_stats = stats['基本统计']
            print(f"  均值: {basic_stats['均值']:.2f}")
            print(f"  偏度: {basic_stats['偏度']:.3f}")
            print(f"  峰度: {basic_stats['峰度']:.3f}")
    
    # 前50城市分析
    print("\n3. 前50城市分析:")
    top_cities = analyzer.top_cities_analysis(top_n=10)  # 使用10个城市进行测试
    if '统计摘要' in top_cities:
        summary = top_cities['统计摘要']
        print(f"最佳城市: {summary['最佳城市']} (AQI: {summary['最佳值']:.2f})")
        print(f"分析城市数: {summary['分析城市数']}")
    
    # 生成完整报告
    print("\n4. 生成高级分析报告:")
    report = analyzer.generate_advanced_report()
    print("报告生成完成")

if __name__ == "__main__":
    main()
