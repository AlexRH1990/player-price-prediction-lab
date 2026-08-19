import os
import io
import boto3
import pandas as pd

def obtener_cliente_s3():
    return boto3.client('s3')

def leer_csv_desde_s3(cliente_s3, nombre_bucket, clave_archivo):
    try:
        print(f"[Ingesta] Obteniendo {clave_archivo} desde S3...")
        respuesta = cliente_s3.get_object(Bucket=nombre_bucket, Key=clave_archivo)
        contenido = respuesta['Body'].read()
        df = pd.read_csv(io.BytesIO(contenido))
        print(f"[Ingesta] -> Cargado exitosamente: {clave_archivo} | Forma: {df.shape}")
        return df
    except Exception as e:
        print(f"Error al leer {clave_archivo}: {e}")
        return None

def preparar_y_limpiar_datos(df_jugadores, df_apariciones):
    print("\n[Transformación] - Iniciando limpieza y cruce de datos...")
    
    print("Calculando edades de los jugadores...")
    if 'date_of_birth' in df_jugadores.columns:
        df_jugadores['date_of_birth'] = pd.to_datetime(df_jugadores['date_of_birth'], errors='coerce')
        fecha_actual = pd.to_datetime('2026-08-19')
        df_jugadores['age'] = (fecha_actual - df_jugadores['date_of_birth']).dt.days / 365.25
    
    print("Agrupando estadísticas de apariciones (goles, asistencias, minutos)...")
    stats_jugador = df_apariciones.groupby('player_id').agg({
        'goals': 'sum',
        'assists': 'sum',
        'minutes_played': 'sum'
    }).reset_index()
    
    print("Uniendo datasets (Merge)...")
    df_completo = pd.merge(df_jugadores, stats_jugador, on='player_id', how='left')
    
    print("Limpiando valores nulos...")
    columnas_stats = ['goals', 'assists', 'minutes_played']
    for col in columnas_stats:
        if col in df_completo.columns:
            df_completo[col] = df_completo[col].fillna(0)
            
    if 'position' in df_completo.columns:
        df_completo['position'] = df_completo['position'].fillna('Unknown')
        
    if 'market_value_in_eur' in df_completo.columns:
        print(f"Filas antes de limpiar 'market_value_in_eur': {len(df_completo)}")
        df_completo = df_completo.dropna(subset=['market_value_in_eur'])
        print(f"Filas después de limpiar 'market_value_in_eur': {len(df_completo)}")
        
    print(f"[Transformación] - ¡Limpieza completada! Tamaño del dataset listo: {df_completo.shape}")
    return df_completo

def explorar_correlaciones(df, target_column='market_value_in_eur'):
    print(f"\n[Análisis EDA] - Analizando correlaciones con '{target_column}'...")
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    
    if target_column not in numeric_df.columns:
         print(f"Error: La columna objetivo '{target_column}' no existe en los datos numéricos.")
         return

    corr_matrix = numeric_df.corr()
    print(f"\n--- Top Variables con mayor impacto en el Precio ---")
    correlaciones = corr_matrix[target_column].sort_values(ascending=False)
    print(correlaciones[1:11]) 
    print("\n[Análisis EDA] - Análisis finalizado. ¡Datos listos para Machine Learning!")

if __name__ == "__main__":
    NOMBRE_BUCKET = "player-price-prediction-lab"
    s3 = obtener_cliente_s3()
    
    jugadores = leer_csv_desde_s3(s3, NOMBRE_BUCKET, 'players.csv')
    apariciones = leer_csv_desde_s3(s3, NOMBRE_BUCKET, 'appearances.csv')
    
    if jugadores is not None and apariciones is not None:
        dataset_final = preparar_y_limpiar_datos(jugadores, apariciones)
        explorar_correlaciones(dataset_final)
    else:
        print("Error al cargar datos.")
