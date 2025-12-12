import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
from scipy.io import wavfile

sample_rate, data = wavfile.read("/home/zeckre/Descargas/respiratory_sound_database/Respiratory_Sound_Database/audio_and_txt_files/132_2b2_Lr_mc_LittC2SE.wav")

print("FS: ", sample_rate)

df = pd.DataFrame(data)
df.to_csv("salida.csv", index=False)
print("Archivo CSV guardado")

t = np.linspace(0, len(data)/sample_rate, num=len(data))
plt.plot(t, data)
plt.title("EPOC/COPD")
plt.xlabel("T(s)")
plt.ylabel("Amplitud")
plt.tight_layout()
plt.show()
