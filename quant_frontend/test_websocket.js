// 测试WebSocket连接脚本
import { io } from 'socket.io-client';

const socket = io('http://localhost:5002', {
  reconnectionAttempts: 3,
  timeout: 10000
});

socket.on('connect', () => {
  console.log('连接成功！Socket ID:', socket.id);
  
  // 发送测试消息
  socket.emit('client_event', { 
    message: '来自测试脚本的消息', 
    timestamp: new Date().toISOString() 
  });
  
  console.log('测试消息已发送，等待服务器响应...');
});

socket.on('connect_error', (error) => {
  console.error('连接错误:', error);
});

socket.on('server_response', (data) => {
  console.log('收到服务器响应:', data);
  
  // 测试完成后断开连接
  setTimeout(() => {
    socket.disconnect();
    console.log('测试完成，Socket已断开连接');
    process.exit(0);
  }, 1000);
});

// 如果10秒内没有收到响应，则超时
setTimeout(() => {
  console.error('测试超时，未收到服务器响应');
  socket.disconnect();
  process.exit(1);
}, 10000);

console.log('正在尝试连接到WebSocket服务器...'); 