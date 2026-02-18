# app.py

import sys
import os
import streamlit as st

# ======================================
# FIX para Streamlit Cloud: asegurar que /lib siempre está en sys.path
# ======================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Asegura que la carpeta del proyecto está en sys.path
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Asegura lib/ en sys.path
LIB_DIR = os.path.join(BASE_DIR, "lib")
if os.path.isdir(LIB_DIR) and LIB_DIR not in sys.path:
    sys.path.insert(0, LIB_DIR)

# Buscar lib/ en subcarpetas por si el contenedor lo monta diferente
for root, dirs, files in os.walk(BASE_DIR):
    if "lib" in dirs:
        full_lib_path = os.path.join(root, "lib")
        if full_lib_path not in sys.path:
            sys.path.insert(0, full_lib_path)
        break

# IMPORTS — ahora debe funcionar
try:
    from lib.mapping import MACRO_MAP, DESCRICOES
    from lib.data_loader import load_csv
    from lib.ui import company_row, show_company_sidebar
except Exception as e:
    st.error(f"⚠️ Erro ao importar módulos da pasta lib: {e}")
    st.stop()


# ======================================
# Helper de rerun seguro
# ======================================
def do_rerun():
    try:
        st.rerun()
    except:
        pass


# ======================================
# CONFIG + CSS ANA
# ======================================
st.set_page_config(page_title="Fornecedores ANA", layout="wide")

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.title-green {
    color: #7BC242 !important;
    font-weight: 900 !important;
    font-size: 3rem !important;
    margin-bottom: 0.5rem !important;
}

.badge-ana {
    background-color: #7BC242;
    color: white;
    padding: 3px 8px;
    border-radius: 6px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-left: 8px;
}

h2, h3, h4 {
    color: #003087 !important;
    font-weight: 600 !important;
}

section[data-testid="stSidebar"] {
    background-color: #F0F4F8 !important;
    padding-top: 1rem !important;
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
# CARGAR CSV (siempre desde data/)
# ======================================
df = load_csv(os.path.join("data", "fornecedores.csv"))


# ======================================
# HOME PAGE
# ======================================
if st.session_state.page == "home":

    st.markdown("<h1 class='title-green'>Fornecedores ANA</h1>", unsafe_allow_html=True)
    st.markdown("### Selecione uma Macro‑Especialidade ou explore os Generalistas")

    col_top = st.columns([1, 6])[0]
    if col_top.button("⭐ Generalistas", type="primary", key="go_generalistas"):
        st.session_state.page = "generalistas"
        do_rerun()

    st.markdown("---")
    st.subheader("Macro‑Especialidades")

    cols = st.columns(3)
    macros = list(MACRO_MAP.keys())

    for i, macro in enumerate(macros):
        with cols[i % 3]:
            if st.button(macro, key=f"macro_{i}"):
                st.session_state.page = "macro"
                st.session_state.macro = macro
                do_rerun()


# ======================================
# MACRO PAGE
# ======================================
elif st.session_state.page == "macro":

    macro = st.session_state.macro

    # Voltar arriba
    if st.columns([1,6])[0].button("⬅ Voltar", key="back_home_top"):
        st.session_state.page = "home"
        do_rerun()

    st.header(macro)
    show_ana = st.checkbox("Mostrar apenas Fornecedores ANA", key="filter_macro_ana")

    for spec in MACRO_MAP[macro]:

        subset = df[df[spec] == 1]
        if show_ana:
            subset = subset[subset["ANA"] == 1]
        if subset.empty:
            continue

        st.subheader(DESCRICOES.get(spec, spec))

        for _, row in subset.sort_values("Nome").iterrows():
            company_row(row, btn_key_suffix=f"{macro}_{spec}_{row.name}")

    st.markdown("---")
    if st.button("⬅ Voltar", key="back_home_bottom"):
        st.session_state.page = "home"
        do_rerun()


# ======================================
# GENERALISTAS PAGE
# ======================================
elif st.session_state.page == "generalistas":

    # Voltar arriba
    if st.columns([1, 6])[0].button("⬅ Voltar", key="back_gen_top"):
        st.session_state.page = "home"
        do_rerun()

    st.header("⭐ Fornecedores Generalistas (≥ 4 macros)")

    show_ana = st.checkbox("Mostrar apenas Fornecedores ANA", key="filter_gen_ana")

    subset = df[df["macro_count"] >= 4]
    if show_ana:
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
                active = [c for c in specs if row.get(c, 0) == 1]
                if active:
                    st.write(f"- **{m}:** " + " - ".join(active))

            if st.button("Ver perfil", key=f"profile_gen_{row.name}"):
                st.session_state["profile_row_index"] = row.name
                do_rerun()

    st.markdown("---")

    if st.button("⬅ Voltar", key="back_gen_bottom"):
        st.session_state.page = "home"
        do_rerun()


# ======================================
# SIDEBAR PERFIL (SE DEBE RENDERIZAR SIEMPRE AL FINAL)
# ======================================
if "profile_row_index" in st.session_state:
    idx = st.session_state["profile_row_index"]
    if idx in df.index:
        show_company_sidebar(df.loc[idx])
