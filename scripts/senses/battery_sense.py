#!/usr/bin/env python3
"""
电池感知模块 - Battery Sense (Cross-Platform)
让 AI Agent 感知设备的电池状态

包括：电池电量、充电状态、剩余时间、健康度等

支持平台: Linux / macOS / Windows

Author: GitHub@StarsailsClover
Version: v26.0 Alpha 2
"""

import os
import json
import subprocess
import platform
import re

_PLATFORM = platform.system()


def get_battery_info() -> dict:
    """获取电池信息"""
    result = {"sense_type": "battery", "has_battery": False, "status": "unknown"}

    if _PLATFORM == "Linux":
        return _battery_linux(result)
    elif _PLATFORM == "Darwin":
        return _battery_macos(result)
    elif _PLATFORM == "Windows":
        return _battery_windows(result)
    else:
        result["status"] = "no_battery"
        result["message"] = f"不支持的平台: {_PLATFORM}"
        return result


def _battery_linux(result):
    """Linux: sysfs → upower → acpi"""
    # 方法1: sysfs
    try:
        battery_dir = "/sys/class/power_supply"
        if os.path.exists(battery_dir):
            devices = [d for d in os.listdir(battery_dir)
                       if d.startswith("BAT") or d.startswith("battery")]
            if devices:
                bpath = os.path.join(battery_dir, devices[0])
                result["has_battery"] = True
                result["battery_device"] = devices[0]
                _read_sysfs(bpath, result)
                result["source"] = "sysfs"
                result["status"] = "success"
                return result
    except Exception as e:
        result["sysfs_error"] = str(e)

    # 方法2: upower
    try:
        output = subprocess.check_output(
            ["upower", "-i", "/org/freedesktop/UPower/devices/battery_BAT0"],
            universal_newlines=True, timeout=5)
        if output:
            result["has_battery"] = True
            _parse_upower(output, result)
            result["source"] = "upower"
            result["status"] = "success"
            return result
    except Exception as e:
        result["upower_error"] = str(e)

    # 方法3: acpi
    try:
        output = subprocess.check_output(["acpi", "-b"], universal_newlines=True, timeout=5)
        if output and "Battery" in output:
            result["has_battery"] = True
            _parse_acpi(output, result)
            result["source"] = "acpi"
            result["status"] = "success"
            return result
    except Exception as e:
        result["acpi_error"] = str(e)

    result["status"] = "no_battery"
    result["message"] = "未检测到电池设备，可能是台式机或服务器"
    return result


def _read_sysfs(bpath, result):
    """从 sysfs 读取电池信息"""
    attr_map = {
        "capacity": ("capacity_percent", int),
        "status": ("charging_status", str),
        "energy_now": ("energy_now_wh", lambda v: float(v) / 1_000_000),
        "energy_full": ("energy_full_wh", lambda v: float(v) / 1_000_000),
        "energy_full_design": ("energy_full_design_wh", lambda v: float(v) / 1_000_000),
        "voltage_now": ("voltage_now_mv", lambda v: float(v) / 1000),
        "current_now": ("current_now_ma", lambda v: float(v) / 1000),
        "power_now": ("power_now_mw", lambda v: float(v) / 1_000_000),
        "technology": ("technology", str),
        "manufacturer": ("manufacturer", str),
        "model_name": ("model_name", str),
        "serial_number": ("serial_number", str),
        "cycle_count": ("cycle_count", int),
        "temp": ("temperature_c", lambda v: float(v) / 10.0),
    }
    for attr, (rkey, conv) in attr_map.items():
        apath = os.path.join(bpath, attr)
        if os.path.exists(apath):
            try:
                with open(apath, "r") as f:
                    v = f.read().strip()
                    try:
                        result[rkey] = conv(v)
                    except:
                        result[rkey] = v
            except:
                pass

    # 健康度
    if "energy_full_wh" in result and "energy_full_design_wh" in result:
        if result["energy_full_design_wh"] > 0:
            result["health_percent"] = round(
                (result["energy_full_wh"] / result["energy_full_design_wh"]) * 100, 2)

    # 估算剩余时间
    pw = result.get("power_now_mw", 0)
    if pw and pw > 0 and result.get("charging_status") == "Discharging":
        en = result.get("energy_now_wh", 0)
        if en > 0:
            rh = en / pw
            result["remaining_time_hours"] = round(rh, 2)
            result["remaining_time_minutes"] = round(rh * 60, 1)


