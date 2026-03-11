from pathlib import Path
from datetime import date, timedelta, datetime
from streamlit_extras.bottom_container import bottom

import streamlit as st
import pandas as pd
import locale
import plotly.express as px

st.set_page_config(
    page_title="Projetos Águas do Rio & Prolagos",
    page_icon="📝",
    layout="wide"
)

#Indicando com é o padrão de numeros - Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    pass

#Funções


#Declaração de Variaveis para filtragem

STATUS_CONTRATO = ['Planejado','TR em Elaboração','Tomada de Preço','Equalização','Minuta de Contrato','Assinatura','Contratado','Demandas']
REGIONAL = ['Geral','Baixada 1','Baixada 2','Centro-Sul/Comunidades','Interior','Leste','Norte','Prolagos']
PRIORIDADE = ['0-Crítica','1-Muito Alta','2-Alta','3-Média','4-Baixa','5-Muito Baixa']
STATUS_PROJETO = ['Em Linha','Atrasado','Em Risco','Concluído','Cancelado','Paralisado','Não Iniciado','ATO']


#Carregando os Arquivos
pasta_datasets = Path(__file__).parent.parent / 'datasets'
df_projetos = pd.read_csv(pasta_datasets / 'Relacao_Projetos.csv', sep=";", encoding="utf-8-sig",decimal=',', index_col=0)


df_projetos["Saldo_Contrato"] = df_projetos["Valor_Previsto"].fillna(0) + df_projetos["Aditivo"].fillna(0) - df_projetos["Medido"].fillna(0)
df_projetos.loc[df_projetos[["Valor_Previsto", "Aditivo", "Medido"]].isna().all(axis=1),"Saldo_Contrato"] = pd.NA


st.markdown('# Projetos Águas do Rio & Prolagos')

#Preparando os filtros da sidebar

df_projetos['N_Contrato_Nome'] = "["+df_projetos['N_Contrato'].fillna("S/N")+"] " + df_projetos['Nome_Projeto'].fillna("")

gestores_contratante = df_projetos["Gestor_Contratante"].dropna().unique()
gestor_contratante = st.sidebar.selectbox("Gestor",gestores_contratante)

df_projetos_gestor = df_projetos[(df_projetos["Gestor_Contratante"] == gestor_contratante)]
projetos = df_projetos_gestor['N_Contrato_Nome']
projeto = st.sidebar.selectbox("Gestor",projetos)

#Informações da Página
projeto_escolhido = df_projetos[df_projetos['N_Contrato_Nome'] == projeto].iloc[0]

st.header(projeto_escolhido['N_Contrato_Nome'])



with st.expander("Dados do Projeto"):
    col11, col12, col13, col14, col15 = st.columns(5)
    col11.markdown(f"**Regional:** {projeto_escolhido["Regional"].upper()}")
    sistema = projeto_escolhido["Sistema"]
    if pd.isna(sistema):
        sistema = "NÃO INFORMADO"
    col12.markdown(f"**Sistema:** {sistema.upper()}")
    empresa = projeto_escolhido["Empresa"]
    if pd.isna(empresa):
        empresa = "NÃO INFORMADO"
    col13.markdown(f"**Projetista:** {empresa.upper()}")
    gestor = projeto_escolhido["Gestor_Contratada"]
    if pd.isna(gestor):
        gestor = "NÃO INFORMADO"
    col14.markdown(f"**Gestor Responsável:** {gestor.upper()}")
    duracao = projeto_escolhido["Duracao"]
    if pd.isna(duracao):
        duracao = "NÃO INFORMADO"
    col15.markdown(f"**Prazo Contrato:** {duracao}")
    st.markdown('**Escopo do Projeto:**')
    st.text(projeto_escolhido["Escopo"])

with st.expander("Números Gerais"):
    previsto_total = 0 if pd.isna(projeto_escolhido["Valor_Previsto"]) else projeto_escolhido["Valor_Previsto"].sum()
    aditivo_total = 0 if pd.isna(projeto_escolhido["Aditivo"]) else projeto_escolhido["Aditivo"].sum()
    medido_total = 0 if pd.isna(projeto_escolhido["Medido"]) else projeto_escolhido["Medido"].sum()
    saldo_total = previsto_total + aditivo_total - medido_total
    valor_ano_total = 0 if pd.isna(projeto_escolhido["Disp_Ano"]) else projeto_escolhido["Disp_Ano"].sum()
    saldo_total_ano = valor_ano_total - saldo_total


    previsto_total = locale.currency(previsto_total, grouping=True)
    aditivo_total = locale.currency(aditivo_total, grouping=True)
    medido_total = locale.currency(medido_total, grouping=True)
    saldo_total = locale.currency(saldo_total, grouping=True)
    valor_ano_total = locale.currency(valor_ano_total, grouping=True)
    saldo_total_ano = locale.currency(saldo_total_ano, grouping=True)

    col21, col22, col23 = st.columns(3)
    col31, col32, col33 = st.columns(3)
    col21.metric('Valor Total Previsto:',previsto_total)
    col22.metric('Valor Total de Aditivos:',aditivo_total)
    col23.metric('Valor Total de Medido:',medido_total)
    col31.metric('Saldo Total do Contrato:',saldo_total)
    col32.metric('Valor disponível no ano:',valor_ano_total)
    col33.metric('Saldo Total no Ano:',saldo_total_ano)

status_projeto = projeto_escolhido["Status_Projeto"]

col41, col42 = st.columns([2,26])

if status_projeto.lower() == 'em linha':
    col41.badge(status_projeto,icon = '🚀',color='green')
elif status_projeto.lower() == 'atrasado':
    col41.badge(status_projeto, icon='🧨', color='red')
elif status_projeto.lower() == 'em risco':
    col41.badge(status_projeto, icon='⚠️', color='orange')
elif status_projeto.lower() == 'concluído':
    col41.badge(status_projeto, icon='🍾', color='blue')
elif status_projeto.lower() == 'cancelado':
    col41.badge(status_projeto, icon='❌', color='gray')
elif status_projeto.lower() == 'paralisado':
    col41.badge(status_projeto, icon='🤚', color='yellow')
elif status_projeto.lower() == 'não iniciado':
    col41.badge(status_projeto, icon='⌛', color='violet')
else:
    col41.badge(status_projeto, icon='🤌', color='orange')

progresso = 0 if pd.isna(projeto_escolhido["Progresso_Projeto"]) else projeto_escolhido["Progresso_Projeto"]
col42.progress(progresso,text=f"**{progresso*100:.0f}%**")

#st.dataframe(df_projetos_gestor)




with bottom():
    st.write("Desenvolvido por Felipe Aranha")
