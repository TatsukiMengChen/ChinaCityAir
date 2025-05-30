# -*- coding: utf-8 -*-
"""
统计分析模块
用于对空气质量数据进行基础统计分析
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
import sys
import os

# 添加父目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from data_processor.data_loader import DataLoader

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class StatisticalAnalyzer:
    """统计分析器"""
    
    def __init__(self):
        self.data_loader = DataLoader()
        self.data = None
        
    def load_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """加载数据"""
        try:
            if file_path:
                self.data = self.data_loader.load_csv(file_path)
            else:
                self.data = self.data_loader.load_latest_data()
            if self.data is not None:
                logger.info(f"成功加载数据，形状：{self.data.shape}")
            return self.data
        except Exception as e:
            logger.error(f"加载数据失败：{e}")
            return None
    
    def descriptive_statistics(self, columns: Optional[List[str]] = None) -> Dict:
        """描述性统计分析"""
        if self.data is None:
            logger.error("请先加载数据")
            return {}
        
        logger.info("开始描述性统计分析...")
        
        # 数值型列
        numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
        if columns:
            numeric_columns = [col for col in columns if col in numeric_columns]
        
        # 确保列存在
        available_columns = [col for col in numeric_columns if col in self.data.columns]
        
        stats = {}
        
        for col in available_columns:
            try:
                col_data = pd.to_numeric(self.data[col], errors='coerce')
                stats[col] = {
                    '均值': float(np.mean(col_data.dropna())),
                    '中位数': float(np.median(col_data.dropna())),
                    '众数': float(col_data.mode().iloc[0]) if not col_data.mode().empty else None,
                    '标准差': float(np.std(col_data.dropna())),
                    '方差': float(np.var(col_data.dropna())),
                    '最小值': float(np.min(col_data.dropna())),
                    '最大值': float(np.max(col_data.dropna())),
                    '25%分位数': float(np.percentile(col_data.dropna(), 25)),
                    '75%分位数': float(np.percentile(col_data.dropna(), 75)),
                    '数据量': int(col_data.notna().sum()),
                    '缺失值': int(col_data.isna().sum())
                }
            except Exception as e:
                logger.error(f"计算列 {col} 的统计信息时出错：{e}")
                stats[col] = {}
        
        logger.info(f"完成 {len(stats)} 个指标的描述性统计")
        return stats
    
    def air_quality_ranking(self, top_n: int = 50, metric: str = 'aqi') -> pd.DataFrame:
        """空气质量排名分析"""
        if self.data is None:
            logger.error("请先加载数据")
            return pd.DataFrame()
        
        logger.info(f"开始空气质量排名分析（前{top_n}城市，按{metric}排序）...")
        
        try:
            # 确保metric列存在且为数值型
            if metric not in self.data.columns:
                logger.error(f"指标 {metric} 不存在于数据中")
                return pd.DataFrame()
            
            # 转换为数值型
            ranking_data = self.data.copy()
            ranking_data[metric] = pd.to_numeric(ranking_data[metric], errors='coerce')
            
            # 去除缺失值
            ranking_data = ranking_data.dropna(subset=[metric])
            
            # 按城市分组，计算平均值（如果有多条记录）
            if 'city' in ranking_data.columns:
                numeric_cols = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
                agg_dict = {}
                for col in numeric_cols:
                    if col in ranking_data.columns:
                        agg_dict[col] = 'mean'
                if 'quality' in ranking_data.columns:
                    agg_dict['quality'] = lambda x: x.mode().iloc[0] if not x.mode().empty else x.iloc[0]
                
                city_stats = ranking_data.groupby('city').agg(agg_dict).round(2)
            else:
                logger.error("数据中缺少城市信息")
                return pd.DataFrame()
            
            # 排序（AQI越低越好）
            city_stats = city_stats.sort_values(metric, ascending=True)
            
            # 取前N名
            top_cities = city_stats.head(top_n).copy()
            
            # 添加排名
            top_cities['排名'] = range(1, len(top_cities) + 1)
            
            # 重新排列列的顺序
            columns_order = ['排名'] + [col for col in city_stats.columns if col != '排名']
            top_cities = top_cities[columns_order]
            
            logger.info(f"完成排名分析，共 {len(top_cities)} 个城市")
            return top_cities
            
        except Exception as e:
            logger.error(f"排名分析失败：{e}")
            return pd.DataFrame()
    
    def correlation_analysis(self) -> pd.DataFrame:
        """相关性分析"""
        if self.data is None:
            logger.error("请先加载数据")
            return pd.DataFrame()
        
        logger.info("开始相关性分析...")
        
        try:
            # 选择数值型列
            numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
            available_columns = [col for col in numeric_columns if col in self.data.columns]
            
            if len(available_columns) < 2:
                logger.error("数值型列不足，无法进行相关性分析")
                return pd.DataFrame()
            
            # 转换为数值型
            correlation_data = self.data[available_columns].copy()
            for col in available_columns:
                correlation_data[col] = pd.to_numeric(correlation_data[col], errors='coerce')
            
            # 计算相关系数矩阵
            correlation_matrix = correlation_data.corr()
            
            logger.info("相关性分析完成")
            return correlation_matrix
            
        except Exception as e:
            logger.error(f"相关性分析失败：{e}")
            return pd.DataFrame()
    
    def quality_distribution(self) -> Dict:
        """空气质量等级分布分析"""
        if self.data is None:
            logger.error("请先加载数据")
            return {}
        
        logger.info("开始空气质量等级分布分析...")
        
        try:
            if 'quality' not in self.data.columns:
                logger.error("数据中缺少空气质量等级信息")
                return {}
            
            # 统计各等级的分布
            quality_counts = self.data['quality'].value_counts()
            total = len(self.data)
            
            distribution = {}
            for quality, count in quality_counts.items():
                distribution[quality] = {
                    '数量': int(count),
                    '比例': float(count / total * 100)
                }
            
            logger.info(f"完成空气质量等级分布分析，共 {len(distribution)} 个等级")
            return distribution
            
        except Exception as e:
            logger.error(f"空气质量等级分布分析失败：{e}")
            return {}

def main():
    """主函数，用于测试"""
    analyzer = StatisticalAnalyzer()
    
    # 加载数据
    data = analyzer.load_data()
    if data is None:
        print("数据加载失败")
        return
    
    print("="*50)
    print("统计分析模块测试")
    print("="*50)
    
    # 描述性统计
    print("\n1. 描述性统计分析:")
    desc_stats = analyzer.descriptive_statistics()
    for indicator, stats in desc_stats.items():
        print(f"\n{indicator.upper()}:")
        for stat_name, value in stats.items():
            if value is not None:
                if isinstance(value, float):
                    print(f"  {stat_name}: {value:.2f}")
                else:
                    print(f"  {stat_name}: {value}")
    
    # 排名分析
    print("\n2. 空气质量排名分析:")
    ranking = analyzer.air_quality_ranking(top_n=10)
    if not ranking.empty:
        print(ranking)
    else:
        print("无排名数据")
    
    # 相关性分析
    print("\n3. 污染物相关性分析:")
    correlation = analyzer.correlation_analysis()
    if not correlation.empty:
        print(correlation.round(3))
    else:
        print("无相关性数据")
    
    # 质量等级分布
    print("\n4. 空气质量等级分布:")
    quality_dist = analyzer.quality_distribution()
    for quality, stats in quality_dist.items():
        print(f"{quality}: {stats['数量']}个 ({stats['比例']:.1f}%)")

if __name__ == "__main__":
    main()
