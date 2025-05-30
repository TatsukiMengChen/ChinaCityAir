import requests
import sys

BASE_URL = "https://air.cnemc.cn:18007/CityData"

def get_all_provinces():
    url = f"{BASE_URL}/GetProvince"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def get_cities_by_province(pid):
    url = f"{BASE_URL}/GetCitiesByPid?pid={pid}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def get_all_city_realtime_aqi():
    url = f"{BASE_URL}/GetAllCityRealTimeAQIModels"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def get_city_aqi_detail(city_code):
    url = f"{BASE_URL}/GetAQIDataPublishLiveInfo?cityCode={city_code}"
    resp = requests.get(url)
    resp.raise_for_status()
    return resp.json()

def main():
    if len(sys.argv) < 2:
        print("用法：python aqi_spider.py [provinces|cities <pid>|all|detail <city_code>]")
        return

    cmd = sys.argv[1]
    if cmd == "provinces":
        provinces = get_all_provinces()
        for p in provinces:
            print(f"{p['Id']}: {p['ProvinceName']} ({p['ProvinceJC']})")
    elif cmd == "cities":
        if len(sys.argv) < 3:
            print("请提供省份ID")
            return
        pid = sys.argv[2]
        cities = get_cities_by_province(pid)
        for c in cities:
            print(f"{c['CityCode']}: {c['CityName']} ({c['CityJC']})")
    elif cmd == "all":
        data = get_all_city_realtime_aqi()
        for item in data:
            print(f"{item['Area']}({item['CityCode']}): AQI={item['AQI']} 质量={item['Quality']} 主污染物={item['PrimaryPollutant']}")
    elif cmd == "detail":
        if len(sys.argv) < 3:
            print("请提供城市代码")
            return
        city_code = sys.argv[2]
        detail = get_city_aqi_detail(city_code)
        print(detail)
    else:
        print("未知命令")

if __name__ == "__main__":
    main()
