import streamlit as st
import pandas as pd
import datetime
import os
import base64
from io import BytesIO
import uuid

st.set_page_config(
    page_title="Exxata Lançamento de Artia",
    page_icon="🐺",
    layout='centered',
    initial_sidebar_state='expanded'
)    

class RegistroAtividades:
    def __init__(self, user_id):
        self.user_id = user_id
        self.arquivo_dados = f'registros_atividades_{self.user_id}.xlsx'
        self.iniciar_arquivo_excel()
        self.iniciar_sessao()

    def iniciar_arquivo_excel(self):
        if not os.path.exists(self.arquivo_dados):
            df = pd.DataFrame(columns=['ID', 'Nome_Usuário', 'Numero_Projeto', 'Atividade', 'Data', 'Início', 'Fim', 'Duração'])
            df.to_excel(self.arquivo_dados, index=False)

    def iniciar_sessao(self):
        if 'registro' not in st.session_state:
            st.session_state.registro = {
                'nome_usuario': '',
                'numero_projeto': '',
                'df': pd.DataFrame(columns=['ID', 'Nome_Usuário', 'Numero_Projeto', 'Atividade', 'Data', 'Início', 'Fim', 'Duração'])
            }

    def obter_informacoes_iniciais(self):
        st.session_state.registro['nome_usuario'] = st.text_input("Digite seu nome: ").upper()
        st.session_state.registro['numero_projeto'] = st.text_input("Digite o número do projeto: ").upper()

    def registrar_atividades(self):
        self.obter_informacoes_iniciais()

        # Registrar atividade para o usuário atual
        self.registrar_atividade()

        # Adiciona botão para download do Excel preenchido
        if st.button("Baixar Relatório Excel"):
            self.gerar_relatorio_excel()

        # Adiciona botão para reiniciar os dados
        if st.button("Zerar Dados"):
            self.zerar_dados()

    def registrar_atividade(self):
        st.write(f"Atividade para o usuário {st.session_state.registro['nome_usuario']}:")

        # Alterado de solicitar função para informar atividade em andamento
        atividade_em_andamento = st.text_input("Informe a atividade em andamento: ").upper()

        iniciar = st.button("Iniciar atividade")
        encerrar = st.button("Encerrar atividade")

        if iniciar:
            self.iniciar_atividade(atividade_em_andamento)

        if encerrar:
            self.encerrar_atividade()

    def iniciar_atividade(self, atividade_em_andamento):
        novo_registro = {
            'ID': 1,  # Apenas um usuário
            'Nome_Usuário': st.session_state.registro['nome_usuario'],
            'Numero_Projeto': st.session_state.registro['numero_projeto'],
            'Atividade': atividade_em_andamento,
            'Data': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%Y-%m-%d"),
            'Início': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%H:%M:%S"),
            'Fim': datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%H:%M:%S"),
            'Duração': ''
        }

        df = st.session_state.registro['df']
        df = pd.concat([df, pd.DataFrame([novo_registro])], ignore_index=True)
        st.session_state.registro['df'] = df

        st.success(f"Atividade '{atividade_em_andamento}' iniciada para o usuário {st.session_state.registro['nome_usuario']}")

    def encerrar_atividade(self):
        st.write("Encerrando atividade...")

        df = st.session_state.registro['df']

        atividade_em_andamento = df.iloc[-1]['Atividade']

        if atividade_em_andamento:
            inicio = df.iloc[-1]['Início']
            if pd.isnull(inicio):
                st.error("Atividade ainda não iniciada.")
                return

            df.loc[df.index == len(df) - 1, 'Fim'] = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-3))).strftime("%H:%M:%S")
            fim = datetime.datetime.now()
            duracao = fim - pd.to_datetime(inicio)
            df.loc[df.index == len(df) - 1, 'Duração'] = duracao
            st.session_state.registro['df'] = df
            st.success(f"Atividade '{atividade_em_andamento}' encerrada às {fim.strftime('%H:%M:%S')}")

        else:
            st.error("Atividade inválida.")

    def gerar_relatorio_excel(self):
        st.write(f"Dados salvos em '{self.arquivo_dados}'")

        df = st.session_state.registro['df']

        if not df.empty:
            df.to_excel(self.arquivo_dados, index=False)
            st.markdown(get_binary_file_downloader_html(self.arquivo_dados, 'Relatório Atividades'), unsafe_allow_html=True)
        else:
            st.warning("Nenhum dado disponível para exportação.")

    def zerar_dados(self):
        st.write("Zerando dados...")
        st.session_state.registro['df'] = pd.DataFrame(columns=['ID', 'Nome_Usuário', 'Numero_Projeto', 'Atividade', 'Data', 'Início', 'Fim', 'Duração'])
        st.success("Dados zerados. Você pode iniciar novos registros.")

# Função auxiliar para criar botão de download
def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">{file_label}</a>'
    return href

# Adicionado um identificador único para cada usuário usando o UUID
user_id = str(uuid.uuid4())
registro = RegistroAtividades(user_id)

# Função principal
def main():
    st.sidebar.title("Menu de Navegação")
    app_choice = st.sidebar.radio("Selecione uma opção:", ("App 1 - AtividadeTracker", "Informações", "Gráficos"))

    if app_choice == "App 1 - AtividadeTracker":
        registro.registrar_atividades()

    elif app_choice == "Informações":
        informacoes()

    elif app_choice == "Gráficos":
        graficos()
