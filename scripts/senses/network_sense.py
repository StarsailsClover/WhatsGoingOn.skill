#!/usr/bin/env python3
"""
网络感知模块 - Network Sense (Cross-Platform)
让 AI Agent 感知当前网络连接状态

包括：网络接口、IP地址、连接状态、网络延迟、带宽等

支持平台: Linux / macOS / Windows

Author: GitHub@StarsailsClover
Version: v26.0 Alpha 2
"""

import os
import socket
import json
import urllib.request
import subprocess
import platform
import time

_PLATFORM = platform.system()


def get_network_interfaces() -> dict:
    """获取网络接口信息"""
    result = {"sense_type": "network_interfaces", "interfaces": {}}

    try:
        if _PLATFORM == "Linux":
            return _interfaces_linux(result)
        elif _PLATFORM == "Darwin":
            return _interfaces_macos(result)
        elif _PLATFORM == "Windows":
            return _interfaces_windows(result)
        else:
            return _interfaces_socket_fallback(result)
    except Exception as e:
        result["error"] = str(e)
    return result


def _interfaces_linux(result):
    output = subprocess.check_output(["ip", "-j", "addr"], universal_newlines=True, timeout=5)
    interfaces = json.loads(output)
    for iface in interfaces:
        name = iface.get("ifname", "unknown")
        result["interfaces"][name] = {
            "state": iface.get("operstate", "unknown"),
            "mtu": iface.get("mtu", 0),
            "mac_address": iface.get("address"),
            "ipv4": [],
            "ipv6": []
        }
        for addr_info in iface.get("addr_info", []):
            addr = {"address": addr_info.get("local"), "prefixlen": addr_info.get("prefixlen"), "scope": addr_info.get("scope")}
            if addr_info.get("family") == "inet":
                result["interfaces"][name]["ipv4"].append(addr)
            elif addr_info.get("family") == "inet6":
                result["interfaces"][name]["ipv6"].append(addr)
    return result


def _interfaces_macos(result):
    output = subprocess.check_output(["ifconfig"], universal_newlines=True, timeout=10)
    current = None
    for line in output.split("\n"):
        if line and not line.startswith("\t") and ":" in line:
            parts = line.split(":", 1)
            name = parts[0].strip()
            if name and name != "lo0":
                current = name
                result["interfaces"][current] = {"state": "UNKNOWN", "mtu": None, "mac_address": None, "ipv4": [], "ipv6": []}
                if "UP" in line:
                    result["interfaces"][current]["state"] = "UP"
                m = __import__("re").search(r'mtu\s+(\d+)', line)
                if m:
                    result["interfaces"][current]["mtu"] = int(m.group(1))
        elif current and line.startswith("\t"):
            ls = line.strip()
            if ls.startswith("ether "):
                result["interfaces"][current]["mac_address"] = ls.split()[1]
            elif ls.startswith("inet "):
                parts = ls.split()
                if len(parts) >= 2:
                    result["interfaces"][current]["ipv4"].append({"address": parts[1], "prefixlen": None})
            elif ls.startswith("inet6 "):
                parts = ls.split()
                if len(parts) >= 2:
                    result["interfaces"][current]["ipv6"].append({"address": parts[1], "prefixlen": None})
    return result


def _interfaces_windows(result):
    output = subprocess.check_output(["ipconfig", "/all"], universal_newlines=True, timeout=10, encoding="gbk", errors="ignore")
    current = None
    for line in output.split("\n"):
        ls = line.strip()
        if ls.endswith(":") and ("适配器" in ls or "adapter" in ls.lower()):
            name = ls.rstrip(":").strip()
            if name:
                current = name
                result["interfaces"][current] = {"state": "UNKNOWN", "mtu": None, "mac_address": None, "ipv4": [], "ipv6": []}
        elif current and ls:
            if "物理地址" in ls or "Physical Address" in ls:
                parts = ls.split(":", 1)
                if len(parts) == 2:
                    result["interfaces"][current]["mac_address"] = parts[1].strip().replace("-", ":")
            elif "IPv4 地址" in ls or "IPv4 Address" in ls:
                parts = ls.split(":", 1)
                if len(parts) == 2:
                    result["interfaces"][current]["ipv4"].append({"address": parts[1].strip().split("(")[0].strip(), "prefixlen": None})
            elif "IPv6 地址" in ls or "IPv6 Address" in ls:
                parts = ls.split(":", 1)
                if len(parts) == 2:
                    result["interfaces"][current]["ipv6"].append({"address": parts[1].strip().split("(")[0].strip(), "prefixlen": None})
    return result


def _interfaces_socket_fallback(result):
    hostname = socket.gethostname()
    addrs = socket.getaddrinfo(hostname, None)
    ipv4, ipv6 = [], []
    for addr in addrs:
        if addr[0] == socket.AF_INET:
            ipv4.append(addr[4][0])
        elif addr[0] == socket.AF_INET6:
            ipv6.append(addr[4][0])
    result["interfaces"]["primary"] = {"state": "unknown", "ipv4": list(set(ipv4)), "ipv6": list(set(ipv6))}
    return result


