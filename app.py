from flask import Flask
from flask_cors import CORS
from config import conectar_db
from config import SECRET_KEY
# Importar blueprints
from routes.token import token_bp
from routes.productos import productos_bp
from routes.usuarios import usuarios_bp
from routes.auth import auth_bp
from routes.bitacoras import bitacora_bp
from routes.carrito import carrito_bp
from routes.detalle_carrito import detalle_carrito_bp
from routes.ventas import ventas_bp
from routes.clientes import clientes_bp
from routes.inventario import inventario_bp
from routes.reportes import reportes_bp
from routes.roles import roles_bp
from routes.categorias import categorias_bp
from routes.catalogo import catalogo_bp
from dotenv import load_dotenv
load_dotenv()

from flask_sqlalchemy import SQLAlchemy
from routes.stripe_pago import stripe_pago_bp

import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clave_secreta_smart_cart'

# 🔁 Conexión a base de datos en Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})

#conexion = conectar_db()

# Registrar rutas
app.register_blueprint(token_bp)
app.register_blueprint(productos_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(bitacora_bp)
app.register_blueprint(carrito_bp)
app.register_blueprint(detalle_carrito_bp)
app.register_blueprint(ventas_bp)
app.register_blueprint(clientes_bp)
app.register_blueprint(inventario_bp)
app.register_blueprint(reportes_bp)
app.register_blueprint(roles_bp)
app.register_blueprint(categorias_bp)
app.register_blueprint(catalogo_bp)
app.register_blueprint(stripe_pago_bp)

@app.route('/')
def home():
    return '🚀 ¡Smart Cart backend funcionando!'

@app.route("/prueba-db")
def prueba_db():
    try:
        conexion = conectar_db()
        cursor = conexion.cursor()
        cursor.execute("SELECT 1;")
        return {"exito": True, "mensaje": "Base de datos conectada correctamente"}
    except Exception as e:
        return {"exito": False, "error": str(e)}


if __name__ == '__main__':
    app.run(debug=True)
