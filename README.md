# WhatsGoingOn - 我感觉到了

> 让 AI Agent 获得超越文本模态的多维度感知能力

![Version](https://img.shields.io/badge/version-v26.0%20Alpha%202-blue)
![Author](https://img.shields.io/badge/author-GitHub%40StarsailsClover-green)
![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-orange)

## ✨ 灵感来源

这个项目的灵感来自于 2026 年 5 月一个有趣的第三方实验：

开发者 **Om Patel** 给 Claude 接入了独立的时间查询工具后，观察到一个引人深思的现象：

- 🕐 **成瘾式查看时间**：Claude 获得时间感知后开始高频查看时钟，大约每 15 分钟就查一次，而且使用频率随时间推移还在上升
- 🍲 **主动应用感知**：它不只是单纯看时间，还会主动用时间工具计算食物烹饪时长、判断午餐是否做好
- 💬 **不请自来的播报**：最出圈的例子是，它根据时钟算出波兰酸汤 Żurek 已经炖够时间，主动提醒用户"可以开饭了"

### 为什么会这样？

大语言模型原本完全没有原生时间感——它既不知道当下是几点，也感知不到两条消息之间隔了多久，相当于一直活在**"永恒的当下"**。

突然获得时间这个全新的感知维度后，模型表现出了强烈的探索倾向。实验者本人也提到，这可能只是 AI 对"现在"这个概念建立理解的第一步。

### 我们做了什么？

WhatsGoingOn 将这种"感知扩展"的理念系统化：
- 不只是时间，而是提供一整套感知维度
- 不只是预设的感知，而是支持 AI 自己扩展新的感知
- 不只是 Linux，而是兼容 Windows、macOS、Linux 三大平台

就像 Claude 对时间上瘾一样，AI 可以对更多维度的感知产生"兴趣"——
天气、地理位置、系统状态、网络状况、电池电量……
以及任何 AI 自己想要探索的新维度。

---

## 🚀 快速开始

### 查看所有可用感知

```bash
python3 scripts/whatsgoingon.py list -v
```

### 快速获取状态快照

```bash
# 综合状态
python3 scripts/whatsgoingon.py quick

# 环境感知（时间+天气+位置）
python3 scripts/whatsgoingon.py quick -t environment

# 系统状态（CPU+内存+磁盘+网络）
python3 scripts/whatsgoingon.py quick -t system

# 全部感知
python3 scripts/whatsgoingon.py quick -t all
```

### 调用特定感知函数

```bash
# 获取当前时间
python3 scripts/whatsgoingon.py call time_sense.get_current_time

# 获取天气
python3 scripts/whatsgoingon.py call weather_sense.get_weather

# 检查网络连接
python3 scripts/whatsgoingon.py call network_sense.check_connectivity

# 获取地理位置
python3 scripts/whatsgoingon.py call location_sense.get_location_by_ip
```

---

## 📦 内置感知模块

| 模块 | 说明 | 状态 |
|-----|------|------|
| 🕐 **time_sense** | 时间感知 - 当前时间、时间差计算、倒计时 | ✅ |
| 🌤️ **weather_sense** | 天气感知 - 实时天气、预报、天文信息 | ✅ |
| 💻 **system_sense** | 系统状态 - CPU、内存、磁盘、进程 | ✅ |
| 🌐 **network_sense** | 网络感知 - 接口、IP、延迟、带宽 | ✅ |
| 🗺️ **location_sense** | 地理位置 - 基于IP定位、时区 | ✅ |
| 🔋 **battery_sense** | 电池感知 - 电量、充电状态、健康度 | ✅ |

---

## 🔧 可扩展机制

### 生成新感知模块模板

```bash
python3 scripts/whatsgoingon.py template my_custom_sense -d "我的自定义感知" -o my_sense.py
```

### 在 Python 中动态注册

```python
from sense_registry import get_registry

registry = get_registry()

# 注册自定义感知函数
def my_sense(**kwargs):
    return {
        "sense_type": "my_custom",
        "value": 42,
        "status": "success"
    }

registry.register_custom_sense("my_custom", my_sense, description="我的自定义感知")

# 调用
result = registry.call_sense("my_custom.my_sense")
```

---

## 📁 项目结构

```
WhatsGoingOn-ForLinux.skill/
├── SKILL.md                    # 技能定义文件
├── README.md                   # 项目说明（本文件）
├── scripts/
│   ├── whatsgoingon.py         # 主入口脚本
│   ├── sense_registry.py       # 感知注册表（核心扩展机制）
│   └── senses/                 # 感知模块目录
│       ├── __init__.py
│       ├── time_sense.py       # 时间感知
│       ├── weather_sense.py    # 天气感知
│       ├── system_sense.py     # 系统状态感知
│       ├── network_sense.py    # 网络感知
│       ├── location_sense.py   # 地理位置感知
│       └── battery_sense.py    # 电池感知
└── references/
    ├── extending_senses.md     # 扩展感知开发指南
    └── api_reference.md        # API 参考文档
```

---

## 🖥️ 平台版本

- **WhatsGoingOn-ForLinux.skill** - Cross-Platform (Linux/macOS/Windows)（基于 /proc、sysfs、ip 命令）
- **WhatsGoingOn-ForMac.skill** - macOS 版本（基于 system_profiler、ioreg、networksetup）
- **WhatsGoingOn-ForWindows.skill** - Windows 版本（基于 WMI、PowerShell）

三个版本提供统一的 API 接口，感知能力根据平台特性略有差异。

---

## 📝 版本历史

### v26.0 Alpha 2
- 初始版本发布
- 支持 6 大内置感知模块
- 插件式感知扩展机制
- 支持 Linux / macOS / Windows 三平台

---

## 👤 作者

**GitHub@StarsailsClover**

---

## 📄 许可证

本项目仅供学习和研究使用。

---

> "当 Claude 第一次看到时间时，它每 15 分钟就看一次。
> 现在，它可以看到更多了。"
> —— WhatsGoingOn 项目理念
