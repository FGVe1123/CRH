import psycopg2 
import pandas as pd


def leer_datos_db():
    try:
        DATABASE_URL = "postgresql://victor_flores:victor.flores@db.rijyeympgerxlwvyemwe.supabase.co:5432/postgres"

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        query = "SELECT * FROM dataset_hipertension" #select de los datos en dataset
    
        cursor.execute("SELECT * FROM evaluaciones_hipertension")

        # 2. Recorrer el cursor directamente
        print("--- Resultados de la Tabla ---")
        for fila in cursor:
            # 'fila' es una tupla: (id, edad, riesgo)
            print(cursor)
            #print(f"ID: {fila[0]} | SEXO: {fila[1]} | Riesgo: {fila[8]}")
            print(fila)
            print(f" ID: {fila[0]} SEXO:{fila[1]} EDAD: {fila[2]} PESO: {fila[3]} ESTATURA: {fila[4]}  IMC: {fila[5]}   TENSION: {fila[6]}  PREDICCION: {fila[7]} SCORE: {fila[8]} FECHA: {fila[9]} DIASTOLICA: {fila[10]}")
            

        cursor.execute(query)
        columnas = [desc[0] for desc in cursor.description]
        datos = cursor.fetchall()
            ##leer datos
        df = pd.DataFrame(datos, columns=columnas)
        cursor.close
        return df
    except Exception as error:
        print(f"Error al leer datos: {error}")
    finally:
        if conn is not None:
            conn.close() # Siempre cerrar la conexión 

def insertar_datos(datos_formulario):
    try:
        DATABASE_URL = "postgresql://victor_flores:victor.flores@db.rijyeympgerxlwvyemwe.supabase.co:5432/postgres"

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        #Sentencia SQL
        insertar_sql = """INSERT INTO evaluaciones_hipertension (sexo, edad, peso, estatura_cm, imc, tension_arterial, resultado_modelo, tension_diastolica)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s)""" 

        #Ejecutar
        cursor.execute(insertar_sql, datos_formulario)

        #Confirmar cambios
        conn.commit()
        print("Registro insertado correctamente")

    except Exception as error:
        if conn:
            conn.rollback()
        print(f"error al insertar", {error})
