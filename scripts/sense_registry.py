#!/usr/bin/env python3
"""
感知注册表 - Sense Registry
WhatsGoingOn 的核心扩展机制

允许 AI Agent 动态注册、发现和调用各种感知模块
支持插件式架构，模型可以自己编写并加载新的感知能力

灵感来源：Claude 获得时间感知后的成瘾式探索行为
- 当模型获得一个新的感知维度时，会表现出强烈的探索倾向
- 这个注册表让模型可以无限扩展自己的感知边界

Author: GitHub@StarsailsClover
Version: v26.0 Alpha 2
"""

import os
import sys
import importlib
import importlib.util
import json
from typing import Dict, List, Callable, Any, Optional


class SenseRegistry:
    """
    感知注册表 - 管理所有感知模块
    
    核心功能：
    1. 自动发现和加载内置感知模块
    2. 支持动态注册新的感知模块
    3. 统一的感知调用接口
    4. 感知元数据管理
    """
    
    def __init__(self, senses_dir: str = None):
        """
        初始化感知注册表
        
        Args:
            senses_dir: 感知模块目录，为 None 时使用默认目录
        """
        self._senses: Dict[str, dict] = {}
        self._sense_functions: Dict[str, Callable] = {}
        
        if senses_dir is None:
            # 默认使用当前脚本所在目录下的 senses 子目录
            senses_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "senses")
        
        self._senses_dir = senses_dir
        
        # 自动加载内置感知模块
        self._load_builtin_senses()
    
    def _load_builtin_senses(self):
        """自动加载内置感知模块"""
        if not os.path.exists(self._senses_dir):
            return
        
        # 添加感知模块目录到 Python 路径
        if self._senses_dir not in sys.path:
            sys.path.insert(0, os.path.dirname(self._senses_dir))
        
        # 遍历感知模块文件
        for filename in os.listdir(self._senses_dir):
            if filename.endswith("_sense.py") and not filename.startswith("_"):
                sense_name = filename[:-3]  # 去掉 .py
                try:
                    # 导入模块
                    module_name = f"senses.{sense_name}"
                    module = importlib.import_module(module_name)
                    
                    # 注册感知模块
                    self._register_sense_module(sense_name, module)
                except Exception as e:
                    print(f"警告: 加载感知模块 {sense_name} 失败: {e}", file=sys.stderr)
    
    def _register_sense_module(self, sense_name: str, module: Any):
        """
        注册一个感知模块
        
        Args:
            sense_name: 感知名称
            module: Python 模块对象
        """
        # 提取模块中的主要函数
        functions = {}
        for attr_name in dir(module):
            if attr_name.startswith("get_") or attr_name.startswith("check_") or attr_name.startswith("sense_"):
                func = getattr(module, attr_name)
                if callable(func):
                    functions[attr_name] = func
        
        # 获取模块文档字符串
        doc = module.__doc__ or ""
        
        # 注册感知元数据
        self._senses[sense_name] = {
            "name": sense_name,
            "description": doc.split("\n")[1].strip() if doc else "",
            "full_doc": doc,
            "functions": list(functions.keys()),
            "source": "builtin",
            "module": module
        }
        
        # 注册函数
        for func_name, func in functions.items():
            full_name = f"{sense_name}.{func_name}"
            self._sense_functions[full_name] = func
    
    def register_custom_sense(self, sense_name: str, sense_function: Callable, 
                              description: str = "", metadata: dict = None) -> bool:
        """
        注册自定义感知函数
        
        AI Agent 可以使用此方法动态扩展自己的感知能力
        
        Args:
            sense_name: 感知名称（唯一标识）
            sense_function: 感知函数，应返回一个字典
            description: 感知描述
            metadata: 额外的元数据
        
        Returns:
            是否注册成功
        """
        if sense_name in self._senses:
            # 已存在，更新
            pass
        
        self._senses[sense_name] = {
            "name": sense_name,
            "description": description,
            "functions": [sense_function.__name__],
            "source": "custom",
            "metadata": metadata or {}
        }
        
        full_name = f"{sense_name}.{sense_function.__name__}"
        self._sense_functions[full_name] = sense_function
        
        return True
    
    def register_sense_from_file(self, filepath: str, sense_name: str = None) -> bool:
        """
        从文件加载自定义感知模块
        
        AI Agent 可以编写自己的感知模块文件，然后通过此方法加载
        
        Args:
            filepath: 感知模块文件路径
            sense_name: 感知名称，为 None 时从文件名推断
        
        Returns:
            是否加载成功
        """
        if not os.path.exists(filepath):
            return False
        
        if sense_name is None:
            sense_name = os.path.splitext(os.path.basename(filepath))[0]
        
        try:
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(sense_name, filepath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 注册模块
            self._register_sense_module(sense_name, module)
            
            # 标记为自定义来源
            self._senses[sense_name]["source"] = "file"
            self._senses[sense_name]["filepath"] = filepath
            
            return True
        except Exception as e:
            print(f"警告: 从文件加载感知模块失败: {e}", file=sys.stderr)
            return False
    
    def call_sense(self, sense_function_name: str, **kwargs) -> dict:
        """
        调用感知函数
        
        Args:
            sense_function_name: 感知函数全名，格式为 "sense_name.function_name"
            **kwargs: 传递给感知函数的参数
        
        Returns:
            感知结果字典
        """
        if sense_function_name not in self._sense_functions:
            return {
                "error": f"感知函数不存在: {sense_function_name}",
                "available_senses": self.list_senses()
            }
        
        try:
            func = self._sense_functions[sense_function_name]
            result = func(**kwargs)
            
            # 确保结果是字典
            if not isinstance(result, dict):
                result = {"result": result}
            
            # 添加感知元数据
            result["_sense_function"] = sense_function_name
            result["_sense_name"] = sense_function_name.split(".")[0]
            
            return result
        except Exception as e:
            return {
                "error": f"感知调用失败: {e}",
                "sense_function": sense_function_name
            }
    
    def list_senses(self) -> List[dict]:
        """
        列出所有可用的感知模块
        
        Returns:
            感知模块列表
        """
        return list(self._senses.values())
    
    def get_sense_info(self, sense_name: str) -> Optional[dict]:
        """
        获取指定感知模块的详细信息
        
        Args:
            sense_name: 感知名称
        
        Returns:
            感知模块信息，不存在时返回 None
        """
        return self._senses.get(sense_name)
    
    def get_all_functions(self) -> List[str]:
        """
        获取所有可用的感知函数名称
        
        Returns:
            感知函数名称列表
        """
        return list(self._sense_functions.keys())
    
    def quick_sense(self, sense_type: str = "all") -> dict:
        """
        快速获取多种感知信息的汇总
        
        Args:
            sense_type: 感知类型
                - "all": 获取所有快速感知
                - "environment": 环境相关（时间、天气、位置）
                - "system": 系统相关（CPU、内存、磁盘、网络）
                - "status": 状态摘要
        
        Returns:
            感知信息汇总
        """
        result = {
            "sense_type": sense_type,
            "timestamp": __import__("time").time(),
            "senses": {}
        }
        
        # 定义各类型包含的感知函数
        sense_map = {
            "environment": [
                "time_sense.get_current_time",
                "weather_sense.get_weather",
                "location_sense.get_location_by_ip",
                "storage_sense.get_disk_usage",
                "cpu_sense.get_cpu_info",
                "memory_sense.get_memory_info"
            ],
            "system": [
                "system_sense.get_cpu_info",
                "system_sense.get_memory_info",
                "system_sense.get_disk_info",
                "storage_sense.get_disk_usage",
                "cpu_sense.get_cpu_info",
                "memory_sense.get_memory_info",
                "network_sense.check_connectivity"
            ],
            "status": [
                "time_sense.get_current_time",
                "cpu_sense.get_cpu_info",
                "memory_sense.get_memory_info",
                "storage_sense.get_disk_usage",
                "battery_sense.get_battery_info",
                "network_sense.check_connectivity"
            ],
            "storage": [
                "storage_sense.get_disk_usage"
            ],
            "cpu": [
                "cpu_sense.get_cpu_info"
            ],
            "memory": [
                "memory_sense.get_memory_info"
            ]
        }
        
        if sense_type == "all":
            functions = []
            for funcs in sense_map.values():
                functions.extend(funcs)
        elif sense_type in sense_map:
            functions = sense_map[sense_type]
        else:
            functions = [sense_type] if sense_type in self._sense_functions else []
        
        for func_name in functions:
            if func_name in self._sense_functions:
                try:
                    sense_result = self.call_sense(func_name)
                    sense_name = func_name.split(".")[0]
                    result["senses"][sense_name] = sense_result
                except Exception as e:
                    result["senses"][func_name] = {"error": str(e)}
        
        return result
    
    def create_sense_template(self, sense_name: str, description: str = "") -> str:
        """
        生成一个新感知模块的代码模板
        
        AI Agent 可以使用此模板创建自己的感知模块
        
        Args:
            sense_name: 感知名称
            description: 感知描述
        
        Returns:
            感知模块代码模板
        """
        template = f'''#!/usr/bin/env python3
"""
{sense_name} - {description}

自定义感知模块 - 由 AI Agent 动态创建
使用 SenseRegistry.register_sense_from_file() 加载此模块

Author: AI Agent (WhatsGoingOn Framework)
Created: {__import__('datetime').datetime.now().isoformat()}
"""

import json


def get_{sense_name}(**kwargs) -> dict:
    """
    获取 {sense_name} 感知信息
    
    Args:
        **kwargs: 感知参数
    
    Returns:
        感知结果字典，必须包含 sense_type 字段
    """
    result = {{
        "sense_type": "{sense_name}",
        "status": "success"
        # 在这里添加你的感知逻辑
        # 例如:
        # "value": some_value,
        # "details": {{...}}
    }}
    
    return result


def check_{sense_name}(**kwargs) -> dict:
    """
    检查 {sense_name} 状态（可选）
    
    Returns:
        状态检查结果
    """
    return {{
        "sense_type": "{sense_name}_check",
        "available": True,
        "message": "感知模块正常工作"
    }}


if __name__ == "__main__":
    # 测试代码
    print("=== {sense_name} 感知测试 ===")
    print(json.dumps(get_{sense_name}(), ensure_ascii=False, indent=2))
'''
        return template


# 全局单例
_registry_instance = None


def get_registry(senses_dir: str = None) -> SenseRegistry:
    """
    获取全局感知注册表单例
    
    Args:
        senses_dir: 感知模块目录（仅首次调用时有效）
    
    Returns:
        感知注册表实例
    """
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = SenseRegistry(senses_dir)
    return _registry_instance


if __name__ == "__main__":
    # 测试注册表
    registry = get_registry()
    
    print("=== WhatsGoingOn 感知注册表 ===")
    print(f"版本: v26.0 Alpha 2")
    print(f"作者: GitHub@StarsailsClover")
    print()
    
    print("已加载的感知模块:")
    for sense in registry.list_senses():
        print(f"  - {sense['name']}: {sense['description']}")
        print(f"    函数: {', '.join(sense['functions'])}")
        print(f"    来源: {sense['source']}")
        print()
    
    print("所有可用的感知函数:")
    for func in registry.get_all_functions():
        print(f"  - {func}")
    print()
    
    print("快速环境感知:")
    quick = registry.quick_sense("environment")
    print(json.dumps(quick, ensure_ascii=False, indent=2))
