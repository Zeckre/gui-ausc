import os, librosa, joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
import matplotlib.pyplot as plt
import seaborn as sns

# Se cargan las etiquetas desde la base de datos de sonidos resiratorios
labels = pd.read_csv(
    "/home/zeckre/Descargas/respiratory_sound_database/Respiratory_Sound_Database/patient_diagnosis.csv",
    header=None, names=["patient_id","label"]
)

labels_binary = labels[labels['label'].isin(['Healthy','COPD'])]
label_dict = dict(zip(labels_binary['patient_id'], labels_binary['label']))

# Se extrae MFCC
def extract_features(file_path, n_mfcc=13):
    try:
        y, sr = librosa.load(file_path, sr=None)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
        return np.mean(mfcc.T, axis=0)
    except Exception as e:
        print(f"Error procesando {file_path}: {e}")
        return None

# Dataset, tomado de la base de datos de sonidos resiratorios
X, y = [], []
audio_folder = "/home/zeckre/Descargas/respiratory_sound_database/Respiratory_Sound_Database/audio_and_txt_files/"

for filename in os.listdir(audio_folder):
    if filename.endswith(".wav"):
        pid_str = filename.split("_")[0]
        try:
            pid = int(pid_str)
        except ValueError:
            continue

        if pid in label_dict:
            label = label_dict[pid]
            wav_path = os.path.join(audio_folder, filename)
            feat = extract_features(wav_path)
            if feat is not None:
                X.append(feat)
                y.append(0 if label=="Healthy" else 1)

X = np.vstack(X)
y = np.array(y)

print("Dataset original:", X.shape, "Healthy:", sum(y==0), "COPD:", sum(y==1))

# Balanceo de los datos con menor cantidad de muestras
healthy_idx = np.where(y==0)[0]
copd_count = sum(y==1)
healthy_count = len(healthy_idx)

factor = copd_count // healthy_count
print("Duplicando Healthy por factor:", factor)

X_balanced = np.vstack([X] + [X[healthy_idx]]*factor)
y_balanced = np.concatenate([y] + [y[healthy_idx]]*factor)

print("Dataset balanceado:", X_balanced.shape)

# Datos para Train y Test
X_train, X_test, y_train, y_test = train_test_split(
    X_balanced, y_balanced, test_size=0.2, random_state=42, stratify=y_balanced
)

# Pipeline (Scaler + SVM)
# Normaliza -> Entrena el modelo
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(kernel='rbf', C=1, gamma='scale'))
])
pipeline.fit(X_train, y_train)

# Matriz de confusion (Evaluación del modelo)
y_pred = pipeline.predict(X_test)
print(classification_report(y_test, y_pred, target_names=['Healthy','COPD']))

cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(5,4))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=['Healthy','COPD'],
            yticklabels=['Healthy','COPD'])
plt.xlabel("Predicted")
plt.ylabel("True")
plt.title("Matriz de confusión SVM balanceado")
plt.show()

# Guardar el modelo entrenado
joblib.dump(pipeline, "./models/modelo_svm.pkl")
print("Modelo guardado como modelo_svm.pkl")
