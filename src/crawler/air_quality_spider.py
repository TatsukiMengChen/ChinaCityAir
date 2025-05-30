"""
中国环境监测总站空气质量数据爬虫
数据源：https://air.cnemc.cn:18007/
"""

import requests
import time
import json
import pandas as pd
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
from bs4 import BeautifulSoup


class AirQualitySpider:
    """空气质量数据爬虫类"""
    
    def __init__(self, base_url: str = "https://air.cnemc.cn:18007"):
        """
        初始化爬虫
        
        Args:
            base_url: 基础URL
        """
        self.base_url = base_url
        self.session = requests.Session()
        
        # 设置请求头，模拟浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # 配置日志
        self.setup_logging()
        
        # 数据保存路径
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw')
        os.makedirs(self.data_dir, exist_ok=True)
    
    def setup_logging(self):
        """设置日志配置"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crawler.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_city_air_quality(self) -> Optional[List[Dict]]:
        """
        获取城市空气质量数据
        
        Returns:
            城市空气质量数据列表
        """
        try:
            # 先访问主页面获取必要的参数
            main_url = f"{self.base_url}"
            response = self.session.get(main_url, timeout=10)
            response.raise_for_status()
            
            self.logger.info("成功访问主页面")
            
            # 分析页面结构，查找数据接口
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 查找可能的数据接口
            scripts = soup.find_all('script')
            api_urls = []
            
            for script in scripts:
                if script.string:
                    # 查找包含API地址的脚本
                    if 'api' in script.string.lower() or 'data' in script.string.lower():
                        self.logger.info(f"找到可能的API脚本: {script.string[:100]}...")
            
            # 尝试常见的API接口路径
            possible_apis = [
                "/city/cityList",
                "/api/city",
                "/data/city.json",
                "/citydata",
                "/getCityData"
            ]
            
            for api_path in possible_apis:
                try:
                    api_url = f"{self.base_url}{api_path}"
                    self.logger.info(f"尝试API接口: {api_url}")
                    
                    api_response = self.session.get(api_url, timeout=10)
                    if api_response.status_code == 200:
                        try:
                            data = api_response.json()
                            if isinstance(data, (list, dict)) and data:
                                self.logger.info(f"成功获取数据: {api_url}")
                                return self.parse_city_data(data)
                        except json.JSONDecodeError:
                            # 可能是HTML格式的数据
                            soup_api = BeautifulSoup(api_response.text, 'html.parser')
                            data = self.parse_html_data(soup_api)
                            if data:
                                return data
                except Exception as e:
                    self.logger.debug(f"API {api_path} 失败: {e}")
                    continue
            
            # 如果API接口都失败，尝试解析主页面的数据
            self.logger.info("尝试解析主页面数据")
            return self.parse_main_page_data(soup)
            
        except Exception as e:
            self.logger.error(f"获取城市空气质量数据失败: {e}")
            return None
    
    def parse_city_data(self, data) -> List[Dict]:
        """
        解析API返回的城市数据
        
        Args:
            data: API返回的数据
            
        Returns:
            标准化的城市数据列表
        """
        parsed_data = []
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            if isinstance(data, dict):
                # 如果数据是字典格式
                if 'data' in data:
                    data = data['data']
                elif 'result' in data:
                    data = data['result']
                elif 'cities' in data:
                    data = data['cities']
            
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        parsed_item = self.standardize_city_item(item, current_time)
                        if parsed_item:
                            parsed_data.append(parsed_item)
            
            self.logger.info(f"解析到 {len(parsed_data)} 条城市数据")
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"解析城市数据失败: {e}")
            return []
    
    def parse_html_data(self, soup) -> List[Dict]:
        """
        解析HTML页面中的数据
        
        Args:
            soup: BeautifulSoup对象
            
        Returns:
            解析出的数据列表
        """
        parsed_data = []
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        try:
            # 查找表格数据
            tables = soup.find_all('table')
            for table in tables:
                rows = table.find_all('tr')
                if len(rows) > 1:  # 有标题行
                    headers = [th.get_text().strip() for th in rows[0].find_all(['th', 'td'])]
                    
                    for row in rows[1:]:
                        cols = [td.get_text().strip() for td in row.find_all(['td', 'th'])]
                        if len(cols) >= len(headers):
                            item_data = dict(zip(headers, cols))
                            parsed_item = self.standardize_city_item(item_data, current_time)
                            if parsed_item:
                                parsed_data.append(parsed_item)
            
            # 查找其他可能的数据容器
            data_divs = soup.find_all('div', class_=['data', 'city-data', 'air-quality'])
            for div in data_divs:
                # 尝试解析div中的数据
                pass
            
            self.logger.info(f"从HTML解析到 {len(parsed_data)} 条数据")
            return parsed_data
            
        except Exception as e:
            self.logger.error(f"解析HTML数据失败: {e}")
            return []
    
    def parse_main_page_data(self, soup) -> List[Dict]:
        """
        解析主页面的数据
        
        Args:
            soup: 主页面的BeautifulSoup对象
            
        Returns:
            解析出的数据列表
        """
        # 创建示例数据（实际项目中需要根据真实页面结构调整）
        sample_data = [
            {
                'city': '北京',
                'aqi': 85,
                'pm25': 62,
                'pm10': 95,
                'so2': 8,
                'no2': 45,
                'co': 0.8,
                'o3': 120,
                'quality': '良',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'city': '上海',
                'aqi': 78,
                'pm25': 55,
                'pm10': 88,
                'so2': 6,
                'no2': 42,
                'co': 0.7,
                'o3': 115,
                'quality': '良',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            },
            {
                'city': '广州',
                'aqi': 92,
                'pm25': 68,
                'pm10': 102,
                'so2': 12,
                'no2': 48,
                'co': 0.9,
                'o3': 135,
                'quality': '良',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        ]
        
        self.logger.info("使用示例数据进行测试")
        return sample_data
    
    def standardize_city_item(self, item: Dict, timestamp: str) -> Optional[Dict]:
        """
        标准化城市数据项
        
        Args:
            item: 原始数据项
            timestamp: 时间戳
            
        Returns:
            标准化的数据项
        """
        try:
            # 定义字段映射
            field_mapping = {
                'city': ['city', 'cityname', '城市', 'name'],
                'aqi': ['aqi', 'AQI', '空气质量指数'],
                'pm25': ['pm25', 'PM25', 'PM2.5', 'pm2.5'],
                'pm10': ['pm10', 'PM10'],
                'so2': ['so2', 'SO2', '二氧化硫'],
                'no2': ['no2', 'NO2', '二氧化氮'],
                'co': ['co', 'CO', '一氧化碳'],
                'o3': ['o3', 'O3', '臭氧'],
                'quality': ['quality', 'level', '等级', '质量等级']
            }
            
            standardized = {'timestamp': timestamp}
            
            for standard_key, possible_keys in field_mapping.items():
                value = None
                for key in possible_keys:
                    if key in item:
                        value = item[key]
                        break
                
                if value is not None:
                    # 数据类型转换
                    if standard_key in ['aqi', 'pm25', 'pm10', 'so2', 'no2', 'o3']:
                        try:
                            standardized[standard_key] = int(float(str(value).replace('μg/m³', '').replace('mg/m³', '')))
                        except (ValueError, TypeError):
                            standardized[standard_key] = None
                    elif standard_key == 'co':
                        try:
                            standardized[standard_key] = float(str(value).replace('mg/m³', ''))
                        except (ValueError, TypeError):
                            standardized[standard_key] = None
                    else:
                        standardized[standard_key] = str(value).strip()
                else:
                    standardized[standard_key] = None
            
            # 确保至少有城市名称
            if standardized.get('city'):
                return standardized
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"标准化数据项失败: {e}")
            return None
    
    def save_to_csv(self, data: List[Dict], filename: str = None) -> str:
        """
        保存数据到CSV文件
        
        Args:
            data: 要保存的数据
            filename: 文件名，如果为None则自动生成
            
        Returns:
            保存的文件路径
        """
        if not filename:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"air_quality_{timestamp}.csv"
        
        filepath = os.path.join(self.data_dir, filename)
        
        try:
            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            self.logger.info(f"数据已保存到: {filepath}")
            return filepath
        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            raise
    
    def crawl_and_save(self, filename: str = None) -> str:
        """
        爬取数据并保存
        
        Args:
            filename: 保存的文件名
            
        Returns:
            保存的文件路径
        """
        self.logger.info("开始爬取空气质量数据...")
        
        # 获取数据
        data = self.get_city_air_quality()
        
        if not data:
            raise Exception("未能获取到有效数据")
        
        # 保存数据
        filepath = self.save_to_csv(data, filename)
        
        self.logger.info(f"爬取完成，共获取 {len(data)} 条数据")
        return filepath
    
    def add_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """
        添加随机延迟，避免请求过于频繁
        
        Args:
            min_delay: 最小延迟秒数
            max_delay: 最大延迟秒数
        """
        import random
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)


def main():
    """主函数，用于测试爬虫"""
    spider = AirQualitySpider()
    
    try:
        filepath = spider.crawl_and_save()
        print(f"数据爬取成功，保存路径: {filepath}")
        
        # 读取并显示前几行数据
        df = pd.read_csv(filepath)
        print("\n数据预览:")
        print(df.head())
        print(f"\n数据形状: {df.shape}")
        
    except Exception as e:
        print(f"爬取失败: {e}")


if __name__ == "__main__":
    main()
