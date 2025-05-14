import { io, Socket } from 'socket.io-client';

// Flask-SocketIO 服务器地址 - 注意后端使用5002端口
const SOCKET_URL = 'http://localhost:5002';
let socket: Socket | null = null;

export const initSocket = (): Socket | null => {
  if (socket && socket.connected) return socket; // 防止重复初始化

  socket = io(SOCKET_URL, {
    // 可选配置
    // transports: ['websocket'],
    // autoConnect: true,
    // reconnection: true,
    // reconnectionAttempts: 5,
  });

  socket.on('connect', () => {
    console.log('成功连接到WebSocket服务器，ID:', socket?.id);
  });

  socket.on('disconnect', (reason) => {
    console.log('WebSocket连接断开:', reason);
  });

  socket.on('connect_error', (error) => {
    console.error('WebSocket连接错误:', error);
  });

  // 监听服务器响应事件
  socket.on('server_response', (data) => {
    console.log('收到服务器响应:', data);
  });

  return socket;
};

export const disconnectSocket = (): void => {
  if (socket) {
    socket.disconnect();
  }
};

export const sendMessage = (eventName: string, data: any): void => {
  if (socket && socket.connected) {
    socket.emit(eventName, data);
    console.log(`发送消息: ${eventName}`, data);
  } else {
    console.error('Socket未连接，无法发送消息');
  }
};

// 获取socket实例
export const getSocket = (): Socket | null => socket; 