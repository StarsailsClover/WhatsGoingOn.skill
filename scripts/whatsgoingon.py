#!/usr/bin/env python3
"""
WhatsGoingOn - 我感觉到了
让 AI Agent 获得超越文本模态的多维度感知能力

主入口脚本 - 提供统一的命令行接口

灵感来源：
    Claude 获得时间查询工具后表现出的成瘾式探索行为
    - 每15分钟就查询一次时间
    - 主动计算烹饪时长
    - 不请自来地宣布"现在几点了"
    
    这个技能包让 AI Agent 可以获得更多类似的感知维度
    并且支持无限扩展自己的感知边界

版本: v26.0 Alpha 2
作者: GitHub@StarsailsClover
平台: Linux
"""

import sys
import os
import json
import argparse

# 添加脚本目录到路径
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from sense_registry import get_registry


def print_banner():
    """打印欢迎横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    WhatsGoingOn - 我感觉到了                  ║
║           让 AI Agent 获得多维度感知能力的技能包               ║
╠══════════════════════════════════════════════════════════════╣
║  Version: v26.0 Alpha 2  |  Author: GitHub@StarsailsClover   ║
║  Cross-Platform (Linux/macOS/Windows)
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def list_senses(args):
    """列出所有可用的感知模块"""
    registry = get_registry()
    
    if args.verbose:
        print("\n📋 所有可用的感知模块:\n")
        for sense in registry.list_senses():
            print(f"  📦 {sense['name']}")
            print(f"     描述: {sense['description']}")
            print(f"     来源: {sense['source']}")
            print(f"     函数: {', '.join(sense['functions'])}")
            print()
    else:
        print("\n📋 可用感知模块:")
        for sense in registry.list_senses():
            print(f"  - {sense['name']}: {sense['description']}")
        print()
    
    if args.functions:
        print("\n🔧 所有感知函数:")
        for func in registry.get_all_functions():
            print(f"  - {func}")
        print()


def quick_sense(args):
    """快速获取感知信息"""
    registry = get_registry()
    sense_type = args.type or "status"
    
    print(f"\n⚡ 快速感知 ({sense_type}):\n")
    
    result = registry.quick_sense(sense_type)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 人类可读格式
        for sense_name, sense_data in result.get("senses", {}).items():
            _print_sense_human(sense_name, sense_data)


def call_sense(args):
    """调用指定的感知函数"""
    registry = get_registry()
    func_name = args.function
    
    # 解析参数
    kwargs = {}
    if args.params:
        for param in args.params:
            if "=" in param:
                key, value = param.split("=", 1)
                # 尝试转换类型
                try:
                    value = int(value)
                except ValueError:
                    try:
                        value = float(value)
                    except ValueError:
                        if value.lower() == "true":
                            value = True
                        elif value.lower() == "false":
                            value = False
                kwargs[key] = value
    
    print(f"\n🔍 调用感知函数: {func_name}\n")
    
    result = registry.call_sense(func_name, **kwargs)
    
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        _print_sense_human(func_name.split(".")[0], result)


def _print_sense_human(sense_name: str, data: dict):
    """以人类可读格式打印感知数据"""
    # 图标映射
    icons = {
        "time": "🕐",
        "weather": "🌤️",
        "system_info": "💻",
        "cpu": "⚙️",
        "memory": "🧠",
        "disk": "💾",
        "process": "📊",
        "uptime": "⏱️",
        "network_interfaces": "🌐",
        "public_ip": "📍",
        "connectivity": "📶",
        "dns": "🔍",
        "location": "🗺️",
        "timezone": "🌍",
        "battery": "🔋"
    }
    
    sense_type = data.get("sense_type", sense_name)
    icon = icons.get(sense_type, "📡")
    
    print(f"{icon} {sense_name} ({sense_type})")
    
    if "error" in data:
        print(f"   ❌ 错误: {data['error']}")
        print()
        return
    
    # 根据不同感知类型格式化输出
    if sense_type == "time":
        print(f"   📅 {data.get('datetime_string', 'N/A')}")
        print(f"   📆 {data.get('weekday_cn', '')} | 第{data.get('week_of_year', '?')}周 | {data.get('time_of_day', '')}")
        print(f"   ⏰ 一年中的第 {data.get('day_of_year', '?')} 天 | 季度: Q{data.get('quarter', '?')}")
    
    elif sense_type == "weather":
        print(f"   🌡️ 温度: {data.get('temperature_c', '?')}°C (体感 {data.get('feels_like_c', '?')}°C)")
        print(f"   💧 湿度: {data.get('humidity', '?')}% | 🌬️ 风速: {data.get('wind_speed_kmph', '?')} km/h")
        print(f"   ☁️ 天气: {data.get('weather_desc', '?')}")
        print(f"   📍 位置: {data.get('location', '?')}")
    
    elif sense_type == "cpu":
        print(f"   🧮 逻辑核心: {data.get('cpu_count_logical', '?')}")
        if data.get("cpu_count_physical"):
            print(f"   🔩 物理核心: {data.get('cpu_count_physical', '?')}")
        if data.get("load_average"):
            load = data["load_average"]
            print(f"   📊 负载: {load['1min']} / {load['5min']} / {load['15min']} (1/5/15min)")
        if data.get("usage_percent") is not None:
            print(f"   ⚡ 使用率: {data['usage_percent']}%")
    
    elif sense_type == "memory":
        print(f"   💾 总量: {data.get('total_human', '?')}")
        print(f"   ✅ 可用: {data.get('available_human', '?')}")
        print(f"   📈 已用: {data.get('used_human', '?')} ({data.get('usage_percent', '?')}%)")
    
    elif sense_type == "disk":
        print(f"   💿 路径: {data.get('path', '?')}")
        print(f"   📦 总量: {data.get('total_human', '?')}")
        print(f"   ✅ 可用: {data.get('available_human', '?')}")
        print(f"   📈 已用: {data.get('used_human', '?')} ({data.get('usage_percent', '?')}%)")
    
    elif sense_type == "battery":
        if not data.get("has_battery"):
            print(f"   🔌 未检测到电池")
        else:
            print(f"   🔋 电量: {data.get('capacity_percent', '?')}%")
            print(f"   ⚡ 状态: {data.get('charging_status', '?')}")
            if "remaining_time_hours" in data:
                print(f"   ⏳ 剩余: {data['remaining_time_hours']} 小时")
            if "health_percent" in data:
                print(f"   💚 健康度: {data['health_percent']}%")
    
    elif sense_type == "location":
        parts = []
        if "city" in data:
            parts.append(data["city"])
        if "region" in data:
            parts.append(data["region"])
        if "country" in data:
            parts.append(data["country"])
        print(f"   📍 位置: {', '.join(parts) if parts else '未知'}")
        if "latitude" in data and "longitude" in data:
            print(f"   🗺️ 坐标: {data['latitude']}, {data['longitude']}")
        if "timezone" in data:
            print(f"   🌍 时区: {data['timezone']}")
    
    elif sense_type == "connectivity":
        print(f"   🌐 互联网: {'✅ 已连接' if data.get('internet_access') else '❌ 未连接'}")
        print(f"   🔍 DNS: {'✅ 正常' if data.get('dns_ok') else '❌ 异常'}")
        if "average_latency_ms" in data:
            print(f"   ⚡ 平均延迟: {data['average_latency_ms']} ms")
    
    else:
        # 通用格式
        for key, value in data.items():
            if not key.startswith("_") and key != "sense_type":
                if isinstance(value, (dict, list)):
                    print(f"   {key}: {json.dumps(value, ensure_ascii=False)}")
                else:
                    print(f"   {key}: {value}")
    
    print()


def create_template(args):
    """生成新感知模块的模板"""
    registry = get_registry()
    sense_name = args.name
    description = args.description or ""
    
    template = registry.create_sense_template(sense_name, description)
    
    if args.output:
        with open(args.output, "w") as f:
            f.write(template)
        print(f"\n✅ 感知模块模板已生成: {args.output}\n")
    else:
        print(f"\n📝 感知模块模板 ({sense_name}):\n")
        print(template)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="WhatsGoingOn - 让 AI Agent 获得多维度感知能力",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  whatsgoingon.py list                    列出所有感知模块
  whatsgoingon.py quick                   快速获取状态感知
  whatsgoingon.py quick -t environment    获取环境感知
  whatsgoingOn.py call time_sense.get_current_time  调用指定感知函数
  whatsgoingon.py template my_sense       生成新感知模块模板
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # list 命令
    list_parser = subparsers.add_parser("list", help="列出所有可用的感知模块")
    list_parser.add_argument("-v", "--verbose", action="store_true", help="详细输出")
    list_parser.add_argument("-f", "--functions", action="store_true", help="显示所有函数")
    list_parser.set_defaults(func=list_senses)
    
    # quick 命令
    quick_parser = subparsers.add_parser("quick", help="快速获取感知信息")
    quick_parser.add_argument("-t", "--type", default="status",
                             choices=["all", "environment", "system", "status"],
                             help="感知类型 (默认: status)")
    quick_parser.add_argument("-j", "--json", action="store_true", help="JSON 格式输出")
    quick_parser.set_defaults(func=quick_sense)
    
    # call 命令
    call_parser = subparsers.add_parser("call", help="调用指定的感知函数")
    call_parser.add_argument("function", help="感知函数名，格式: sense_name.function_name")
    call_parser.add_argument("-p", "--params", nargs="*", help="参数，格式: key=value")
    call_parser.add_argument("-j", "--json", action="store_true", help="JSON 格式输出")
    call_parser.set_defaults(func=call_sense)
    
    # template 命令
    template_parser = subparsers.add_parser("template", help="生成新感知模块模板")
    template_parser.add_argument("name", help="感知模块名称")
    template_parser.add_argument("-d", "--description", help="感知模块描述")
    template_parser.add_argument("-o", "--output", help="输出文件路径")
    template_parser.set_defaults(func=create_template)
    
    args = parser.parse_args()
    
    if args.command is None:
        print_banner()
        parser.print_help()
        return
    
    if not args.quiet if hasattr(args, 'quiet') else False:
        if args.command != "list" or args.verbose:
            print_banner()
    
    args.func(args)


if __name__ == "__main__":
    main()
