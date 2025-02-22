import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Carregar credenciais do secrets
credentials_dict = dict(st.secrets["google_credentials"])
st.write(type(credentials_dict))

if "private_key" in credentials_dict:
    credentials_dict["private_key"] = credentials_dict["private_key"].replace("\\n", "\n")

# Criar as credenciais
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict, scope)

# Autenticar no Google Sheets
client = gspread.authorize(credentials)
sheet = client.open("Streamlit Fit").sheet1

st.write("Conexão bem-sucedida!")

# Funções CRUD
def carregar_dados():
    """Carrega os dados da planilha."""
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def adicionar_registro(novo_registro):
    """Adiciona um novo registro à planilha."""
    sheet.append_row(novo_registro)

def atualizar_registro(indice, dados_atualizados):
    """Atualiza um registro existente na planilha."""
    for col, valor in enumerate(dados_atualizados, start=1):
        sheet.update_cell(indice + 1, col, valor)  # +1 para compensar o cabeçalho

def deletar_registro(indice):
    """Deleta um registro da planilha."""
    sheet.delete_rows(indice + 1)  # +1 para compensar o cabeçalho

# Interface Streamlit
st.title("CRUD com Google Sheets")

# Exibir dados existentes
st.subheader("Dados Atuais")
dados = carregar_dados()
st.dataframe(dados)

# Seção para adicionar registros
st.subheader("Adicionar Novo Registro")
colunas = dados.columns.tolist() if not dados.empty else ["Coluna1", "Coluna2", "Coluna3"]
novo_registro = [st.text_input(f"Insira {col}") for col in colunas]

if st.button("Adicionar"):
    if all(novo_registro):
        adicionar_registro(novo_registro)
        st.success("Registro adicionado com sucesso!")
        st.experimental_rerun()
    else:
        st.error("Por favor, preencha todos os campos.")

# Seção para atualizar registros
st.subheader("Atualizar Registro")
indice_atualizar = st.number_input("Índice do registro (começa em 0)", min_value=0, max_value=len(dados) - 1, step=1)
if st.button("Carregar Registro para Atualizar"):
    registro_selecionado = dados.iloc[indice_atualizar].tolist()
    dados_atualizados = [st.text_input(f"{col}", value=str(registro_selecionado[i])) for i, col in enumerate(colunas)]
    if st.button("Atualizar"):
        atualizar_registro(indice_atualizar, dados_atualizados)
        st.success("Registro atualizado com sucesso!")
        st.experimental_rerun()

# Seção para deletar registros
st.subheader("Deletar Registro")
indice_deletar = st.number_input("Índice do registro para deletar (começa em 0)", min_value=0, max_value=len(dados) - 1, step=1)
if st.button("Deletar"):
    deletar_registro(indice_deletar)
    st.success("Registro deletado com sucesso!")
    st.experimental_rerun()