def get_public_ip() -> dict:
    """获取公网 IP 地址（跨平台，使用在线服务）"""
    result = {"sense_type": "public_ip"}
    services = [
        ("https://api.ipify.org?format=json", "ip"),
        ("https://ipapi.co/json/", "ip"),
        ("https://ipinfo.io/json", "ip"),
    ]
    for url, ip_key in services:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "WhatsGoingOn/v26.0"})
            with urllib.request.urlopen(req, timeout=5) as r:
                data = json.loads(r.read().decode("utf-8"))
            result["ip"] = data.get(ip_key)
            result["source"] = url
            for geo in ["city", "region", "country", "org", "timezone"]:
                if geo in data:
                    result[geo] = data[geo]
            break
        except:
            continue
    if "ip" not in result:
        result["error"] = "无法获取公网 IP"
        result["status"] = "failed"
    return result


def check_connectivity() -> dict:
    """检查网络连接状态和延迟（跨平台）"""
    result = {"sense_type": "connectivity", "internet_access": False, "dns_ok": False, "targets": []}
    targets = [
        {"name": "Google DNS", "host": "8.8.8.8", "port": 53, "timeout": 3},
        {"name": "Cloudflare DNS", "host": "1.1.1.1", "port": 53, "timeout": 3},
        {"name": "Baidu", "host": "baidu.com", "port": 80, "timeout": 5},
        {"name": "GitHub", "host": "github.com", "port": 443, "timeout": 5},
    ]
    for target in targets:
        tr = {"name": target["name"], "host": target["host"], "reachable": False, "latency_ms": None}
        try:
            start = time.time()
            sock = socket.create_connection((target["host"], target["port"]), timeout=target["timeout"])
            tr["latency_ms"] = round((time.time() - start) * 1000, 2)
            tr["reachable"] = True
            result["internet_access"] = True
            sock.close()
        except Exception as e:
            tr["error"] = str(e)
        result["targets"].append(tr)
    try:
        socket.gethostbyname("baidu.com")
        result["dns_ok"] = True
    except:
        result["dns_ok"] = False
    reachable = [t for t in result["targets"] if t["reachable"] and t["latency_ms"]]
    if reachable:
        result["average_latency_ms"] = round(sum(t["latency_ms"] for t in reachable) / len(reachable), 2)
    return result


def get_dns_servers() -> dict:
    """获取 DNS 服务器配置"""
    result = {"sense_type": "dns", "servers": []}
    try:
        if _PLATFORM == "Windows":
            output = subprocess.check_output(["ipconfig", "/all"], universal_newlines=True, timeout=10, encoding="gbk", errors="ignore")
            in_dns = False
            for line in output.split("\n"):
                ls = line.strip()
                if "DNS 服务器" in ls or "DNS Servers" in ls:
                    in_dns = True
                    parts = ls.split(":", 1)
                    if len(parts) == 2:
                        s = parts[1].strip()
                        if s and s not in result["servers"]:
                            result["servers"].append(s)
                elif in_dns and ls and not ls.startswith(" ") and ":" in ls:
                    in_dns = False
        elif _PLATFORM == "Darwin":
            output = subprocess.check_output(["scutil", "--dns"], universal_newlines=True, timeout=5)
            for line in output.split("\n"):
                ls = line.strip()
                if ls.startswith("nameserver["):
                    parts = ls.split(":", 1)
                    if len(parts) == 2:
                        s = parts[1].strip()
                        if s and s not in result["servers"]:
                            result["servers"].append(s)
        else:
            if os.path.exists("/etc/resolv.conf"):
                with open("/etc/resolv.conf", "r") as f:
                    for line in f:
                        ls = line.strip()
                        if ls.startswith("nameserver"):
                            parts = ls.split()
                            if len(parts) >= 2:
                                result["servers"].append(parts[1])
    except Exception as e:
        result["error"] = str(e)
    return result


def get_network_speed_test() -> dict:
    """简单的网络速度测试（跨平台）"""
    result = {"sense_type": "network_speed", "download_speed_mbps": None}
    try:
        test_url = "https://speed.cloudflare.com/__down?bytes=1000000"
        start = time.time()
        req = urllib.request.Request(test_url, headers={"User-Agent": "WhatsGoingOn/v26.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            data = r.read()
            elapsed = time.time() - start
        if elapsed > 0:
            speed_mbps = (len(data) * 8) / elapsed / 1_000_000
            result["download_speed_mbps"] = round(speed_mbps, 2)
            result["downloaded_bytes"] = len(data)
            result["elapsed_seconds"] = round(elapsed, 2)
            result["status"] = "success"
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
    return result


def get_full_network_status() -> dict:
    """获取完整的网络状态快照"""
    return {
        "sense_type": "network_full",
        "timestamp": time.time(),
        "interfaces": get_network_interfaces(),
        "public_ip": get_public_ip(),
        "connectivity": check_connectivity(),
        "dns": get_dns_servers(),
    }


if __name__ == "__main__":
    print("=== 网络感知测试 ===")
    print(json.dumps(get_full_network_status(), ensure_ascii=False, indent=2))
