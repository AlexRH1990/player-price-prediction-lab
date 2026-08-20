import io
import boto3
import pandas as pd

BUCKET_NAME = "player-price-prediction-lab"

def get_s3_client():
    return boto3.client('s3')

def explorar_eventos_S3(s3_client):
    file_key = 'game_events.csv'
    print(f"\n[Dr. Hacker] -> Iniciando escaneo de {file_key}...")
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
        chunk = pd.read_csv(io.BytesIO(response['Body'].read()), nrows=50000)
        print("\n--- COLUMNAS DISPONIBLES ---")
        print(list(chunk.columns))
        print("\n--- TIPOS DE EVENTOS ENCONTRADOS ---")
        if 'type' in chunk.columns:
             print(chunk['type'].value_counts())
        print("\n--- VISTA PREVIA (3 filas) ---")
        print(chunk.head(3))
    except Exception as e:
        print(f"[Dr. Hacker] -> Error: {e}")

if __name__ == "__main__":
    s3 = get_s3_client()
    explorar_eventos_S3(s3)
