from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config

# Inicializar SQLAlchemy
db = SQLAlchemy()

def init_db(app):
    """Inicializar la base de datos con la aplicación Flask"""
    print("\n=== INICIALIZACIÓN DE BASE DE DATOS ===")
    
    # Cargar configuración
    app.config.from_object(Config)
    
    # Inicializar SQLAlchemy
    db.init_app(app)
    
    # Configurar Flask-Migrate
    migrate = Migrate(app, db)
    
    # Crear todas las tablas si no existen
    with app.app_context():
        try:
            print("Intentando crear tablas...")
            db.create_all()
            print("✅ Base de datos inicializada correctamente.")
        except Exception as e:
            print(f" Error al inicializar la base de datos: {str(e)}")
            raise e
    
    print("=== FIN DE INICIALIZACIÓN ===\n")
    return db
        
    return db 

