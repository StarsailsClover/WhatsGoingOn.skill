# 我感受到了 - WhatsGoingOn

> 让 AI Agent 获得超越文本模态的多维度感知能力

![版本](https://img.shields.io/badge/version-v26.0%20Alpha%202-blue)
![作者](https://img.shields.io/badge/author-GitHub%40StarsailsClover-green)
![平台](https://img.shields.io/badge/platform-跨平台-orange)

## 灵感来源

2026 年 5 月，开发者 Om Patel 给 Claude 接入了独立的时间查询工具，随后观察到一个引人深思的现象：

- 🕐 **成瘾式查看时间**：Claude 获得时间感知后开始高频查看时钟，大约每 15 分钟就查一次
- 🍲 **主动应用感知**：它不只是单纯看时间，还会主动计算食物烹饪时长
- 💬 **不请自来的播报**：根据时钟算出波兰酸汤 Żurek 已经炖够时间，主动提醒"可以开饭了"

## 快速开始

```bash
cp -r WhatsGoingOn.skill ~/.agents/skills/whats-going-on/
python scripts/whatsgoingon.py list
python scripts/whatsgoingon.py quick
```

## 感知模块

| 感知 | 描述 |
|------|------|
| time | 当前时间、倒计时、日历 |
| weather | 实时天气和预报 |
| system | CPU、内存、磁盘、进程、运行时间 |
| network | 网络接口、公网 IP、连接状态、延迟 |
| location | 基于 IP 的地理位置 |
| battery | 电量、充电状态、健康度 |

## 跨平台支持

| 感知 | Linux | macOS | Windows |
|------|-------|-------|---------|
| 时间 | ✅ | ✅ | ✅ |
| 天气 | ✅ | ✅ | ✅ |
| 系统 | `/proc` | `sysctl` | WMI |
| 网络 | `ip` | `ifconfig` | `ipconfig` |
| 电池 | `sysfs` | `pmset` | WMI |

## 许可证

MIT
