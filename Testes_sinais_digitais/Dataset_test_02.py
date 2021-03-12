# %%
from qampy import signals, impairments, equalisation, phaserec, helpers
from qampy.theory import ber_vs_es_over_n0_qam as ber_theory
from qampy.helpers import normalise_and_center as normcenter
from qampy.core.filter import rrcos_pulseshaping as lowpassFilter
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd

# %%
plt.rcParams['font.size'] = 18
plt.rcParams['figure.figsize'] = [16, 8]
plt.rcParams['lines.linewidth'] = 2

# %%
# Geração do sinal QAM

M = 64        # ordem da modulação
Fb = 40e9      # taxa de símbolos
SpS = 4         # amostras por símbolo
Fs = SpS*Fb    # taxa de amostragem
SNR = 40        # relação sinal ruído (dB)
rolloff = 0.01  # Rolloff do filtro formatador de pulso

# Gera sequência de símbolos QAM e a filtra com um filtro formatador de pulso rrc (root-raised cosine)
s = signals.ResampledQAM(M, 2**16, fb=Fb, fs=Fs, nmodes=2,
                         resamplekwargs={"beta": rolloff, "renormalise": True})

# Adiciona ruído gaussiano
s = impairments.simulate_transmission(s, snr=SNR)
sfilt = normcenter(lowpassFilter(s, Fs, 1/Fb, 0.001, taps=4001))

sfm = sfilt.copy()

t = np.arange(0, s[0].size)*1/s.fs

A = (np.max(np.abs(sfilt)))*np.exp(1j*np.deg2rad(45))
Δf = 2*np.pi*(sfilt.fb/2)*t
sfm = A + sfilt*np.exp(1j*Δf)

# %%
# valor absoluto do sinal -> entrada da rede
n_features = SpS*2
amplitudes_train = np.abs(sfm[0])
# fase do sinal     -> saída desejada
phases_train = np.angle(sfm[0, ::n_features])

# valor absoluto do sinal  -> entrada da rede
amplitudes_test = np.abs(sfm[1])
# fase do sinal      -> saída desejada
phases_test = np.angle(sfm[1, ::n_features])

# %%
size = 5000
X_train = amplitudes_train.reshape(-1, n_features)[:size]
X_test = amplitudes_test.reshape(-1, n_features)[:size]

# %%
y_train = phases_train.reshape(-1, 1)[:size]

y_test = phases_test.reshape(-1, 1)[:size]

# %%
dataset_train = np.concatenate((X_train, y_train), axis=1)
dataset_test = np.concatenate((X_test, y_test), axis=1)
# %%
pd.DataFrame(dataset_train).to_pickle('dataset_train_02.pkl')
pd.DataFrame(dataset_test).to_pickle('dataset_test_02.pkl')

#%%----------------------------------------------------------------