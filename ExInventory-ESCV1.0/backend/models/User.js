import mongoose from 'mongoose';

const userSchema = new mongoose.Schema({
  // Campos comunes
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  tipo: { type: String, enum: ['cliente', 'emprendedor'], default: 'cliente' },
  createdAt: { type: Date, default: Date.now },

  // Campos adicionales para emprendedores (opcionales para clientes)
  nombres: { type: String, required: function() { return this.tipo === 'emprendedor'; } },
  apellidos: { type: String, required: function() { return this.tipo === 'emprendedor'; } },
  telefono: { type: String, required: function() { return this.tipo === 'emprendedor'; } },
  tipoPersona: { type: String, enum: ['natural', 'juridica'], required: function() { return this.tipo === 'emprendedor'; } },
  marca: { type: String, required: function() { return this.tipo === 'emprendedor'; }, unique: true }, // Único para evitar duplicados
  ubicacion: { type: String, required: function() { return this.tipo === 'emprendedor'; }},
  aceptarDatos: { type: Boolean, required: function() { return this.tipo === 'emprendedor'; } },
  aceptarCondiciones: { type: Boolean, required: function() { return this.tipo === 'emprendedor'; } },
});

export default mongoose.model('User', userSchema, "Usuarios");