# lib/ui.py

import streamlit as st

def clean(v):
    if v is None: return ""
    s = str(v).strip()
    if s.lower() in ("nan", "none", "null"):
        return ""
    return s

def fmt_money(v):
    s = clean(v)
    if not s: return ""
    try:
        x = float(s.replace(" ", "").replace(",", "."))
        return "{:,.2f}".format(x).replace(",", " ").replace(".", ",")
    except:
        return s

def specialties(row):
    from lib.mapping import DESCRICOES
    act = [c for c in DESCRICOES if row.get(c,0)==1]
    act.sort()
    return " - ".join(act)

# ==========================================================
# PANEL DERECHO (NO ES SIDEBAR, ES COLUMNA DERECHA → 0 doble click)
# ==========================================================
def render_company_panel(row):

    st.markdown(f"## {clean(row['Nome'])}")

    if int(row["ANA"]) == 1:
        st.markdown("<span class='badge-ana'>Fornecedor ANA</span>", unsafe_allow_html=True)
    else:
        st.write("Fornecedor ANA: Não")

    st.markdown("### Especialidades")
    st.write(specialties(row) or "-")

    st.markdown("---")

    st.write(f"**Serviços:** {clean(row.get('Serviços',''))}")

    st.write(f"**Website:** {clean(row.get('Website',''))}")
    st.write(f"**Email:** {clean(row.get('Email',''))}")
    st.write(f"**Telefone:** {clean(row.get('Telefone',''))}")

    st.markdown("---")

    st.write(f"**Capital Social:** {fmt_money(row.get('Capital Social',''))} €")
    st.write(f"**Volume de Negócios:** {fmt_money(row.get('Volume de Negócios (€)',''))} €")
    st.write(f"**Ano:** {clean(row.get('Ano Volume Negócios',''))}")
    st.write(f"**Pessoal Permanente:** {clean(row.get('Pessoal Permamente Total',''))}")

    if st.button("Fechar perfil"):
        st.session_state.profile_row_index = None
