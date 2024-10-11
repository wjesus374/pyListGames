import pandas as pd
import sqlite3  # Use o driver correspondente ao seu banco de dados (e.g., psycopg2 para PostgreSQL)

# Configuração do banco de dados (ajuste o caminho conforme necessário)
DATABASE_URL = 'game_catalog.db'  # Para SQLite, ajuste para seu banco se necessário

# Criar uma conexão com o banco de dados
conn = sqlite3.connect(DATABASE_URL)

# Função para importar jogos do CSV
def import_games_from_csv(csv_file):
    # Ler o arquivo CSV
    df = pd.read_csv(csv_file, sep=';', encoding='iso-8859-1')

    # Inserir os dados no banco de dados
    for index, row in df.iterrows():
        # Criar a consulta SQL
        columns = ', '.join(row.index)
        placeholders = ', '.join('?' * len(row))
        sql = f'INSERT INTO game ({columns}) VALUES ({placeholders})'

        # Executar a consulta
        conn.execute(sql, tuple(row))

    # Salvar as alterações
    conn.commit()
    print("Jogos importados com sucesso!")

# Executar a função com o arquivo CSV
import_games_from_csv('lista_de_jogos.csv')

# Fechar a conexão
conn.close()
