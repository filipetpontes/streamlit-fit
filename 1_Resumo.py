import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import os

# Configuração para autenticação com o Google Sheets
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
]

def authenticate_google_sheets(json_keyfile):
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile, SCOPE)
    client = gspread.authorize(creds)
    return client

# Função para carregar a planilha
def load_sheet(client, spreadsheet_name):
    return client.open(spreadsheet_name).sheet1

# Função para exibir a planilha como DataFrame
def fetch_data(sheet):
    data = sheet.get_all_records()
    return pd.DataFrame(data)

# Função para atualizar os dados na planilha
def update_sheet(sheet, df):
    sheet.clear()
    sheet.update([df.columns.values.tolist()] + df.values.tolist())

# Início do aplicativo Streamlit
st.title("CRUD com Google Sheets")

# Upload do arquivo JSON de credenciais
json_keyfile = st.file_uploader("Faça upload do arquivo de credenciais JSON", type="json")

if json_keyfile:
    # Autenticação
    client = authenticate_google_sheets(json_keyfile)

    # Nome da planilha
    spreadsheet_name = st.text_input("Digite o nome da planilha do Google Sheets")

    if spreadsheet_name:
        try:
            # Carregar a planilha
            sheet = load_sheet(client, spreadsheet_name)

            # Dados da planilha
            st.subheader("Dados Atuais da Planilha")
            df = fetch_data(sheet)
            st.dataframe(df)

            # Operações CRUD
            st.subheader("Operações CRUD")

            # Adicionar uma nova linha
            st.write("Adicionar nova linha")
            new_row = {}
            for col in df.columns:
                new_row[col] = st.text_input(f"Valor para {col}", key=f"new_{col}")

            if st.button("Adicionar Linha"):
                df = df.append(new_row, ignore_index=True)
                update_sheet(sheet, df)
                st.success("Linha adicionada com sucesso!")

            # Editar uma linha existente
            st.write("Editar uma linha existente")
            row_to_edit = st.number_input("Número da linha para editar (começando em 0)", min_value=0, max_value=len(df)-1, step=1)
            edited_row = {}
            for col in df.columns:
                edited_row[col] = st.text_input(f"Novo valor para {col}", value=df.iloc[row_to_edit][col], key=f"edit_{col}")

            if st.button("Salvar Edição"):
                for col in df.columns:
                    df.at[row_to_edit, col] = edited_row[col]
                update_sheet(sheet, df)
                st.success("Linha editada com sucesso!")

            # Excluir uma linha
            st.write("Excluir uma linha")
            row_to_delete = st.number_input("Número da linha para excluir (começando em 0)", min_value=0, max_value=len(df)-1, step=1)
            if st.button("Excluir Linha"):
                df = df.drop(row_to_delete).reset_index(drop=True)
                update_sheet(sheet, df)
                st.success("Linha excluída com sucesso!")
            
            valor_teste = os.getenv("teste")
            
            st.write(f"Valor: {valor_teste}")
        except Exception as e:
            st.error(f"Erro ao acessar a planilha: {e}")
