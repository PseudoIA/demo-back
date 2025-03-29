from flask import jsonify, request
from flask_jwt_extended import (
    create_access_token,
    get_jwt_identity,
    jwt_required
)
from models import Usuario
from database import db

def register_user():
    """Registrar un nuevo usuario"""
    data = request.get_json()
    
    # Verificar datos requeridos
    required_fields = ['nombre', 'email', 'password', 'rol']
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"El campo '{field}' es requerido"}), 400
    
    # Verificar que el rol sea válido
    if data['rol'] not in ['maestro', 'coordinador']:
        return jsonify({"error": "El rol debe ser 'maestro' o 'coordinador'"}), 400
    
    # Verificar si el email ya existe
    existing_user = Usuario.query.filter_by(email=data['email']).first()
    if existing_user:
        return jsonify({"error": "El email ya está registrado"}), 409
    
    # Crear nuevo usuario
    try:
        nuevo_usuario = Usuario(
            nombre=data['nombre'],
            email=data['email'],
            password=data['password'],
            rol=data['rol']
        )
        
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        # Generar token de acceso
        access_token = create_access_token(identity=nuevo_usuario.id)
        
        return jsonify({
            "mensaje": "Usuario registrado exitosamente",
            "usuario": nuevo_usuario.to_dict(),
            "access_token": access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def login_user():
    """Iniciar sesión y obtener token JWT"""
    data = request.get_json()
    
    # Verificar datos requeridos
    if not data or 'email' not in data or 'password' not in data:
        return jsonify({"error": "Email y password son requeridos"}), 400
    
    # Buscar usuario por email
    usuario = Usuario.query.filter_by(email=data['email']).first()
    
    # Verificar si el usuario existe y la contraseña es correcta
    if not usuario or not usuario.check_password(data['password']):
        return jsonify({"error": "Credenciales inválidas"}), 401
    
    # Generar token de accesoidentity=str(usuario.id)
    access_token = create_access_token(identity=str(usuario.id))
    print(f"--- Login User: Token Generado={access_token}")
    return jsonify({
        "mensaje": "Inicio de sesión exitoso",
        "usuario": usuario.to_dict(),
        "access_token": access_token
    }), 200

@jwt_required()
def get_current_user():
    """Obtener información del usuario actual"""
    current_user_id = get_jwt_identity()
    
    usuario = Usuario.query.get(current_user_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    return jsonify(usuario.to_dict()), 200

@jwt_required()
def check_is_coordinator():
    """Verificar si el usuario actual es coordinador"""
    current_user_id = get_jwt_identity()
    
    usuario = Usuario.query.get(current_user_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    return jsonify({"is_coordinator": usuario.rol == 'coordinador'}), 200 