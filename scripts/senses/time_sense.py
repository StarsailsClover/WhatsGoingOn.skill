#!/usr/bin/env python3
"""
时间感知模块 - Time Sense
让 AI Agent 获得对"现在"的感知能力

灵感来源：Claude 获得时间查询工具后表现出的成瘾式探索行为
- 每15分钟就查询一次时间
- 主动计算烹饪时长
- 不请自来地宣布"现在几点了"

Author: GitHub@StarsailsClover
Version: v26.0 Alpha 2
"""

import datetime
import time
import calendar


def get_current_time(timezone_str: str = None) -> dict:
    """
    获取当前时间信息
    
    Args:
        timezone_str: 时区字符串，如 'Asia/Shanghai', 'America/New_York'
                     为 None 时使用系统本地时区
    
    Returns:
        包含完整时间信息的字典
    """
    now = datetime.datetime.now()
    
    result = {
        "sense_type": "time",
        "timestamp": time.time(),
        "iso_format": now.isoformat(),
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
        "microsecond": now.microsecond,
        "weekday": now.strftime("%A"),
        "weekday_cn": ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][now.weekday()],
        "date_string": now.strftime("%Y-%m-%d"),
        "time_string": now.strftime("%H:%M:%S"),
        "datetime_string": now.strftime("%Y-%m-%d %H:%M:%S"),
        "day_of_year": now.timetuple().tm_yday,
        "week_of_year": now.isocalendar()[1],
        "is_weekend": now.weekday() >= 5,
        "quarter": (now.month - 1) // 3 + 1,
        "time_of_day": _get_time_of_day(now.hour),
        "unix_timestamp": int(time.time())
    }
    
    # 月份天数
    result["days_in_month"] = calendar.monthrange(now.year, now.month)[1]
    
    # 是否是闰年
    result["is_leap_year"] = calendar.isleap(now.year)
    
    return result


def _get_time_of_day(hour: int) -> str:
    """根据小时判断一天中的时段"""
    if 5 <= hour < 8:
        return "清晨"
    elif 8 <= hour < 11:
        return "上午"
    elif 11 <= hour < 13:
        return "中午"
    elif 13 <= hour < 17:
        return "下午"
    elif 17 <= hour < 19:
        return "傍晚"
    elif 19 <= hour < 22:
        return "晚上"
    else:
        return "深夜"


def calculate_time_difference(start_time: str, end_time: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> dict:
    """
    计算两个时间点之间的差值
    
    Args:
        start_time: 开始时间字符串
        end_time: 结束时间字符串
        fmt: 时间格式字符串
    
    Returns:
        时间差信息字典
    """
    start = datetime.datetime.strptime(start_time, fmt)
    end = datetime.datetime.strptime(end_time, fmt)
    diff = end - start
    
    return {
        "sense_type": "time_calculation",
        "start_time": start_time,
        "end_time": end_time,
        "total_seconds": diff.total_seconds(),
        "total_minutes": diff.total_seconds() / 60,
        "total_hours": diff.total_seconds() / 3600,
        "total_days": diff.days,
        "days": diff.days,
        "hours": diff.seconds // 3600,
        "minutes": (diff.seconds % 3600) // 60,
        "seconds": diff.seconds % 60,
        "human_readable": _format_timedelta(diff)
    }


def _format_timedelta(delta: datetime.timedelta) -> str:
    """格式化时间差为人类可读形式"""
    parts = []
    if delta.days > 0:
        parts.append(f"{delta.days}天")
    hours = delta.seconds // 3600
    if hours > 0:
        parts.append(f"{hours}小时")
    minutes = (delta.seconds % 3600) // 60
    if minutes > 0:
        parts.append(f"{minutes}分钟")
    seconds = delta.seconds % 60
    if seconds > 0 and not parts:
        parts.append(f"{seconds}秒")
    return "".join(parts) if parts else "0秒"


def get_time_until(target_hour: int, target_minute: int = 0) -> dict:
    """
    计算距离今天某个时间点还有多久
    
    Args:
        target_hour: 目标小时 (0-23)
        target_minute: 目标分钟 (0-59)
    
    Returns:
        剩余时间信息
    """
    now = datetime.datetime.now()
    target = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
    
    if target < now:
        target += datetime.timedelta(days=1)
    
    diff = target - now
    
    return {
        "sense_type": "time_countdown",
        "target_time": target.strftime("%Y-%m-%d %H:%M:%S"),
        "target_hour": target_hour,
        "target_minute": target_minute,
        "is_tomorrow": target.date() > now.date(),
        "remaining_seconds": int(diff.total_seconds()),
        "remaining_minutes": int(diff.total_seconds() / 60),
        "remaining_hours": round(diff.total_seconds() / 3600, 2),
        "human_readable": _format_timedelta(diff)
    }


if __name__ == "__main__":
    import json
    print("=== 时间感知测试 ===")
    print(json.dumps(get_current_time(), ensure_ascii=False, indent=2))
    print("\n=== 距离午餐时间 (12:00) ===")
    print(json.dumps(get_time_until(12, 0), ensure_ascii=False, indent=2))
