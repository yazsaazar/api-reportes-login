from flask import Flask, jsonify, request
from config import config
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from flask_jwt_extended import create_access_token, get_jwt_identity
from werkzeug.security import generate_password_hash
import pymysql
from flask_jwt_extended import create_access_token
from flask import request, jsonify

import bcrypt

from flask_jwt_extended import JWTManager


app = Flask(__name__)
CORS(app) 
conexion = MySQL(app)
app.config['JWT_SECRET_KEY'] = '123'  # Reemplaza 'your-secret-key' con tu propia clave secreta
jwt = JWTManager(app)
@cross_origin
@app.route('/reportes', methods=['GET'])
def listar_reportes():
    try:
        cursor=conexion.connection.cursor()
        sql="SELECT id, propietario, modelo, marca, color, placa FROM reportes"
        cursor.execute(sql)
        datos=cursor.fetchall()
        reportes=[]
        for fila in datos:
            reporte={'id':fila[0], 'propietario':fila[1], 'modelo':fila[2], 'marca':fila[3], 'color':fila[4], 'placa':fila[5]}
            reportes.append(reporte)
        return jsonify({'reportes':reportes, 'mensaje':"Reportes listados."})
    except Exception as ex:
        return jsonify({'mensaje':"Error"})
    
@app.route('/reportes/<idreportes>', methods=['GET'])
def leer_reporte(idreportes): 
 try: 
    cursor=conexion.connection.cursor()
    sql="SELECT idreportes, propietario, modelo, marca, color, placa FROM reportes WHERE idreportes = '{0}'".format(idreportes)
    cursor.execute(sql)
    datos=cursor.fetchone()
    if datos != None: 
        reporte = {'idreportes':datos[0], 'propietario':datos[1], 'modelo':datos[2], 'marca':datos[3], 'color':datos[4], 'placa':datos[5]}
        return jsonify({'reporte':reporte, 'mensaje':"Reporte encontrado."})
    else:
        return jsonify({'mensaje':"Reporte no encontrado."})
 except Exception as ex:
        return jsonify({'mensaje':"Error"})

@app.route('/reportes', methods=['POST'])
def registrar_reporte():
    # ...
    try:
        cursor = conexion.connection.cursor()
        sql = """INSERT INTO reportes (propietario, modelo, marca, color, placa) 
                VALUES ('{0}', '{1}', '{2}', '{3}', '{4}')""".format(request.json['propietario'], request.json['modelo'], request.json['marca'], request.json['color'], request.json['placa'])
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({'mensaje': "Reporte registrado."})  
    except Exception as ex:
        return jsonify({'mensaje': "Error" + str(ex)})
    

@app.route('/reportes/<id>', methods=['PUT'])
def actualizar_reporte(id):
    try:
        cursor = conexion.connection.cursor()

        # Comprobamos si el reporte existe en la base de datos
        sql_verificar = "SELECT id FROM reportes WHERE id = %s"
        cursor.execute(sql_verificar, (id,))
        datos = cursor.fetchone()

        if not datos:
            return jsonify({'mensaje': "Reporte no encontrado."}), 404

        # Actualizamos el reporte en la base de datos
        sql_actualizar = """UPDATE reportes 
                            SET propietario = %s, modelo = %s, marca = %s, color = %s, placa = %s
                            WHERE id = %s"""

        data = (request.json['propietario'], request.json['modelo'], request.json['marca'], request.json['color'], request.json['placa'], id)
        cursor.execute(sql_actualizar, data)
        conexion.connection.commit()

        return jsonify({'mensaje': "Reporte actualizado correctamente."}), 200

    except Exception as ex:
        return jsonify({'mensaje': "Error" + str(ex)}), 500



@app.route('/reportes/<id>', methods=['DELETE'])
def eliminar_reporte(id):
    try:
        cursor = conexion.connection.cursor()

        # Comprobamos si el reporte existe en la base de datos
        sql_verificar = "SELECT id FROM reportes WHERE id = %s"
        cursor.execute(sql_verificar, (id,))
        datos = cursor.fetchone()

        if not datos:
            return jsonify({'mensaje': "Reporte no encontrado."}), 404

        # Eliminamos el reporte de la base de datos
        sql_eliminar = "DELETE FROM reportes WHERE id = %s"
        cursor.execute(sql_eliminar, (id,))
        conexion.connection.commit()

        return jsonify({'mensaje': "Reporte eliminado correctamente."}), 200

    except Exception as ex:
        return jsonify({'mensaje': "Error" + str(ex)}), 500
    




@app.route('/register', methods=['POST'])
@cross_origin()
def registrar_usuario():
    try:
        email = request.json.get('email')
        raw_password = request.json.get('password')

        # Encriptar la contraseña antes de almacenarla en la base de datos
        hashed_password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt())

        cursor = conexion.connection.cursor()
        sql = "INSERT INTO users (email, password) VALUES (%s, %s)"
        cursor.execute(sql, (email, hashed_password.decode('utf-8')))
        conexion.connection.commit()

        return jsonify({'mensaje': 'Usuario registrado correctamente'}), 201
    except pymysql.Error as ex:
        return jsonify({'mensaje': 'Error en la base de datos'}), 500
    except Exception as ex:
        return jsonify({'mensaje': 'Error: ' + str(ex)}), 500
    

@app.route('/login_jwt', methods=['POST'])
@cross_origin()
def login_jwt():
    try:
        email = request.json.get('email')
        password = request.json.get('password')

        # Verificar las credenciales del usuario en la base de datos
        try:
            cursor = conexion.connection.cursor()
            sql = "SELECT id, password FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            user_data = cursor.fetchone()

            if user_data and bcrypt.checkpw(password.encode('utf-8'), user_data[1].encode('utf-8')):
                # Crear un token de acceso
                access_token = create_access_token(identity=user_data[0])
                return jsonify({'access_token': access_token}), 200
            else:
                raise Exception('Credenciales incorrectas')  # Lanzar excepción
        except pymysql.Error as db_error:
            return jsonify({'mensaje': 'Error de base de datos: ' + str(db_error)}), 500
    except Exception as ex:
        if str(ex) == 'Credenciales incorrectas':
            return jsonify({'mensaje': 'Credenciales incorrectas'}), 401
        else:
            return jsonify({'mensaje': 'Error: ' + str(ex)}), 500


def no_encontrada(error):
    return "<h1>Página no encontrada...</h1>"







if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, no_encontrada)
    app.run(debug=True)


