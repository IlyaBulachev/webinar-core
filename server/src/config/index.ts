import dotenv from 'dotenv'; 
dotenv.config(); 
 
export const config = { 
  port: parseInt(process.env.PORT || '3000'), 
  jwt: { 
    secret: process.env.JWT_SECRET || 'dev-secret', 
    accessExpiresIn: '15m', 
  }, 
  database: { 
    url: process.env.DATABASE_URL || '', 
  }, 
  redis: { 
    url: process.env.REDIS_URL || 'redis://localhost:6379', 
  }, 
  janus: { 
    adminUrl: process.env.JANUS_ADMIN_URL || 'http://localhost:7088/admin', 
    adminSecret: process.env.JANUS_ADMIN_SECRET || 'janusoverlord', 
  }, 
  client: { 
    origin: process.env.CLIENT_ORIGIN || 'http://localhost:3001', 
  }, 
}; 
