import { Router } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import User from '../models/User.js';

const router = Router();

router.post('/', async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ email });
    if (!user) return res.status(400).json({ error: 'Usuario no encontrado' });
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) return res.status(400).json({ error: 'Contraseña incorrecta' });
    const token = jwt.sign({ id: user._id, tipo: user.tipo }, process.env.JWT_SECRET, { expiresIn: '1h' });
    // Para emprendedores, usa nombres + apellidos; para clientes, nombre
    let nombreDisplay = user.nombre;  // Para clientes
    if (user.tipo === 'emprendedor') {
      nombreDisplay = `${user.nombres} ${user.apellidos}`.trim();  // Para emprendedores
    }
    res.json({
      message: 'Login exitoso',
      token,
      user: { _id: user._id, nombre: nombreDisplay, email: user.email, tipo: user.tipo }
    });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
});

export default router;
