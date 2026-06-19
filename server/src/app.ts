import express from 'express'; 
import cors from 'cors'; 
import helmet from 'helmet'; 
import { config } from './config'; 
 
const app = express(); 
app.use(helmet({ contentSecurityPolicy: false })); 
app.use(cors({ origin: config.client.origin, credentials: true })); 
app.use(express.json()); 
 
app.get('/api/health', (_req, res) => { 
  res.json({ status: 'ok' }); 
}); 
 
export { app }; 
