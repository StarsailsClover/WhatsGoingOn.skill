#!/usr/bin/env python3
"""
CPU 感知模块 - CPU Sense (Cross-Platform)
让 AI Agent 感知处理器状态

包括：CPU 使用率、核心数、频率、负载平均值等

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


def get_cpu_info() -> dict:
    """获取 CPU 详细信息和使用率"""
    result = {
        "sense_type": "cpu",
        "cpu_count_logical": os.cpu_count(),
        "cpu_count_physical": None,
        "cpu_model": None,
        "cpu_frequency_hz": None,
        "cpu_frequency_ghz": None,
        "load_average": None,
        "usage_percent": None
    }

    try:
        if _PLATFORM == "Linux":
            return _cpu_info_linux(result)
        elif _PLATFORM == "Darwin":
            return _cpu_info_macos(result)
        elif _PLATFORM == "Windows":
            return _cpu_info_windows(result)
        else:
            result["error"] = f"不支持的平台: {_PLATFORM}"
            return result
    except Exception as e:
        result["error"] = str(e)
        return result


def _cpu_info_linux(result):
    """Linux: /proc/cpuinfo, /proc/stat, os.getloadavg"""
    # Load average
    try:
        if hasattr(os, "getloadavg"):
            load = os.getloadavg()
            result["load_average"] = {
                "1min": round(load[0], 2),
                "5min": round(load[1], 2),
                "15min": round(load[2], 2)
            }
    except Exception:
        pass

    # /proc/cpuinfo - physical cores, model name
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
                if line.startswith("model name"):
                    result["cpu_model"] = line.split(":")[1].strip()
            if physical_ids and core_ids:
                result["cpu_count_physical"] = len(physical_ids) * len(core_ids)
    except Exception:
        pass

    # CPU frequency
    try:
        if os.path.exists("/proc/cpuinfo"):
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if line.startswith("cpu MHz"):
                        freq_mhz = float(line.split(":")[1].strip())
                        result["cpu_frequency_hz"] = int(freq_mhz * 1_000_000)
                        result["cpu_frequency_ghz"] = round(freq_mhz / 1000, 2)
                        break
    except Exception:
        pass

    # CPU 使用率 from /proc/stat (单次采样)
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
    except Exception:
        pass

    # psutil 可选
    if result["usage_percent"] is None:
        try:
            import psutil
            result["cpu_count_physical"] = psutil.cpu_count(logical=False)
            result["cpu_count_logical"] = psutil.cpu_count(logical=True)
            result["usage_percent"] = round(psutil.cpu_percent(interval=0.5), 2)
            freq = psutil.cpu_freq()
            if freq:
                result["cpu_frequency_hz"] = freq.current
                result["cpu_frequency_ghz"] = round(freq.current / 1_000_000_000, 2)
        except ImportError:
            pass
        except Exception:
            pass

    return result


def _cpu_info_macos(result):
    """macOS: sysctl, top"""
    # 物理核心数和型号
    try:
        output = subprocess.check_output(["sysctl", "-n", "hw.physicalcpu"], universal_newlines=True, timeout=5)
        result["cpu_count_physical"] = int(output.strip())
    except Exception:
        pass

    try:
        output = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"], universal_newlines=True, timeout=5)
        result["cpu_model"] = output.strip()
    except Exception:
        pass

    # CPU 频率
    try:
        output = subprocess.check_output(["sysctl", "-n", "hw.cpufrequency"], universal_newlines=True, timeout=5)
        freq = int(output.strip())
        result["cpu_frequency_hz"] = freq
        result["cpu_frequency_ghz"] = round(freq / 1_000_000_000, 2)
    except Exception:
        pass

    # 负载平均值
    try:
        la = os.getloadavg()
        result["load_average"] = {
            "1min": round(la[0], 2),
            "5min": round(la[1], 2),
            "15min": round(la[2], 2)
        }
    except Exception:
        pass

    # CPU 使用率 from top
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
    except Exception:
        pass

    # psutil 可选回退
    if result["usage_percent"] is None:
        try:
            import psutil
            result["usage_percent"] = round(psutil.cpu_percent(interval=0.5), 2)
        except (ImportError, Exception):
            pass

    return result


def _cpu_info_windows(result):
    """Windows: WMI / PowerShell"""
    # 方法1: wmi 库
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
            result["cpu_frequency_hz"] = proc.MaxClockSpeed * 1_000_000
            result["cpu_frequency_ghz"] = round(proc.MaxClockSpeed / 1000, 2)
            cpu_usage = sum(p.LoadPercentage for p in processors) / len(processors)
            result["usage_percent"] = round(cpu_usage, 2)
            result["load_average"] = {
                "1min": round(cpu_usage, 2),
                "5min": round(cpu_usage, 2),
                "15min": round(cpu_usage, 2)
            }
            return result
    except ImportError:
        pass
    except Exception:
        pass

    # 方法2: PowerShell
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
        freq_mhz = data.get("MaxClockSpeed")
        if freq_mhz:
            result["cpu_frequency_mhz"] = freq_mhz
            result["cpu_frequency_hz"] = freq_mhz * 1_000_000
            result["cpu_frequency_ghz"] = round(freq_mhz / 1000, 2)
        result["usage_percent"] = data.get("LoadPercentage", 0)
        result["load_average"] = {
            "1min": result["usage_percent"],
            "5min": result["usage_percent"],
            "15min": result["usage_percent"]
        }
    except Exception:
        pass

    return result


def get_cpu_summary() -> str:
    """获取 CPU 状态的简洁文本摘要"""
    info = get_cpu_info()

    if info.get("error"):
        return f"⚙️ CPU 信息获取失败: {info['error']}"

    parts = []
    if info.get("cpu_count_logical"):
        parts.append(f"{info['cpu_count_logical']} 逻辑核心")
    if info.get("cpu_count_physical"):
        parts.append(f"({info['cpu_count_physical']} 物理核心)")
    if info.get("cpu_model"):
        parts.append(f"| {info['cpu_model']}")
    if info.get("cpu_frequency_ghz"):
        parts.append(f"| {info['cpu_frequency_ghz']} GHz")
    if info.get("usage_percent") is not None:
        parts.append(f"| 使用率 {info['usage_percent']}%")
    if info.get("load_average"):
        la = info["load_average"]
        parts.append(f"| 负载 {la['1min']}/{la['5min']}/{la['15min']}")

    return "⚙️ CPU: " + " ".join(parts) if parts else "⚙️ CPU: 信息不可用"


if __name__ == "__main__":
    print(f"=== CPU 感知测试 ({_PLATFORM}) ===")
    print(json.dumps(get_cpu_info(), ensure_ascii=False, indent=2))
    print("\n摘要:", get_cpu_summary())
