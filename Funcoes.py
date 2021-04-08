from qampy import signals, impairments, equalisation, phaserec, helpers
from qampy.theory import ber_vs_es_over_n0_qam as ber_theory
from qampy.helpers import normalise_and_center as normcenter
from qampy.core.filter import rrcos_pulseshaping as lowpassFilter
import numpy as np
from collections.abc import Sequence
import matplotlib.pyplot as plt


def sinal_qam_fase_min(M: int, Fb: int, SpS: int, SNR: float, rolloff=0.01):
    """Criação do sinal QAM em fase mínima.

    Args:
        M (int): Ordem da modulação.
        Fb (int): Taxa de símbolos.
        SpS (int): Amostras por símbolo.
        SNR (float): Relação sinal-ruído.
        rolloff (float, optional): Fator de roll off do filtro cosseno levantado. Defaults to 0.01.

    Returns:
        sfm (ResampledQAM: np.ndarray): Símbolos complexos do sinal QAM gerado.
    """
    Fs = SpS*Fb
    s = signals.ResampledQAM(M, 2**16, fb=Fb, fs=Fs, nmodes=1,
                             resamplekwargs={"beta": rolloff, "renormalise": True})
    s = impairments.simulate_transmission(s, snr=SNR)
    sfilt = normcenter(lowpassFilter(s, Fs, 1/Fb, 0.001, taps=4001))
    sfm = sfilt.copy()
    t = np.arange(0, s[0].size)*1/s.fs
    A = (np.max(np.abs(sfilt)))*np.exp(1j*np.deg2rad(45))
    Δf = 2*np.pi*(sfilt.fb/2)*t
    sfm = A + sfilt*np.exp(1j*Δf)

    return sfm , A

def reverter_sinal_fase_min(sinal, A):
    sinal_fase_min = sinal.copy()
    t = np.arange(0, sinal_fase_min[0].size)*1/sinal_fase_min.fs
    Δf = 2*np.pi*(sinal_fase_min.fb/2)*t
    sinal_revertido = (sinal_fase_min - A)/np.exp(1j*Δf)
    return sinal_revertido

def abs_and_phases(sfm):
    """ Divisão do sinal em fase mínima em componentes de amplitudes e fases.

    Args:
        sfm (ResampledQAM: np.ndarray): Sinal QAM reamostrado com frequência de amostragem maior 
        que a taxa de símbolos.

    Returns:
        data (dict): Dicionário com os arrays contendo as informações de
        amplitudes e fases do sinal.
    """
    amplitudes = np.abs(sfm.copy()[0])
    phases = np.angle(sfm.copy()[0])
    data = {'amplitudes': amplitudes, 'phases': phases}
    return data


def dataset_01(sfm, ordem: int):
    """O dataset criado pela função é o resultado de uma convolução simples ao longo
    do vetor das amplitudes, para a criação das features, e a fase correspondente à
    ultima amostra de amplitude em cada passo da convolução.

    Args:
        sfm (ResampledQAM: np.ndarray): Símbolos do sinal QAM a ser observado.
        ordem (int): Número de amostras de amplitudes a serem observadas para a análise
            de uma amostra de fase.

    Returns:
        data (dict[np.ndarray, np.ndarray]): Dicionário com os arrays contendo as informações de
            amplitudes e fases do sinal.
        X (np.ndarray): Matriz contendo as informações de amplitudes do sinal dispostas de tal 
            forma que qualquer algorítmo de regressão de ML pode utilizar como features.
        y (np.ndarray): Vetor coluna contendo as informações de fases do sinal dispostas de tal 
            forma que qualquer algorítmo de regressão de ML pode utilizar como features.
    """
    size = 60000
    data = abs_and_phases(sfm)
    amplitudes = data['amplitudes'].copy()
    phases = data['phases'].copy()
    X = np.zeros((size, ordem))
    for n in range(size):
        aux = amplitudes[n:ordem+n]
        X[n] = aux
    y = phases[ordem-1:size+ordem-1]
    data['amplitudes'] = data['amplitudes'][ordem-1:size+ordem-1]
    data['phases'] = data['phases'][ordem-1:size+ordem-1]

    return data, X, y.reshape(-1,)


