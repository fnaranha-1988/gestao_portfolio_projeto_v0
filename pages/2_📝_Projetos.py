from pathlib import Path
from datetime import date, timedelta, datetime
from streamlit_extras.bottom_container import bottom

import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.set_page_config(
    page_title="Projetos Águas do Rio & Prolagos",
    page_icon="📝",
    layout="wide"
)



#Funções
def moeda_br(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


#Declaração de Variaveis para filtragem

STATUS_CONTRATO = ['Planejado','TR em Elaboração','Tomada de Preço','Equalização','Minuta de Contrato','Assinatura','Contratado','Demandas']
REGIONAL = ['Geral','Baixada 1','Baixada 2','Centro-Sul/Comunidades','Interior','Leste','Norte','Prolagos']
PRIORIDADE = ['0-Crítica','1-Muito Alta','2-Alta','3-Média','4-Baixa','5-Muito Baixa']
STATUS_PROJETO = ['Em Linha','Atrasado','Em Risco','Concluído','Cancelado','Paralisado','Não Iniciado','ATO']
TIPO_TAREFA = ['Projeto','Gerencial','Orçamento','Serviço de Campo','Legal','Outro']
STATUS_TAREFA = ['Sem Status','Em Andamento','Atrasado','Em Risco','Concluído','Aprovado','Cancelado','Paralisado','Não Iniciado','Em Análise', 'Em Revisão']


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


    previsto_total = moeda_br(previsto_total)
    aditivo_total = moeda_br(aditivo_total)
    medido_total = moeda_br(medido_total)
    saldo_total = moeda_br(saldo_total)
    valor_ano_total = moeda_br(valor_ano_total)
    saldo_total_ano = moeda_br(saldo_total_ano)

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


#Controle de Tarefas
st.subheader('Lista de tarefas do projeto')
arquivo_tasks = pasta_datasets / 'df_projetos_tasks.csv'

# =========================
# 1) Criar ou ler o arquivo
# =========================
if not arquivo_tasks.exists():
    df_projetos_tasks = pd.DataFrame(columns=[
        'TaskID',
        'N_Contrato_Nome',
        'Tarefa',
        'Tipo da Tarefa',
        'Responsável',
        'Início',
        'Término / Prazo',
        'Status',
        'Comentarios / Atualizações',
        'Atualizado por',
        'Data de Atualização'
    ])
else:
    df_projetos_tasks = pd.read_csv(
        arquivo_tasks,
        sep=';',
        encoding='utf-8-sig',
        decimal=','
    )

# garante colunas
colunas_necessarias = [
    'TaskID',
    'N_Contrato_Nome',
    'Tarefa',
    'Tipo da Tarefa',
    'Responsável',
    'Início',
    'Término / Prazo',
    'Status',
    'Comentarios / Atualizações',
    'Atualizado por',
    'Data de Atualização'
]

for col in colunas_necessarias:
    if col not in df_projetos_tasks.columns:
        if col in ['Início', 'Término / Prazo', 'Data de Atualização']:
            df_projetos_tasks[col] = pd.NaT
        else:
            df_projetos_tasks[col] = ''

# converte datas
for col in ['Início', 'Término / Prazo', 'Data de Atualização']:
    df_projetos_tasks[col] = pd.to_datetime(df_projetos_tasks[col], errors='coerce')

# garante TaskID
if df_projetos_tasks['TaskID'].isna().any() or (df_projetos_tasks['TaskID'] == '').any():
    df_projetos_tasks['TaskID'] = range(1, len(df_projetos_tasks) + 1)

# =========================
# 2) Filtrar projeto
# =========================
projeto_tasks = df_projetos_tasks[df_projetos_tasks['N_Contrato_Nome'] == projeto].copy()


if not projeto_tasks.empty:
    st.dataframe(
        projeto_tasks.drop(columns=['N_Contrato_Nome']),
        hide_index=True,
        use_container_width=True
    )
else:
    st.info('Este projeto ainda não tem tarefas cadastradas.')

# =========================
# 3) Escolher tarefa
# =========================
opcoes_tarefa = ['Nova tarefa']

if not projeto_tasks.empty:
    projeto_tasks['rotulo_tarefa'] = (
        projeto_tasks['TaskID'].astype(str) + ' | ' +
        projeto_tasks['Tarefa'].fillna('').replace('', 'Sem título')
    )
    opcoes_tarefa += projeto_tasks['rotulo_tarefa'].tolist()

with st.expander("Atualização, Criação e Edição de Tarefas"):
    tarefa_escolhida = st.selectbox('Selecione uma tarefa para editar ou criar nova', opcoes_tarefa)

    # dados padrão
    task_id = None
    tarefa = ''
    tipo_tarefa = ''
    responsavel = ''
    inicio = None
    prazo = None
    status = ''
    comentarios = ''

    if tarefa_escolhida != 'Nova tarefa':
        task_id = int(tarefa_escolhida.split(' | ')[0])
        linha = df_projetos_tasks[df_projetos_tasks['TaskID'] == task_id].iloc[0]

        tarefa = linha['Tarefa'] if pd.notna(linha['Tarefa']) else ''
        tipo_tarefa = linha['Tipo da Tarefa'] if pd.notna(linha['Tipo da Tarefa']) else ''
        responsavel = linha['Responsável'] if pd.notna(linha['Responsável']) else ''
        inicio = linha['Início']
        prazo = linha['Término / Prazo']
        status = linha['Status'] if pd.notna(linha['Status']) else ''
        comentarios = linha['Comentarios / Atualizações'] if pd.notna(linha['Comentarios / Atualizações']) else ''

    # =========================
    # 4) Formulário individual
    # =========================
    with st.form('form_tarefa_individual'):
        tarefa = st.text_input('Tarefa', value=tarefa)
        tipo_tarefa = st.selectbox(
            'Tipo da Tarefa',
            options=TIPO_TAREFA,
            index=TIPO_TAREFA.index(tipo_tarefa) if tipo_tarefa in TIPO_TAREFA else 0
        )
        responsavel = st.text_input('Responsável', value=responsavel)
        inicio = st.date_input('Início', value=inicio if pd.notna(inicio) else None)
        prazo = st.date_input('Término / Prazo', value=prazo if pd.notna(prazo) else None)
        status = st.selectbox(
            'Status',
            options=STATUS_TAREFA,
            index=STATUS_TAREFA.index(status) if status in STATUS_TAREFA else 0
        )
        comentarios = st.text_area('Comentarios / Atualizações', value=comentarios, height=150)

        col1, col2 = st.columns(2)
        with col1:
            salvar_tarefa = st.form_submit_button('Salvar tarefa')
        with col2:
            excluir_tarefa = st.form_submit_button('Excluir tarefa')

    # =========================
    # 5) Salvar só a tarefa editada
    # =========================
    if salvar_tarefa:
        agora = datetime.now()

        if task_id is None:
            novo_id = 1 if df_projetos_tasks.empty else int(pd.to_numeric(df_projetos_tasks['TaskID'], errors='coerce').max()) + 1

            nova_linha = pd.DataFrame([{
                'TaskID': novo_id,
                'N_Contrato_Nome': projeto,
                'Tarefa': tarefa,
                'Tipo da Tarefa': tipo_tarefa,
                'Responsável': responsavel,
                'Início': inicio,
                'Término / Prazo': prazo,
                'Status': status,
                'Comentarios / Atualizações': comentarios,
                'Atualizado por': 'Felipe',
                'Data de Atualização': agora
            }])

            df_projetos_tasks = pd.concat([df_projetos_tasks, nova_linha], ignore_index=True)

        else:
            idx = df_projetos_tasks.index[df_projetos_tasks['TaskID'] == task_id][0]

            df_projetos_tasks.at[idx, 'N_Contrato_Nome'] = projeto
            df_projetos_tasks.at[idx, 'Tarefa'] = tarefa
            df_projetos_tasks.at[idx, 'Tipo da Tarefa'] = tipo_tarefa
            df_projetos_tasks.at[idx, 'Responsável'] = responsavel
            df_projetos_tasks.at[idx, 'Início'] = inicio
            df_projetos_tasks.at[idx, 'Término / Prazo'] = prazo
            df_projetos_tasks.at[idx, 'Status'] = status
            df_projetos_tasks.at[idx, 'Comentarios / Atualizações'] = comentarios
            df_projetos_tasks.at[idx, 'Atualizado por'] = 'Felipe'
            df_projetos_tasks.at[idx, 'Data de Atualização'] = agora

        df_projetos_tasks.to_csv(
            arquivo_tasks,
            sep=';',
            encoding='utf-8-sig',
            decimal=',',
            index=False
        )

        st.success('Tarefa salva com sucesso!')
        st.rerun()

# =========================
# 6) Excluir só a tarefa escolhida
# =========================
if excluir_tarefa:
    if task_id is None:
        st.warning('Selecione uma tarefa existente para excluir.')
    else:
        df_projetos_tasks = df_projetos_tasks[df_projetos_tasks['TaskID'] != task_id].copy()

        df_projetos_tasks.to_csv(
            arquivo_tasks,
            sep=';',
            encoding='utf-8-sig',
            decimal=',',
            index=False
        )

        st.success('Tarefa excluída com sucesso!')
        st.rerun()


st.dataframe(df_projetos_tasks)




st.divider()
st.caption("Desenvolvido por Felipe Aranha")
