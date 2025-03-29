from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import Usuario, Cronograma
from database import db

# Crear blueprints
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
cronogramas_bp = Blueprint('cronogramas', __name__, url_prefix='/cronogramas')

# Importar funciones de autenticación
from auth import register_user, login_user, get_current_user, check_is_coordinator

# Rutas de autenticación
auth_bp.route('/register', methods=['POST'])(register_user)
auth_bp.route('/login', methods=['POST'])(login_user)
auth_bp.route('/me', methods=['GET'])(get_current_user)
auth_bp.route('/is-coordinator', methods=['GET'])(check_is_coordinator)

# Rutas de cronogramas
@cronogramas_bp.route('', methods=['GET'])
@jwt_required()

def get_cronogramas():
    """Obtener cronogramas (maestro: solo propios, coordinador: todos)"""
    usuario_id = get_jwt_identity()
    
    # Verificar si el usuario existe
    usuario = Usuario.query.get(usuario_id)
    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404
    
    # Filtrar cronogramas según el rol
    if usuario.rol == 'coordinador':
        # Los coordinadores pueden ver todos los cronogramas
        cronogramas = Cronograma.query.all()
    else:
        # Los maestros solo pueden ver sus propios cronogramas
        cronogramas = Cronograma.query.filter_by(usuario_id=usuario_id).all()
    
    # Convertir a formato JSON
    cronogramas_json = [cronograma.to_dict() for cronograma in cronogramas]
    
    return jsonify(cronogramas_json), 200

