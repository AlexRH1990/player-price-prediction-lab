import boto3
import pandas as pd
import io

s3 = boto3.client('s3')
NOMBRE_BUCKET = "player-price-prediction-lab"

try:
    resp = s3.get_object(Bucket=NOMBRE_BUCKET, Key='players.csv')
    df_players = pd.read_csv(io.BytesIO(resp['Body'].read()), nrows=5)
    print("\n=== REVISIÓN DE PLAYERS.CSV ===")
    print("Columnas que contienen 'value' o 'price':")
    print([col for col in df_players.columns if 'value' in col.lower() or 'price' in col.lower()])
except Exception as e:
    print(f"Error con players.csv: {e}")

try:
    resp2 = s3.get_object(Bucket=NOMBRE_BUCKET, Key='player_valuations.csv')
    df_val = pd.read_csv(io.BytesIO(resp2['Body'].read()), nrows=2)
    print("\n=== REVISIÓN DE PLAYER_VALUATIONS.CSV ===")
    print("Primeras 2 filas:")
    print(df_val)
except Exception as e:
    print(f"Error con player_valuations.csv: {e}")