def _parse_upower(output, result):
    """解析 upower 输出"""
    for line in output.split("\n"):
        line = line.strip()
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if key == "percentage":
            result["capacity_percent"] = int(value.replace("%", ""))
        elif key == "state":
            result["charging_status"] = value
        elif key == "energy":
            result["energy_now_wh"] = float(value.split()[0])
        elif key == "energy-full":
            result["energy_full_wh"] = float(value.split()[0])
        elif key == "energy-full-design":
            result["energy_full_design_wh"] = float(value.split()[0])
        elif key == "capacity":
            result["health_percent"] = float(value.replace("%", ""))
        elif key == "time to empty":
            result["remaining_time_hours"] = float(value.split()[0])
        elif key == "time to full":
            result["time_to_full_hours"] = float(value.split()[0])


def _parse_acpi(output, result):
    """解析 acpi 输出"""
    for line in output.split("\n"):
        if "Battery" not in line:
            continue
        parts = line.split(",")
        if len(parts) >= 2:
            result["charging_status"] = parts[0].split(":")[-1].strip()
            for part in parts:
                if "%" in part:
                    result["capacity_percent"] = int(part.strip().replace("%", ""))
                    break
            for part in parts:
                if "remaining" in part or "until charged" in part:
                    try:
                        t = part.strip().split()[0]
                        h, m, s = t.split(":")
                        rh = int(h) + int(m) / 60
                        result["remaining_time_hours"] = round(rh, 2)
                        result["remaining_time_minutes"] = int(h) * 60 + int(m)
                    except:
                        pass


def _battery_macos(result):
    """macOS: pmset → ioreg → system_profiler"""
    # 方法1: pmset
    try:
        output = subprocess.check_output(["pmset", "-g", "batt"], universal_newlines=True, timeout=5)
        if "Battery" in output or "InternalBattery" in output:
            result["has_battery"] = True
            _parse_pmset(output, result)
            result["source"] = "pmset"
            result["status"] = "success"
            return result
    except Exception as e:
        result["pmset_error"] = str(e)

    # 方法2: ioreg
    try:
        output = subprocess.check_output(["ioreg", "-l", "-n", "AppleSmartBattery"],
                                         universal_newlines=True, timeout=5)
        if "AppleSmartBattery" in output:
            result["has_battery"] = True
            _parse_ioreg(output, result)
            result["source"] = "ioreg"
            result["status"] = "success"
            return result
    except Exception as e:
        result["ioreg_error"] = str(e)

    # 方法3: system_profiler
    try:
        output = subprocess.check_output(["system_profiler", "SPPowerDataType"],
                                         universal_newlines=True, timeout=10)
        if "Battery Information" in output:
            result["has_battery"] = True
            _parse_system_profiler(output, result)
            result["source"] = "system_profiler"
            result["status"] = "success"
            return result
    except Exception as e:
        result["system_profiler_error"] = str(e)

    result["status"] = "no_battery"
    result["message"] = "未检测到电池设备，可能是台式机或服务器"
    return result


