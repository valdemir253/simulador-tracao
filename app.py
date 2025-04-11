import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import time

st.set_page_config(page_title="Simulador de Ensaio de Tração", layout="wide")

st.title("Simulador de Ensaio de Tração de Materiais")
st.caption("Desenvolvido por Prof. Valdemir — IFSP Campus Guarulhos | www.mestre-federal.com")

# Dados dos materiais
MATERIAIS = {
    "Aço": {"E": 200e9, "limite_escoamento": 250e6, "ruptura": 400e6, "deform_max": 0.20, "n": 0.2, "K": 800e6, "escoamento_duracao": 0.01},
    "Alumínio": {"E": 70e9, "limite_escoamento": 150e6, "ruptura": 300e6, "deform_max": 0.12, "n": 0.15, "K": 500e6, "escoamento_duracao": 0.005},
    "Cobre": {"E": 110e9, "limite_escoamento": 210e6, "ruptura": 350e6, "deform_max": 0.35, "n": 0.25, "K": 650e6, "escoamento_duracao": 0.0},
}
cores = {"Aço": "blue", "Alumínio": "green", "Cobre": "red"}
Lo = 50  # mm

def curva_realista(material):
    props = MATERIAIS[material]
    E = props["E"]
    sigma_y = props["limite_escoamento"]
    deform_max = props["deform_max"]
    epsilon_elastico = sigma_y / E
    epsilon_plato = epsilon_elastico + props["escoamento_duracao"]
    n_fino = 150
    n_grosso = 50

    eps_fino = np.linspace(0, epsilon_plato, n_fino)
    eps_grosso = np.linspace(epsilon_plato, deform_max, n_grosso + 1)[1:]
    epsilon = np.concatenate((eps_fino, eps_grosso))
    sigma = np.zeros_like(epsilon)

    for i, e in enumerate(epsilon):
        if e <= epsilon_elastico:
            sigma[i] = E * e
        elif e <= epsilon_plato:
            fator = (e - epsilon_elastico) / (epsilon_plato - epsilon_elastico)
            sigma[i] = sigma_y + 0.05 * sigma_y * np.sin(np.pi * fator)
        else:
            e_plast = e - epsilon_plato
            sigma[i] = sigma_y + props["K"] * e_plast**props["n"]

    idx_pico = np.argmax(sigma)
    for i in range(idx_pico + 1, len(epsilon)):
        queda = (i - idx_pico) / (len(epsilon) - idx_pico)
        sigma[i] = sigma[idx_pico] * (1 - 0.5 * queda)

    delta_L = epsilon * Lo
    sigma_mpa = sigma / 1e6
    return epsilon, delta_L, sigma_mpa, epsilon_elastico * Lo, epsilon_plato * Lo, deform_max * Lo, max(sigma_mpa)

# Interface
material = st.selectbox("Selecione o material para o ensaio:", list(MATERIAIS.keys()))
if st.button("Iniciar Simulação"):
    epsilon, delta_L, tensao, deltaL_elastico, deltaL_plato, deltaL_ruptura, tensao_ruptura = curva_realista(material)
    cor = cores[material]

    grafico, ax1 = plt.subplots(figsize=(8, 5))
    ax1.plot(delta_L, tensao, color=cor)
    ax1.set_title(f"Ensaio de Tração - {material}")
    ax1.set_xlabel("Deformação Real ∆L (mm)\nwww.mestre-federal.com - Prof. Valdemir - IFSP - Campus Guarulhos")
    ax1.set_ylabel("Tensão (MPa)")
    ax1.set_xlim(0, deltaL_ruptura * 1.05)
    ax1.set_ylim(0, tensao_ruptura * 1.2)
    ax1.grid(True)
    ax1.minorticks_on()

    ax1.axvspan(0, deltaL_elastico, color='orange', alpha=0.2, label='Zona Elástica')
    if deltaL_plato > deltaL_elastico:
        ax1.axvspan(deltaL_elastico, deltaL_plato, color='yellow', alpha=0.2, label='Escoamento')
    ax1.axvline(x=deltaL_elastico, color='orange', linestyle='--')
    ax1.axvline(x=deltaL_plato, color='gold', linestyle='--')
    ax1.axvline(x=deltaL_ruptura, color='purple', linestyle='--')
    ax1.axhline(y=tensao_ruptura, color='red', linestyle='--')

    ax1.legend(loc='lower right')
    st.pyplot(grafico)