@cronogramas_bp.route('', methods=['POST'])
@jwt_required()
def create_cronograma():
    """Crear un nuevo cronograma"""
    print("--- Iniciando create_cronograma ---") # <-- AÑADIR
    usuario_id = get_jwt_identity()
    print(f"Usuario ID autenticado: {usuario_id}") # <-- AÑADIR
    data = request.get_json()
    print(f"Datos recibidos del frontend: {data}") # <-- AÑADIR

    # Verificar datos requeridos (sin cambios)
    required_fields = ['titulo', 'materia', 'fecha_inicio', 'fecha_fin']
    for field in required_fields:
        if field not in data:
            print(f"!!! Error: Falta el campo requerido '{field}'") # <-- AÑADIR
            return jsonify({"error": f"El campo '{field}' es requerido"}), 400

    try:
        print("Intentando convertir fechas...") # <-- AÑADIR
        # Convertir fechas de string a datetime
        fecha_inicio = datetime.fromisoformat(data['fecha_inicio'])
        fecha_fin = datetime.fromisoformat(data['fecha_fin'])
        print(f"Fechas convertidas: Inicio={fecha_inicio}, Fin={fecha_fin}") # <-- AÑADIR

        # Verificar que la fecha de fin sea posterior a la de inicio
        if fecha_fin <= fecha_inicio:
            print("!!! Error: Fecha de fin no es posterior a fecha de inicio") # <-- AÑADIR
            return jsonify({"error": "La fecha de fin debe ser posterior a la fecha de inicio"}), 400

        print("Creando objeto Cronograma...") # <-- AÑADIR
        # Crear nuevo cronograma
        nuevo_cronograma = Cronograma(
            titulo=data['titulo'],
            materia=data['materia'],
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            usuario_id=usuario_id,
            color=data.get('color', '#3788d8'),
            descripcion=data.get('descripcion')
        )
        # Imprimir representación del objeto antes de añadirlo
        print(f"Objeto Cronograma creado: {nuevo_cronograma.to_dict()}") # <-- AÑADIR

        print("Añadiendo a la sesión de DB (db.session.add)...") # <-- AÑADIR
        db.session.add(nuevo_cronograma)

        print("Intentando guardar en DB (db.session.commit)...") # <-- AÑADIR
        db.session.commit()
        print("--- COMMIT EXITOSO ---") # <-- AÑADIR

        return jsonify(nuevo_cronograma.to_dict()), 201

    except ValueError as e: # Captura errores de formato de fecha
        print(f"!!! ValueError al procesar fechas: {e}") # <-- AÑADIR
        return jsonify({"error": "Formato de fecha inválido. Use ISO format (YYYY-MM-DDTHH:MM)"}), 400 # Ajustado formato ejemplo
    except Exception as e: # Captura cualquier otro error
        print(f"!!! EXCEPCIÓN GENERAL durante la creación: {e}") # <-- AÑADIR
        print("!!! Realizando ROLLBACK de la sesión...") # <-- AÑADIR
        db.session.rollback()
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500 # Más info del error
        
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido. Use ISO format (YYYY-MM-DDTHH:MM:SS)"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@cronogramas_bp.route('/<int:cronograma_id>', methods=['PUT'])
@jwt_required()
def update_cronograma(cronograma_id):
    """Editar un cronograma (propietario o coordinador)."""
    identity = get_jwt_identity()
    data = request.get_json()

    try:
        usuario_id_actual = int(identity)
    except ValueError:
        return jsonify({"error": "Identidad de usuario inválida en el token"}), 400

    cronograma = Cronograma.query.get(cronograma_id)
    if not cronograma:
        return jsonify({"error": "Cronograma no encontrado"}), 404

    usuario_actual = Usuario.query.get(usuario_id_actual)
    if not usuario_actual:
        return jsonify({"error": "Usuario autenticado no encontrado en la base de datos"}), 404

    es_propietario = (usuario_id_actual == cronograma.usuario_id)
    es_coordinador = (usuario_actual.rol == 'coordinador')

    if not (es_propietario or es_coordinador):
        return jsonify({"error": "No tienes permiso para editar este cronograma"}), 403

    try:
        if 'titulo' in data:
            cronograma.titulo = data['titulo']
        if 'materia' in data:
            cronograma.materia = data['materia']
        if 'fecha_inicio' in data:
            cronograma.fecha_inicio = datetime.fromisoformat(data['fecha_inicio'])
        if 'fecha_fin' in data:
            cronograma.fecha_fin = datetime.fromisoformat(data['fecha_fin'])
        if 'color' in data:
            cronograma.color = data['color']
        if 'descripcion' in data:
            cronograma.descripcion = data['descripcion']

        if cronograma.fecha_fin <= cronograma.fecha_inicio:
            db.session.rollback()
            return jsonify({"error": "La fecha de fin debe ser posterior a la fecha de inicio"}), 400

        db.session.commit()
        return jsonify(cronograma.to_dict()), 200

    except ValueError:
        db.session.rollback()
        return jsonify({"error": "Formato de fecha inválido. Use ISO format (YYYY-MM-DDTHH:MM)"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno del servidor durante la actualización: {str(e)}"}), 500

@cronogramas_bp.route('/<int:cronograma_id>', methods=['DELETE'])
@jwt_required()
def delete_cronograma(cronograma_id):
    """Eliminar un cronograma (propietario o coordinador)."""
    identity = get_jwt_identity()

    try:
        usuario_id_actual = int(identity)
    except ValueError:
        return jsonify({"error": "Identidad de usuario inválida en el token"}), 400

    try:
        cronograma = Cronograma.query.get(cronograma_id)
        if not cronograma:
            return jsonify({"error": "Cronograma no encontrado"}), 404

        usuario_actual = Usuario.query.get(usuario_id_actual)
        if not usuario_actual:
            return jsonify({"error": "Usuario autenticado no encontrado en la base de datos"}), 404

        es_propietario = (usuario_id_actual == cronograma.usuario_id)
        es_coordinador = (usuario_actual.rol == 'coordinador')

        if not (es_propietario or es_coordinador):
            return jsonify({"error": "No tienes permiso para eliminar este cronograma"}), 403

        db.session.delete(cronograma)
        db.session.commit()
        return jsonify({"mensaje": "Cronograma eliminado exitosamente"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500