#!/usr/bin/env python3
"""
内存感知模块 - Memory Sense (Cross-Platform)
让 AI Agent 感知内存使用情况

包括：内存总量、已用、可用、交换空间等

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


def get_memory_info() -> dict:
    """获取内存使用信息"""
    result = {
        "sense_type": "memory",
        "total": None,
        "total_human": None,
        "used": None,
        "used_human": None,
        "available": None,
        "available_human": None,
        "free": None,
        "usage_percent": None,
        "swap_total": None,
        "swap_used": None,
        "swap_usage_percent": None
    }

    try:
        if _PLATFORM == "Linux":
            return _mem_info_linux(result)
        elif _PLATFORM == "Darwin":
            return _mem_info_macos(result)
        elif _PLATFORM == "Windows":
            return _mem_info_windows(result)
        else:
            result["error"] = f"不支持的平台: {_PLATFORM}"
            return result
    except Exception as e:
        result["error"] = str(e)
        return result


def _mem_info_linux(result):
    """Linux: /proc/meminfo"""
    try:
        if os.path.exists("/proc/meminfo"):
            meminfo = {}
            with open("/proc/meminfo", "r") as f:
                for line in f:
                    parts = line.split(":")
                    if len(parts) == 2:
                        key = parts[0].strip()
                        val = parts[1].strip().split()[0]
                        try:
                            meminfo[key] = int(val) * 1024  # kB → bytes
                        except ValueError:
                            pass

            result["total"] = meminfo.get("MemTotal", 0)
            result["free"] = meminfo.get("MemFree", 0)
            # MemAvailable 是最准确的可用内存 (kernel 3.14+)
            result["available"] = meminfo.get("MemAvailable", result["free"])
            result["used"] = result["total"] - result["available"]
            result["buffers"] = meminfo.get("Buffers", 0)
            result["cached"] = meminfo.get("Cached", 0)
            result["swap_total"] = meminfo.get("SwapTotal", 0)
            result["swap_free"] = meminfo.get("SwapFree", 0)
            result["swap_used"] = result["swap_total"] - result["swap_free"]

            if result["total"] > 0:
                result["usage_percent"] = round((result["used"] / result["total"]) * 100, 2)
            if result["swap_total"] > 0:
                result["swap_usage_percent"] = round((result["swap_used"] / result["swap_total"]) * 100, 2)

            for key in ["total", "free", "available", "used", "buffers", "cached",
                        "swap_total", "swap_free", "swap_used"]:
                result[f"{key}_human"] = _format_bytes(result.get(key, 0))

            result["source"] = "/proc/meminfo"
    except Exception as e:
        result["error"] = str(e)

    # psutil 可选回退
    if result.get("error"):
        try:
            import psutil
            mem = psutil.virtual_memory()
            result["total"] = mem.total
            result["total_human"] = _format_bytes(mem.total)
            result["available"] = mem.available
            result["available_human"] = _format_bytes(mem.available)
            result["used"] = mem.used
            result["used_human"] = _format_bytes(mem.used)
            result["free"] = mem.free
            result["usage_percent"] = mem.percent
            result["buffers"] = getattr(mem, "buffers", 0)
            result["cached"] = getattr(mem, "cached", 0)
            swap = psutil.swap_memory()
            result["swap_total"] = swap.total
            result["swap_used"] = swap.used
            result["swap_usage_percent"] = swap.percent
            result["source"] = "psutil"
            if "error" in result:
                del result["error"]
        except (ImportError, Exception):
            pass

    return result


def _mem_info_macos(result):
    """macOS: sysctl hw.memsize, vm_stat"""
    # 总内存
    try:
        output = subprocess.check_output(["sysctl", "-n", "hw.memsize"], universal_newlines=True, timeout=5)
        total_bytes = int(output.strip())
        result["total"] = total_bytes
        result["total_human"] = _format_bytes(total_bytes)
    except Exception as e:
        result["error"] = str(e)
        return result

    # vm_stat
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
                except ValueError:
                    pass

        if "pages_free" in stats:
            result["free"] = stats["pages_free"] * page_size
            result["free_human"] = _format_bytes(result["free"])

        # 已用 = active + wired + compressed (approximate)
        used_pages = stats.get("pages_active", 0) + stats.get("pages_wired_down", 0)
        result["used"] = used_pages * page_size
        result["used_human"] = _format_bytes(result["used"])

        if "pages_inactive" in stats:
            result["inactive"] = stats["pages_inactive"] * page_size
            result["inactive_human"] = _format_bytes(result["inactive"])

        result["available"] = result["total"] - result["used"]
        result["available_human"] = _format_bytes(result["available"])

        if result["total"] > 0:
            result["usage_percent"] = round((result["used"] / result["total"]) * 100, 2)

        result["source"] = "sysctl+vm_stat"
    except Exception as e:
        result["vm_stat_error"] = str(e)

    # psutil 回退
    if result.get("error") and result["total"] is None:
        try:
            import psutil
            mem = psutil.virtual_memory()
            result["total"] = mem.total
            result["total_human"] = _format_bytes(mem.total)
            result["available"] = mem.available
            result["available_human"] = _format_bytes(mem.available)
            result["used"] = mem.used
            result["used_human"] = _format_bytes(mem.used)
            result["usage_percent"] = mem.percent
            swap = psutil.swap_memory()
            result["swap_total"] = swap.total
            result["swap_used"] = swap.used
            result["swap_usage_percent"] = swap.percent
            if "error" in result:
                del result["error"]
        except (ImportError, Exception):
            pass

    return result


def _mem_info_windows(result):
    """Windows: PowerShell / ctypes GlobalMemoryStatusEx"""
    # 方法1: psutil
    try:
        import psutil
        mem = psutil.virtual_memory()
        result["total"] = mem.total
        result["total_human"] = _format_bytes(mem.total)
        result["available"] = mem.available
        result["available_human"] = _format_bytes(mem.available)
        result["used"] = mem.used
        result["used_human"] = _format_bytes(mem.used)
        result["usage_percent"] = mem.percent
        swap = psutil.swap_memory()
        result["swap_total"] = swap.total
        result["swap_used"] = swap.used
        result["swap_usage_percent"] = swap.percent
        result["source"] = "psutil"
        return result
    except ImportError:
        pass
    except Exception:
        pass

    # 方法2: PowerShell
    try:
        output = subprocess.check_output(
            ["powershell", "-Command",
             "$os = Get-CimInstance Win32_OperatingSystem; [PSCustomObject]@{"
             "total=$os.TotalVisibleMemorySize; free=$os.FreePhysicalMemory; "
             "used=$os.TotalVisibleMemorySize - $os.FreePhysicalMemory; "
             "swap_total=$os.TotalVirtualMemorySize - $os.TotalVisibleMemorySize; "
             "swap_free=$os.FreeVirtualMemory; "
             "} | ConvertTo-Json"],
            universal_newlines=True, timeout=10)
        data = json.loads(output)
        total_kb = int(data.get("total", 0))
        result["total"] = total_kb * 1024
        result["total_human"] = _format_bytes(result["total"])
        free_kb = int(data.get("free", 0))
        result["free"] = free_kb * 1024
        result["free_human"] = _format_bytes(result["free"])
        used_kb = int(data.get("used", 0))
        result["used"] = used_kb * 1024
        result["used_human"] = _format_bytes(result["used"])
        result["available"] = result["free"]
        result["available_human"] = result["free_human"]
        if total_kb > 0:
            result["usage_percent"] = round((used_kb / total_kb) * 100, 2)

        swap_total_kb = int(data.get("swap_total", 0))
        result["swap_total"] = swap_total_kb * 1024
        swap_free_kb = int(data.get("swap_free", 0))
        result["swap_free"] = swap_free_kb * 1024
        result["swap_used"] = result["swap_total"] - result["swap_free"]
        result["swap_human"] = _format_bytes(result["swap_total"])
        if swap_total_kb > 0:
            result["swap_usage_percent"] = round(
                ((swap_total_kb - swap_free_kb) / swap_total_kb) * 100, 2)

        result["source"] = "powershell"
    except Exception as e:
        result["error"] = str(e)

    # 方法3: ctypes GlobalMemoryStatusEx
    if result.get("error"):
        try:
            import ctypes

            class MEMORYSTATUSEX(ctypes.Structure):
                _fields_ = [
                    ("dwLength", ctypes.c_ulong),
                    ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong),
                    ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong),
                    ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong),
                    ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("sullAvailExtendedVirtual", ctypes.c_ulonglong),
                ]

            ms = MEMORYSTATUSEX()
            ms.dwLength = ctypes.sizeof(ms)
            ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))

            result["total"] = ms.ullTotalPhys
            result["total_human"] = _format_bytes(ms.ullTotalPhys)
            result["available"] = ms.ullAvailPhys
            result["available_human"] = _format_bytes(ms.ullAvailPhys)
            result["used"] = ms.ullTotalPhys - ms.ullAvailPhys
            result["used_human"] = _format_bytes(result["used"])
            result["usage_percent"] = ms.dwMemoryLoad
            result["swap_total"] = ms.ullTotalPageFile - ms.ullTotalPhys
            result["swap_used"] = ms.ullTotalPageFile - ms.ullAvailPageFile
            result["source"] = "ctypes"
            if "error" in result:
                del result["error"]
        except Exception:
            pass

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


def get_memory_summary() -> str:
    """获取内存状态的简洁文本摘要"""
    info = get_memory_info()

    if info.get("error"):
        return f"🧠 内存信息获取失败: {info['error']}"

    parts = []
    if info.get("total_human"):
        parts.append(f"总量 {info['total_human']}")
    if info.get("available_human"):
        parts.append(f"可用 {info['available_human']}")
    if info.get("used_human"):
        parts.append(f"已用 {info['used_human']}")
    if info.get("usage_percent") is not None:
        parts.append(f"({info['usage_percent']}%)")
    if info.get("swap_total") and info["swap_total"] > 0:
        parts.append(f"| 交换 {info.get('swap_usage_percent', '?')}%")

    return "🧠 内存: " + " ".join(parts) if parts else "🧠 内存: 信息不可用"


if __name__ == "__main__":
    print(f"=== 内存感知测试 ({_PLATFORM}) ===")
    print(json.dumps(get_memory_info(), ensure_ascii=False, indent=2))
    print("\n摘要:", get_memory_summary())
