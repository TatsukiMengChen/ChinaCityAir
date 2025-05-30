# -*- coding: utf-8 -*-
"""
数据清洗和预处理模块
处理缺失值、数据类型转换、异常值检测等
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataCleaner:
    """数据清洗和预处理类"""
    
    def __init__(self):
        """初始化数据清洗器"""
        self.original_shape = None
        self.cleaning_report = {}
        
        # 定义空气质量数据的正常范围
        self.value_ranges = {
            'aqi': (0, 500),
            'pm25': (0, 500),
            'pm10': (0, 600),
            'so2': (0, 1000),
            'no2': (0, 500),
            'co': (0, 50),
            'o3': (0, 800)
        }
        
        # 空气质量等级映射
        self.quality_mapping = {
            '优': 1, '良': 2, '轻度污染': 3, 
            '中度污染': 4, '重度污染': 5, '严重污染': 6
        }
    
    def clean_data(self, df: pd.DataFrame, 
                   missing_strategy: str = 'median',
                   outlier_method: str = 'iqr',
                   outlier_factor: float = 1.5) -> pd.DataFrame:
        """
        完整的数据清洗流程
        
        Args:
            df: 原始数据DataFrame
            missing_strategy: 缺失值处理策略 ('mean', 'median', 'forward', 'backward', 'interpolate')
            outlier_method: 异常值检测方法 ('iqr', 'zscore', 'isolation')
            outlier_factor: 异常值检测因子
            
        Returns:
            清洗后的DataFrame
        """
        logger.info("开始数据清洗流程...")
        
        # 记录原始数据信息
        self.original_shape = df.shape
        self.cleaning_report = {
            'original_shape': self.original_shape,
            'original_missing': df.isnull().sum().to_dict(),
            'steps': []
        }
        
        # 创建数据副本
        cleaned_df = df.copy()
        
        # 1. 数据类型转换
        cleaned_df = self._convert_data_types(cleaned_df)
        
        # 2. 处理缺失值
        cleaned_df = self._handle_missing_values(cleaned_df, missing_strategy)
        
        # 3. 异常值检测和处理
        cleaned_df = self._handle_outliers(cleaned_df, outlier_method, outlier_factor)
        
        # 4. 数据标准化
        cleaned_df = self._standardize_data(cleaned_df)
        
        # 5. 数据验证
        validation_result = self._validate_cleaned_data(cleaned_df)
        
        # 生成清洗报告
        self._generate_cleaning_report(cleaned_df, validation_result)
        
        logger.info(f"数据清洗完成，形状从 {self.original_shape} 变为 {cleaned_df.shape}")
        
        return cleaned_df
    
    def _convert_data_types(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据类型转换"""
        logger.info("执行数据类型转换...")
        
        df_converted = df.copy()
        conversions = {}
        
        # 数值列转换
        numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
        for col in numeric_columns:
            if col in df_converted.columns:
                original_type = df_converted[col].dtype
                if col == 'co':
                    df_converted[col] = pd.to_numeric(df_converted[col], errors='coerce').astype('float64')
                else:
                    df_converted[col] = pd.to_numeric(df_converted[col], errors='coerce').astype('int64')
                conversions[col] = f"{original_type} -> {df_converted[col].dtype}"
        
        # 时间戳转换
        if 'timestamp' in df_converted.columns:
            original_type = df_converted['timestamp'].dtype
            df_converted['timestamp'] = pd.to_datetime(df_converted['timestamp'], errors='coerce')
            conversions['timestamp'] = f"{original_type} -> {df_converted['timestamp'].dtype}"
        
        # 城市名和质量等级保持为字符串
        string_columns = ['city', 'quality']
        for col in string_columns:
            if col in df_converted.columns:
                df_converted[col] = df_converted[col].astype('string')
        
        self.cleaning_report['steps'].append({
            'step': 'data_type_conversion',
            'conversions': conversions
        })
        
        logger.info(f"数据类型转换完成，转换了 {len(conversions)} 列")
        return df_converted
    
    def _handle_missing_values(self, df: pd.DataFrame, strategy: str) -> pd.DataFrame:
        """处理缺失值"""
        logger.info(f"使用策略 '{strategy}' 处理缺失值...")
        
        df_filled = df.copy()
        missing_before = df_filled.isnull().sum()
        filled_info = {}
        
        numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
        
        for col in numeric_columns:
            if col in df_filled.columns and df_filled[col].isnull().any():
                missing_count = df_filled[col].isnull().sum()
                
                if strategy == 'mean':
                    fill_value = df_filled[col].mean()
                    df_filled[col].fillna(fill_value, inplace=True)
                elif strategy == 'median':
                    fill_value = df_filled[col].median()
                    df_filled[col].fillna(fill_value, inplace=True)
                elif strategy == 'forward':
                    df_filled[col].fillna(method='ffill', inplace=True)
                elif strategy == 'backward':
                    df_filled[col].fillna(method='bfill', inplace=True)
                elif strategy == 'interpolate':
                    df_filled[col].interpolate(method='linear', inplace=True)
                
                filled_info[col] = {
                    'missing_count': missing_count,
                    'fill_method': strategy,
                    'fill_value': fill_value if strategy in ['mean', 'median'] else 'dynamic'
                }
        
        # 处理分类变量的缺失值
        if 'quality' in df_filled.columns and df_filled['quality'].isnull().any():
            # 根据AQI值推断空气质量等级
            df_filled['quality'] = df_filled.apply(self._infer_quality_from_aqi, axis=1)
            filled_info['quality'] = {
                'missing_count': df_filled['quality'].isnull().sum(),
                'fill_method': 'inferred_from_aqi'
            }
        
        missing_after = df_filled.isnull().sum()
        
        self.cleaning_report['steps'].append({
            'step': 'missing_value_handling',
            'strategy': strategy,
            'missing_before': missing_before.to_dict(),
            'missing_after': missing_after.to_dict(),
            'filled_info': filled_info
        })
        
        logger.info(f"缺失值处理完成，填补了 {sum(filled_info.values() if isinstance(v, dict) else 0 for v in filled_info.values() if isinstance(v, dict))} 个值")
        return df_filled
    
    def _infer_quality_from_aqi(self, row):
        """根据AQI值推断空气质量等级"""
        if pd.isna(row['quality']) and not pd.isna(row['aqi']):
            aqi = row['aqi']
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
        return row['quality']
    
    def _handle_outliers(self, df: pd.DataFrame, method: str, factor: float) -> pd.DataFrame:
        """异常值检测和处理"""
        logger.info(f"使用方法 '{method}' 检测和处理异常值...")
        
        df_cleaned = df.copy()
        outlier_info = {}
        
        numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
        
        for col in numeric_columns:
            if col in df_cleaned.columns:
                original_count = len(df_cleaned)
                
                if method == 'iqr':
                    outliers = self._detect_outliers_iqr(df_cleaned[col], factor)
                elif method == 'zscore':
                    outliers = self._detect_outliers_zscore(df_cleaned[col], factor)
                elif method == 'range':
                    outliers = self._detect_outliers_range(df_cleaned[col], col)
                else:
                    continue
                
                outlier_count = outliers.sum()
                
                if outlier_count > 0:
                    # 使用中位数替换异常值
                    median_value = df_cleaned[col].median()
                    df_cleaned.loc[outliers, col] = median_value
                    
                    outlier_info[col] = {
                        'outlier_count': outlier_count,
                        'outlier_percentage': (outlier_count / original_count) * 100,
                        'replacement_value': median_value,
                        'method': method
                    }
        
        self.cleaning_report['steps'].append({
            'step': 'outlier_handling',
            'method': method,
            'factor': factor,
            'outlier_info': outlier_info
        })
        
        total_outliers = sum(info['outlier_count'] for info in outlier_info.values())
        logger.info(f"异常值处理完成，处理了 {total_outliers} 个异常值")
        
        return df_cleaned
    
    def _detect_outliers_iqr(self, series: pd.Series, factor: float) -> pd.Series:
        """使用IQR方法检测异常值"""
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - factor * IQR
        upper_bound = Q3 + factor * IQR
        return (series < lower_bound) | (series > upper_bound)
    
    def _detect_outliers_zscore(self, series: pd.Series, threshold: float) -> pd.Series:
        """使用Z-score方法检测异常值"""
        z_scores = np.abs((series - series.mean()) / series.std())
        return z_scores > threshold
    
    def _detect_outliers_range(self, series: pd.Series, column: str) -> pd.Series:
        """使用预定义范围检测异常值"""
        if column in self.value_ranges:
            min_val, max_val = self.value_ranges[column]
            return (series < min_val) | (series > max_val)
        return pd.Series([False] * len(series), index=series.index)
    
    def _standardize_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """数据标准化"""
        logger.info("执行数据标准化...")
        
        df_std = df.copy()
        standardization_info = {}
        
        # 确保城市名称格式一致
        if 'city' in df_std.columns:
            df_std['city'] = df_std['city'].str.strip()
            unique_cities_before = df_std['city'].nunique()
            
            # 去除重复城市记录（如果有的话）
            df_std = df_std.drop_duplicates(subset=['city', 'timestamp'], keep='first')
            
            standardization_info['city'] = {
                'unique_cities_before': unique_cities_before,
                'unique_cities_after': df_std['city'].nunique(),
                'duplicates_removed': len(df) - len(df_std)
            }
        
        # 添加质量等级编码
        if 'quality' in df_std.columns:
            df_std['quality_code'] = df_std['quality'].map(self.quality_mapping)
            standardization_info['quality_encoding'] = self.quality_mapping
        
        self.cleaning_report['steps'].append({
            'step': 'data_standardization',
            'standardization_info': standardization_info
        })
        
        logger.info("数据标准化完成")
        return df_std
    
    def _validate_cleaned_data(self, df: pd.DataFrame) -> Dict[str, Any]:
        """验证清洗后的数据"""
        logger.info("验证清洗后的数据...")
        
        validation_result = {
            'final_shape': df.shape,
            'missing_values': df.isnull().sum().to_dict(),
            'data_types': df.dtypes.to_dict(),
            'value_ranges': {},
            'is_valid': True,
            'issues': []
        }
        
        # 检查数值范围
        numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
        for col in numeric_columns:
            if col in df.columns:
                min_val = df[col].min()
                max_val = df[col].max()
                validation_result['value_ranges'][col] = {'min': min_val, 'max': max_val}
                
                # 检查是否在合理范围内
                if col in self.value_ranges:
                    expected_min, expected_max = self.value_ranges[col]
                    if min_val < expected_min or max_val > expected_max:
                        validation_result['issues'].append(f"{col} 值超出预期范围 {self.value_ranges[col]}")
                        validation_result['is_valid'] = False
        
        # 检查是否还有缺失值
        total_missing = df.isnull().sum().sum()
        if total_missing > 0:
            validation_result['issues'].append(f"仍有 {total_missing} 个缺失值")
            validation_result['is_valid'] = False
        
        return validation_result
    
    def _generate_cleaning_report(self, df: pd.DataFrame, validation_result: Dict[str, Any]):
        """生成清洗报告"""
        self.cleaning_report.update({
            'final_shape': df.shape,
            'final_missing': df.isnull().sum().to_dict(),
            'validation_result': validation_result,
            'cleaning_summary': {
                'rows_removed': self.original_shape[0] - df.shape[0],
                'columns_processed': df.shape[1],
                'is_successful': validation_result['is_valid']
            }
        })
    
    def get_cleaning_report(self) -> Dict[str, Any]:
        """获取清洗报告"""
        return self.cleaning_report
    
    def save_cleaned_data(self, df: pd.DataFrame, output_path: str) -> str:
        """保存清洗后的数据"""
        try:
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            logger.info(f"清洗后的数据已保存到: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            raise


def main():
    """测试数据清洗功能"""
    import os
    import sys
    
    # 添加项目根目录到路径
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    sys.path.insert(0, project_root)
    
    from src.data_processor.data_loader import DataLoader
    
    # 初始化
    loader = DataLoader()
    cleaner = DataCleaner()
    
    try:
        # 加载数据
        df = loader.load_latest_data()
        print(f"原始数据形状: {df.shape}")
        print("\n原始数据预览:")
        print(df.head())
        
        # 清洗数据
        cleaned_df = cleaner.clean_data(df, 
                                       missing_strategy='median',
                                       outlier_method='iqr',
                                       outlier_factor=1.5)
        
        print(f"\n清洗后数据形状: {cleaned_df.shape}")
        print("\n清洗后数据预览:")
        print(cleaned_df.head())
        
        # 显示清洗报告
        report = cleaner.get_cleaning_report()
        print("\n" + "="*50)
        print("数据清洗报告")
        print("="*50)
        print(f"原始数据形状: {report['original_shape']}")
        print(f"清洗后数据形状: {report['final_shape']}")
        print(f"删除行数: {report['cleaning_summary']['rows_removed']}")
        print(f"清洗是否成功: {report['cleaning_summary']['is_successful']}")
        
        if report['validation_result']['issues']:
            print(f"发现问题: {report['validation_result']['issues']}")
        
        # 保存清洗后的数据
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(project_root, 'data', 'processed', f'cleaned_air_quality_{timestamp}.csv')
        cleaner.save_cleaned_data(cleaned_df, output_path)
        
        print(f"\n清洗后的数据已保存到: {output_path}")
        
    except Exception as e:
        logger.error(f"数据清洗测试失败: {e}")
        raise


if __name__ == "__main__":
    main()
