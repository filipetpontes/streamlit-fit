import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# Configuração das credenciais do Google Sheets
def autenticar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_name('credenciais.json', scope)
    client = gspread.authorize(credentials)
    return client

def carregar_dados(sheet):
    data = sheet.get_all_records()
    return pd.DataFrame(data)

def adicionar_linha(sheet, nova_linha):
    sheet.append_row(nova_linha)

def atualizar_linha(sheet, indice, dados_atualizados):
    for col, valor in enumerate(dados_atualizados, start=1):
        sheet.update_cell(indice, col, valor)

def deletar_linha(sheet, indice):
    sheet.delete_rows(indice)

def main():
    st.title("CRUD com Google Sheets")

    # Autenticação no Google Sheets
    cliente = autenticar_google_sheets()
    planilha = cliente.open("NomeDaSuaPlanilha")
    aba = planilha.sheet1

    # Carregar os dados existentes
    dados = carregar_dados(aba)
    st.write("Dados Atuais:")
    st.dataframe(dados)

    # CRUD
    acao = st.sidebar.selectbox("Ação", ["Adicionar", "Atualizar", "Deletar"])

    if acao == "Adicionar":
        st.subheader("Adicionar Novo Registro")
        colunas = dados.columns.tolist()
        nova_linha = [st.text_input(f"{col}") for col in colunas]
        if st.button("Adicionar"):
            if all(nova_linha):
                adicionar_linha(aba, nova_linha)
                st.success("Registro adicionado com sucesso!")
                st.experimental_rerun()
            else:
                st.error("Preencha todos os campos.")

    elif acao == "Atualizar":
        st.subheader("Atualizar Registro Existente")
        indice = st.number_input("Índice do registro (começa em 1)", min_value=1, max_value=len(dados), step=1)
        if st.button("Carregar Registro"):
            registro_atual = dados.iloc[indice - 1].tolist()
            dados_atualizados = [st.text_input(f"{col}", value=str(registro_atual[i])) for i, col in enumerate(dados.columns)]

            if st.button("Atualizar"):
                atualizar_linha(aba, indice, dados_atualizados)
                st.success("Registro atualizado com sucesso!")
                st.experimental_rerun()

    elif acao == "Deletar":
        st.subheader("Deletar Registro")
        indice = st.number_input("Índice do registro (começa em 1)", min_value=1, max_value=len(dados), step=1)
        if st.button("Deletar"):
            deletar_linha(aba, indice)
            st.success("Registro deletado com sucesso!")
            st.experimental_rerun()

if __name__ == "__main__":
    main()
