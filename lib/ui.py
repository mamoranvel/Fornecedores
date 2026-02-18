# lib/ui.py

import streamlit as st

def do_rerun():
    try: st.rerun()
    except Exception: pass

def clean_text(v):
    if v is None: return ""
    s = str(v).strip()
    if s.lower() in ("nan", "none", "null"): return ""
    return s

def fmt_money_str(v):
    s = clean_text(v)
    if not s: return ""
    try:
        x = float(s.replace(" ", "").replace(",", "."))
        return "{:,.2f}".format(x).replace(",", " ").replace(".", ",")
    except:
        return s

def specialties_codes_line(row):
    from lib.mapping import DESCRICOES
    active = [c for c in DESCRICOES.keys() if row.get(c, 0) == 1]
    active.sort()
    return " - ".join(active)

def show_company_sidebar(row):

    st.sidebar.header(clean_text(row["Nome"]))

    website = clean_text(row.get("Website",""))
    email   = clean_text(row.get("Email",""))
    phone   = clean_text(row.get("Telefone",""))

    if website: st.sidebar.write(f"**Website:** {website}")
    if email:   st.sidebar.write(f"**Email:** {email}")
    if phone:   st.sidebar.write(f"**Telefone:** {phone}")

    if int(row["ANA"]) == 1:
        st.sidebar.markdown("<span class='badge-ana'>Fornecedor ANA</span>", unsafe_allow_html=True)
    else:
        st.sidebar.write("Fornecedor ANA: Não")

    st.sidebar.write("**Especialidades:**")
    st.sidebar.write(specialties_codes_line(row) or "-")

    st.sidebar.markdown("---")

    st.sidebar.write(f"**Serviços:** {clean_text(row.get('Serviços',''))}")

    st.sidebar.write(f"**Data de constituição:** {clean_text(row.get('Data de constituição',''))}")
    st.sidebar.write(f"**Capital Social:** {fmt_money_str(row.get('Capital Social',''))}€")
    st.sidebar.write(f"**Volume de Negócios:** {fmt_money_str(row.get('Volume de Negócios (€)',''))}€")
    st.sidebar.write(f"**Pessoal Permanente:** {clean_text(row.get('Pessoal Permamente Total',''))}")

    if st.sidebar.button("Fechar perfil"):
        if "profile_row_index" in st.session_state:
            st.session_state.pop("profile_row_index")
        do_rerun()

def company_row(row, key=""):

    serv = clean_text(row.get("Serviços",""))
    badge = " <span class='badge-ana'>ANA</span>" if row["ANA"] == 1 else ""

    col1, col2 = st.columns([5,1])
    col1.markdown(f"**{row['Nome']}** {badge}<br>{serv}", unsafe_allow_html=True)

    if col2.button("Ver perfil", key=f"profile_{row.name}_{key}"):
        st.session_state["profile_row_index"] = row.name
        do_rerun()
