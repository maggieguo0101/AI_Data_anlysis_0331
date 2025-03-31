#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
配置管理模块 - 负责读取和管理系统配置
"""

import json
import os
from typing import Dict, List, Any, Optional


class ConfigManager:
    """配置管理器类，负责读取和管理agent_config.json配置"""
    
    def __init__(self, config_path: str = "agent_config.json"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为agent_config.json
        """
        self.config_path = config_path
        self.config = self._load_config()
        self.system_info = self.config.get("system", {})
        self.agents_config = self.config.get("agents", [])
        self.workflow_config = self.config.get("workflow", {})
        self.context_sharing = self.config.get("context_sharing", {"enabled": False})
        
    def _load_config(self) -> Dict:
        """
        从配置文件加载配置
        
        Returns:
            Dict: 配置字典
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件出错: {e}")
            return {}
    
    def get_agent_config(self, agent_id: str) -> Optional[Dict]:
        """
        获取指定Agent的配置
        
        Args:
            agent_id: Agent的ID
            
        Returns:
            Dict: Agent的配置信息，如果未找到则返回None
        """
        for agent in self.agents_config:
            if agent.get("id") == agent_id:
                return agent
        return None
    
    def get_main_agent_id(self) -> Optional[str]:
        """
        获取主对话Agent的ID
        
        Returns:
            str: 主对话Agent的ID
        """
        # 在我们的系统中，王晓慧是主对话Agent
        for agent in self.agents_config:
            if agent.get("model") == self.system_info.get("model_config", {}).get("main_agent"):
                return agent.get("id")
        return None
    
    def get_sub_agent_ids(self) -> List[str]:
        """
        获取所有子Agent的ID列表
        
        Returns:
            List[str]: 子Agent的ID列表
        """
        main_agent_id = self.get_main_agent_id()
        return [agent.get("id") for agent in self.agents_config 
                if agent.get("id") != main_agent_id]
    
    def get_workflow(self, workflow_name: str = "default_flow") -> List[Dict]:
        """
        获取指定工作流程
        
        Args:
            workflow_name: 工作流名称，默认为default_flow
            
        Returns:
            List[Dict]: 工作流程配置
        """
        if workflow_name == "default_flow":
            return self.workflow_config.get("default_flow", [])
        
        # 寻找自定义工作流
        custom_flows = self.workflow_config.get("custom_flows", [])
        for flow in custom_flows:
            if flow.get("name") == workflow_name:
                return flow.get("flow", [])
        
        # 如果未找到指定工作流，返回默认工作流
        return self.workflow_config.get("default_flow", [])
    
    def is_context_sharing_enabled(self) -> bool:
        """
        检查上下文共享是否启用
        
        Returns:
            bool: 是否启用上下文共享
        """
        return self.context_sharing.get("enabled", False)
    
    def save_config(self, config: Dict) -> bool:
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置字典
            
        Returns:
            bool: 是否保存成功
        """
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            self.config = config
            return True
        except Exception as e:
            print(f"保存配置文件出错: {e}")
            return False


# 配置管理器单例
_config_manager = None


def get_config_manager(config_path: str = "agent_config.json") -> ConfigManager:
    """
    获取配置管理器单例
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        ConfigManager: 配置管理器实例
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager(config_path)
    return _config_manager
