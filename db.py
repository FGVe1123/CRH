import psycopg2
import pandas as pd

def leer_datos_db():
    try:
        DATABASE_URL = "postgresql://postgres:PASSWORD@db.rijyeympgerxlwvyemwe.supabase.co:5432/postgres"

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        query = "SELECT * FROM dataset_hipertension"
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