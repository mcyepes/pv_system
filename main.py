from flask import Flask, request, render_template_string # Importar Flask para crear la aplicación web,  y request para manejar solicitudes HTTP y render_template_string para renderizar plantillas
import sqlite3
from pv_model import PVModel
app = Flask(__name__) # Crear una aplicación de Flask

# Función para conectarse a la base de datos SQLite
def get_db_connection():
    conn = sqlite3.connect('pv_system.db')
    conn.row_factory = sqlite3.Row # Para poder acceder a las columnas por nombre en lugar de índice
    return conn

# Ruta para la página de inicio
@app.route('/') # Decorador para indicar la ruta de la página
def index():
    """
    Página de inicio con un formulario para realizar búsquedas de Punto Maximo de Panel Fotovoltaico.
    """
    return render_template_string('''
                                    <style>
                                        body {
                                            font-family: 'Arial', sans-serif;
                                            background-color: #f7f7f7;
                                            text-align: center;
                                            margin: 50px;
                                        }
                                        h1 {
                                            color: #333;
                                        }
                                        form {
                                            display: flex;
                                            flex-direction: column;
                                            align-items: center;
                                            background-color: #fff;
                                            padding: 20px;
                                            border-radius: 10px;
                                            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                                        }
                                        label {
                                            margin-bottom: 5px;
                                            color: #333;
                                            font-weight: bold;
                                        }
                                        select, input {
                                            padding: 10px;
                                            margin: 5px 0 15px 0;
                                            width: 200px;
                                            border: 1px solid #ccc;
                                            border-radius: 5px;
                                            box-sizing: border-box;
                                        }
                                        button {
                                            padding: 10px;
                                            background-color: #4caf50;
                                            color: #fff;
                                            border: none;
                                            border-radius: 5px;
                                            cursor: pointer;
                                        }
                                    </style>

                                    <h1>Calculo del Punto Máximo Para Panel Fotovoltaico</h1>
                                    <p>Ingrese Irradiancia y Temperatura Deseada</p>
                                    <form action="/buscar" method="post">
                                        <label for="irradiancia">Irradiancia:</label>
                                        <select name="irradiancia" id="irradiancia">
                                            <option value="100">100</option>
                                            <option value="200">200</option>
                                            <option value="500">500</option>
                                            <option value="800">800</option>
                                            <option value="1_000">1000</option>
                                            <option value="1_100">1100</option>
                                        </select>
                                        <label for="temperatura">Temperatura:</label>
                                        <p>El rango aconsejado de temperatura es de 15-40 grados.</p>
                                        <input type="number" name="temperatura" id="temperatura" step="1" min="10" max="50" required>
                                        <button type="submit">Buscar</button>
                                    </form>
                                ''')

# Ruta para realizar la búsqueda
@app.route('/buscar', methods=['POST'])
def buscar():

    irradiancia = int(request.form['irradiancia'])
    temperatura = int(request.form['temperatura'])
    conn = get_db_connection()
    resultados = None
    
    try: 
        resultados = conn.execute('SELECT * FROM pv_system WHERE irradiancia = ? AND temperature = ?', (irradiancia, temperatura)).fetchone()
        conn.close()
        resultados_dict = {'Irradiancia': irradiancia,'Temperatura': temperatura,'Vmp': resultados[3], 'Imp': resultados[4], 'Pmax': resultados[5]}
    except:
        print('hereeeee')
        pv = PVModel(4,3)
        # Calcular el modelo PV
        resultados, Vmpp, Impp, P_max = pv.modelo_pv(G=irradiancia, T=temperatura)
        resultados_dict = {'Irradiancia': irradiancia,'Temperatura': temperatura,'Vmp': round(Vmpp,2), 'Imp': round(Impp,2), 'Pmax': round(P_max,2)}
        
        conn = sqlite3.connect("pv_system.db")
        c = conn.cursor()
        c.execute('INSERT INTO pv_system (irradiancia, temperature, vpm, ipm, pmax) VALUES (?, ?, ?, ?, ?)', (irradiancia,temperatura,Vmpp,Impp,P_max ))
        conn.commit() # Guardar los cambios en la base de datos
        conn.close() # Cerrar la conexión a la base de datos

    if resultados_dict:
        print(resultados_dict['Vmp'])
        return render_template_string('''
                                        <style>
                                            body {
                                                font-family: 'Arial', sans-serif;
                                                background-color: #f7f7f7;
                                                text-align: center;
                                                margin: 50px;
                                            }
                                            h1 {
                                                color: #333;
                                            }
                                            table {
                                                border-collapse: collapse;
                                                width: 50%;
                                                margin: 20px auto;
                                                background-color: #fff;
                                                border-radius: 10px;
                                                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                                            }
                                            th, td {
                                                border: 1px solid #dddddd;
                                                text-align: left;
                                                padding: 15px;
                                            }
                                            th {
                                                background-color: #f2f2f2;
                                            }
                                            a {
                                                display: inline-block;
                                                padding: 10px;
                                                margin-top: 20px;
                                                text-decoration: none;
                                                color: #fff;
                                                background-color: #4caf50;
                                                border-radius: 5px;
                                                transition: background-color 0.3s;
                                            }
                                            a:hover {
                                                background-color: #45a049;
                                            }
                                        </style>

                                        <h1>Resultado del Cálculo</h1>
                                        <table>
                                            <tr>
                                                <th>Parámetro</th>
                                                <th>Valor</th>
                                            </tr>
                                            <tr>
                                                <td>Irradiancia</td>
                                                <td>{{ resultados['Irradiancia'] }}</td>
                                            </tr>
                                            <tr>
                                                <td>Temperatura</td>
                                                <td>{{ resultados['Temperatura'] }}</td>
                                            </tr>
                                            <tr>
                                                <td>Vmpp</td>
                                                <td>{{ resultados['Vmp'] }}</td>
                                            </tr>
                                            <tr>
                                                <td>Impp</td>
                                                <td>{{ resultados['Imp'] }}</td>
                                            </tr>
                                            <tr>
                                                <td>P_max</td>
                                                <td>{{ resultados['Pmax'] }}</td>
                                            </tr>
                                        </table>
                                        <a href="/">Volver</a>
                                    ''', resultados=resultados_dict)
    
    else:
        return 'Los valores de temperatura o irradiancia no son validos. <a href="/">Volver</a>'

if __name__ == '__main__':
    app.run('0.0.0.0', port=5050)