def _parse_pmset(output, result):
    """解析 pmset -g batt"""
    for line in output.split("\n"):
        line = line.strip()
        if "drawing from" in line:
            if "Battery Power" in line:
                result["charging_status"] = "Discharging"
            elif "AC Power" in line:
                result["charging_status"] = "Charging"
        if "InternalBattery" in line or "Battery" in line:
            pm = re.search(r'(\d+)%', line)
            if pm:
                result["capacity_percent"] = int(pm.group(1))
            if "charged" in line:
                result["charging_status"] = "Full"
            tm = re.search(r'(\d+):(\d+)\s+remaining', line)
            if tm:
                result["remaining_time_hours"] = round(int(tm.group(1)) + int(tm.group(2)) / 60, 2)
                result["remaining_time_minutes"] = int(tm.group(1)) * 60 + int(tm.group(2))


def _parse_ioreg(output, result):
    """解析 ioreg -l -n AppleSmartBattery"""
    fields = {
        "CurrentCapacity": "current_capacity",
        "MaxCapacity": "max_capacity",
        "DesignCapacity": "design_capacity",
        "CycleCount": "cycle_count",
        "Temperature": "temperature",
        "Voltage": "voltage",
        "Amperage": "amperage",
        "IsCharging": "is_charging",
        "FullyCharged": "fully_charged",
    }
    extracted = {}
    for line in output.split("\n"):
        for iok, rk in fields.items():
            if f'"{iok}"' in line:
                m = re.search(r'=\s*"?([^"\n]+)"?', line)
                if m:
                    v = m.group(1).strip()
                    try: v = int(v)
                    except ValueError:
                        try: v = float(v)
                        except ValueError:
                            if v.lower() == "yes": v = True
                            elif v.lower() == "no": v = False
                    extracted[rk] = v

    if extracted.get("max_capacity", 0) > 0:
        result["capacity_percent"] = round(extracted["current_capacity"] / extracted["max_capacity"] * 100, 1)
    if extracted.get("design_capacity", 0) > 0 and extracted.get("max_capacity", 0) > 0:
        result["health_percent"] = round(extracted["max_capacity"] / extracted["design_capacity"] * 100, 2)
    if extracted.get("fully_charged"):
        result["charging_status"] = "Full"
    elif extracted.get("is_charging"):
        result["charging_status"] = "Charging"
    else:
        result["charging_status"] = "Discharging"
    for k in ["cycle_count", "temperature_c", "voltage_now_mv"]:
        if k in extracted:
            result[k] = extracted[k]


def _parse_system_profiler(output, result):
    """解析 system_profiler SPPowerDataType"""
    current_section = None
    for line in output.split("\n"):
        line = line.strip()
        if "Battery Information:" in line:
            current_section = "battery"
        elif "Health Information" in line:
            current_section = "health"
        elif "Power Settings:" in line:
            current_section = None

        if current_section and ":" in line:
            key, value = line.split(":", 1)
            key, value = key.strip(), value.strip()
            if key == "Full Charge Capacity (mAh)":
                try: result["energy_full_mah"] = int(value)
                except: pass
            elif key == "Cycle Count":
                try: result["cycle_count"] = int(value)
                except: pass
            elif key == "Condition":
                result["condition"] = value
            elif key == "Amperage (mA)":
                try: result["amperage_now_ma"] = int(value)
                except: pass
            elif key == "Voltage (mV)":
                try: result["voltage_now_mv"] = int(value)
                except: pass


