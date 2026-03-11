from itertools import count
from pathlib import Path
from datetime import date, timedelta, datetime
from streamlit_extras.bottom_container import bottom

import streamlit as st
import pandas as pd
import locale
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Portfólio Águas do Rio & Prolagos",
    page_icon="🗂️️",
    layout="wide"
)

#Indicando com é o padrão de numeros - Brasil
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_ALL, '')

#Funções


#Declaração de Variaveis para filtragem

STATUS_CONTRATO = ['Planejado','TR em Elaboração','Tomada de Preço','Equalização','Minuta de Contrato','Assinatura','Contratado','Demandas']
REGIONAL = ['Geral','Baixada 1','Baixada 2','Centro-Sul/Comunidades','Interior','Leste','Norte','Prolagos']
PRIORIDADE = ['0-Crítica','1-Muito Alta','2-Alta','3-Média','4-Baixa','5-Muito Baixa']
STATUS_PROJETO = ['Em Linha','Atrasado','Em Risco','Concluído','Cancelado','Paralisado','Não Iniciado','ATO']


#Carregando os Arquivos
pasta_datasets = Path(__file__).parent / 'datasets'
df_projetos = pd.read_csv(pasta_datasets / 'Relacao_Projetos.csv', sep=";", encoding="utf-8-sig",decimal=',', index_col=0)


df_projetos["Saldo_Contrato"] = df_projetos["Valor_Previsto"].fillna(0) + df_projetos["Aditivo"].fillna(0) - df_projetos["Medido"].fillna(0)
df_projetos.loc[df_projetos[["Valor_Previsto", "Aditivo", "Medido"]].isna().all(axis=1),"Saldo_Contrato"] = pd.NA


st.markdown('# Portfólio de Projetos Rio de Janeiro')
st.header("Relação de Projetos")

#filtrando colunas
colunas = list(df_projetos.columns)
colunas_exibicao= {
"Status_Contrato":"Status do Contrato",
"Gestor_Contratante":"Gestor Contratante",
"Gestor_Contratada":"Gestor Contratada",
"N_Contrato":"Número do Contrato",
"Empresa":"Empresa Contratada",
"Regional":"Regional",
"Sistema":"Sistema",
"Plan_Med_Mes":"Planejamento & Medição do Mês",
"Nome_Projeto":"Nome do Projeto",
"Escopo":"Descrição do Escopo",
"Prioridade":"Prioridade",
"Motivo_Prioridade":"Justificativa da Prioridade",
"Ano_Obra":"Ano da Obra",
"Progresso_Projeto":"Progresso",
"Status_Projeto":"Status do Projeto",
"Duracao":"Duração do Projeto",
"Inicio_Previsto":"Início Previsto",
"Termino_Previsto":"Término Previsto",
"Inicio_Real":"Início Real",
"Termino_Real":"Término Real",
"Valor_Previsto":"Valor Previsto em Contrato",
"Aditivo":"Valor Aditivado",
"Justificativa_Aditivo":"Justificativa do Aditivo",
"Medido":"Valor Medido",
"Saldo_Contrato":"Saldo do Contrato",
"Disp_Ano":"Valor no Ano",
"ETE":"Estação de Tratamento de Esgoto",
"EEE":"Estação Elevatória de Esgoto",
"INT_CT":"Interceptor/Coletor Tronco",
"RCE":"Rede Coletora de Esgoto",
"LRE":"Linha de Recalque de Esgoto",
"ETA":"Estação de Tratamento de Água",
"AAB":"Adutora de Água Bruta",
"AAT":"Adutora de Água Tratada",
"RDA":"Rede de Distribuição de Água",
"EAB":"Estação Elevatória de Água Bruta",
"EAT":"Estação de Elevtória de Água Tratada",
"BOOSTER":"Booster",
"RAB":"Reservatório de Água Bruta",
"RAT":"Reservatório de Água Tratada",
"CAP_SUP":"Captação Superficial",
"CAP_SUB":"Captação Subterrânea",
"CTS_GAP":"CTS Galeria Pluvial",
"CTS_CH":"CTS Corpo Hídrico",
"Data_Atualizacao":"Data de Atualização",
"Atualizado_Por":"Atualizado Por"
}
st.sidebar.markdown('Filtros')
selecao_colunas = st.sidebar.multiselect('Escolha as Colunas:',
                                         options=colunas,
                                         default=["Regional",
                                          "Sistema",
                                          "N_Contrato",
                                          "Empresa",
                                          "Gestor_Contratante",
                                          "Nome_Projeto",
                                          "Prioridade",
                                          "Ano_Obra",
                                          "Progresso_Projeto",
                                          "Status_Projeto",
                                          "Termino_Real",
                                          "Valor_Previsto",
                                          "Aditivo",
                                          "Medido",
                                          "Saldo_Contrato",
                                          "Disp_Ano"],
                                 format_func=lambda x: colunas_exibicao.get(x, x))


