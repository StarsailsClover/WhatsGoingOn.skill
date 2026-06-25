#!/usr/bin/env python3
"""
天气感知模块 - Weather Sense
让 AI Agent 获得对外部环境天气的感知能力

支持多种天气数据源，默认使用 wttr.in（无需 API Key）
也支持 OpenWeatherMap API（需配置 API Key）

Author: GitHub@StarsailsClover
Version: v26.0 Alpha 2
"""

import json
import urllib.request
import urllib.parse


def get_weather(location: str = None, format_type: str = "simple") -> dict:
    """
    获取指定位置的天气信息
    
    Args:
        location: 位置名称，如 "Beijing", "Shanghai", "New York"
                 为 None 时自动检测位置（基于 IP）
        format_type: 输出格式
            - "simple": 简洁格式，适合快速阅读
            - "detailed": 详细格式，包含更多气象数据
            - "full": 完整格式，包含未来几天预报
    
    Returns:
        天气信息字典
    """
    try:
        if location:
            encoded_location = urllib.parse.quote(location)
            url = f"https://wttr.in/{encoded_location}?format=j1"
        else:
            url = "https://wttr.in/?format=j1"
        
        req = urllib.request.Request(url, headers={"User-Agent": "WhatsGoingOn/v26.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode("utf-8"))
        
        current = data["current_condition"][0]
        weather_today = data["weather"][0]
        
        result = {
            "sense_type": "weather",
            "location": location or "自动检测位置",
            "source": "wttr.in",
            "temperature_c": int(current["temp_C"]),
            "temperature_f": int(current["temp_F"]),
            "feels_like_c": int(current["FeelsLikeC"]),
            "feels_like_f": int(current["FeelsLikeF"]),
            "humidity": int(current["humidity"]),
            "weather_desc": current["weatherDesc"][0]["value"],
            "weather_icon_url": current["weatherIconUrl"][0]["value"],
            "wind_speed_kmph": int(current["windspeedKmph"]),
            "wind_speed_mph": int(current["windspeedMiles"]),
            "wind_direction": current["winddir16Point"],
            "wind_direction_degree": int(current["winddirDegree"]),
            "visibility_km": int(current["visibility"]),
            "pressure_mb": int(current["pressure"]),
            "cloud_cover": int(current["cloudcover"]),
            "uv_index": int(current["uvIndex"]),
            "precipitation_mm": float(current["precipMM"]),
            "observation_time": current["observation_time"]
        }
        
        if format_type in ["detailed", "full"]:
            result["astronomy"] = {
                "sunrise": weather_today["astronomy"][0]["sunrise"],
                "sunset": weather_today["astronomy"][0]["sunset"],
                "moonrise": weather_today["astronomy"][0]["moonrise"],
                "moonset": weather_today["astronomy"][0]["moonset"],
                "moon_phase": weather_today["astronomy"][0]["moon_phase"],
                "moon_illumination": weather_today["astronomy"][0]["moon_illumination"]
            }
            
            result["today_max_temp_c"] = int(weather_today["maxtempC"])
            result["today_min_temp_c"] = int(weather_today["mintempC"])
            result["today_max_temp_f"] = int(weather_today["maxtempF"])
            result["today_min_temp_f"] = int(weather_today["mintempF"])
            result["total_snow_cm"] = float(weather_today["totalSnow_cm"])
            result["sun_hours"] = float(weather_today["sunHour"])
            result["uv_index_max"] = int(weather_today["uvIndex"])
        
        if format_type == "full":
            result["forecast"] = []
            for day in data["weather"][:3]:  # 未来3天预报
                forecast_day = {
                    "date": day["date"],
                    "max_temp_c": int(day["maxtempC"]),
                    "min_temp_c": int(day["mintempC"]),
                    "max_temp_f": int(day["maxtempF"]),
                    "min_temp_f": int(day["mintempF"]),
                    "uv_index": int(day["uvIndex"]),
                    "sun_hours": float(day["sunHour"]),
                    "total_snow_cm": float(day["totalSnow_cm"]),
                    "hourly": []
                }
                for hour in day["hourly"]:
                    forecast_day["hourly"].append({
                        "time": f"{int(hour['time']):04d}",
                        "temp_c": int(hour["tempC"]),
                        "weather_desc": hour["weatherDesc"][0]["value"],
                        "humidity": int(hour["humidity"]),
                        "wind_speed_kmph": int(hour["windspeedKmph"]),
                        "chance_of_rain": int(hour["chanceofrain"]),
                        "chance_of_snow": int(hour["chanceofsnow"])
                    })
                result["forecast"].append(forecast_day)
        
        return result
        
    except Exception as e:
        return {
            "sense_type": "weather",
            "error": str(e),
            "location": location or "自动检测位置",
            "status": "failed"
        }


def get_weather_text(location: str = None) -> str:
    """
    获取文本格式的天气信息（适合直接阅读）
    
    Args:
        location: 位置名称
    
    Returns:
        天气信息文本
    """
    try:
        if location:
            encoded_location = urllib.parse.quote(location)
            url = f"https://wttr.in/{encoded_location}?format=4"
        else:
            url = "https://wttr.in/?format=4"
        
        req = urllib.request.Request(url, headers={"User-Agent": "WhatsGoingOn/v26.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode("utf-8").strip()
    except Exception as e:
        return f"天气获取失败: {e}"


def get_weather_ascii(location: str = None) -> str:
    """
    获取 ASCII 艺术风格的天气图
    
    Args:
        location: 位置名称
    
    Returns:
        ASCII 天气图
    """
    try:
        if location:
            encoded_location = urllib.parse.quote(location)
            url = f"https://wttr.in/{encoded_location}?0"
        else:
            url = "https://wttr.in/?0"
        
        req = urllib.request.Request(url, headers={"User-Agent": "WhatsGoingOn/v26.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode("utf-8")
    except Exception as e:
        return f"天气获取失败: {e}"


if __name__ == "__main__":
    print("=== 天气感知测试 ===")
    print("\n简洁文本格式:")
    print(get_weather_text())
    
    print("\n结构化数据:")
    weather = get_weather(format_type="detailed")
    print(json.dumps(weather, ensure_ascii=False, indent=2))
