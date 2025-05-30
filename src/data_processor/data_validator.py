#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据验证模块
用于验证数据质量和生成数据质量报告
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Tuple
from pathlib import Path
import os

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataValidator:
    """数据验证器"""
    
    def __init__(self):
        """初始化数据验证器"""
        self.required_columns = ['city', 'aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3', 'quality', 'timestamp']
        self.numeric_columns = ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3']
        
        # 数据范围约束（基于中国环境监测标准）
        self.data_ranges = {
            'aqi': (0, 500),
            'pm25': (0, 1000),
            'pm10': (0, 1000),
            'so2': (0, 1000),
            'no2': (0, 1000),
            'co': (0, 50),
            'o3': (0, 1000)
        }
        
        # 空气质量等级
        self.quality_levels = ['优', '良', '轻度污染', '中度污染', '重度污染', '严重污染']
    
    def validate_data_completeness(self, df: pd.DataFrame) -> Dict[str, Any]:
        """验证数据完整性"""
        logger.info("验证数据完整性...")
        
        validation_result = {
            'is_complete': True,
            'missing_columns': [],
            'missing_values': {},
            'empty_rows': 0,
            'duplicate_rows': 0
        }
        
        # 检查必需列
        missing_columns = [col for col in self.required_columns if col not in df.columns]
        validation_result['missing_columns'] = missing_columns
        if missing_columns:
            validation_result['is_complete'] = False
            logger.warning(f"缺少必需列: {missing_columns}")
        
        # 检查缺失值
        missing_values = df.isnull().sum().to_dict()
        validation_result['missing_values'] = missing_values
        total_missing = sum(missing_values.values())
        if total_missing > 0:
            validation_result['is_complete'] = False
            logger.warning(f"发现 {total_missing} 个缺失值")
        
        # 检查空行
        empty_rows = df.isnull().all(axis=1).sum()
        validation_result['empty_rows'] = empty_rows
        if empty_rows > 0:
            validation_result['is_complete'] = False
            logger.warning(f"发现 {empty_rows} 个空行")
        
        # 检查重复行
        duplicate_rows = df.duplicated().sum()
        validation_result['duplicate_rows'] = duplicate_rows
        if duplicate_rows > 0:
            logger.warning(f"发现 {duplicate_rows} 个重复行")
        
        return validation_result
    
    def validate_data_types(self, df: pd.DataFrame) -> Dict[str, Any]:
        """验证数据类型"""
        logger.info("验证数据类型...")
        
        validation_result = {
            'is_valid': True,
            'type_errors': {},
            'current_types': df.dtypes.to_dict()
        }
        
        # 检查数值列的数据类型
        for col in self.numeric_columns:
            if col in df.columns:
                if not pd.api.types.is_numeric_dtype(df[col]):
                    validation_result['is_valid'] = False
                    validation_result['type_errors'][col] = f"应为数值类型，当前为 {df[col].dtype}"
                    logger.error(f"列 {col} 数据类型错误: {df[col].dtype}")
        
        # 检查字符串列
        string_columns = ['city', 'quality']
        for col in string_columns:
            if col in df.columns:
                if not pd.api.types.is_object_dtype(df[col]):
                    validation_result['is_valid'] = False
                    validation_result['type_errors'][col] = f"应为字符串类型，当前为 {df[col].dtype}"
                    logger.error(f"列 {col} 数据类型错误: {df[col].dtype}")
        
        return validation_result
    
    def validate_data_ranges(self, df: pd.DataFrame) -> Dict[str, Any]:
        """验证数据范围"""
        logger.info("验证数据范围...")
        
        validation_result = {
            'is_valid': True,
            'range_errors': {},
            'outliers': {}
        }
        
        # 检查数值范围
        for col, (min_val, max_val) in self.data_ranges.items():
            if col in df.columns:
                out_of_range = df[(df[col] < min_val) | (df[col] > max_val)]
                if not out_of_range.empty:
                    validation_result['is_valid'] = False
                    validation_result['range_errors'][col] = {
                        'count': len(out_of_range),
                        'expected_range': (min_val, max_val),
                        'actual_range': (df[col].min(), df[col].max())
                    }
                    logger.warning(f"列 {col} 有 {len(out_of_range)} 个值超出正常范围")
        
        # 检查空气质量等级
        if 'quality' in df.columns:
            invalid_quality = df[~df['quality'].isin(self.quality_levels)]
            if not invalid_quality.empty:
                validation_result['is_valid'] = False
                validation_result['range_errors']['quality'] = {
                    'count': len(invalid_quality),
                    'invalid_values': invalid_quality['quality'].unique().tolist()
                }
                logger.warning(f"发现 {len(invalid_quality)} 个无效的空气质量等级")
        
        return validation_result
    
    def validate_data_consistency(self, df: pd.DataFrame) -> Dict[str, Any]:
        """验证数据一致性"""
        logger.info("验证数据一致性...")
        
        validation_result = {
            'is_consistent': True,
            'consistency_errors': []
        }
        
        # 检查AQI与空气质量等级的一致性
        if 'aqi' in df.columns and 'quality' in df.columns:
            aqi_quality_map = {
                (0, 50): '优',
                (51, 100): '良',
                (101, 150): '轻度污染',
                (151, 200): '中度污染',
                (201, 300): '重度污染',
                (301, 500): '严重污染'
            }
            
            for idx, row in df.iterrows():
                aqi_val = row['aqi']
                quality_val = row['quality']
                
                expected_quality = None
                for (min_aqi, max_aqi), quality in aqi_quality_map.items():
                    if min_aqi <= aqi_val <= max_aqi:
                        expected_quality = quality
                        break
                
                if expected_quality and expected_quality != quality_val:
                    validation_result['is_consistent'] = False
                    validation_result['consistency_errors'].append({
                        'row': idx,
                        'city': row.get('city', 'Unknown'),
                        'aqi': aqi_val,
                        'actual_quality': quality_val,
                        'expected_quality': expected_quality
                    })
        
        if not validation_result['is_consistent']:
            logger.warning(f"发现 {len(validation_result['consistency_errors'])} 个数据一致性问题")
        
        return validation_result
    
    def generate_quality_report(self, df: pd.DataFrame) -> Dict[str, Any]:
        """生成数据质量报告"""
        logger.info("生成数据质量报告...")
        
        # 执行所有验证
        completeness = self.validate_data_completeness(df)
        types = self.validate_data_types(df)
        ranges = self.validate_data_ranges(df)
        consistency = self.validate_data_consistency(df)
        
        # 计算质量分数
        quality_score = self._calculate_quality_score(completeness, types, ranges, consistency)
        
        # 生成报告
        report = {
            'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'data_shape': df.shape,
            'quality_score': quality_score,
            'completeness': completeness,
            'data_types': types,
            'data_ranges': ranges,
            'consistency': consistency,
            'summary': {
                'total_issues': (
                    len(completeness.get('missing_columns', [])) +
                    completeness.get('empty_rows', 0) +
                    len(types.get('type_errors', {})) +
                    len(ranges.get('range_errors', {})) +
                    len(consistency.get('consistency_errors', []))
                ),
                'is_high_quality': quality_score >= 0.8
            }
        }
        
        return report
    
    def _calculate_quality_score(self, completeness: Dict, types: Dict, ranges: Dict, consistency: Dict) -> float:
        """计算数据质量分数 (0-1)"""
        score = 1.0
        
        # 完整性权重 40%
        if not completeness['is_complete']:
            missing_penalty = len(completeness.get('missing_columns', [])) * 0.1
            empty_penalty = completeness.get('empty_rows', 0) * 0.01
            score -= (missing_penalty + empty_penalty) * 0.4
        
        # 类型正确性权重 20%
        if not types['is_valid']:
            type_penalty = len(types.get('type_errors', {})) * 0.1
            score -= type_penalty * 0.2
        
        # 范围正确性权重 25%
        if not ranges['is_valid']:
            range_penalty = len(ranges.get('range_errors', {})) * 0.1
            score -= range_penalty * 0.25
        
        # 一致性权重 15%
        if not consistency['is_consistent']:
            consistency_penalty = len(consistency.get('consistency_errors', [])) * 0.01
            score -= consistency_penalty * 0.15
        
        return max(0.0, score)
    
    def save_quality_report(self, report: Dict[str, Any], output_path: str = None) -> str:
        """保存数据质量报告"""
        if output_path is None:
            timestamp = pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"data_quality_report_{timestamp}.txt"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("数据质量报告\n")
            f.write("=" * 80 + "\n")
            f.write(f"生成时间: {report['timestamp']}\n")
            f.write(f"数据形状: {report['data_shape']}\n")
            f.write(f"质量分数: {report['quality_score']:.2f}\n")
            f.write(f"是否高质量: {'是' if report['summary']['is_high_quality'] else '否'}\n")
            f.write(f"问题总数: {report['summary']['total_issues']}\n\n")
            
            # 完整性报告
            f.write("1. 数据完整性\n")
            f.write("-" * 40 + "\n")
            completeness = report['completeness']
            f.write(f"是否完整: {'是' if completeness['is_complete'] else '否'}\n")
            if completeness['missing_columns']:
                f.write(f"缺少列: {completeness['missing_columns']}\n")
            f.write(f"空行数: {completeness['empty_rows']}\n")
            f.write(f"重复行数: {completeness['duplicate_rows']}\n\n")
            
            # 数据类型报告
            f.write("2. 数据类型\n")
            f.write("-" * 40 + "\n")
            types = report['data_types']
            f.write(f"类型正确: {'是' if types['is_valid'] else '否'}\n")
            if types['type_errors']:
                f.write("类型错误:\n")
                for col, error in types['type_errors'].items():
                    f.write(f"  {col}: {error}\n")
            f.write("\n")
            
            # 数据范围报告
            f.write("3. 数据范围\n")
            f.write("-" * 40 + "\n")
            ranges = report['data_ranges']
            f.write(f"范围正确: {'是' if ranges['is_valid'] else '否'}\n")
            if ranges['range_errors']:
                f.write("范围错误:\n")
                for col, error in ranges['range_errors'].items():
                    f.write(f"  {col}: {error}\n")
            f.write("\n")
            
            # 一致性报告
            f.write("4. 数据一致性\n")
            f.write("-" * 40 + "\n")
            consistency = report['consistency']
            f.write(f"数据一致: {'是' if consistency['is_consistent'] else '否'}\n")
            if consistency['consistency_errors']:
                f.write(f"一致性错误数: {len(consistency['consistency_errors'])}\n")
        
        logger.info(f"数据质量报告已保存到: {output_path}")
        return output_path

