// DOM元素
const sidebar = document.getElementById('sidebar');
const sidebarToggle = document.getElementById('sidebar-toggle');
const previewPanel = document.getElementById('preview-panel');
const previewToggle = document.getElementById('preview-toggle');
const previewClose = document.getElementById('preview-close');
const chatMessages = document.getElementById('chat-messages');
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const newChatButton = document.getElementById('new-chat-btn');
const chatHistory = document.getElementById('chat-history');

// 侧边栏折叠/展开功能
sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
});

// 预览面板显示/隐藏功能
function togglePreview() {
    previewPanel.classList.toggle('expanded');
}

if (previewToggle) {
    previewToggle.addEventListener('click', togglePreview);
}

if (previewClose) {
    previewClose.addEventListener('click', togglePreview);
}

// 消息发送功能
function sendMessage() {
    const message = messageInput.value.trim();
    if (message) {
        // 禁用发送按钮，防止重复发送
        sendButton.disabled = true;
        messageInput.disabled = true;
        
        // 添加用户消息到对话区域
        addMessage('用户', message, 'user-message');
        
        // 清空输入框
        messageInput.value = '';
        
        // 添加"正在思考"消息
        const thinkingId = addThinkingMessage();
        
        // 向服务器发送消息并获取回复
        fetch('/api/send_message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message })
        })
        .then(response => response.json())
        .then(data => {
            // 移除"正在思考"消息
            removeThinkingMessage(thinkingId);
            
            // 如果有思考过程，先显示思考过程
            if (data.thinking) {
                addThinkingContent(data.thinking);
            }
            
            // 添加回复消息
            addMessage('王晓慧', data.response, 'agent-message');
            
            // 如果有预览内容，显示在预览面板
            if (data.preview_html) {
                displayPreview(data.preview_html);
            }
            
            // 启用发送按钮
            sendButton.disabled = false;
            messageInput.disabled = false;
            messageInput.focus();
            
            // 滚动到底部
            scrollToBottom();
        })
        .catch(error => {
            console.error('Error:', error);
            removeThinkingMessage(thinkingId);
            addMessage('系统', '消息发送失败，请重试。', 'system-message');
            sendButton.disabled = false;
            messageInput.disabled = false;
        });
    }
}

// 按钮点击发送消息
sendButton.addEventListener('click', sendMessage);

