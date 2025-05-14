import { io, Socket } from 'socket.io-client';

// WebSocket 配置 - 自动检测后端地址
// 首先尝试使用当前 window.location 的主机名和对应协议
// 如果运行在开发环境，则默认使用 localhost:5002
const getBaseUrl = () => {
  // 如果是生产环境，使用相同的主机名，只改变端口
  if (window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
    const protocol = window.location.protocol === 'https:' ? 'https:' : 'http:';
    return `${protocol}//${window.location.hostname}:5002`;
  }
  
  // 默认后端地址
  return 'http://localhost:5002';
};

export const WS_BASE_URL = getBaseUrl();
console.log('使用 WebSocket 地址:', WS_BASE_URL);

// 创建 Socket.IO 实例
export const socket: Socket = io(WS_BASE_URL, {
  autoConnect: true, // 自动连接
  reconnection: true,
  reconnectionAttempts: 10,
  reconnectionDelay: 1000,
  reconnectionDelayMax: 5000,
  randomizationFactor: 0.5,
  transports: ['websocket', 'polling'], // 优先使用 WebSocket
  timeout: 10000,
  forceNew: true,
});

// WebSocket 事件处理
export const initWebSocket = () => {
  // 避免重复事件监听
  socket.off('connect').on('connect', () => {
    console.log('WebSocket连接成功，ID:', socket.id);
  });

  socket.off('connect_error').on('connect_error', (error) => {
    console.error('WebSocket连接错误:', error.message);
  });

  socket.off('disconnect').on('disconnect', (reason) => {
    console.log('WebSocket连接断开，原因:', reason);
  });

  socket.off('error').on('error', (error) => {
    console.error('WebSocket错误:', error);
  });

  // 监听服务器响应事件
  socket.off('server_response').on('server_response', (data) => {
    console.log('收到服务器响应:', data);
  });

  // 初始化 WebSocket 连接
  if (!socket.connected) {
    console.log('尝试连接 WebSocket...');
    socket.connect();
  } else {
    console.log('WebSocket 已连接');
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

// 发送消息到服务器
export const sendMessage = (event: string, data: any) => {
  console.log(`尝试发送 ${event} 事件`);
  if (socket.connected) {
    socket.emit(event, data);
    console.log(`已发送消息: ${event}`, data);
    return true;
  } else {
    console.error(`WebSocket 未连接，无法发送 ${event} 事件`);
    // 尝试重连
    socket.connect();
    return false;
  }
}; 