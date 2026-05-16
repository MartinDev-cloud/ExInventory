// Fixed version of the registration router in register.js
// Changes:
// - Added server-side validation for all fields (lengths, formats, etc.)
// - Improved error handling
// - Ensured consistency with frontend validations

import { Router } from 'express';
import bcrypt from 'bcryptjs';
import jwt from 'jsonwebtoken';
import User from '../models/User.js';

const router = Router();

router.post('/', async (req, res) => {
  try {
    const {
      nombres,
      apellidos,
      email,
      telefono,
      password,
      tipoPersona,
      marca,
      ubicacion,
      aceptarDatos,
      aceptarCondiciones,
      tipo
    } = req.body;

    // Verificar que el tipo sea 'emprendedor'
    if (tipo !== 'emprendedor') {
      return res.status(400).json({ message: 'Tipo de usuario no válido. Solo se permite registro de emprendedores.' });
    }

    // Validaciones server-side
    const errores = [];
    if (!nombres || nombres.length > 255) errores.push('Nombres inválidos');
    if (!apellidos || apellidos.length > 255) errores.push('Apellidos inválidos');
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || email.length > 255) errores.push('Correo inválido');
    if (!telefono || !/^\d{7,15}$/.test(telefono)) errores.push('Teléfono inválido');
    if (!password || password.length < 6 || password.length > 255) errores.push('Contraseña inválida');
    if (!['natural', 'juridica'].includes(tipoPersona)) errores.push('Tipo de persona inválido');
    if (!marca || marca.length > 255) errores.push('Nombre de marca inválido');
    if (!ubicacion || ubicacion.length > 40) errores.push('Ubicación inválida');
    if (typeof aceptarDatos !== 'boolean' || !aceptarDatos) errores.push('Debes aceptar el tratamiento de datos');
    if (typeof aceptarCondiciones !== 'boolean' || !aceptarCondiciones) errores.push('Debes aceptar las condiciones');

    if (errores.length > 0) {
      return res.status(400).json({ message: 'Errores de validación', errors: errores });
    }

    // Verificar duplicados
    const userExistente = await User.findOne({ email });
    if (userExistente) {
      return res.status(400).json({ message: 'Correo ya registrado o error en el registro. Inténtalo de nuevo.' });
    }

    const marcaExistente = await User.findOne({ marca });
    if (marcaExistente) {
      return res.status(400).json({ message: 'Este nombre de marca ya se encuentra registrado.' });
    }

    // Hash de la contraseña
    const hash = await bcrypt.hash(password, 10);

    // Crear el usuario con todos los campos
    const nuevoUser = await User.create({
      nombres,
      apellidos,
      email,
      telefono,
      password: hash,
      tipoPersona,
      marca,
      ubicacion,
      aceptarDatos,
      aceptarCondiciones,
      tipo
    });

    // Generar token
    const token = jwt.sign({ id: nuevoUser._id, tipo: nuevoUser.tipo }, process.env.JWT_SECRET, { expiresIn: '1h' });

    res.status(201).json({
      message: 'Usuario registrado exitosamente',
      token,
      user: {
        _id: nuevoUser._id,
        nombres: nuevoUser.nombres,
        apellidos: nuevoUser.apellidos,
        email: nuevoUser.email,
        telefono: nuevoUser.telefono,
        tipoPersona: nuevoUser.tipoPersona,
        marca: nuevoUser.marca,
        ubicacion: nuevoUser.ubicacion,
        tipo: nuevoUser.tipo
      }
    });
  } catch (e) {
    console.error('Error en registro:', e);
    res.status(500).json({ message: 'Error interno del servidor', error: e.message });
  }
});

export default router;