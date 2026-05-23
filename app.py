import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from src.financial_model import simular_emprestimo
from src.analysis_text import gerar_analise_textual
from src.export_handlers import gerar_excel_bytes, gerar_pdf_bytes, gerar_word_bytes

def formatar_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

st.set_page_config(page_title="Modelagem Financeira - CDI", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #1E3A8A;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 2rem;
        border-bottom: 1px solid #E5E7EB;
        padding-bottom: 0.5rem;
    }
    .metric-card {
        background-color: #F9FAFB;
        border-radius: 0.5rem;
        padding: 1rem;
        text-align: center;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    .metric-label {
        font-size: 0.9rem;
        font-weight: 500;
        color: #6B7280;
    }
    .metric-value {
        font-size: 1.6rem;
        font-weight: 600;
        color: #111827;
    }
    .section-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1F2937;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

if "resultado" not in st.session_state:
    st.session_state["resultado"] = None

with st.sidebar:
    st.markdown("### Parâmetros do Contrato")
    principal = st.number_input("Principal (R$)", value=3_000_000.00, step=100_000.00, format="%.2f")
    data_liberacao = st.date_input("Data de Liberação", datetime(2025, 10, 1))
    taxa_cdi = st.number_input("Taxa CDI (% a.d. útil)", value=0.05, step=0.01, format="%.4f") / 100
    taxa_fixa = st.number_input("Taxa Fixa (% a.d. útil)", value=0.02, step=0.01, format="%.4f") / 100
    parcela_mensal = st.number_input("Valor da Parcela (R$)", value=150_000.00, step=10_000.00, format="%.2f")
    num_meses = st.number_input("Meses de Simulação", min_value=1, max_value=120, value=12, step=1)
    st.markdown("---")
    executar = st.button("Executar Simulação", type="primary", use_container_width=True)

st.markdown('<div class="main-header">Gestão de Passivos e Projeção de Fluxo de Caixa</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Capitalização composta diária (Base 252) · Taxa CDI + spread</div>', unsafe_allow_html=True)

if executar:
    try:
        with st.spinner("Processando modelo financeiro..."):
            resultado = simular_emprestimo(
                principal=principal,
                data_liberacao=data_liberacao,
                taxa_cdi=taxa_cdi,
                taxa_fixa=taxa_fixa,
                parcela_mensal=parcela_mensal,
                num_meses=num_meses
            )
        st.session_state["resultado"] = resultado
        st.success("Simulação concluída com sucesso!")
    except Exception as e:
        st.error(f"Erro na simulação: {str(e)}")
        st.stop()

if st.session_state["resultado"] is None:
    st.info("### Sobre a ferramenta")
    st.markdown("""
    Esta aplicação simula o fluxo de caixa de uma linha de crédito para capital de giro, utilizando **capitalização composta diária apenas em dias úteis** (convenção Base 252), conforme práticas do mercado financeiro brasileiro.
    
    **O que cada parâmetro significa:**
    - **Principal**: valor inicial do empréstimo (R$ 3.000.000,00 padrão).
    - **Data de Liberação**: data em que o crédito é disponibilizado (01/10/2025 padrão).
    - **Taxa CDI**: taxa diária útil do CDI (0,05% ao dia útil padrão).
    - **Taxa Fixa**: spread adicional cobrado pelo banco (0,02% ao dia útil padrão).
    - **Valor da Parcela**: pagamento mensal fixo (R$ 150.000,00 padrão).
    - **Meses de Simulação**: período da análise (12 meses padrão, podendo ser ajustado até 120 meses).
    
    **Como a simulação funciona:**
    - A cada dia útil, o saldo devedor é atualizado pelo fator `(1+CDI) × (1+TaxaFixa)`.
    - No primeiro dia útil de cada mês, a parcela é paga: primeiro abate os juros acumulados do período; o restante amortiza o principal.
    - O relatório mensal apresenta juros acumulados, amortização e saldo remanescente.
    """)
    st.stop()

resultado = st.session_state["resultado"]
relatorio = resultado["relatorio"]

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Valor Total Pago</div><div class="metric-value">{formatar_br(resultado["valor_total_pago"])}</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Juros Totais Pagos</div><div class="metric-value">{formatar_br(resultado["juros_totais_pagos"])}</div></div>', unsafe_allow_html=True)
with col3:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Amortização Total</div><div class="metric-value">{formatar_br(resultado["amortizacao_total"])}</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown(f'<div class="metric-card"><div class="metric-label">Saldo Devedor Final</div><div class="metric-value">{formatar_br(resultado["saldo_devedor_final"])}</div></div>', unsafe_allow_html=True)

st.markdown('<div class="section-title">Relatório Mensal</div>', unsafe_allow_html=True)
df_relatorio = pd.DataFrame(relatorio)
df_relatorio["data_pagamento"] = df_relatorio["data_pagamento"].dt.strftime("%d/%m/%Y")
df_relatorio["juros_acumulados_periodo"] = df_relatorio["juros_acumulados_periodo"].apply(formatar_br)
df_relatorio["amortizacao_principal"] = df_relatorio["amortizacao_principal"].apply(formatar_br)
df_relatorio["saldo_devedor_rem"] = df_relatorio["saldo_devedor_rem"].apply(formatar_br)
st.dataframe(df_relatorio, width="stretch")

st.markdown('<div class="section-title">Evolução do Saldo Devedor</div>', unsafe_allow_html=True)
fig_linha = px.line(
    x=[r["data_pagamento"] for r in relatorio],
    y=[r["saldo_devedor_rem"] for r in relatorio],
    labels={"x": "Data de Pagamento", "y": "Saldo Devedor (R$)"},
    title="Evolução do Saldo Devedor",
    markers=True
)
fig_linha.update_layout(
    plot_bgcolor='white',
    hovermode="x unified",
    title_font_size=14,
    font=dict(color="#4B5563"),
    xaxis=dict(showgrid=True, gridcolor="#E5E7EB"),
    yaxis=dict(showgrid=True, gridcolor="#E5E7EB", tickformat=",.2f"),
    separators=',.'
)
fig_linha.update_traces(hovertemplate="Data: %{x}<br>Saldo: R$ %{y:,.2f}")
st.plotly_chart(fig_linha, width="stretch")

st.markdown('<div class="section-title">Composição das Parcelas</div>', unsafe_allow_html=True)
df_composicao = pd.DataFrame({
    "Mês": [f"{r['data_pagamento'].strftime('%b/%Y')}" for r in relatorio],
    "Juros": [r["juros_acumulados_periodo"] for r in relatorio],
    "Amortização": [r["amortizacao_principal"] for r in relatorio]
})
fig_barras = px.bar(
    df_composicao,
    x="Mês",
    y=["Juros", "Amortização"],
    title="Juros vs Amortização por Parcela",
    barmode="group",
    text_auto=".2s"
)
fig_barras.update_layout(
    plot_bgcolor='white',
    font=dict(color="#4B5563"),
    xaxis=dict(showgrid=False),
    yaxis=dict(showgrid=True, gridcolor="#E5E7EB", tickformat=",.2f"),
    legend=dict(title=None, orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    separators=',.'
)
fig_barras.update_traces(textfont_size=10, textangle=0, textposition="outside",
                         hovertemplate="%{y:,.2f}<extra></extra>")
st.plotly_chart(fig_barras, width="stretch")

st.markdown('<div class="section-title">Proporção de Juros por Parcela</div>', unsafe_allow_html=True)
df_proporcao = df_composicao.copy()
df_proporcao["Proporção Juros"] = df_proporcao["Juros"] / (df_proporcao["Juros"] + df_proporcao["Amortização"])
fig_area = px.area(
    df_proporcao,
    x="Mês",
    y="Proporção Juros",
    title="Evolução da Proporção de Juros na Parcela",
    markers=True
)
fig_area.update_layout(
    plot_bgcolor='white',
    yaxis=dict(tickformat=".1%", showgrid=True, gridcolor="#E5E7EB"),
    xaxis=dict(showgrid=False),
    font=dict(color="#4B5563")
)
st.plotly_chart(fig_area, width="stretch")

st.markdown('<div class="section-title">Acumulado de Juros e Amortização</div>', unsafe_allow_html=True)
juros_acum = [sum(r["juros_acumulados_periodo"] for r in relatorio[:i+1]) for i in range(len(relatorio))]
amort_acum = [sum(r["amortizacao_principal"] for r in relatorio[:i+1]) for i in range(len(relatorio))]
df_acum = pd.DataFrame({
    "Mês": [f"{r['data_pagamento'].strftime('%b/%Y')}" for r in relatorio],
    "Juros Acumulados": juros_acum,
    "Amortização Acumulada": amort_acum
})
fig_acum = px.line(
    df_acum,
    x="Mês",
    y=["Juros Acumulados", "Amortização Acumulada"],
    title="Evolução dos Valores Acumulados",
    markers=True
)
fig_acum.update_layout(
    plot_bgcolor='white',
    yaxis=dict(tickformat=",.2f", showgrid=True, gridcolor="#E5E7EB"),
    xaxis=dict(showgrid=False),
    font=dict(color="#4B5563"),
    separators=',.'
)
st.plotly_chart(fig_acum, width="stretch")

texto_analise = gerar_analise_textual(
    relatorio,
    resultado["juros_totais_pagos"],
    resultado["amortizacao_total"],
    parcela_mensal,
    num_meses
)
st.markdown('<div class="section-title">Análise Executiva</div>', unsafe_allow_html=True)
st.info(texto_analise)

st.markdown("---")
st.markdown('<div class="section-title">Exportar Resultados</div>', unsafe_allow_html=True)
col_btn1, col_btn2, col_btn3 = st.columns(3)

with col_btn1:
    excel_bytes = gerar_excel_bytes(relatorio, df_composicao, df_acum, df_proporcao)
    st.download_button(
        label="Exportar para Excel",
        data=excel_bytes,
        file_name="relatorio_financeiro.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )

with col_btn2:
    pdf_bytes = gerar_pdf_bytes(relatorio, texto_analise, fig_linha, fig_barras)
    st.download_button(
        label="Exportar para PDF",
        data=pdf_bytes,
        file_name="relatorio_financeiro.pdf",
        mime="application/pdf",
        use_container_width=True
    )

with col_btn3:
    word_bytes = gerar_word_bytes(relatorio, texto_analise, fig_linha, fig_barras)
    st.download_button(
        label="Exportar para Word",
        data=word_bytes,
        file_name="relatorio_financeiro.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True
    )