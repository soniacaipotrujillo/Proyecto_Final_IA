import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import joblib # Para guardar el modelo

print("Iniciando entrenamiento...")

# 1. Cargar el dataset
try:
    data = pd.read_csv('videojuegos_data.csv')
except FileNotFoundError:
    print("Error: No se encontró el archivo 'videojuegos_data.csv'.")
    print("Asegúrate de que el archivo exista en la misma carpeta.")
    exit()

# 2. Definir Características (X) y Objetivo (y)
features = ['presupuesto_marketing', 'score_metacritic', 'es_secuela']
target = 'jugadores_pico'

X = data[features]
y = data[target]

# 3. Usar todos los datos para entrenar (para este ejemplo simple)
X_train = X
y_train = y
print(f"Datos cargados de '{data.shape[0]}' juegos. Entrenando modelo...")

# 4. Crear y Entrenar el Modelo
model = LinearRegression()
model.fit(X_train, y_train)

# 5. ¡GUARDAR EL MODELO!
joblib.dump(model, 'game_predictor_model.pkl')

print("¡Entrenamiento completado y modelo guardado como 'game_predictor_model.pkl'!")