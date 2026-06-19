import http from 'http'; 
import { WebSocketServer } from 'ws'; 
 
export function setupWebSocket(server: http.Server) { 
  const wss = new WebSocketServer({ server, path: '/ws' }); 
  wss.on('connection', (socket) => { 
    console.log('Новое WebSocket-подключение'); 
    socket.on('message', (data) => { 
      try { 
        const message = JSON.parse(data.toString()); 
        console.log('Получено сообщение:', message.type); 
      } catch (err) { 
        socket.send(JSON.stringify({ type: 'ERROR', payload: 'Invalid format' })); 
      } 
    }); 
    socket.send(JSON.stringify({ type: 'CONNECTED', payload: { message: 'Соединение установлено' } })); 
  }); 
  console.log('WebSocket-сервер запущен'); 
} 
