#!/usr/bin/env python3
"""
系统状态感知模块 - System Sense (Cross-Platform)
让 AI Agent 感知当前运行环境的系统状态

支持平台: Linux / macOS / Windows

Author: GitHub@StarsailsClover
Version: v26.0 Alpha 2
"""

import os
import sys
import platform
import subprocess
import json
import time
import re


_PLATFORM = platform.system()  # "Linux", "Darwin", "Windows"


def get_system_info() -> dict:
    """获取系统基本信息"""
    return {
        "sense_type": "system_info",
        "os": platform.system(),
        "os_release": platform.release(),
        "os_version": platform.version(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "platform": sys.platform,
        "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
        "home_directory": os.path.expanduser("~"),
        "current_directory": os.getcwd(),
        "pid": os.getpid()
    }


def get_cpu_info() -> dict:
    """获取 CPU 信息和使用率"""
    result = {
        "sense_type": "cpu",
        "cpu_count_logical": os.cpu_count(),
        "cpu_count_physical": None,
        "load_average": None,
        "usage_percent": None
    }

    if _PLATFORM == "Linux":
        return _cpu_info_linux(result)
    elif _PLATFORM == "Darwin":
        return _cpu_info_macos(result)
    elif _PLATFORM == "Windows":
        return _cpu_info_windows(result)
    else:
        return result


def _cpu_info_linux(result):
    """Linux CPU 信息"""
    # Load average
    if hasattr(os, "getloadavg"):
        load = os.getloadavg()
        result["load_average"] = {
            "1min": round(load[0], 2),
            "5min": round(load[1], 2),
            "15min": round(load[2], 2)
        }

    # /proc/cpuinfo
    try:
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r") as f:
                cpuinfo = f.read()
            physical_ids = set()
            core_ids = set()
            for line in cpuinfo.split("\n"):
                if line.startswith("physical id"):
                    physical_ids.add(line.split(":")[1].strip())
                if line.startswith("core id"):
                    core_ids.add(line.split(":")[1].strip())
            if physical_ids and core_ids:
                result["cpu_count_physical"] = len(physical_ids) * len(core_ids)
            for line in cpuinfo.split("\n"):
                if line.startswith("model name"):
                    result["cpu_model"] = line.split(":")[1].strip()
                    break
    except:
        pass

    # CPU 使用率
    try:
        if os.path.exists("/proc/stat"):
            with open("/proc/stat", "r") as f:
                first_line = f.readline().split()
            if first_line and first_line[0] == "cpu":
                user, nice, system = int(first_line[1]), int(first_line[2]), int(first_line[3])
                idle, iowait = int(first_line[4]), int(first_line[5]) if len(first_line) > 5 else 0
                total = user + nice + system + idle + iowait
                used = user + nice + system
                result["usage_percent"] = round((used / total) * 100, 2) if total > 0 else 0
    except:
        pass

    return result


def _cpu_info_macos(result):
    """macOS CPU 信息"""
    # 物理核心数
    try:
        output = subprocess.check_output(["sysctl", "-n", "hw.physicalcpu"], universal_newlines=True, timeout=5)
        result["cpu_count_physical"] = int(output.strip())
    except:
        pass

    # CPU 型号
    try:
        output = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], universal_newlines=True, timeout=5)
        result["cpu_model"] = output.strip()
    except:
        pass

    # CPU 频率
    try:
        output = subprocess.check_output(["sysctl", "-n", "hw.cpufrequency"], universal_newlines=True, timeout=5)
        freq = int(output.strip())
        result["cpu_frequency_hz"] = freq
        result["cpu_frequency_ghz"] = round(freq / 1_000_000_000, 2)
    except:
        pass

    # 负载平均值
    try:
        la = os.getloadavg()
        result["load_average"] = {"1min": round(la[0], 2), "5min": round(la[1], 2), "15min": round(la[2], 2)}
    except:
        pass

    # CPU 使用率
    try:
        output = subprocess.check_output(["top", "-l", "1", "-n", "0"], universal_newlines=True, timeout=10)
        for line in output.split("\n"):
            if "CPU usage" in line:
                parts = line.split(":")[-1].strip()
                idle_pct = 0
                for part in parts.split(","):
                    part = part.strip()
                    if "idle" in part:
                        idle_pct = float(part.split("%")[0].strip())
                        break
                result["usage_percent"] = round(100 - idle_pct, 2)
                break
    except:
        pass

    return result


