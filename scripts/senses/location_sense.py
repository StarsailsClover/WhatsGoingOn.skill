#!/usr/bin/env python3
"""
地理位置感知模块 - Location Sense
让 AI Agent 感知当前所在的地理位置

基于 IP 地址进行地理位置推断，支持多种数据源

Author: GitHub@StarsailsClover
Version: v26.0 Alpha 2
"""

import json
import urllib.request


def get_location_by_ip() -> dict:
    """
    基于 IP 地址获取地理位置信息
    
    Returns:
        地理位置信息字典
    """
    result = {
        "sense_type": "location",
        "method": "ip_geolocation",
        "accuracy": "approximate"
    }
    
    try:
        # 使用多个地理定位服务，提高可靠性
        services = [
            {
                "url": "https://ipapi.co/json/",
                "fields": {
                    "ip": "ip",
                    "city": "city",
                    "region": "region",
                    "region_code": "region_code",
                    "country": "country_name",
                    "country_code": "country_code",
                    "continent": "continent_code",
                    "postal": "postal",
                    "latitude": "latitude",
                    "longitude": "longitude",
                    "timezone": "timezone",
                    "utc_offset": "utc_offset",
                    "country_calling_code": "country_calling_code",
                    "currency": "currency",
                    "currency_name": "currency_name",
                    "languages": "languages",
                    "country_area": "country_area",
                    "country_population": "country_population",
                    "asn": "asn",
                    "org": "org"
                }
            },
            {
                "url": "https://ipinfo.io/json",
                "fields": {
                    "ip": "ip",
                    "city": "city",
                    "region": "region",
                    "country": "country",
                    "postal": "postal",
                    "timezone": "timezone",
                    "org": "org"
                }
            }
        ]
        
        for service in services:
            try:
                req = urllib.request.Request(
                    service["url"],
                    headers={"User-Agent": "WhatsGoingOn/v26.0"}
                )
                with urllib.request.urlopen(req, timeout=8) as response:
                    data = json.loads(response.read().decode("utf-8"))
                
                # 提取字段
                for target_key, source_key in service["fields"].items():
                    if source_key in data and data[source_key]:
                        result[target_key] = data[source_key]
                
                # 特殊处理 ipinfo 的 loc 字段
                if "loc" in data and "latitude" not in result:
                    loc_parts = data["loc"].split(",")
                    if len(loc_parts) == 2:
                        result["latitude"] = float(loc_parts[0])
                        result["longitude"] = float(loc_parts[1])
                
                result["source"] = service["url"]
                result["status"] = "success"
                break
            except Exception:
                continue
        
        if "status" not in result:
            result["status"] = "failed"
            result["error"] = "所有地理定位服务均不可用"
            
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
    
    return result


def get_timezone_info() -> dict:
    """
    获取时区信息
    
    Returns:
        时区信息字典
    """
    result = {
        "sense_type": "timezone"
    }
    
    try:
        import time
        import datetime
        
        # 获取本地时区
        local_tz = datetime.datetime.now(datetime.timezone.utc).astimezone().tzinfo
        utc_offset = datetime.datetime.now().astimezone().utcoffset()
        
        result["timezone_name"] = str(local_tz)
        result["utc_offset_hours"] = utc_offset.total_seconds() / 3600 if utc_offset else 0
        result["utc_offset_string"] = str(utc_offset) if utc_offset else "UTC+0"
        result["is_dst"] = time.daylight and time.localtime().tm_isdst > 0
        result["tzname"] = time.tzname
        
        # 尝试获取更详细的时区信息
        try:
            with open("/etc/timezone", "r") as f:
                result["timezone_file"] = f.read().strip()
        except:
            pass
        
        result["status"] = "success"
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
    
    return result


def get_nearby_places(latitude: float, longitude: float, radius: int = 1000) -> dict:
    """
    获取附近的地点（需要 API Key，预留接口）
    
    Args:
        latitude: 纬度
        longitude: 经度
        radius: 搜索半径（米）
    
    Returns:
        附近地点信息
    """
    # 预留接口，需要配置相应的地图 API Key 才能使用
    return {
        "sense_type": "nearby_places",
        "status": "not_configured",
        "message": "此功能需要配置地图服务 API Key",
        "latitude": latitude,
        "longitude": longitude,
        "radius": radius
    }


def format_location_readable(location_data: dict) -> str:
    """
    将地理位置信息格式化为人类可读的字符串
    
    Args:
        location_data: 地理位置数据字典
    
    Returns:
        格式化的位置字符串
    """
    parts = []
    
    if "city" in location_data:
        parts.append(location_data["city"])
    if "region" in location_data:
        parts.append(location_data["region"])
    if "country" in location_data:
        parts.append(location_data["country"])
    
    if not parts:
        return "未知位置"
    
    return ", ".join(parts)


if __name__ == "__main__":
    print("=== 地理位置感知测试 ===")
    
    print("\nIP 地理位置:")
    location = get_location_by_ip()
    print(json.dumps(location, ensure_ascii=False, indent=2))
    
    print("\n人类可读格式:")
    print(format_location_readable(location))
    
    print("\n时区信息:")
    print(json.dumps(get_timezone_info(), ensure_ascii=False, indent=2))
