#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Web应用程序 - 提供王晓慧对话界面的Web服务
"""

import os
import sys
import json
from flask import Flask, render_template, request, jsonify

# 添加项目根目录到Python路径，以便导入system模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from system.app import MultiAgentSystem

# 创建Flask应用
app = Flask(__name__, static_folder='static', template_folder='templates')

# 创建多Agent系统实例
multi_agent_system = MultiAgentSystem(os.path.join(parent_dir, "agent_config.json"))

# 当前会话历史
chat_sessions = {}
current_session_id = "default"

@app.route('/')
def index():
    """渲染主页面"""
    return render_template('index.html')

@app.route('/api/send_message', methods=['POST'])
def send_message():
    """处理发送消息请求"""
    data = request.json
    message = data.get('message', '')
    session_id = data.get('session_id', current_session_id)
    
    if not message:
        return jsonify({
            'status': 'error',
            'message': '消息不能为空'
        }), 400
    
    # 确保会话存在
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    # 添加用户消息到会话历史
    chat_sessions[session_id].append({
        'role': 'user',
        'content': message
    })
    
    try:
        # 调用多Agent系统处理消息
        # 这里假设process_user_input会返回完整的响应，包括思考过程
        response = multi_agent_system.process_user_input(message)
        
        # 模拟分离思考过程和最终回复
        # 实际实现中，可能需要修改MultiAgentSystem的返回格式
        thinking = ""
        final_response = response
        preview_html = ""
        
        # 如果回复包含特定格式，可以提取思考过程和预览HTML
        # 这里是一个示例格式，实际格式需要与后端对齐
        if "【思考过程】" in response:
            parts = response.split("【思考过程】")
            if len(parts) > 1:
                final_response = parts[0].strip()
                thinking = parts[1].strip()
        
        # 检查是否包含预览HTML
        if "【预览内容】" in response:
            parts = response.split("【预览内容】")
            if len(parts) > 1:
                preview_parts = parts[1].split("【预览结束】")
                if len(preview_parts) > 1:
                    preview_html = preview_parts[0].strip()
        
        # 添加回复到会话历史
        chat_sessions[session_id].append({
            'role': 'assistant',
            'content': final_response,
            'thinking': thinking
        })
        
        return jsonify({
            'status': 'success',
            'response': final_response,
            'thinking': thinking,
            'preview_html': preview_html
        })
    
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'处理消息时出错: {str(e)}'
        }), 500

@app.route('/api/chat_sessions', methods=['GET'])
def get_chat_sessions():
    """获取所有聊天会话"""
    return jsonify({
        'status': 'success',
        'sessions': list(chat_sessions.keys())
    })

@app.route('/api/chat_history/<session_id>', methods=['GET'])
def get_chat_history(session_id):
    """获取特定会话的聊天历史"""
    if session_id not in chat_sessions:
        return jsonify({
            'status': 'error',
            'message': f'会话 {session_id} 不存在'
        }), 404
    
    return jsonify({
        'status': 'success',
        'history': chat_sessions[session_id]
    })

@app.route('/api/new_session', methods=['POST'])
def new_session():
    """创建新的聊天会话"""
    global current_session_id
    session_id = f"session_{len(chat_sessions) + 1}"
    chat_sessions[session_id] = []
    current_session_id = session_id
    
    return jsonify({
        'status': 'success',
        'session_id': session_id
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
