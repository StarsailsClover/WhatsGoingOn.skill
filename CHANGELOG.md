# Changelog

## [v26.0 Alpha 2] - 2026-06-26

### Added
- 新增 `storage_sense` 感知模块：磁盘使用情况检测（总容量、已用、可用、使用百分比），跨平台支持
- 新增 `cpu_sense` 感知模块：CPU 使用率、核心数、频率、负载平均值，独立于 system_sense
- 新增 `memory_sense` 感知模块：内存总量、已用、可用、交换空间，独立于 system_sense
- `quick_sense` 新增 `storage`、`cpu`、`memory` 感知类型选项
- `quick_sense` 的 `environment` 类型新增 storage、cpu、memory 感知
- `quick_sense` 的 `status` 类型使用独立的 cpu_sense 和 memory_sense 替换 system_sense 中的对应调用
- `_print_sense_human` 新增 storage、cpu、memory 感知类型的人类可读格式化输出
- `_print_sense_human` 图标映射新增 storage、cpu、memory 条目

### Changed
- 所有文件版本标识更新为 v26.0 Alpha 2

### Cross-Platform
- storage_sense: Linux(df/mount)、macOS(df)、Windows(wmic/ctypes)
- cpu_sense: Linux(/proc/stat)、macOS(sysctl/top)、Windows(WMI/PowerShell)
- memory_sense: Linux(/proc/meminfo)、macOS(sysctl/vm_stat)、Windows(PowerShell/ctypes)
