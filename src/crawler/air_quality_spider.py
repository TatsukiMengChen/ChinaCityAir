"""
中国环境监测总站空气质量数据爬虫
数据源：https://air.cnemc.cn:18007/
"""

import requests
import time
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional
import os

class AirQualitySpider:
    """空气质量数据爬虫类"""

    def __init__(self, base_url: str = "https://air.cnemc.cn:18007"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
        })
        self.setup_logging()
        self.data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'raw')
        os.makedirs(self.data_dir, exist_ok=True)
        self.progress_callback = None
        self.status_callback = None
        self.should_stop = False

    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('crawler.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def set_progress_callback(self, callback):
        self.progress_callback = callback

    def set_status_callback(self, callback):
        self.status_callback = callback

    def stop(self):
        self.should_stop = True

    def get_all_city_realtime_aqi(self) -> List[Dict]:
        """获取所有城市实时AQI数据，并标准化为通用格式"""
        url = f"{self.base_url}/CityData/GetAllCityRealTimeAQIModels"
        resp = self.session.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        # 标准化数据
        standardized = [self._standardize_api_item(item) for item in data]
        return standardized

    def _standardize_api_item(self, item: Dict) -> Dict:
        """将API返回的单条数据转换为通用格式"""
        # 字段映射
        return {
            "city": item.get("Area") or item.get("CityName") or "",
            "aqi": item.get("AQI"),
            "pm25": item.get("PM2_5") if "PM2_5" in item else item.get("PM2_5Level"),
            "pm10": item.get("PM10") if "PM10" in item else item.get("PM10Level"),
            "so2": item.get("SO2") if "SO2" in item else item.get("SO2Level"),
            "no2": item.get("NO2") if "NO2" in item else item.get("NO2Level"),
            "co": item.get("CO") if "CO" in item else item.get("COLevel"),
            "o3": item.get("O3") if "O3" in item else item.get("O3Level"),
            "quality": item.get("Quality"),
            "timestamp": item.get("TimePoint") or datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def crawl_data(self, count: int = 100, delay: float = 1.0) -> Optional[str]:
        """
        爬取指定数量的数据（每次获取全部城市，按count截断）
        Args:
            count: 爬取数据条数
            delay: 请求间隔（仅用于多次循环时）
        Returns:
            保存的文件路径
        """
        try:
            if self.status_callback:
                self.status_callback("开始爬取空气质量数据...")

            all_data = []
            current_count = 0

            # 只需请求一次即可获得全部城市数据
            data = self.get_all_city_realtime_aqi()
            if data:
                all_data.extend(data[:count])
                current_count = len(all_data)
                if self.progress_callback:
                    self.progress_callback(current_count, count)
                if self.status_callback:
                    self.status_callback(f"已获取 {current_count} 条数据")
            else:
                raise Exception("未能获取到有效数据")

            if self.should_stop:
                if self.status_callback:
                    self.status_callback("爬取已停止")
                return None

            filepath = self.save_to_csv(all_data)
            if self.status_callback:
                self.status_callback(f"爬取完成，共获取 {len(all_data)} 条数据")
            return filepath

        except Exception as e:
            if self.status_callback:
                self.status_callback(f"爬取失败: {str(e)}")
            self.logger.error(f"爬取数据失败: {e}")
            return None

    def save_to_csv(self, data: List[Dict], filename: str = None) -> str:
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

def main():
    spider = AirQualitySpider()
    try:
        filepath = spider.crawl_data(count=100)
        print(f"数据爬取成功，保存路径: {filepath}")
        df = pd.read_csv(filepath)
        print("\n数据预览:")
        print(df.head())
        print(f"\n数据形状: {df.shape}")
    except Exception as e:
        print(f"爬取失败: {e}")

if __name__ == "__main__":
    main()