// 按Enter键发送消息
messageInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// 添加消息到对话区域
function addMessage(sender, content, className) {
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${className}`;
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'avatar';
    avatarDiv.textContent = sender.charAt(0);
    
    const senderSpan = document.createElement('span');
    senderSpan.className = 'message-sender';
    senderSpan.textContent = sender;
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = time;
    
    headerDiv.appendChild(avatarDiv);
    headerDiv.appendChild(senderSpan);
    headerDiv.appendChild(timeSpan);
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    
    // 检查内容是否包含表格标记，如果有，转换为HTML表格
    if (content.includes('|')) {
        const lines = content.split('\n');
        let inTable = false;
        let tableHTML = '';
        let processedContent = '';
        
        for (const line of lines) {
            if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
                if (!inTable) {
                    inTable = true;
                    tableHTML = '<table class="message-table">';
                }
                
                // 处理表格行
                const cells = line.split('|').filter(cell => cell.trim() !== '');
                const isHeader = line.includes('---');
                
                if (isHeader) {
                    continue; // 跳过分隔行
                }
                
                tableHTML += '<tr>';
                for (const cell of cells) {
                    if (inTable && tableHTML.includes('<tr>') && !tableHTML.includes('</tr>')) {
                        tableHTML += `<th>${cell.trim()}</th>`;
                    } else {
                        tableHTML += `<td>${cell.trim()}</td>`;
                    }
                }
                tableHTML += '</tr>';
            } else {
                if (inTable) {
                    // 结束表格
                    tableHTML += '</table>';
                    processedContent += tableHTML;
                    inTable = false;
                    tableHTML = '';
                }
                processedContent += line + '\n';
            }
        }
        
        if (inTable) {
            tableHTML += '</table>';
            processedContent += tableHTML;
        }
        
        // 将处理后的内容设置为HTML
        contentDiv.innerHTML = processedContent.replace(/\n/g, '<br>');
    } else {
        // 普通文本，替换换行符为<br>
        contentDiv.innerHTML = content.replace(/\n/g, '<br>');
    }
    
    messageDiv.appendChild(headerDiv);
    messageDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(messageDiv);
    scrollToBottom();
    
    // 更新历史对话列表（仅当是新对话时）
    updateChatHistory(content);
}

// 添加"正在思考"消息
function addThinkingMessage() {
    const thinkingId = 'thinking-' + Date.now();
    const thinkingDiv = document.createElement('div');
    thinkingDiv.id = thinkingId;
    thinkingDiv.className = 'thinking';
    thinkingDiv.innerHTML = '王晓慧正在思考<span class="loading-dots"></span>';
    
    chatMessages.appendChild(thinkingDiv);
    scrollToBottom();
    
    return thinkingId;
}

// 移除"正在思考"消息
function removeThinkingMessage(id) {
    const thinkingDiv = document.getElementById(id);
    if (thinkingDiv) {
        thinkingDiv.remove();
    }
}

// 添加思考内容
function addThinkingContent(thinking) {
    if (!thinking) return;
    
    const thinkingDiv = document.createElement('div');
    thinkingDiv.className = 'message agent-message';
    
    const headerDiv = document.createElement('div');
    headerDiv.className = 'message-header';
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'avatar';
    avatarDiv.textContent = '思';
    
    const senderSpan = document.createElement('span');
    senderSpan.className = 'message-sender';
    senderSpan.textContent = '思考过程';
    
    const timeSpan = document.createElement('span');
    timeSpan.className = 'message-time';
    timeSpan.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    headerDiv.appendChild(avatarDiv);
    headerDiv.appendChild(senderSpan);
    headerDiv.appendChild(timeSpan);
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content thinking';
    contentDiv.innerHTML = thinking.replace(/\n/g, '<br>');
    
    thinkingDiv.appendChild(headerDiv);
    thinkingDiv.appendChild(contentDiv);
    
    chatMessages.appendChild(thinkingDiv);
    scrollToBottom();
}

// 显示预览内容
function displayPreview(html) {
    // 如果预览面板是隐藏的，显示它
    if (!previewPanel.classList.contains('expanded')) {
        previewPanel.classList.add('expanded');
    }
    
    // 获取预览内容区域
    const previewContent = document.getElementById('preview-content');
    
    // 创建一个iframe来显示HTML内容
    const iframe = document.createElement('iframe');
    iframe.className = 'preview-iframe';
    
    // 清空预览内容区域
    previewContent.innerHTML = '';
    
    // 添加iframe到预览内容区域
    previewContent.appendChild(iframe);
    
    // 设置iframe内容
    setTimeout(() => {
        iframe.contentWindow.document.open();
        iframe.contentWindow.document.write(html);
        iframe.contentWindow.document.close();
    }, 100);
}

// 滚动到底部
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 更新历史对话列表
function updateChatHistory(content) {
    // 提取对话标题（取前10个字符）
    const title = content.length > 10 ? content.substring(0, 10) + '...' : content;
    
    // 检查是否已经有这个对话在历史列表中
    const existingItems = chatHistory.querySelectorAll('.history-item');
    for (const item of existingItems) {
        if (item.getAttribute('data-title') === title) {
            return; // 如果已存在，不再添加
        }
    }
    
    // 创建新的历史对话项
    const historyItem = document.createElement('div');
    historyItem.className = 'history-item';
    historyItem.setAttribute('data-title', title);
    
    const icon = document.createElement('i');
    icon.className = 'fas fa-comment';
    
    const span = document.createElement('span');
    span.textContent = title;
    
    historyItem.appendChild(icon);
    historyItem.appendChild(span);
    
    // 为新的历史对话项添加点击事件
    historyItem.addEventListener('click', () => {
        // 移除其他项的active类
        const items = chatHistory.querySelectorAll('.history-item');
        items.forEach(item => item.classList.remove('active'));
        
        // 添加active类到当前项
        historyItem.classList.add('active');
        
        // 加载对话内容（这里需要后端支持）
        // 此处仅为示例，实际实现需要与后端交互
        // loadChatHistory(title);
    });
    
    // 将新的历史对话项添加到历史列表最前面
    chatHistory.insertBefore(historyItem, chatHistory.firstChild);
}

// 新对话功能
newChatButton.addEventListener('click', () => {
    // 清空对话区域
    chatMessages.innerHTML = '';
    
    // 移除历史项的active类
    const items = chatHistory.querySelectorAll('.history-item');
    items.forEach(item => item.classList.remove('active'));
    
    // 启用发送按钮和输入框
    sendButton.disabled = false;
    messageInput.disabled = false;
    messageInput.value = '';
    messageInput.focus();
    
    // 隐藏预览面板
    previewPanel.classList.remove('expanded');
});

// 在页面加载完成后执行
document.addEventListener('DOMContentLoaded', () => {
    // 示例：添加一条欢迎消息
    addMessage('王晓慧', '您好，我是品牌服务报告系统的主对话Agent王晓慧。请问有什么可以帮助您？', 'agent-message');
    
    // 聚焦到输入框
    messageInput.focus();
});