def _cpu_info_windows(result):
    """Windows CPU 信息"""
    try:
        import wmi
        c = wmi.WMI()
        processors = c.Win32_Processor()
        if processors:
            proc = processors[0]
            result["cpu_model"] = proc.Name
            result["cpu_count_physical"] = proc.NumberOfCores
            result["cpu_count_logical"] = proc.NumberOfLogicalProcessors
            result["cpu_frequency_mhz"] = proc.MaxClockSpeed
            cpu_usage = sum(p.LoadPercentage for p in processors) / len(processors)
            result["usage_percent"] = cpu_usage
    except ImportError:
        try:
            output = subprocess.check_output(
                ["powershell", "-Command",
                 "Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed, LoadPercentage | ConvertTo-Json"],
                universal_newlines=True, timeout=10)
            data = json.loads(output)
            if isinstance(data, list):
                data = data[0]
            result["cpu_model"] = data.get("Name", "")
            result["cpu_count_physical"] = data.get("NumberOfCores")
            result["cpu_count_logical"] = data.get("NumberOfLogicalProcessors")
            result["cpu_frequency_mhz"] = data.get("MaxClockSpeed")
            result["usage_percent"] = data.get("LoadPercentage", 0)
        except:
            pass
    except:
        pass

    if "usage_percent" in result:
        result["load_average"] = {
            "1min": result["usage_percent"],
            "5min": result["usage_percent"],
            "15min": result["usage_percent"]
        }

    return result


def get_memory_info() -> dict:
    """获取内存使用信息"""
    result = {"sense_type": "memory"}

    if _PLATFORM == "Linux":
        return _mem_info_linux(result)
    elif _PLATFORM == "Darwin":
        return _mem_info_macos(result)
    elif _PLATFORM == "Windows":
        return _mem_info_windows(result)
    else:
        return result


def _mem_info_linux(result):
    try:
        if os.path.exists("/proc/meminfo"):
            meminfo = {}
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val = parts[1].strip().split()[0]
                        meminfo[key] = int(val) * 1024

            result["total"] = meminfo.get("MemTotal", 0)
            result["free"] = meminfo.get("MemFree", 0)
            result["available"] = meminfo.get("MemAvailable", 0)
            result["used"] = result["total"] - result["available"]
            result["buffers"] = meminfo.get("Buffers", 0)
            result["cached"] = meminfo.get("Cached", 0)
            result["swap_total"] = meminfo.get("SwapTotal", 0)
            result["swap_free"] = meminfo.get("SwapFree", 0)
            result["swap_used"] = result["swap_total"] - result["swap_free"]
            result["usage_percent"] = round((result["used"] / result["total"]) * 100, 2) if result["total"] > 0 else 0
            result["swap_usage_percent"] = round((result["swap_used"] / result["swap_total"]) * 100, 2) if result["swap_total"] > 0 else 0
            for key in ["total", "free", "available", "used", "buffers", "cached", "swap_total", "swap_free", "swap_used"]:
                result[f"{key}_human"] = _format_bytes(result.get(key, 0))
    except:
        pass
    return result


def _mem_info_macos(result):
    try:
        output = subprocess.check_output(["sysctl", "-n", "hw.memsize"], universal_newlines=True, timeout=5)
        total_bytes = int(output.strip())
        result["total"] = total_bytes
        result["total_human"] = _format_bytes(total_bytes)
    except:
        pass

    try:
        output = subprocess.check_output(["vm_stat"], universal_newlines=True, timeout=5)
        page_size = 4096
        stats = {}
        for line in output.split("\n"):
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower().replace(" ", "_")
                value = value.strip().rstrip(".")
                try:
                    stats[key] = int(value)
                except:
                    pass

        if "pages_free" in stats:
            result["free"] = stats["pages_free"] * page_size
            result["free_human"] = _format_bytes(result["free"])
        if "pages_active" in stats and "pages_wired" in stats:
            used_pages = stats.get("pages_active", 0) + stats.get("pages_wired", 0)
            result["used"] = used_pages * page_size
            result["used_human"] = _format_bytes(result["used"])
        if "total" in result and "used" in result:
            result["usage_percent"] = round((result["used"] / result["total"]) * 100, 2)
    except:
        pass

    return result


def _mem_info_windows(result):
    try:
        output = subprocess.check_output(
            ["powershell", "-Command",
             "$os = Get-CimInstance Win32_OperatingSystem; [PSCustomObject]@{total=$os.TotalVisibleMemorySize; free=$os.FreePhysicalMemory; used=$os.TotalVisibleMemorySize - $os.FreePhysicalMemory} | ConvertTo-Json"],
            universal_newlines=True, timeout=10)
        data = json.loads(output)
        result["total"] = int(data.get("total", 0)) * 1024
        result["free"] = int(data.get("free", 0)) * 1024
        result["used"] = int(data.get("used", 0)) * 1024
        result["usage_percent"] = round((result["used"] / result["total"]) * 100, 2) if result["total"] > 0 else 0
        for key in ["total", "free", "used"]:
            result[f"{key}_human"] = _format_bytes(result.get(key, 0))
    except:
        pass
    return result


