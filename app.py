from flask import Flask, render_template, request
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import plotly.io as pio
from sklearn.metrics import confusion_matrix, f1_score
import db
from supabase import create_client

SUPABASE_URL = "https://rijyeympgerxlwvyemwe.supabase.co"
SUPABASE_KEY = "sb_publishable_4Ap1ApV_qdeWhRqWYlJJSQ_43uTu55X"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)



##TRABAJAR LA CONEXIÓN A LA BASE DE DATOS
##REVISAR TABLAS, POSIBLEMENTE SE DEBA MODIFICAR PARA EL ALMACENAMIENTO DE LOS DATOS
##REVISAR LO QUE SE PUSO EN DOCUMENTOS QUE SE VA A ENTREGAR, SE PUEDEN ALMACENAR DATOS "CONFIRMADOS" POR MEDICO O LOS DATOS QUE SE VAYAN GENERANDO CON EL MODELO PERMISO DEL USUARIO
app = Flask(__name__)


        
#CARGAR EL MODELO
#El archivo .pkl debe estar en la misma carpeta para funcionar 
try:
    modelo = joblib.load('modelo_hipertension8020.pkl')
    df_datos_prueba = pd.read_csv('datos_prueba.csv')
    print("Modelo y csv cargados exitosamente.")
    X_test = df_datos_prueba.drop('riesgo_hipertension', axis=1)
    y_test = df_datos_prueba['riesgo_hipertension']
    y_prediccion = modelo.predict(X_test)
    f1_global = round(f1_score(y_test, y_prediccion, average='weighted'), 2)
# Generar el gráfico de la matriz
    matriz = confusion_matrix(y_test, y_prediccion)

except:
    print("Error: No se encuantra uno o variso archivos.")

f1_var_global =0
matriz_var_global = " "



@app.route('/')
def index():
    # Renderiza el archivo index.html 
    return render_template('index.html')

@app.route('/formulario')
def formulario():
    return render_template('formulario.html')

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        try:
            # Capturar datos del formulario (importante utilizar los "name" utilizados en HTML)
            sexo = int(request.form.get('sexo'))
            edad = int(request.form.get('edad'))
            peso = int(request.form.get('peso'))
            estatura = int(request.form.get('estatura'))
            tension_arterial = int(request.form.get('tension_arterial'))
            estatura_m = estatura / 100
            imc = peso / (estatura_m ** 2)
            
            if not (12 <= edad <= 65):
                return render_template(index.html, error="La edad debe estar dentro del rango propuesto")
            if not (29 <= peso <= 200):
                return render_template(index.html, error="El peso debe estar dentro del rango propuesto")
            if not (137 <= estatura <= 192):
                return render_template(index.html, error="La estatura debe estar dentro del rango propuesto")
            if not (90 <= estatura <= 200):
                return render_template(index.html, error="La tension arterial debe estar dentro del rango propuesto")

            # Convertir a una lista para mandarlo al modelo
            datos_entrada = np.array([[sexo, edad, peso, estatura, tension_arterial, imc]])
            
            # Realizar la predicción, recibe los datos de entrada
            prediccion = modelo.predict(datos_entrada)[0]
            
            # Simplificar el resultado para interpretación
            resultado_texto = "Riesgo Alto" if prediccion == 1 else "Riesgo Bajo"
            
            # Enviar el resultado de vuelta a una página de resultados
            return render_template('resultado.html', prediccion=resultado_texto)
        except Exception as e:
            return f"Hubo un error en el procesamiento: {str(e)}"

## VISTA PARA USUARIO
##AGREGAR DATOS DE REFERENCIA PARA COMPARATIVAS, CANTIDAD DE REGISTROS EN EL DATASET
##VALDIAR QUE TIPOS DE GRAFICOS PRESENTAR
@app.route('/dashboard')
def dashboard():
    fig = px.imshow(matriz, 
                        text_auto=True, 
                        aspect="auto", 
                        labels=dict(x="Predicción", y="Real", color="Cantidad"),
                        x=['Normal', 'Riesgo'], 
                        y=['Normal', 'Riesgo'],
                        color_continuous_scale='Blues')
        
    fig.update_layout(title="Matriz de Confusión Actualizada")
    matriz_var_global = pio.to_html(fig, full_html=False,include_plotlyjs='cdn') 

    try:
        df = db.leer_datos_db()
        # Gráfico 1: Distribución de Riesgo (Pastel)
        fig1 = px.pie(df, names='riesgo_hipertension', title='Distribución de Pacientes',
        color_discrete_sequence=['#2ecc71', '#e74c3c'])
    
    # Gráfico 2: Relación tension arterial y masa corporal
        fig2 = px.scatter(df, x='masa_corporal', y='tension_arterial', color='riesgo_hipertension',
        title='Relacion masa corporal y tension arterial')

    # Convertir gráficos a HTML 
        graph1_html = pio.to_html(fig1, full_html=False)
        graph2_html = pio.to_html(fig2, full_html=False)  
        
        
        # ENVIAMOS LOS DATOS A LA PLANTILLA
        return render_template("dashboard.html", status="Conectado", graph1=graph1_html,graph2=graph2_html,f1_score=f1_global,matriz_html=matriz_var_global)
    except Exception as e:
        return render_template("dashboard.html", status="Error", error=str(e), f1_score=f1_global,matriz_html=matriz_var_global)




## ESTA VISTA SE DEBE PRESENTAR SOLO PARA EL "ADMINISTRADOR DEL PROYECTO"
##VISTA PARA ADMINISTRADOR PENDIENTE



if __name__ == '__main__':
    app.run(debug=True)
