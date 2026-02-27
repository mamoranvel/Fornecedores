# app.py

import sys
import os
import streamlit as st

# ======================
# FIX: Asegurar que lib/ se pueda importar
# ======================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, os.path.join(BASE_DIR, "lib"))

for root, dirs, _ in os.walk(BASE_DIR):
    if "lib" in dirs:
        sys.path.insert(0, os.path.join(root, "lib"))
        break

from lib.mapping import MACRO_MAP, DESCRICOES
from lib.data_loader import load_csv
from lib.ui import company_row, render_company_panel


# ======================
# CONFIG + CSS ANA
# ======================
st.set_page_config(page_title="Fornecedores ANA", layout="wide")

st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)


# ======================
# SESSION STATE
# ======================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "macro" not in st.session_state:
    st.session_state.macro = None

if "profile_row_index" not in st.session_state:
    st.session_state.profile_row_index = None


# ======================
# LOAD DATA
# ======================
df = load_csv("data/fornecedores.csv")


# ======================
# LAYOUT
# ======================
left, right = st.columns([0.65, 0.35], gap="large")


# ======================
# PANEL DERECHO
# ======================
with right:

    if st.session_state.profile_row_index is not None:

        idx = st.session_state.profile_row_index

        if idx in df.index:
            render_company_panel(df.loc[idx])

    else:
        st.write("")


# ======================
# PANEL IZQUIERDO
# ======================
with left:

    # -------- HOME --------
    if st.session_state.page == "home":

        st.markdown("<h1 class='title-green'>Fornecedores ANA</h1>", unsafe_allow_html=True)
        st.markdown("### Selecione uma Macro-Especialidade ou explore os Generalistas")

        if st.button("⭐ Generalistas", type="primary"):
            st.session_state.page = "generalistas"
            st.session_state.profile_row_index = None
            st.rerun()

        st.markdown("---")
        st.subheader("Macro-Especialidades")

        cols = st.columns(3)

        for i, macro in enumerate(MACRO_MAP.keys()):

            with cols[i % 3]:

                if st.button(macro, key=f"macro_{i}"):

                    st.session_state.page = "macro"
                    st.session_state.macro = macro
                    st.session_state.profile_row_index = None
                    st.rerun()


    # -------- MACRO --------
    elif st.session_state.page == "macro":

        macro = st.session_state.macro

        if st.button("⬅ Voltar"):
            st.session_state.page = "home"
            st.session_state.profile_row_index = None
            st.rerun()

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
            st.session_state.profile_row_index = None
            st.rerun()


    # -------- GENERALISTAS --------
    elif st.session_state.page == "generalistas":

        if st.button("⬅ Voltar"):

            st.session_state.page = "home"
            st.session_state.profile_row_index = None
            st.rerun()

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

                st.session_state.profile_row_index = row.name
                st.rerun()

        st.markdown("---")

        if st.button("⬅ Voltar", key="back_general_bottom"):

            st.session_state.page = "home"
            st.session_state.profile_row_index = None
            st.rerun()
