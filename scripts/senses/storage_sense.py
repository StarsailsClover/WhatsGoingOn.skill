#!/usr/bin/env python3
"""
存储感知模块 - Storage Sense (Cross-Platform)
让 AI Agent 感知磁盘使用情况

包括：磁盘总容量、已用、可用、使用百分比等

支持平台: Linux / macOS / Windows

Author: GitHub@StarsailsClover
Version: v26.0 Alpha 2
"""

import os
import sys
import platform
import subprocess
import json


_PLATFORM = platform.system()


def get_disk_usage(path: str = None) -> dict:
    """
    获取磁盘使用情况

    Args:
        path: 要检测的路径，默认根据平台选择根目录

    Returns:
        磁盘使用信息字典
    """
    if path is None:
        if _PLATFORM == "Windows":
            path = "C:\\"
        else:
            path = "/"

    result = {
        "sense_type": "storage",
        "path": path,
        "total": None,
        "total_human": None,
        "used": None,
        "used_human": None,
        "available": None,
        "available_human": None,
        "free": None,
        "free_human": None,
        "usage_percent": None
    }

    try:
        if _PLATFORM == "Linux":
            return _disk_usage_linux(result, path)
        elif _PLATFORM == "Darwin":
            return _disk_usage_macos(result, path)
        elif _PLATFORM == "Windows":
            return _disk_usage_windows(result, path)
        else:
            # 通用回退：使用 shutil
            return _disk_usage_shutil(result, path)
    except Exception as e:
        result["error"] = str(e)
        return result


def _disk_usage_linux(result, path):
    """Linux: os.statvfs / df"""
    # 方法1: os.statvfs
    try:
        stat = os.statvfs(path)
        total = stat.f_frsize * stat.f_blocks
        free = stat.f_frsize * stat.f_bfree
        available = stat.f_frsize * stat.f_bavail
        used = total - free

        result["total"] = total
        result["free"] = free
        result["available"] = available
        result["used"] = used
        result["usage_percent"] = round((used / total) * 100, 2) if total > 0 else 0
        result["source"] = "statvfs"
        _format_result(result)
        return result
    except Exception:
        pass

    # 方法2: df 命令
    try:
        output = subprocess.check_output(
            ["df", "-B1", path], universal_newlines=True, timeout=5
        )
        lines = output.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 6:
                result["total"] = int(parts[1])
                result["used"] = int(parts[2])
                result["available"] = int(parts[3])
                result["usage_percent"] = float(parts[4].replace("%", ""))
                result["source"] = "df"
                _format_result(result)
                return result
    except Exception:
        pass

    result["error"] = "无法获取磁盘信息"
    return result


def _disk_usage_macos(result, path):
    """macOS: df"""
    try:
        output = subprocess.check_output(
            ["df", "-k", path], universal_newlines=True, timeout=5
        )
        lines = output.strip().split("\n")
        if len(lines) >= 2:
            parts = lines[1].split()
            if len(parts) >= 6:
                total_kb = int(parts[1])
                used_kb = int(parts[2])
                avail_kb = int(parts[3])
                pct = parts[4].replace("%", "")
                try:
                    result["usage_percent"] = float(pct)
                except ValueError:
                    result["usage_percent"] = None

                result["total"] = total_kb * 1024
                result["used"] = used_kb * 1024
                result["available"] = avail_kb * 1024
                result["free"] = result["available"]
                result["source"] = "df"
                _format_result(result)
                return result
    except Exception as e:
        result["error"] = str(e)

    # 回退
    return _disk_usage_shutil(result, path)


def _disk_usage_windows(result, path):
    """Windows: psutil / wmic / PowerShell"""
    # 方法1: psutil
    try:
        import shutil
        usage = shutil.disk_usage(path)
        result["total"] = usage.total
        result["used"] = usage.used
        result["free"] = usage.free
        result["available"] = usage.free
        result["usage_percent"] = round((usage.used / usage.total) * 100, 2) if usage.total > 0 else 0
        result["source"] = "shutil"
        _format_result(result)
        return result
    except Exception:
        pass

    # 方法2: wmic
    try:
        output = subprocess.check_output(
            ["wmic", "logicaldisk", "where", f"DeviceID='{path[0]}'",
             "get", "Size,FreeSpace,DeviceID", "/format:csv"],
            universal_newlines=True, timeout=10
        )
        lines = output.strip().split("\n")
        for line in lines:
            parts = line.strip().split(",")
            if len(parts) >= 3 and parts[1]:
                total = int(parts[1]) if parts[1].strip() else 0
                free = int(parts[2]) if parts[2].strip() else 0
                result["total"] = total
                result["free"] = free
                result["available"] = free
                result["used"] = total - free
                result["usage_percent"] = round(((total - free) / total) * 100, 2) if total > 0 else 0
                result["source"] = "wmic"
                _format_result(result)
                return result
    except Exception:
        pass

    # 方法3: PowerShell
    try:
        output = subprocess.check_output(
            ["powershell", "-Command",
             f"Get-PSDrive -Name {path[0]} | Select-Object Used, Free | ConvertTo-Json"],
            universal_newlines=True, timeout=10
        )
        data = json.loads(output)
        used = int(data.get("Used", 0))
        free = int(data.get("Free", 0))
        result["total"] = used + free
        result["used"] = used
        result["free"] = free
        result["available"] = free
        result["usage_percent"] = round((used / (used + free)) * 100, 2) if (used + free) > 0 else 0
        result["source"] = "powershell"
        _format_result(result)
        return result
    except Exception as e:
        result["error"] = str(e)

    return result