if selecao_colunas:
    df_exibicao = df_projetos[selecao_colunas].rename(columns=colunas_exibicao)
else:
    df_exibicao = df_projetos.rename(columns=colunas_exibicao)

#Passando para o Padrão BR


filtro_status_contrato = st.sidebar.multiselect('Escolha o Status do Contrato:',STATUS_CONTRATO)
filtro_regional = st.sidebar.multiselect('Escolha a Regional:',REGIONAL)
filtro_gestor_contratante = st.sidebar.multiselect(
    'Escolha o Gestor Contratante:',
    df_projetos["Gestor_Contratante"].replace("", pd.NA).fillna("Não Atribuído").astype(str).unique()
)
filtro_prioridade = st.sidebar.multiselect('Escolha a Prioridade:',PRIORIDADE)
filtro_status_projeto = st.sidebar.multiselect('Escolha Status do Projeto:',STATUS_PROJETO)
filtro_empresa = st.sidebar.multiselect(
    'Escolha a Empresa Contratada:',
    df_projetos["Empresa"].replace("", pd.NA).fillna("Não Atribuído").astype(str).unique()
)

# filtros
filtros = {
    "Status_Contrato": filtro_status_contrato,
    "Regional": filtro_regional,
    "Gestor_Contratante": filtro_gestor_contratante,
    "Prioridade": filtro_prioridade,
    "Status_Projeto": filtro_status_projeto,
    "Empresa": filtro_empresa,
}

# filtra na base original
df_filtrado = df_projetos.copy()

for coluna, valores in filtros.items():
    if valores:
        serie = df_filtrado[coluna].replace("", pd.NA).fillna("Não Atribuído").astype(str)
        df_filtrado = df_filtrado[serie.isin(valores)]

# só depois escolhe colunas e renomeia
if selecao_colunas:
    df_exibicao = df_filtrado[selecao_colunas].rename(columns=colunas_exibicao)
else:
    df_exibicao = df_filtrado.rename(columns=colunas_exibicao)

st.dataframe(df_exibicao,
             column_config={
                 "Progresso": st.column_config.ProgressColumn(
                    min_value=0, max_value=1
                 ),
                 "Valor Previsto em Contrato":st.column_config.NumberColumn(format="localized"),
                 "Valor Aditivado": st.column_config.NumberColumn(format="localized"),
                 "Valor Medido": st.column_config.NumberColumn(format="localized"),
                 "Saldo do Contrato": st.column_config.NumberColumn(format="localized"),
                 "Valor no Ano": st.column_config.NumberColumn(format="localized")


             }, hide_index=True)
st.divider()

previsto_total = df_exibicao["Valor Previsto em Contrato"].sum()
aditivo_total = df_exibicao["Valor Aditivado"].sum()
medido_total = df_exibicao["Valor Medido"].sum()
saldo_total = previsto_total + aditivo_total - medido_total
valor_ano_total = df_exibicao["Valor no Ano"].sum()
saldo_total_ano = valor_ano_total - saldo_total


