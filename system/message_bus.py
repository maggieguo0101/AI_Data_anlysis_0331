#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
消息总线模块 - 负责Agent之间的消息传递和工作流管理
"""

from typing import Dict, List, Any, Optional, Callable
import logging
from .config_manager import get_config_manager


class Message:
    """消息类，表示Agent之间传递的消息"""
    
    def __init__(self, from_agent: str, to_agent: str, content: str, message_type: str = "text"):
        """
        初始化消息
        
        Args:
            from_agent: 发送方Agent的ID
            to_agent: 接收方Agent的ID
            content: 消息内容
            message_type: 消息类型，默认为text
        """
        self.from_agent = from_agent
        self.to_agent = to_agent
        self.content = content
        self.message_type = message_type
        
    def to_dict(self) -> Dict:
        """
        转换为字典格式
        
        Returns:
            Dict: 消息字典
        """
        return {
            "from": self.from_agent,
            "to": self.to_agent,
            "content": self.content,
            "type": self.message_type
        }


class MessageBus:
    """消息总线类，负责管理消息路由和工作流执行"""
    
    def __init__(self):
        """初始化消息总线"""
        self.config_manager = get_config_manager()
        self.message_handlers = {}  # 消息处理器字典，键为agent_id
        self.message_queue = []  # 消息队列
        
    def register_handler(self, agent_id: str, handler: Callable[[Message], Optional[str]]) -> None:
        """
        注册消息处理器
        
        Args:
            agent_id: Agent的ID
            handler: 消息处理函数，接收Message对象，返回处理结果
        """
        self.message_handlers[agent_id] = handler
        
    def send_message(self, message: Message) -> Optional[str]:
        """
        发送消息
        
        Args:
            message: 要发送的消息
            
        Returns:
            Optional[str]: 接收方处理后的回复，若无回复则返回None
        """
        # 添加到消息队列
        self.message_queue.append(message)
        
        # 查找接收方的处理器
        handler = self.message_handlers.get(message.to_agent)
        if not handler:
            logging.warning(f"未找到接收方 {message.to_agent} 的消息处理器")
            return None
        
        # 调用处理器处理消息
        try:
            return handler(message)
        except Exception as e:
            logging.error(f"处理消息时出错: {e}")
            return None
    
    def broadcast_message(self, from_agent: str, content: str, 
                         to_agents: List[str], message_type: str = "text") -> Dict[str, str]:
        """
        广播消息给多个Agent
        
        Args:
            from_agent: 发送方Agent的ID
            content: 消息内容
            to_agents: 接收方Agent的ID列表
            message_type: 消息类型
            
        Returns:
            Dict[str, str]: 各接收方的回复，键为agent_id，值为回复内容
        """
        responses = {}
        for to_agent in to_agents:
            message = Message(from_agent, to_agent, content, message_type)
            response = self.send_message(message)
            responses[to_agent] = response if response else ""
        return responses
    
    def execute_workflow(self, workflow_name: str, initial_message: str, 
                        from_agent: str = "user") -> Optional[str]:
        """
        执行指定的工作流
        
        Args:
            workflow_name: 工作流名称
            initial_message: 初始消息内容
            from_agent: 初始发送方，默认为user
            
        Returns:
            Optional[str]: 工作流执行的最终结果
        """
        workflow = self.config_manager.get_workflow(workflow_name)
        if not workflow:
            logging.error(f"未找到工作流: {workflow_name}")
            return None
        
        current_message = initial_message
        current_from = from_agent
        
        # 按工作流顺序执行每一步
        for step in workflow:
            step_from = step.get("from")
            step_to = step.get("to")
            
            # 跳过不匹配当前发送方的步骤
            if step_from != current_from:
                continue
                
            # 处理接收方为列表的情况（并行处理）
            if isinstance(step_to, list):
                responses = self.broadcast_message(current_from, current_message, step_to)
                # TODO: 实现并行处理结果的合并逻辑
                # 这里简单地将所有回复连接起来
                current_message = "\n".join(responses.values())
            else:
                # 单一接收方
                message = Message(current_from, step_to, current_message)
                response = self.send_message(message)
                if response:
                    current_message = response
                    
            # 更新下一步的发送方
            current_from = step_to if not isinstance(step_to, list) else step_to[-1]
            
        return current_message


# 消息总线单例
_message_bus = None


def get_message_bus() -> MessageBus:
    """
    获取消息总线单例
    
    Returns:
        MessageBus: 消息总线实例
    """
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus
