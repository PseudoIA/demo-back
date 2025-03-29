from database import db
from datetime import datetime
import bcrypt

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    rol = db.Column(db.String(20), nullable=False)  # 'maestro' o 'coordinador'
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relación con cronogramas
    cronogramas = db.relationship('Cronograma', backref='usuario', lazy=True, cascade="all, delete-orphan")
    
    def __init__(self, nombre, email, password, rol):
        self.nombre = nombre
        self.email = email
        self.rol = rol
        self.set_password(password)
    
    def set_password(self, password):
        """Hashear la contraseña"""
        password_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')
    
    def check_password(self, password):
        """Verificar la contraseña"""
        password_bytes = password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, self.password_hash.encode('utf-8'))
    
    def to_dict(self):
        """Convertir a diccionario para API"""
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'rol': self.rol,
            'fecha_registro': self.fecha_registro.isoformat() if self.fecha_registro else None
        }

class Cronograma(db.Model):
    __tablename__ = 'cronogramas'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    materia = db.Column(db.String(100), nullable=False)
    fecha_inicio = db.Column(db.DateTime, nullable=False)
    fecha_fin = db.Column(db.DateTime, nullable=False)
    color = db.Column(db.String(20), default='#3788d8')
    descripcion = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    def __init__(self, titulo, materia, fecha_inicio, fecha_fin, usuario_id, color='#3788d8', descripcion=None):
        print(f"\n=== CREACIÓN DE CRONOGRAMA ===")
        print(f"Datos recibidos:")
        print(f"- Título: {titulo}")
        print(f"- Materia: {materia}")
        print(f"- Usuario ID: {usuario_id} (tipo: {type(usuario_id)})")
        
        self.titulo = titulo
        self.materia = materia
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.usuario_id = int(usuario_id)  # Asegurar que sea entero
        self.color = color
        self.descripcion = descripcion
        
        print(f"Cronograma inicializado:")
        print(f"- ID Usuario asignado: {self.usuario_id} (tipo: {type(self.usuario_id)})")
    
    def to_dict(self):
        """Convertir a diccionario para API y formato FullCalendar"""
        return {
            'id': self.id,
            'title': self.titulo,
            'start': self.fecha_inicio.isoformat(),
            'end': self.fecha_fin.isoformat(),
            'color': self.color,
            'description': self.descripcion,
            'materia': self.materia,
            'usuario_id': self.usuario_id,
            'creado': self.fecha_creacion.isoformat() if self.fecha_creacion else None
        } 