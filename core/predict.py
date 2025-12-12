import joblib, librosa, os
import numpy as np

# Cargar modelo entrenado
model_path = os.path.join(os.path.dirname(__file__), "..", "models", "modelo_svm.pkl")
modelo = joblib.load(model_path)

def extract_features(file_path, n_mfcc=13):
    y, sr = librosa.load(file_path, sr=None)
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return np.mean(mfcc.T, axis=0)

def predict_audio(file_path):
    feat = extract_features(file_path).reshape(1, -1)
    pred = modelo.predict(feat)[0]
    return "Healthy" if pred == 0 else "COPD"

if __name__ == "__main__":
    # Ejemplo de prueba
    ruta = "ejemplo.wav"
    print("Predicción:", predict_audio(ruta))