def _battery_windows(result):
    """Windows: WMI → PowerShell → systeminfo"""
    # 方法1: WMI
    try:
        import wmi
        c = wmi.WMI()
        batteries = c.Win32_Battery()
        if batteries:
            b = batteries[0]
            result["has_battery"] = True
            result["capacity_percent"] = b.EstimatedChargeRemaining
            sm = {1:"Other",2:"Unknown",3:"Full",4:"Low",5:"Critical",
                  6:"Charging",7:"Charging and Full",8:"Charging and Low",
                  9:"Charging and High",10:"Discharging"}
            result["charging_status"] = sm.get(b.BatteryStatus, "Unknown")
            if b.EstimatedRunTime:
                result["remaining_time_minutes"] = b.EstimatedRunTime
                result["remaining_time_hours"] = round(b.EstimatedRunTime / 60, 2)
            if b.DesignCapacity and b.FullChargeCapacity and b.DesignCapacity > 0:
                result["health_percent"] = round(b.FullChargeCapacity / b.DesignCapacity * 100, 2)
                result["design_capacity_mwh"] = b.DesignCapacity
                result["full_charge_capacity_mwh"] = b.FullChargeCapacity
            if b.Name: result["model_name"] = b.Name
            if b.Manufacturer: result["manufacturer"] = b.Manufacturer
            result["source"] = "wmi"
            result["status"] = "success"
            return result
    except ImportError:
        pass
    except Exception as e:
        result["wmi_error"] = str(e)

    # 方法2: PowerShell
    try:
        output = subprocess.check_output(
            ["powershell", "-Command",
             "Get-CimInstance Win32_Battery | Select-Object EstimatedChargeRemaining, BatteryStatus, EstimatedRunTime, DesignCapacity, FullChargeCapacity, Name, Manufacturer | ConvertTo-Json"],
            universal_newlines=True, timeout=10)
        data = json.loads(output)
        if isinstance(data, list) and len(data) == 0:
            result["status"] = "no_battery"
            result["message"] = "未检测到电池设备，可能是台式机"
            return result
        if isinstance(data, list):
            data = data[0]
        result["has_battery"] = True
        if "EstimatedChargeRemaining" in data:
            result["capacity_percent"] = data["EstimatedChargeRemaining"]
        sm = {1:"Other",2:"Unknown",3:"Full",4:"Low",5:"Critical",
              6:"Charging",7:"Charging and Full",10:"Discharging"}
        result["charging_status"] = sm.get(data.get("BatteryStatus"), "Unknown")
        if data.get("EstimatedRunTime"):
            result["remaining_time_minutes"] = data["EstimatedRunTime"]
            result["remaining_time_hours"] = round(data["EstimatedRunTime"] / 60, 2)
        if data.get("DesignCapacity") and data.get("FullChargeCapacity") and data["DesignCapacity"] > 0:
            result["health_percent"] = round(data["FullChargeCapacity"] / data["DesignCapacity"] * 100, 2)
        if data.get("Name"): result["model_name"] = data["Name"]
        if data.get("Manufacturer"): result["manufacturer"] = data["Manufacturer"]
        result["source"] = "powershell"
        result["status"] = "success"
        return result
    except Exception as e:
        result["powershell_error"] = str(e)

    result["status"] = "no_battery"
    result["message"] = "未检测到电池设备，可能是台式机或服务器"
    return result


def get_battery_summary() -> str:
    """获取电池状态的简洁文本摘要"""
    info = get_battery_info()

    if not info.get("has_battery"):
        return "🔌 未检测到电池（台式机/服务器）"

    parts = []
    capacity = info.get("capacity_percent", 0)
    status = info.get("charging_status", "")

    if "Charging" in status:
        parts.append("⚡ 充电中")
    elif "Discharging" in status or status in ("Low", "Critical"):
        parts.append("🔋 放电中")
    elif "Full" in status:
        parts.append("✅ 已充满")
    else:
        parts.append("🔋")

    parts.append(f"{capacity}%")

    if "remaining_time_hours" in info and "Discharging" in status:
        parts.append(f"剩余约 {info['remaining_time_hours']} 小时")
    if "health_percent" in info:
        parts.append(f"健康度 {info['health_percent']}%")
    if "cycle_count" in info:
        parts.append(f"循环 {info['cycle_count']} 次")

    return " | ".join(parts)


if __name__ == "__main__":
    print(f"=== 电池感知测试 ({_PLATFORM}) ===")
    print(json.dumps(get_battery_info(), ensure_ascii=False, indent=2))
    print("\n摘要:", get_battery_summary())