def get_disk_info(path: str = None) -> dict:
    """获取磁盘使用信息"""
    if path is None:
        path = "/" if _PLATFORM != "Windows" else "C:\\"

    result = {"sense_type": "disk", "path": path}

    try:
        if _PLATFORM == "Windows":
            import shutil
            usage = shutil.disk_usage(path)
        else:
            stat = os.statvfs(path)
            usage = type("Usage", (), {})()
            usage.total = stat.f_frsize * stat.f_blocks
            usage.free = stat.f_frsize * stat.f_bfree
            usage.available = stat.f_frsize * stat.f_bavail
            usage.used = usage.total - usage.free

        result["total"] = usage.total
        result["free"] = usage.free
        result["available"] = getattr(usage, "available", usage.free)
        result["used"] = usage.used
        result["usage_percent"] = round((usage.used / usage.total) * 100, 2) if usage.total > 0 else 0
        for key in ["total", "free", "available", "used"]:
            result[f"{key}_human"] = _format_bytes(result.get(key, 0))
    except Exception as e:
        result["error"] = str(e)

    return result


def get_process_info() -> dict:
    """获取进程信息"""
    result = {
        "sense_type": "process",
        "current_pid": os.getpid(),
        "process_count": None,
        "top_processes": []
    }

    try:
        if _PLATFORM == "Windows":
            output = subprocess.check_output(
                ["powershell", "-Command",
                 "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10 | ConvertTo-Json"],
                universal_newlines=True, timeout=5)
            processes = json.loads(output)
            if isinstance(processes, dict):
                processes = [processes]
            result["process_count"] = len(processes)
            result["top_processes"] = [
                {"name": p.get("ProcessName", ""), "pid": p.get("Id", 0),
                 "cpu": p.get("CPU", 0), "mem_mb": round(p.get("WorkingSet64", 0) / 1024 / 1024, 1)}
                for p in processes
            ]
        else:
            output = subprocess.check_output(["ps", "aux"], universal_newlines=True, timeout=5)
            lines = output.strip().split("\n")
            result["process_count"] = max(len(lines) - 1, 0)
            if len(lines) > 1:
                processes = []
                for line in lines[1:11]:
                    parts = line.split(None, 10)
                    if len(parts) >= 11:
                        processes.append({
                            "user": parts[0], "pid": int(parts[1]),
                            "cpu_percent": float(parts[2]), "mem_percent": float(parts[3]),
                            "vsz": int(parts[4]), "rss": int(parts[5]),
                            "tty": parts[6], "stat": parts[7],
                            "start": parts[8], "time": parts[9], "command": parts[10]
                        })
                result["top_processes"] = processes
    except Exception as e:
        result["error"] = str(e)

    return result


def get_uptime() -> dict:
    """获取系统运行时间"""
    result = {"sense_type": "uptime"}

    try:
        if _PLATFORM == "Windows":
            output = subprocess.check_output(
                ["powershell", "-Command",
                 "(Get-CimInstance Win32_OperatingSystem).LastBootUpTime"],
                universal_newlines=True, timeout=5)
            boot_str = output.strip()
            # Parse ISO format
            boot_time = time.mktime(time.strptime(boot_str[:19], "%Y-%m-%dT%H:%M:%S"))
        elif _PLATFORM == "Darwin":
            output = subprocess.check_output(["sysctl", "-n", "kern.boottime"], universal_newlines=True, timeout=5)
            match = re.search(r'sec\s*=\s*(\d+)', output)
            if match:
                boot_time = int(match.group(1))
            else:
                boot_time = time.time() - 3600
        else:
            with open("/proc/uptime", "r") as f:
                uptime_seconds = float(f.readline().split()[0])
            return _format_uptime(result, uptime_seconds)

        uptime_seconds = time.time() - boot_time
        return _format_uptime(result, uptime_seconds)
    except Exception as e:
        result["error"] = str(e)

    return result


def _format_uptime(result, uptime_seconds):
    result["uptime_seconds"] = int(uptime_seconds)
    result["uptime_minutes"] = uptime_seconds // 60
    result["uptime_hours"] = uptime_seconds / 3600
    result["uptime_days"] = uptime_seconds / 86400
    days = int(uptime_seconds // 86400)
    hours = int((uptime_seconds % 86400) // 3600)
    minutes = int((uptime_seconds % 3600) // 60)
    parts = []
    if days > 0: parts.append(f"{days}天")
    if hours > 0: parts.append(f"{hours}小时")
    if minutes > 0: parts.append(f"{minutes}分钟")
    result["uptime_human"] = "".join(parts) if parts else "不到1分钟"
    return result


def _format_bytes(bytes_val: int) -> str:
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


def get_full_system_status() -> dict:
    """获取完整的系统状态快照"""
    return {
        "sense_type": "system_full",
        "timestamp": time.time(),
        "system_info": get_system_info(),
        "cpu": get_cpu_info(),
        "memory": get_memory_info(),
        "disk": get_disk_info(),
        "process": get_process_info(),
        "uptime": get_uptime()
    }


if __name__ == "__main__":
    print("=== 系统状态感知测试 ===")
    print(json.dumps(get_full_system_status(), ensure_ascii=False, indent=2))
