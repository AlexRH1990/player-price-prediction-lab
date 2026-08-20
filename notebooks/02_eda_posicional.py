import io
import boto3
import pandas as pd
import numpy as np

BUCKET_NAME = "player-price-prediction-lab"

def get_s3_client():
    return boto3.client('s3')

def load_csv_from_s3(file_key, s3_client):
    print(f"-> Descargando {file_key}...")
    response = s3_client.get_object(Bucket=BUCKET_NAME, Key=file_key)
    return pd.read_csv(io.BytesIO(response['Body'].read()))

def preparar_datos_posicionales(df_players, df_appearances):
    print("\n-> Uniendo datos y calculando métricas avanzadas (Por 90 min)...")
    
    stats = df_appearances.groupby('player_id').agg({
        'goals': 'sum',
        'assists': 'sum',
        'minutes_played': 'sum'
    }).reset_index()
    
    df = pd.merge(df_players, stats, on='player_id', how='left')
    df = df.dropna(subset=['market_value_in_eur', 'position', 'minutes_played'])
    
    df = df[df['minutes_played'] >= 900].copy()
    
    df['G90'] = (df['goals'] / df['minutes_played']) * 90
    df['A90'] = (df['assists'] / df['minutes_played']) * 90
    
    return df

def analizar_percentiles_por_posicion(df):
    print("\n==================================================")
    print(" RADIOGRAFÍA DE RENDIMIENTO POR POSICIÓN (G90) ")
    print("==================================================")
    
    posiciones = df['position'].unique()
    
    for pos in posiciones:
        df_pos = df[df['position'] == pos]
        if len(df_pos) < 50:
            continue 
            
        p25 = np.percentile(df_pos['G90'], 25)
        p50 = np.percentile(df_pos['G90'], 50)
        p75 = np.percentile(df_pos['G90'], 75)
        
        print(f"Posición: {pos.upper()} (Muestra: {len(df_pos)} jugadores)")
        print(f"  - Decreciente (P25) : {p25:.3f} Goles/90m")
        print(f"  - Medio       (P50) : {p50:.3f} Goles/90m")
        print(f"  - Alto        (P75) : {p75:.3f} Goles/90m")
        print("-" * 40)

if __name__ == "__main__":
    s3 = get_s3_client()
    try:
        df_players = load_csv_from_s3('players.csv', s3)
        df_appearances = load_csv_from_s3('appearances.csv', s3)
        
        df_clean = preparar_datos_posicionales(df_players, df_appearances)
        analizar_percentiles_por_posicion(df_clean)
        
    except Exception as e:
        print(f"Error crítico: {e}")
