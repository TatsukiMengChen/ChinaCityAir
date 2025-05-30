"""
数据加载模块
用于从CSV文件读取空气质量数据并进行基础验证
"""

import pandas as pd
import numpy as np
import os
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataLoader:
    """数据加载器类"""
    
    def __init__(self, data_dir: str = "../../data/raw"):
        """
        初始化数据加载器
        
        Args:
            data_dir: 数据文件目录
        """
        self.data_dir = os.path.abspath(data_dir)
        self.required_columns = [
            'city', 'aqi', 'pm25', 'pm10', 'so2', 'no2', 'co', 'o3', 'quality', 'timestamp'
        ]
        
    def load_csv(self, file_path: str) -> Optional[pd.DataFrame]:
        """
        从CSV文件加载数据
        
        Args:
            file_path: CSV文件路径
            
        Returns:
            pandas DataFrame或None（如果加载失败）
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return None
                
            # 读取CSV文件
            df = pd.read_csv(file_path, encoding='utf-8')
            logger.info(f"成功加载数据文件: {file_path}")
            logger.info(f"数据形状: {df.shape}")
            
            return df
            
        except Exception as e:
            logger.error(f"加载CSV文件失败: {e}")
            return None
    
    def load_latest_data(self) -> Optional[pd.DataFrame]:
        """
        加载最新的数据文件
        
        Returns:
            pandas DataFrame或None
        """
        try:
            # 获取数据目录下的所有CSV文件
            csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
            
            if not csv_files:
                logger.warning("数据目录中没有找到CSV文件")
                return None
                
            # 按文件名排序，获取最新的文件
            csv_files.sort(reverse=True)
            latest_file = os.path.join(self.data_dir, csv_files[0])
            
            logger.info(f"加载最新数据文件: {latest_file}")
            return self.load_csv(latest_file)
            
        except Exception as e:
            logger.error(f"加载最新数据失败: {e}")
            return None
    
    def load_all_data(self) -> Optional[pd.DataFrame]:
        """
        加载所有数据文件并合并
        
        Returns:
            合并后的pandas DataFrame或None
        """
        try:
            # 获取数据目录下的所有CSV文件
            csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('.csv')]
            
            if not csv_files:
                logger.warning("数据目录中没有找到CSV文件")
                return None
                
            all_data = []
            for csv_file in csv_files:
                file_path = os.path.join(self.data_dir, csv_file)
                df = self.load_csv(file_path)
                if df is not None:
                    all_data.append(df)
                    
            if not all_data:
                logger.error("没有成功加载任何数据文件")
                return None
                
            # 合并所有数据
            combined_df = pd.concat(all_data, ignore_index=True)
            
            # 去除重复数据
            combined_df = combined_df.drop_duplicates()
            
            logger.info(f"成功合并 {len(csv_files)} 个数据文件")
            logger.info(f"合并后数据形状: {combined_df.shape}")
            
            return combined_df
            
        except Exception as e:
            logger.error(f"加载所有数据失败: {e}")
            return None
    
    def validate_data_format(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        验证数据格式
        
        Args:
            df: 要验证的DataFrame
            
        Returns:
            验证结果字典
        """
        validation_result = {
            'is_valid': True,
            'missing_columns': [],
            'data_types': {},
            'missing_values': {},
            'summary': {}
        }
        
        try:
            # 检查必需列是否存在
            missing_columns = [col for col in self.required_columns if col not in df.columns]
            validation_result['missing_columns'] = missing_columns
            
            if missing_columns:
                validation_result['is_valid'] = False
                logger.warning(f"缺少必需列: {missing_columns}")
            
            # 检查数据类型
            for col in df.columns:
                validation_result['data_types'][col] = str(df[col].dtype)
            
            # 检查缺失值
            for col in df.columns:
                missing_count = df[col].isnull().sum()
                validation_result['missing_values'][col] = missing_count
                
            # 生成数据摘要
            validation_result['summary'] = {
                'total_rows': len(df),
                'total_columns': len(df.columns),
                'total_missing_values': df.isnull().sum().sum(),
                'duplicate_rows': df.duplicated().sum()
            }
            
            logger.info("数据格式验证完成")
            logger.info(f"数据摘要: {validation_result['summary']}")
            
        except Exception as e:
            logger.error(f"数据格式验证失败: {e}")
            validation_result['is_valid'] = False
            
        return validation_result
    
    def get_data_info(self, df: pd.DataFrame) -> None:
        """
        显示数据基本信息
        
        Args:
            df: 要分析的DataFrame
        """
        try:
            print("=" * 50)
            print("数据基本信息")
            print("=" * 50)
            
            print(f"数据形状: {df.shape}")
            print(f"列名: {list(df.columns)}")
            print()
            
            print("数据类型:")
            print(df.dtypes)
            print()
            
            print("缺失值统计:")
            print(df.isnull().sum())
            print()
            
            print("数据预览:")
            print(df.head())
            print()
            
            print("数据统计信息:")
            print(df.describe())
            
        except Exception as e:
            logger.error(f"显示数据信息失败: {e}")

def main():
    """测试数据加载功能"""
    # 创建数据加载器
    loader = DataLoader()
    
    # 加载最新数据
    df = loader.load_latest_data()
    
    if df is not None:
        # 验证数据格式
        validation_result = loader.validate_data_format(df)
        print("验证结果:", validation_result)
        
        # 显示数据信息
        loader.get_data_info(df)
    else:
        print("数据加载失败")

if __name__ == "__main__":
    main()