def dataset_02(sfm, ordem: int):
    """O dataset criado pela função é o resultado de uma convolução simples ao longo
    do vetor das amplitudes, para a criação das features, e a fase correspondente à
    amostra de amplitude central da janela em cada passo da convolução.

    Args:
        sfm (ResampledQAM: np.ndarray): Símbolos do sinal QAM a ser observado.
        ordem (int): Número de amostras de amplitudes a serem observadas para a análise
            de uma amostra de fase.

    Returns:
        data (dict[np.ndarray, np.ndarray]): Dicionário com os arrays contendo as informações de
            amplitudes e fases do sinal.
        X (np.ndarray): Matriz contendo as informações de amplitudes do sinal dispostas de tal 
            forma que qualquer algorítmo de regressão de ML pode utilizar como features.
        y (np.ndarray): Vetor coluna contendo as informações de fases do sinal dispostas de tal 
            forma que qualquer algorítmo de regressão de ML pode utilizar como features.
    """
    size = 60000
    data = abs_and_phases(sfm)
    amplitudes = data['amplitudes'].copy()
    phases = data['phases'].copy()
    X = np.zeros((size, ordem))
    for n in range(size):
        aux = amplitudes[n:ordem+n]
        X[n] = aux
    y = phases[int(ordem/2):size+int(ordem/2)]
    data['amplitudes'] = data['amplitudes'][int(ordem/2):size+int(ordem/2)]
    data['phases'] = data['phases'][int(ordem/2):size+int(ordem/2)]

    return data, X, y


def dataset_03(sfm, ordem: int):
    """O dataset criado pela função é o resultado de uma convolução simples ao longo
    do vetor das amplitudes, para a criação das features, e a fase correspondente à
    primeira amostra de amplitude em cada passo da convolução.

    Args:
        sfm (ResampledQAM: np.ndarray): Símbolos do sinal QAM a ser observado.
        ordem (int): Número de amostras de amplitudes a serem observadas para a análise
            de uma amostra de fase.

    Returns:
        data (dict[np.ndarray, np.ndarray]): Dicionário com os arrays contendo as informações de
            amplitudes e fases do sinal.
        X (np.ndarray): Matriz contendo as informações de amplitudes do sinal dispostas de tal 
            forma que qualquer algorítmo de regressão de ML pode utilizar como features.
        y (np.ndarray): Vetor coluna contendo as informações de fases do sinal dispostas de tal 
            forma que qualquer algorítmo de regressão de ML pode utilizar como features.
    """
    size = 60000
    data = abs_and_phases(sfm)
    amplitudes = data['amplitudes'].copy()
    phases = data['phases'].copy()
    X = np.zeros((size, ordem))
    for n in range(size):
        aux = amplitudes[n:ordem+n]
        X[n] = aux
    y = phases[:size]
    data['amplitudes'] = data['amplitudes'][:size]
    data['phases'] = data['phases'][:size]

    return data, X, y.reshape(-1,)


def dataset_02_CNN(sfm, ordem: int):
    """O dataset criado pela função é o resultado de uma convolução simples ao longo
    do vetor das amplitudes, para a criação das features, e a fase correspondente à
    primeira amostra de amplitude em cada passo da convolução.

    Args:
        sfm (ResampledQAM: np.ndarray): Símbolos do sinal QAM a ser observado.
        ordem (int): Número de amostras de amplitudes a serem observadas para a análise
            de uma amostra de fase.

    Returns:
        data (dict[np.ndarray, np.ndarray]): Dicionário com os arrays contendo as informações de
            amplitudes e fases do sinal.
        X (np.ndarray): Matriz contendo as informações de amplitudes do sinal dispostas de tal 
            forma que qualquer algorítmo de regressão de ML pode utilizar como features.
        y (np.ndarray): Vetor coluna contendo as informações de fases do sinal dispostas de tal 
            forma que qualquer algorítmo de regressão de ML pode utilizar como features.
    """
    size = 60000
    data = abs_and_phases(sfm)
    amplitudes = data['amplitudes'].copy()
    phases = data['phases'].copy()
    X = np.zeros((size, ordem, ordem))
    for n in range(size):
        aux = amplitudes[n:int(ordem*ordem)+n].reshape(ordem,ordem)
        X[n] = aux
    X = X.reshape((size,ordem,ordem,1))
    y = phases[:size]
    data['amplitudes'] = data['amplitudes'][:size]
    data['phases'] = data['phases'][:size]

    return data, X, y.reshape(-1,)

def plot_constelação(sinal):
    plt.figure(figsize=(16, 8))
    plt.plot(sinal[0,:5000].real, sinal[0,:5000].imag, 'o')
    plt.xlabel('real')
    plt.ylabel('imaginário')
    plt.title('Constelação do sinal')
    plt.grid(True)
    plt.show()

def plot_espectro(sinal):
    plt.figure(figsize=(16, 8), dpi=100, facecolor='w', edgecolor='k')
    plt.magnitude_spectrum(sinal[0,:5000], Fs=sinal.fs, scale='dB', color='C1')
    plt.grid(True)
    plt.show()