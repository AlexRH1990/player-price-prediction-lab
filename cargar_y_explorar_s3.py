import os
import io
import boto3
import pandas as pd

def obtener_cliente_s3():
    return boto3.client('s3')

def leer_csv_desde_s3(cliente_s3, nombre_bucket, clave_archivo):
    try:
        print(f"Obteniendo {clave_archivo} desde S3...")
        respuesta = cliente_s3.get_object(Bucket=nombre_bucket, Key=clave_archivo)
        contenido = respuesta['Body'].read()
        df = pd.read_csv(io.BytesIO(contenido))
        print(f"-> Cargado exitosamente: {clave_archivo} | Forma: {df.shape}")
        return df
    except Exception as e:
        print(f"Error al leer {clave_archivo}: {e}")
        return None

if __name__ == "__main__":
    NOMBRE_BUCKET = "player-price-prediction-lab"
    s3 = obtener_cliente_s3()
    
    jugadores = leer_csv_desde_s3(s3, NOMBRE_BUCKET, 'players.csv')
    apariciones = leer_csv_desde_s3(s3, NOMBRE_BUCKET, 'appearances.csv')
    valuaciones = leer_csv_desde_s3(s3, NOMBRE_BUCKET, 'player_valuations.csv')
    
    if jugadores is not None:
        print("\n--- Vista Previa de Jugadores ---")
        print(jugadores[['player_id', 'name', 'position', 'market_value_in_eur']].head(3))
