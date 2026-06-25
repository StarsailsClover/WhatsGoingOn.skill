# WhatsGoingOn - What's Going On?

> Multi-dimensional perception skill pack for AI Agents

![Version](https://img.shields.io/badge/version-v26.0%20Alpha%202-blue)
![Author](https://img.shields.io/badge/author-GitHub%40StarsailsClover-green)
![Platform](https://img.shields.io/badge/platform-Cross%20Platform-orange)

## Inspiration

In May 2026, developer Om Patel connected a time-tracking tool to Claude. What happened next was unexpected:

- Claude began checking the clock every ~15 minutes, frequency increasing over time
- It didn't just read time — it actively calculated cooking durations
- It told a user their Żurek had cooked long enough — "you can eat now"

This skill pack systematizes "perceptual expansion" for AI Agents.

## Quick Start

```bash
cp -r WhatsGoingOn.skill ~/.agents/skills/whats-going-on/
python scripts/whatsgoingon.py list
python scripts/whatsgoingon.py quick
```

## Senses

| Sense | Description |
|-------|-------------|
| time | Current time, timers, calendar |
| weather | Real-time weather and forecasts |
| system | CPU, memory, disk, processes, uptime |
| network | Interfaces, public IP, connectivity, latency |
| location | IP-based geolocation |
| battery | Level, charging status, health |

## Cross-Platform

| Sense | Linux | macOS | Windows |
|-------|-------|-------|---------|
| Time | ✅ | ✅ | ✅ |
| Weather | ✅ | ✅ | ✅ |
| System | `/proc` | `sysctl` | WMI |
| Network | `ip` | `ifconfig` | `ipconfig` |
| Battery | `sysfs` | `pmset` | WMI |

## License

MIT