def main():
    """测试数据验证功能"""
    try:
        # 导入数据加载器
        from data_loader import DataLoader
        
        # 加载数据
        loader = DataLoader()
        df = loader.load_latest_data()
        
        if df is not None:
            # 创建验证器
            validator = DataValidator()
            
            # 生成质量报告
            report = validator.generate_quality_report(df)
            
            # 打印报告摘要
            print("=" * 60)
            print("数据质量验证报告")
            print("=" * 60)
            print(f"数据形状: {report['data_shape']}")
            print(f"质量分数: {report['quality_score']:.2f}")
            print(f"是否高质量: {'是' if report['summary']['is_high_quality'] else '否'}")
            print(f"问题总数: {report['summary']['total_issues']}")
            
            print("\n详细验证结果:")
            print(f"完整性: {'通过' if report['completeness']['is_complete'] else '未通过'}")
            print(f"数据类型: {'通过' if report['data_types']['is_valid'] else '未通过'}")
            print(f"数据范围: {'通过' if report['data_ranges']['is_valid'] else '未通过'}")
            print(f"数据一致性: {'通过' if report['consistency']['is_consistent'] else '未通过'}")
            
            # 保存报告
            report_path = validator.save_quality_report(report)
            print(f"\n完整报告已保存到: {report_path}")
            
        else:
            print("无法加载数据文件")
            
    except Exception as e:
        logger.error(f"数据验证过程中发生错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