previsto_total = locale.currency(previsto_total, grouping=True)
aditivo_total = locale.currency(aditivo_total, grouping=True)
medido_total = locale.currency(medido_total, grouping=True)
saldo_total = locale.currency(saldo_total, grouping=True)
valor_ano_total = locale.currency(valor_ano_total, grouping=True)
saldo_total_ano = locale.currency(saldo_total_ano, grouping=True)


st.header('Números Gerais')
col11, col12, col13 = st.columns(3)
col21, col22, col23 = st.columns(3)
col11.metric('Valor Total Previsto:',previsto_total)
col12.metric('Valor Total de Aditivos:',aditivo_total)
col13.metric('Valor Total de Medido:',medido_total)
col21.metric('Saldo Total dos Contratos:',saldo_total)
col22.metric('Valor disponível no ano:',valor_ano_total)
col23.metric('Saldo Total no Ano:',saldo_total_ano)

st.divider()
st.header('Quantitativos Gerais')

col51, col52, col53 = st.columns(3)

cont_regional = (df_exibicao.groupby("Regional").size().reset_index(name="Quantidade"))
fig_regional = px.bar(cont_regional,
                       x="Regional",
                       y="Quantidade",
                       color='Regional',
                       title="Quantidade por Regional",
                        )
col51.plotly_chart(fig_regional, use_container_width=True)

cont_progresso = (df_exibicao.groupby("Status do Projeto").size().reset_index(name="Quantidade"))
fig_progresso = px.bar(cont_progresso,
                       x="Status do Projeto",
                       y="Quantidade",
                       color='Status do Projeto',
                       title="Quantidade por Status de Projeto",
                       color_discrete_map={
                           'Em Linha':'green',
                           'Atrasado':'red',
                           'Em Risco':'orange',
                           'Concluído':'blue',
                           'Cancelado':'gray',
                           'Paralisado':'yellow',
                           'Não Iniciado':'pink',
                           'ATO':'violet'
                       })
col52.plotly_chart(fig_progresso, use_container_width=True)

cont_projetista = (df_exibicao.groupby("Empresa Contratada").size().reset_index(name="Quantidade"))
fig_projetista = px.bar(cont_projetista,
                       x="Empresa Contratada",
                       y="Quantidade",
                       color="Empresa Contratada",
                       title="Quantidade por Empresa Contratada",
                        )
col53.plotly_chart(fig_projetista, use_container_width=True)
st.divider()
st.header('Valores Gerais')

df_exibicao['Total Contrato'] = df_exibicao['Valor Previsto em Contrato'].fillna(0) + df_exibicao['Valor Aditivado'].fillna(0)

col61, col62, col63 = st.columns(3)

valor_regional = df_exibicao.groupby('Regional').agg({'Total Contrato':'sum'}).reset_index()
fig_regional_valor = px.bar(valor_regional,
                       x="Regional",
                       y='Total Contrato',
                       color='Regional',
                       title="Valor Total por Regional",
                        )
col61.plotly_chart(fig_regional_valor, use_container_width=True)

valor_empresa = df_exibicao.groupby('Empresa Contratada').agg({'Total Contrato':'sum'}).reset_index()
fig_empresa_valor = px.bar(valor_empresa,
                       x='Empresa Contratada',
                       y='Total Contrato',
                       color='Empresa Contratada',
                       title="Valor Total por Empresa Contratada",
                        )
col62.plotly_chart(fig_empresa_valor, use_container_width=True)

valor_gestor = df_exibicao.groupby('Gestor Contratante').agg({'Total Contrato':'sum'}).reset_index()
fig_gestor_valor = px.bar(valor_gestor,
                       x='Gestor Contratante',
                       y='Total Contrato',
                       color='Gestor Contratante',
                       title="Valor Total por Gestor",
                        )
col63.plotly_chart(fig_gestor_valor, use_container_width=True)


with bottom():
    st.write("Desenvolvido por Felipe Aranha")