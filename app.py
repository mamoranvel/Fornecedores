# app.py

import sys
import os
import streamlit as st

# ======================================
# FIX para Streamlit Cloud
# ======================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "lib"))

# Buscar lib/ por si el contenedor lo ubicó en otro sitio
for root, dirs, files in os.walk(BASE_DIR):
    if "lib" in dirs:
        lib_path = os.path.join(root, "lib")
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)
        break

# Imports
try:
    from lib.mapping import MACRO_MAP, DESCRICOES
    from lib.data_loader import load_csv
    from lib.ui import company_row, show_company_sidebar
except Exception as e:
    st.error("❌ Erro ao importar módulos da pasta lib:")
    st.error(e)
    st.stop()

# ======================================
# Helper
# ======================================
def do_rerun():
    try:
        st.rerun()
    except:
        pass

# ======================================
# CSS ANA
# ======================================
st.set_page_config(page_title="Fornecedores ANA", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.title-green {
    color: #7BC242 !important;
    font-weight: 900 !important;
    font-size: 3rem !important;
}
.badge-ana {
    background-color: #7BC242;
    color: white;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    margin-left: 6px;
}
h2, h3, h4 { color: #003087 !important; font-weight: 600; }
section[data-testid="stSidebar"] {
    background-color: #F0F4F8 !important;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ======================================
# Session state
# ======================================
if "page" not in st.session_state:
    st.session_state.page = "home"
if "macro" not in st.session_state:
    st.session_state.macro = None

# ======================================
# Cargar datos
# ======================================
df = load_csv("data/fornecedores.csv")

# ======================================
# HOME
# ======================================
if st.session_state.page == "home":

    st.markdown("<h1 class='title-green'>Fornecedores ANA</h1>", unsafe_allow_html=True)
    st.markdown("### Selecione uma Macro‑Especialidade ou explore os Generalistas")

    if st.button("⭐ Generalistas", type="primary", key="btn_gen"):
        st.session_state.page = "generalistas"
        do_rerun()

    st.markdown("---")
    st.subheader("Macro‑Especialidades")

    cols = st.columns(3)
    for i, macro in enumerate(MACRO_MAP.keys()):
        with cols[i % 3]:
            if st.button(macro, key=f"macro_{i}"):
                st.session_state.macro = macro
                st.session_state.page = "macro"
                do_rerun()

# ======================================
# MACRO
# ======================================
elif st.session_state.page == "macro":

    macro = st.session_state.macro

    if st.button("⬅ Voltar", key="back_macro_top"):
        st.session_state.page = "home"
        do_rerun()

    st.header(macro)
    filter_ana = st.checkbox("Mostrar apenas Fornecedores ANA", key="filter_macro")

    for spec in MACRO_MAP[macro]:
        subset = df[df[spec] == 1]
        if filter_ana:
            subset = subset[subset["ANA"] == 1]
        if subset.empty:
            continue

        st.subheader(DESCRICOES[spec])

        subset = subset.sort_values("Nome")
        for _, row in subset.iterrows():
            company_row(row, btn_key_suffix=f"{macro}_{spec}")

    st.markdown("---")
    if st.button("⬅ Voltar", key="back_macro_bottom"):
        st.session_state.page = "home"
        do_rerun()

# ======================================
# GENERALISTAS
# ======================================
elif st.session_state.page == "generalistas":

    if st.button("⬅ Voltar", key="back_general_top"):
        st.session_state.page = "home"
        do_rerun()

    st.header("⭐ Fornecedores Generalistas (≥ 4 macros)")

    filter_ana = st.checkbox("Mostrar apenas Fornecedores ANA", key="filter_gen")

    subset = df[df["macro_count"] >= 4]
    if filter_ana:
        subset = subset[subset["ANA"] == 1]

    subset = subset.sort_values("Nome")

    if subset.empty:
        st.info("Nenhuma empresa encontrada.")
    else:
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
                do_rerun()

    st.markdown("---")
    if st.button("⬅ Voltar", key="back_general_bottom"):
        st.session_state.page = "home"
        do_rerun()

# ======================================
# SIDEBAR PERFIL (SE RENDERIZA SIEMPRE)
# ======================================
if "profile_row_index" in st.session_state:
    idx = st.session_state["profile_row_index"]
    if idx in df.index:
        show_company_sidebar(df.loc[idx])
