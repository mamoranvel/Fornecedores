import streamlit as st

def clean(v):
    if v is None:
        return ""
    s = str(v).strip()
    if s.lower() in ("nan", "none", "null"):
        return ""
    return s

def fmt_money(v):
    s = clean(v)
    if not s:
        return ""
    try:
        x = float(s.replace(" ", "").replace(",", "."))
        return "{:,.2f}".format(x).replace(",", " ").replace(".", ",")
    except:
        return s

def specialties(row):
    from lib.mapping import DESCRICOES
    act = [c for c in DESCRICOES if int(row.get(c,0)) == 1]
    act.sort()
    return " - ".join(act)


def render_company_panel(row):

    st.markdown(f"## {clean(row.get('Nome',''))}")

    try:
        ana = int(row.get("ANA", 0))
    except:
        ana = 0

    if ana == 1:
        st.markdown("<span class='badge-ana'>Fornecedor ANA</span>", unsafe_allow_html=True)

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
        st.rerun()


def company_row(row, btn_key_suffix=""):

    serv = clean(row.get("Serviços",""))
    nome = clean(row.get("Nome",""))

    try:
        ana = int(row.get("ANA",0))
    except:
        ana = 0

    badge = " <span class='badge-ana'>ANA</span>" if ana == 1 else ""

    col1, col2 = st.columns([5,1])

    col1.markdown(f"**{nome}** {badge}<br>{serv}", unsafe_allow_html=True)

    if col2.button("Ver perfil", key=f"profile_{row.name}_{btn_key_suffix}"):

        st.session_state.profile_row_index = row.name
        st.rerun()
