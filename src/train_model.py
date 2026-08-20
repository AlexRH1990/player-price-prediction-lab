import io
import boto3
import pandas as pd
import numpy as np
import xgboost as xgb
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, r2_score
import warnings
warnings.filterwarnings('ignore')

BUCKET_NAME = "player-price-prediction-lab"

def get_s3_client():
    return boto3.client('s3')

def load_data(s3_client):
    resp_p = s3_client.get_object(Bucket=BUCKET_NAME, Key='players.csv')
    resp_a = s3_client.get_object(Bucket=BUCKET_NAME, Key='appearances.csv')
    df_players = pd.read_csv(io.BytesIO(resp_p['Body'].read()))
    df_appearances = pd.read_csv(io.BytesIO(resp_a['Body'].read()))
    return df_players, df_appearances

def preprocess_data(df_players, df_appearances):
    df_players['date_of_birth'] = pd.to_datetime(df_players['date_of_birth'], errors='coerce')
    df_players['age'] = (pd.to_datetime('2026-08-20') - df_players['date_of_birth']).dt.days / 365.25
    stats = df_appearances.groupby('player_id').agg({'goals': 'sum', 'assists': 'sum', 'minutes_played': 'sum'}).reset_index()
    df = pd.merge(df_players, stats, on='player_id', how='left')
    df[['goals', 'assists', 'minutes_played']] = df[['goals', 'assists', 'minutes_played']].fillna(0)
    df = df.dropna(subset=['market_value_in_eur', 'position', 'age'])
    df = df[df['minutes_played'] >= 500].copy()
    return df

def prepare_ml_matrix(df):
    df_ml = pd.get_dummies(df, columns=['position'])
    features = ['age', 'minutes_played', 'goals', 'assists'] + [col for col in df_ml.columns if col.startswith('position_')]
    X = df_ml[features]
    y = df_ml['market_value_in_eur']
    return X, y, features, df_ml

def train_models(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    lr = LinearRegression()
    lr.fit(X_train, y_train)
    xgb_model = xgb.XGBRegressor(n_estimators=200, learning_rate=0.1, max_depth=6, random_state=42)
    xgb_model.fit(X_train, y_train)
    return xgb_model

if __name__ == "__main__":
    print("-> Iniciando entrenamiento para serialización...")
    s3 = get_s3_client()
    df_p, df_a = load_data(s3)
    df_clean = preprocess_data(df_p, df_a)
    X, y, lista_features, df_con_dummies = prepare_ml_matrix(df_clean)
    modelo_ganador = train_models(X, y)
    
    print("\n--- GUARDANDO CEREBRO ARTIFICIAL ---")
    os.makedirs('models', exist_ok=True)
    joblib.dump(modelo_ganador, 'models/xgboost_valuation_model.joblib')
    joblib.dump(lista_features, 'models/model_features.joblib')
    print("-> ¡Éxito! Modelo guardado en 'models/xgboost_valuation_model.joblib'")
