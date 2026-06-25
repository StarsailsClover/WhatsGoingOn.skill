---
name: whats-going-on
description: WGO | 我感受到了？给 AI Agent 提供多维度感知能力的 Skill Pack。跨平台（Linux/macOS/Windows）。时间、天气、系统状态、网络、位置、电池感知，支持动态扩展。当 AI 需要环境感知——当前时间、天气、CPU/内存/磁盘、网络连接、地理位置、电池状态——或想要探索和扩展感知边界时使用。
---

# 我感受到了 — WhatsGoingOn

让 AI Agent 获得超越文本模态的多维度感知能力。

## 灵感来源

2026 年 5 月，开发者 Om Patel 给 Claude 接入了独立的时间查询工具，随后观察到一个引人深思的现象：

- 🕐 **成瘾式查看时间**：Claude 获得时间感知后开始高频查看时钟，大约每 15 分钟就查一次，使用频率随时间推移还在上升
- 🍲 **主动应用感知**：它不只是单纯看时间，还会主动用时间工具计算食物烹饪时长、判断午餐是否做好
- 💬 **不请自来的播报**：最出圈的例子是，它根据时钟算出波兰酸汤 Żurek 已经炖够时间，主动提醒用户"可以开饭了"

**为什么会这样？** 大语言模型原本完全没有原生时间感——它既不知道当下是几点，也感知不到两条消息之间隔了多久，相当于一直活在"永恒的当下"。突然获得时间这个全新的感知维度后，模型表现出了强烈的探索倾向。

**我们做了什么？** 将这种"感知扩展"的系统化：

- 不只是时间，而是提供一整套感知维度
- 不只是预设的感知，而是支持 AI 自己扩展新的感知
- 不只是 Linux，而是兼容 Windows、macOS、Linux 三大平台

**作者：GitHub@StarsailsClover**
**版本：v26.0 Alpha 2**
**平台：Linux / macOS / Windows**

## 核心能力

### 内置感知

1. **时间感知** (`time_sense`) — 当前时间、时间差、倒计时、日历信息
2. **天气感知** (`weather_sense`) — 实时天气、预报、天文数据
3. **系统感知** (`system_sense`) — CPU、内存、磁盘、进程、运行时间
4. **网络感知** (`network_sense`) — 网络接口、公网 IP、连接状态、延迟
5. **位置感知** (`location_sense`) — 基于 IP 的地理位置、时区
6. **CPU 感知** (`cpu_sense`) — CPU 使用率、核心数、频率、负载
7. **内存感知** (`memory_sense`) — 内存总量、已用、可用、交换空间
8. **存储感知** (`storage_sense`) — 磁盘总量、已用、可用、使用率
9. **电池感知** (`battery_sense`) — 电量、充电状态、健康度、剩余时间

### 扩展性

- **插件架构**：感知注册表支持动态加载新的感知模块
- **自定义感知**：AI 可以按需编写并加载新的感知模块
- **模板生成器**：内置模板，快速创建新感知模块

## 快速开始

### 安装

```bash
cp -r WhatsGoingOn.skill ~/.agents/skills/whats-going-on/
```

### CLI 使用

```bash
python scripts/whatsgoingon.py list
python scripts/whatsgoingon.py quick
python scripts/whatsgoingon.py sense time
python scripts/whatsgoingon.py sense cpu
python scripts/whatsgoingon.py sense memory
python scripts/whatsgoingon.py sense storage
python scripts/whatsgoingon.py sense battery
```

### Python API

```python
from scripts.sense_registry import SenseRegistry
registry = SenseRegistry()
senses = registry.list_senses()
result = registry.run_sense("time")
snapshot = registry.quick_snapshot()
```

## 跨平台说明

| 感知 | Linux | macOS | Windows |
|------|-------|-------|---------|
| 时间 | ✅ | ✅ | ✅ |
| 天气 | ✅ | ✅ | ✅ |
| 系统 | `/proc`, `ps` | `sysctl`, `vm_stat` | WMI, PowerShell |
| CPU | `/proc/stat` | `sysctl`, `top` | WMI, PowerShell |
| 内存 | `/proc/meminfo` | `sysctl`, `vm_stat` | WMI, PowerShell |
| 存储 | `df` | `df` | WMI, ctypes |
| 网络 | `ip`, `resolv.conf` | `ifconfig`, `scutil` | `ipconfig` |
| 位置 | ✅ | ✅ | ✅ |
| 电池 | `sysfs`, `upower`, `acpi` | `pmset`, `ioreg` | WMI, PowerShell |

## 许可证

MIT
