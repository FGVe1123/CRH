from flask import Flask, render_template, request
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.io as pio

app = Flask(__name__)

# 1. CARGAR EL MODELO
# Asegúrate de que el archivo .pkl esté en la misma carpeta que este script
try:
    modelo = joblib.load('modelo_hipertension.pkl')
    print("Modelo cargado exitosamente.")
except:
    print("Error: No se encontró el archivo 'modelo_hipertension.pkl'. Entrénalo primero.")

# 2. RUTA PRINCIPAL (HOME)
@app.route('/')
def index():
    # Renderiza tu archivo index.html (que debe heredar de base.html)
    return render_template('index.html')

# 3. RUTA PARA RECIBIR DATOS Y PREDECIR
@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # Capturar datos del formulario (usa los 'name' que pusiste en el HTML)
            sexo = float(request.form['sexo'])
            edad = float(request.form['edad'])
            peso = float(request.form['edad'])
            estatura = float(request.form['edad'])
            tension_arterial = float(request.form['tension_arterial'])
            estatura_m = estatura / 100
            imc = peso / (estatura_m ** 2)
            
            # Convertir a formato que el modelo entiende (lista de listas)
            datos_entrada = np.array([[sexo, edad, peso, estatura, tension_arterial, imc]])
            
            # Realizar la predicción
            prediccion = modelo.predict(datos_entrada)[0]
            
            # Convertir el resultado numérico en algo amigable
            resultado_texto = "Riesgo Alto" if prediccion == 1 else "Riesgo Bajo"
            
            # Enviar el resultado de vuelta a una página de resultados
            return render_template('resultado.html', prediccion=resultado_texto)
        
        except Exception as e:
            return f"Hubo un error en el procesamiento: {str(e)}"
        




@app.route('/dashboard')
def dashboard():
    # Leer los datos de entrenamiento
    df = pd.read_csv('datosLimpios.csv')
    
    # Gráfico 1: Distribución de Riesgo (Pastel)
    fig1 = px.pie(df, names='riesgo_hipertension', title='Distribución de Pacientes',
        color_discrete_sequence=['#2ecc71', '#e74c3c'])
    
    # Gráfico 2: Relación Presión Sistólica vs Edad
    fig2 = px.scatter(df, x='edad', y='tension_arterial', color='riesgo_hipertension',
        title='Presión Sistólica por Edad',
        labels={'sistolica': 'Presión Alta', 'edad': 'Edad (años)'})

    # Convertir gráficos a HTML (solo el div)
    graph1_html = pio.to_html(fig1, full_html=False)
    graph2_html = pio.to_html(fig2, full_html=False)

    return render_template('dashboard.html', graph1=graph1_html, graph2=graph2_html)

if __name__ == '__main__':
    app.run(debug=True)