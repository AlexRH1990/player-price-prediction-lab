from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="XGBoost Player Valuation API")

try:
    modelo = joblib.load('models/xgboost_valuation_model.joblib')
    features = joblib.load('models/model_features.joblib')
except Exception as e:
    print(f"Error cargando el modelo: {e}")

class DatosJugador(BaseModel):
    age: float
    minutes_played: int
    goals: int
    asistencias: int
    posicion: str

@app.post("/predict")
def predecir_valor(jugador: DatosJugador):
    datos_fila = {col: 0 for col in features}
    datos_fila['age'] = jugador.age
    datos_fila['minutes_played'] = jugador.minutes_played
    datos_fila['goals'] = jugador.goals
    datos_fila['assists'] = jugador.asistencias
    
    columna_posicion = f"position_{jugador.posicion}"
    if columna_posicion in features:
        datos_fila[columna_posicion] = 1
        
    df_input = pd.DataFrame([datos_fila], columns=features)
    precio_estimado = modelo.predict(df_input)[0]
    
    return {
        "status": "success",
        "datos_recibidos": jugador.dict(),
        "valor_justo_estimado_eur": float(precio_estimado)
    }
