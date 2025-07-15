import joblib
import pandas as pd

# Cargar modelo y vectorizador
modelo = joblib.load("modelo/modelo.pkl")
vectorizer = joblib.load("modelo/vectorizer.pkl")
df = pd.read_csv("modelo/errores.csv")

def clasificar_log(linea):
    vect = vectorizer.transform([linea])
    tipo = modelo.predict(vect)[0]
    row = df[df["error_tipo"] == tipo].iloc[0]
    return tipo, row["solucion"]
