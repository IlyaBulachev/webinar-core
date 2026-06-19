import http from 'http'; 
import { app } from './app'; 
import { config } from './config'; 
import { PrismaClient } from '@prisma/client'; 
 
const prisma = new PrismaClient(); 
 
async function bootstrap() { 
  await prisma.$connect(); 
  console.log('База данных подключена'); 
 
  const server = http.createServer(app); 
 
  server.listen(config.port, () => { 
    console.log('Сервер запущен на порту ' + config.port); 
  }); 
} 
 
bootstrap().catch(console.error); 
