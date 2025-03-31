#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
系统主程序 - 提供系统的主要功能和用户交互界面
"""

import logging
import argparse
from typing import Dict, List, Any, Optional

from .config_manager import get_config_manager
from .agent_manager import get_agent_manager
from .message_bus import get_message_bus, Message
from .model_connector import get_model_connector


class MultiAgentSystem:
    """多Agent协同系统主类"""
    
    def __init__(self, config_path: str = "agent_config.json"):
        """
        初始化系统
        
        Args:
            config_path: 配置文件路径
        """
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 初始化组件
        self.config_manager = get_config_manager(config_path)
        self.agent_manager = get_agent_manager()
        self.message_bus = get_message_bus()
        
        # 注册消息处理器
        self._register_message_handlers()
        
        # 获取主Agent
        self.main_agent = self.agent_manager.get_main_agent()
        self.system_info = self.config_manager.system_info
        
        logging.info(f"系统已初始化: {self.system_info.get('name')}")
        
    def _register_message_handlers(self) -> None:
        """注册所有Agent的消息处理器"""
        for agent_id, agent in self.agent_manager.agents.items():
            self.message_bus.register_handler(agent_id, self._create_message_handler(agent))
            
    def _create_message_handler(self, agent):
        """
        创建Agent的消息处理器
        
        Args:
            agent: Agent实例
            
        Returns:
            function: 消息处理函数
        """
        def handler(message: Message) -> str:
            # 将消息添加到Agent的上下文中
            agent.add_to_context({
                "role": "user" if message.from_agent == "user" else "assistant",
                "content": message.content
            })
            
            # 处理消息
            response = agent.process_message(message.content)
            
            # 将回复添加到Agent的上下文中
            agent.add_to_context({
                "role": "assistant",
                "content": response
            })
            
            return response
            
        return handler
    
    def process_user_input(self, user_input: str, workflow: str = "default_flow") -> str:
        """
        处理用户输入
        
        Args:
            user_input: 用户输入
            workflow: 工作流名称
            
        Returns:
            str: 系统回复
        """
        logging.info(f"收到用户输入: {user_input[:50]}...")
        
        try:
            # 执行工作流
            response = self.message_bus.execute_workflow(workflow, user_input)
            if response:
                return response
                
            # 如果工作流执行失败，直接使用主Agent处理
            logging.warning("工作流执行失败，使用主Agent处理")
            return self.main_agent.process_message(user_input) if self.main_agent else "系统错误"
            
        except Exception as e:
            logging.error(f"处理用户输入时出错: {e}")
            return f"处理您的请求时出错: {str(e)}"
    
    def run_cli(self) -> None:
        """运行命令行交互界面"""
        print(f"======== {self.system_info.get('name')} ========")
        print(f"版本: {self.system_info.get('version')}")
        print(f"描述: {self.system_info.get('description')}")
        print("输入'退出'或'exit'结束对话")
        print("=" * 50)
        
        while True:
            user_input = input("\n用户: ")
            if user_input.lower() in ["退出", "exit", "quit"]:
                print("系统已退出，感谢使用！")
                break
                
            response = self.process_user_input(user_input)
            print(f"\n系统: {response}")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="多Agent协同系统")
    parser.add_argument("--config", type=str, default="agent_config.json", help="配置文件路径")
    args = parser.parse_args()
    
    system = MultiAgentSystem(args.config)
    system.run_cli()


if __name__ == "__main__":
    main()
