import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import joblib

df = pd.read_csv("modelo/errores.csv")
X = df["mensaje"]
y = df["error_tipo"]

vectorizer = TfidfVectorizer()
X_vect = vectorizer.fit_transform(X)

modelo = MultinomialNB()
modelo.fit(X_vect, y)

joblib.dump(modelo, "modelo/modelo.pkl")
joblib.dump(vectorizer, "modelo/vectorizer.pkl")
