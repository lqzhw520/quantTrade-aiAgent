import { io, Socket } from 'socket.io-client';

// WebSocket 配置 - 自动检测后端地址
const getBaseUrl = () => {
  // 优先使用后端 API 地址（与 api.ts 保持一致）
  if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
    return 'http://localhost:5002';
  }
  // 生产环境：同域名+5002端口
  const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
  return `${protocol}//${window.location.hostname}:5002`;
};

export const WS_BASE_URL = getBaseUrl();
console.log('使用 WebSocket 地址:', WS_BASE_URL);

// 创建 Socket.IO 实例
export const socket: Socket = io(WS_BASE_URL, {
  autoConnect: false, // 手动控制连接时机
  reconnection: true,
  reconnectionAttempts: Infinity, // 无限重连尝试
  reconnectionDelay: 1000,
  reconnectionDelayMax: 10000, // 增加最大重连延迟
  randomizationFactor: 0.5,
  timeout: 20000, // 增加连接超时时间
  transports: ['websocket', 'polling'], // 优先使用 WebSocket，失败时退回到轮询
});

// 连接状态变量
let isConnecting = false;
let retryCount = 0;
const maxRetryCount = 5;

// WebSocket 事件处理
export const initWebSocket = () => {
  // 避免重复事件监听，先移除所有已有监听器
  socket.off('connect');
  socket.off('connect_error');
  socket.off('disconnect');
  socket.off('error');
  socket.off('server_response');
  
  // 重新注册事件监听
  socket.on('connect', () => {
    console.log('WebSocket连接成功，ID:', socket.id);
    isConnecting = false;
    retryCount = 0; // 重置重试计数
  });

  socket.on('connect_error', (error) => {
    console.error('WebSocket连接错误:', error.message);
    
    if (!isConnecting && retryCount < maxRetryCount) {
      retryCount++;
      isConnecting = true;
      console.log(`连接失败，${retryCount}/${maxRetryCount}次重试...`);
      
      // 使用递增延迟
      setTimeout(() => {
        isConnecting = false;
        reconnect();
      }, 2000 * retryCount);
    } else if (retryCount >= maxRetryCount) {
      console.error(`已达到最大重试次数(${maxRetryCount})，WebSocket连接失败`);
    }
  });

  socket.on('disconnect', (reason) => {
    console.log('WebSocket连接断开，原因:', reason);
    
    // 如果是服务器端断开连接，则尝试重连
    if (reason === 'io server disconnect') {
      reconnect();
    }
  });

  socket.on('error', (error: any) => {
    console.error('WebSocket错误:', error);
  });

  // 监听服务器响应事件
  socket.on('server_response', (data) => {
    console.log('收到服务器响应:', data);
  });

  // 初始化 WebSocket 连接
  if (!socket.connected && !isConnecting) {
    reconnect();
  } else if (socket.connected) {
    console.log('WebSocket 已连接，ID:', socket.id);
  }
};

// 重连逻辑
const reconnect = () => {
  if (!socket.connected && !isConnecting) {
    console.log('尝试连接 WebSocket...');
    isConnecting = true;
    socket.connect();
    
    // 重置连接状态
    setTimeout(() => {
      isConnecting = false;
    }, 5000);
  }
};

// 断开 WebSocket 连接
export const disconnectWebSocket = () => {
  if (socket.connected) {
    console.log('断开 WebSocket 连接');
    socket.disconnect();
  } else {
    console.log('WebSocket 已断开连接，无需操作');
  }
};

// 发送消息到服务器，带重试
export const sendMessage = (event: string, data: any): boolean => {
  console.log(`尝试发送 ${event} 事件`);
  
  // 检查连接状态
  if (socket.connected) {
    try {
      socket.emit(event, data);
      console.log(`已发送消息: ${event}`, data);
      return true;
    } catch (error: any) {
      console.error(`发送消息失败: ${error.message}`);
      return false;
    }
  } else {
    console.warn(`WebSocket 未连接，正在尝试重连后发送消息...`);
    
    // 尝试重连
    reconnect();
    
    // 延迟重试发送消息
    setTimeout(() => {
      if (socket.connected) {
        try {
          socket.emit(event, data);
          console.log(`重试发送成功: ${event}`, data);
        } catch (error: any) {
          console.error(`重试发送失败: ${error.message}`);
        }
      } else {
        console.error(`WebSocket 连接失败，无法发送 ${event} 事件`);
      }
    }, 2000);
    
    return false;
  }
}; 