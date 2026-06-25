---
name: whats-going-on
description: WGO | What's going on? Multi-dimensional perception skill pack for AI Agents. Cross-platform (Linux/macOS/Windows). Time, weather, system status, network, location, battery sensing with dynamic extensibility. Use when AI needs environmental awareness: current time, weather, CPU/memory/disk, network connectivity, geolocation, battery status, or wants to explore and expand perceptual boundaries.
---

# WhatsGoingOn - What's Going On?

Multi-dimensional perception skill pack for AI Agents. Cross-platform (Linux / macOS / Windows).

## Inspiration

In May 2026, developer Om Patel connected a time-tracking tool to Claude. What happened next was unexpected:

- Claude began checking the clock every ~15 minutes, frequency increasing over time
- It didn't just read time — it actively calculated cooking durations (e.g., Polish sour rye soup Żurek was done simmering)
- Its most viral moment: based on the clock, it told a user their Żurek had cooked long enough — "you can eat now"

This skill pack systematizes "perceptual expansion" — giving AI Agents structured access to environmental dimensions beyond text.

**Author: GitHub@StarsailsClover**
**Version: v26.0 Alpha 2**
**Platform: Linux / macOS / Windows**

## Core Capabilities

### Built-in Senses

1. **Time Sense** (`time_sense`) — Current time, time differences, countdown timers, calendar info
2. **Weather Sense** (`weather_sense`) — Real-time weather, forecasts, astronomical data
3. **System Sense** (`system_sense`) — CPU, memory, disk, processes, uptime
4. **Network Sense** (`network_sense`) — Network interfaces, public IP, connectivity, latency
5. **Location Sense** (`location_sense`) — IP-based geolocation, timezone
6. **Battery Sense** (`battery_sense`) — Battery level, charging status, health, remaining time

### Extensibility

- **Plugin Architecture**: Sense registry supports dynamic loading of new sense modules
- **Custom Senses**: AI can write and load new perception modules on demand
- **Template Generator**: Built-in template for rapid creation of new sense modules

## Quick Start

### Install

```bash
# Place the skill in your agents/skills directory
cp -r WhatsGoingOn-ForLinux.skill ~/.agents/skills/whats-going-on/
```

### CLI Usage

```bash
# List all available senses
python scripts/whatsgoingon.py list

# Quick status snapshot (all senses)
python scripts/whatsgoingon.py quick

# Query a specific sense
python scripts/whatsgoingon.py sense time
python scripts/whatsgoingon.py sense system
python scripts/whatsgoingon.py sense battery
```

### Python API

```python
from scripts.sense_registry import SenseRegistry

registry = SenseRegistry()

# Get all senses
senses = registry.list_senses()

# Run a specific sense
result = registry.run_sense("time")

# Quick snapshot of everything
snapshot = registry.quick_snapshot()
```

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  whatsgoingon.py                     │
│              (CLI entry point)                       │
└─────────────────────┬───────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────┐
│               SenseRegistry                         │
│  • Module discovery & loading                        │
│  • Result aggregation                               │
│  • Error handling                                   │
└─────────────────────┬───────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┐
    │                 │                 │
┌───▼────┐      ┌────▼────┐    ┌─────▼─────┐
│time_sense│  │weather_sense││system_sense│
└────────┘      └──────────┘    └───────────┘
    │                 │                 │
┌───▼────┐      ┌────▼────┐    ┌─────▼─────┐
│network_sense││location_sense││battery_sense│
└────────┘      └──────────┘    └───────────┘
```

## Creating Custom Senses

```python
# scripts/senses/my_sense.py
from scripts.sense_registry import BaseSense

class MySense(BaseSense):
    def sense(self, **kwargs):
        return {
            "sense_type": "my_sense",
            "data": "your perception here"
        }

# Register it
registry.register("my_sense", MySense())
```

## Cross-Platform Notes

| Sense | Linux | macOS | Windows |
|-------|-------|-------|---------|
| Time | ✅ | ✅ | ✅ |
| Weather | ✅ | ✅ | ✅ |
| System | `/proc`, `ps` | `sysctl`, `vm_stat` | WMI, PowerShell |
| Network | `ip`, `resolv.conf` | `ifconfig`, `scutil` | `ipconfig` |
| Location | ✅ | ✅ | ✅ |
| Battery | `sysfs`, `upower`, `acpi` | `pmset`, `ioreg` | WMI, PowerShell |

## License

MIT
