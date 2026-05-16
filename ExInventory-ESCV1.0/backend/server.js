import express from 'express';
import dotenv from 'dotenv';
import mongoose from 'mongoose';
import cors from 'cors';
import registerEscritorio from './routes/register_escritorio.js'; // escritorio
import loginRoutes from './routes/login_escritorio.js'; // login

dotenv.config();
const app = express();

app.use(cors());
app.use(express.json());

// rutas
app.use('/api/auth/register_escritorio', registerEscritorio); // escritorio
app.use('/api/auth/login', loginRoutes);
app.use('/login_escritorio', loginRoutes);

// conexión a MongoDB
mongoose.connect(process.env.MONGO_URI)
  .then(() => console.log('✅ MongoDB conectado'))
  .catch(err => console.log('❌ Error Mongo:', err.message));

// iniciar servidor
app.listen(5001, () => console.log('🚀 Servidor escritorio corriendo en http://localhost:5001'));