def _disk_usage_shutil(result, path):
    """通用回退: shutil.disk_usage"""
    try:
        import shutil
        usage = shutil.disk_usage(path)
        result["total"] = usage.total
        result["used"] = usage.used
        result["free"] = usage.free
        result["available"] = usage.free
        result["usage_percent"] = round((usage.used / usage.total) * 100, 2) if usage.total > 0 else 0
        result["source"] = "shutil"
        _format_result(result)
    except Exception as e:
        result["error"] = str(e)
    return result


def _format_bytes(bytes_val: int) -> str:
    if bytes_val is None:
        return "N/A"
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 ** 2:
        return f"{round(bytes_val / 1024, 2)} KB"
    elif bytes_val < 1024 ** 3:
        return f"{round(bytes_val / 1024 ** 2, 2)} MB"
    elif bytes_val < 1024 ** 4:
        return f"{round(bytes_val / 1024 ** 3, 2)} GB"
    else:
        return f"{round(bytes_val / 1024 ** 4, 2)} TB"


def _format_result(result):
    """格式化结果为人类可读"""
    for key in ["total", "used", "available", "free"]:
        result[f"{key}_human"] = _format_bytes(result.get(key, 0))


def get_all_disks() -> dict:
    """获取所有挂载点的磁盘使用情况"""
    result = {"sense_type": "storage_all", "disks": []}

    try:
        if _PLATFORM == "Linux":
            output = subprocess.check_output(
                ["df", "-h", "--output=target,size,used,avail,pcent,device"],
                universal_newlines=True, timeout=5
            )
            lines = output.strip().split("\n")[1:]  # skip header
            for line in lines:
                parts = line.split()
                if len(parts) >= 5:
                    disk = {
                        "path": parts[0],
                        "total_human": parts[1],
                        "used_human": parts[2],
                        "available_human": parts[3],
                        "usage_percent": float(parts[4].replace("%", ""))
                    }
                    result["disks"].append(disk)

        elif _PLATFORM == "Darwin":
            output = subprocess.check_output(
                ["df", "-h"], universal_newlines=True, timeout=5
            )
            lines = output.strip().split("\n")[1:]
            for line in lines:
                parts = line.split()
                if len(parts) >= 6:
                    disk = {
                        "device": parts[0],
                        "total_human": parts[1],
                        "used_human": parts[2],
                        "available_human": parts[3],
                        "usage_percent": float(parts[4].replace("%", "")),
                        "path": parts[5] if len(parts) > 5 else ""
                    }
                    result["disks"].append(disk)

        elif _PLATFORM == "Windows":
            output = subprocess.check_output(
                ["powershell", "-Command",
                 "Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{N='total';E={$_.Used+$_.Free}}, Used, Free, @{N='pct';E={if(($_.Used+$_.Free)-gt 0){[math]::Round($_.Used/($_.Used+$_.Free)*100,1)}else{0}}} | ConvertTo-Json"],
                universal_newlines=True, timeout=10
            )
            data = json.loads(output)
            if isinstance(data, dict):
                data = [data]
            for d in data:
                total = d.get("total", 0)
                used = d.get("Used", 0)
                disk = {
                    "device": d.get("Name", ""),
                    "total_human": _format_bytes(total),
                    "used_human": _format_bytes(used),
                    "available_human": _format_bytes(d.get("Free", 0)),
                    "usage_percent": d.get("pct", 0)
                }
                result["disks"].append(disk)

    except Exception as e:
        result["error"] = str(e)

    return result


def get_storage_summary() -> str:
    """获取存储状态的简洁文本摘要"""
    info = get_disk_usage()

    if info.get("error"):
        return f"💾 存储信息获取失败: {info['error']}"

    parts = []
    if info.get("path"):
        parts.append(f"[{info['path']}]")
    if info.get("total_human"):
        parts.append(f"总量 {info['total_human']}")
    if info.get("available_human"):
        parts.append(f"可用 {info['available_human']}")
    if info.get("usage_percent") is not None:
        parts.append(f"({info['usage_percent']}%)")

    return "💾 存储: " + " ".join(parts) if parts else "💾 存储: 信息不可用"


if __name__ == "__main__":
    print(f"=== 存储感知测试 ({_PLATFORM}) ===")
    print(json.dumps(get_disk_usage(), ensure_ascii=False, indent=2))
    print("\n所有磁盘:")
    print(json.dumps(get_all_disks(), ensure_ascii=False, indent=2))
    print("\n摘要:", get_storage_summary())
