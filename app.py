# app.py

import sys
import os
import streamlit as st

# ======================================
# FIX para localizar lib/
# ======================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "lib"))

for root, dirs, files in os.walk(BASE_DIR):
    if "lib" in dirs:
        lib_path = os.path.join(root, "lib")
        sys.path.insert(0, lib_path)
        break

from lib.mapping import MACRO_MAP, DESCRICOES
from lib.data_loader import load_csv
from lib.ui import company_row, show_company_sidebar

# ======================================
# CONFIG
# ======================================
st.set_page_config(page_title="Fornecedores ANA", layout="wide")

st.markdown("""
<style>
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.title-green { color: #7BC242 !important; font-weight: 900 !important; font-size: 3rem !important; }
.badge-ana { background-color: #7BC242; color: white; padding: 4px 8px; border-radius: 6px; font-size: 0.75rem; margin-left: 6px; }
section[data-testid="stSidebar"] { background-color: #F0F4F8 !important; }
</style>
""", unsafe_allow_html=True)

# ======================================
# STATE
# ======================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "macro" not in st.session_state:
    st.session_state.macro = None

df = load_csv("data/fornecedores.csv")

# ======================================
# 1) MOSTRAR SIDEBAR ANTES QUE NADA
# ======================================
if "profile_row_index" in st.session_state:
    idx = st.session_state["profile_row_index"]
    if idx in df.index:
        show_company_sidebar(df.loc[idx])

# ======================================
# 2) RENDER DE PÁGINAS
# ======================================

# -------- HOME --------
if st.session_state.page == "home":

    st.markdown("<h1 class='title-green'>Fornecedores ANA</h1>", unsafe_allow_html=True)
    st.markdown("### Selecione uma Macro‑Especialidade ou explore os Generalistas")

    if st.button("⭐ Generalistas", type="primary"):
        st.session_state.page = "generalistas"

    st.markdown("---")
    st.subheader("Macro‑Especialidades")

    cols = st.columns(3)

    for i, macro in enumerate(MACRO_MAP.keys()):
        with cols[i % 3]:
            if st.button(macro, key=f"macro_{i}"):
                st.session_state.page = "macro"
                st.session_state.macro = macro

# -------- MACRO --------
elif st.session_state.page == "macro":

    macro = st.session_state.macro

    if st.button("⬅ Voltar"):
        st.session_state.page = "home"

    st.header(macro)

    filter_ana = st.checkbox("Mostrar apenas Fornecedores ANA")

    for spec in MACRO_MAP[macro]:

        subset = df[df[spec] == 1]
        if filter_ana:
            subset = subset[subset["ANA"] == 1]
        if subset.empty:
            continue

        st.subheader(DESCRICOES[spec])

        for _, row in subset.sort_values("Nome").iterrows():
            company_row(row, btn_key_suffix=f"{macro}_{spec}")

    st.markdown("---")
    if st.button("⬅ Voltar", key="back_macro_bottom"):
        st.session_state.page = "home"

# -------- GENERALISTAS --------
elif st.session_state.page == "generalistas":

    if st.button("⬅ Voltar"):
        st.session_state.page = "home"

    st.header("⭐ Fornecedores Generalistas (≥ 4 macros)")

    filter_ana = st.checkbox("Mostrar apenas Fornecedores ANA")

    subset = df[df["macro_count"] >= 4]
    if filter_ana:
        subset = subset[subset["ANA"] == 1]

    subset = subset.sort_values("Nome")

    for _, row in subset.iterrows():

        st.subheader(row["Nome"])

        macros = [m for m, specs in MACRO_MAP.items() if row[specs].sum() > 0]
        st.write("**Macros:** " + ", ".join(macros))

        for m, specs in MACRO_MAP.items():
            active = [c for c in specs if row[c] == 1]
            if active:
                st.write(f"- **{m}:** " + " - ".join(active))

        if st.button("Ver perfil", key=f"profile_{row.name}"):
            st.session_state["profile_row_index"] = row.name

    st.markdown("---")
    if st.button("⬅ Voltar", key="back_gen_bottom"):
        st.session_state.page = "home"
