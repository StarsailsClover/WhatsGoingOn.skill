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
4. **CPU Sense** (`cpu_sense`) — CPU usage, cores, frequency, load average
5. **Memory Sense** (`memory_sense`) — RAM total, used, available, swap
6. **Storage Sense** (`storage_sense`) — Disk total, used, available, usage percentage
7. **Network Sense** (`network_sense`) — Network interfaces, public IP, connectivity, latency
8. **Location Sense** (`location_sense`) — IP-based geolocation, timezone
9. **Battery Sense** (`battery_sense`) — Battery level, charging status, health, remaining time

### Extensibility

- **Plugin Architecture**: Sense registry supports dynamic loading of new sense modules
- **Custom Senses**: AI can write and load new perception modules on demand
- **Template Generator**: Built-in template for rapid creation of new sense modules

## Quick Start

### Install

```bash
cp -r WhatsGoingOn.skill ~/.agents/skills/whats-going-on/
```

### CLI Usage

```bash
python scripts/whatsgoingon.py list
python scripts/whatsgoingon.py quick
python scripts/whatsgoingon.py sense time
python scripts/whatsgoingon.py sense system
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

## Architecture

```
whatsgoingon.py (CLI)
    → SenseRegistry
        → time_sense / weather_sense / system_sense
        → cpu_sense / memory_sense / storage_sense
        → network_sense / location_sense / battery_sense
```

## Creating Custom Senses

```python
from scripts.sense_registry import BaseSense
class MySense(BaseSense):
    def sense(self, **kwargs):
        return {"sense_type": "my_sense", "data": "your perception here"}
registry.register("my_sense", MySense())
```

## License

MIT
