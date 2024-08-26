import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import pytz
import time

print("Iniciando o aplicativo...")  # Log de depuração

# Definir o fuso horário de Brasília
brasilia_tz = pytz.timezone('America/Sao_Paulo')

# Carregar a planilha de cadastro dos atletas
if not os.path.exists('nfcteste.xlsx'):
    df_vazio = pd.DataFrame(columns=["Código1", "Código2", "Nome", "Categoria", "Sexo", "Modalidade"])
    df_vazio.to_excel('nfcteste.xlsx', index=False)

cadastro_df = pd.read_excel('nfcteste.xlsx')

# Garantir que todos os valores na coluna 'Código1' estejam como strings e sem espaços extras
cadastro_df['Código1'] = cadastro_df['Código1'].astype(str).str.strip()

# Configurar a interface do Streamlit
st.title("Sistema de Registro de Tempo")

# Inicializar o session_state para o código1 e o horário de largada
if 'Código1' not in st.session_state:
    st.session_state.Código1 = ''
if 'horario_largada' not in st.session_state:
    st.session_state.horario_largada = "08:00:00"  # Valor padrão

def registrar_tempo():
    start_time = time.time()  # Marcar o início do processo
    Código1 = st.session_state.Código1
    horario_largada = st.session_state.horario_largada

    # Verificar se o código existe na planilha de cadastro
    atleta_info = cadastro_df[cadastro_df['Código1'] == Código1]
    
    if not atleta_info.empty:
        # Capturar os dados do atleta
        nome = atleta_info.iloc[0]['Nome']
        categoria = atleta_info.iloc[0]['Categoria']
        sexo = atleta_info.iloc[0]['Sexo']
        modalidade = atleta_info.iloc[0]['Modalidade']
        
        # Capturar o horário atual no fuso horário de Brasília
        inicio = datetime.now(brasilia_tz).strftime("%H:%M:%S")
        
        # Calcular o tempo decorrido desde o horário de largada informado
        horario_largada_dt = datetime.strptime(horario_largada, "%H:%M:%S").replace(tzinfo=brasilia_tz)
        tempo_decorrido = datetime.strptime(inicio, "%H:%M:%S").replace(tzinfo=brasilia_tz) - horario_largada_dt

        # Ajustar o tempo decorrido para evitar resultados negativos
        if tempo_decorrido.days < 0:
            tempo_decorrido = timedelta(seconds=tempo_decorrido.seconds)

        # Formatar o tempo decorrido para HH:MM:SS
        tempo_decorrido_formatado = str(tempo_decorrido)

        # Criar uma nova linha com os dados do atleta e o tempo decorrido
        novo_registro = pd.DataFrame({
            "Código1": [Código1],
            "Nome": [nome],
            "Categoria": [categoria],
            "Sexo": [sexo],
            "Inicio": [inicio],
            "Tempo Decorrido": [tempo_decorrido_formatado],
            "Modalidade": [modalidade],
            "Horário de Largada": [horario_largada]
        })
        
        # Verificar se o arquivo Excel já existe
        try:
            resultados_df = pd.read_excel('resultados.xlsx')
        except FileNotFoundError:
            resultados_df = pd.DataFrame(columns=["Código1", "Nome", "Categoria", "Sexo", "Inicio", "Tempo Decorrido", "Modalidade", "Horário de Largada"])
        
        # Adicionar a nova linha ao DataFrame existente usando concat
        resultados_df = pd.concat([resultados_df, novo_registro], ignore_index=True)

        # Salvar em um arquivo temporário primeiro
        resultados_temp_file = 'resultados_temp.xlsx'
        resultados_df.to_excel(resultados_temp_file, index=False)
        
        # Substituir o arquivo original
        os.replace(resultados_temp_file, 'resultados.xlsx')

        end_time = time.time()  # Marcar o fim do processo
        execution_time = end_time - start_time  # Calcular o tempo de execução

        st.success(f"Tempo registrado com sucesso! Tempo de execução: {execution_time:.2f} segundos")

        # Limpar o campo Código1 após o registro, mantendo o horário de largada
        st.session_state.Código1 = ''
    else:
        st.error("Código do atleta não encontrado. Por favor, verifique o código e tente novamente.")
        st.session_state.Código1 = ''

# Campo para o Código1 (via NFC ou manual)
st.text_input("Código do Atleta (via NFC ou Manual)", value=st.session_state.Código1, key='Código1', on_change=registrar_tempo)

# Campo para o horário de largada, mantendo-o estático
st.text_input("Horário de Largada (HH:MM:SS)", value=st.session_state.horario_largada, key='horario_largada')

# Exibir a planilha atualizada
if os.path.exists('resultados.xlsx'):
    resultados_df = pd.read_excel('resultados.xlsx')
    st.write("Planilha Atualizada:")
    st.dataframe(resultados_df, use_container_width=True)

    # Adicionar botão de download
    with open("resultados.xlsx", "rb") as file:
        st.download_button(
            label="Baixar Planilha",
            data=file,
            file_name="resultados.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# Definir as colunas da planilha
colunas = ["Código1", "Nome", "Categoria", "Sexo", "Inicio", "Tempo Decorrido", "Modalidade", "Horário de Largada"]

# Botão para resetar os dados
if st.button('Resetar Dados'):
    # Criar um DataFrame vazio com as colunas definidas
    resultados_df = pd.DataFrame(columns=colunas)
    
    # Salvar o DataFrame vazio no arquivo Excel
    resultados_df.to_excel('resultados.xlsx', index=False)
    
    st.success("Todos os dados foram resetados com sucesso!")
