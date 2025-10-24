import pandas as pd
from sqlalchemy import create_engine
import mysql.connector

# 1. Carregar e padronizar o CSV
caminho_csv = r'C:\Users\luan.diniz\Downloads\glpi.csv'
df = pd.read_csv(caminho_csv, sep=';', encoding='utf-8')

# Padronizar nomes de colunas
df.columns = (
    df.columns.str.lower()
    .str.strip()
    .str.replace(' ', '_')
    .str.replace('-', '_')
    .str.normalize('NFKD')
    .str.encode('ascii', errors='ignore')
    .str.decode('utf-8')
)

print("Colunas disponíveis no DataFrame:", df.columns.tolist())
print(df.head())

# 2. Criar colunas calculadas
df['tempo_resolucao'] = pd.to_datetime(
    df['tempo_para_solucao_+_progresso'], dayfirst=True, errors='coerce'
) - pd.to_datetime(
    df['data_de_abertura'], dayfirst=True, errors='coerce'
)

df['sla_cumprido'] = df['tempo_resolucao'] <= pd.Timedelta(hours=24)

# 3. Renomear colunas
df.rename(columns={
    'atribuido___tecnico': 'tecnico',
    'atribuido___grupo_tecnico': 'grupo_tecnico',
    'tempo_para_solucao_+_progresso': 'tempo_para_solucao',
    'data_de_abertura': 'data_abertura',
}, inplace=True)

# 4. Criar conexão MySQL e tabela 
try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Lu281011*',
        database='service_desk'
    )

    cursor = conn.cursor()

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS chamados (
        id INT PRIMARY KEY,
        titulo VARCHAR(255),
        status VARCHAR(50),
        tecnico VARCHAR(100),
        grupo_tecnico VARCHAR(100),
        prioridade VARCHAR(50),
        data_abertura DATETIME,
        tempo_para_solucao DATETIME,
        ultima_atualizacao DATETIME,
        tempo_resolucao TIME,
        sla_cumprido BIT
    );
    """

    cursor.execute(create_table_sql)
    conn.commit()
    print("Tabela 'chamados' verificada/criada com sucesso.")

except mysql.connector.Error as err:
    print(f"Erro ao conectar ou criar tabela: {err}")

finally:
    if conn.is_connected():
        cursor.close()
        conn.close()

# 5. Inserir dados com SQLAlchemy
engine = create_engine('mysql+pymysql://root:L11*@localhost/service_desk')

# Filtrar as colunas conforme a tabela
colunas_esperadas = [
    'id', 'titulo', 'status', 'tecnico', 'grupo_tecnico', 'prioridade',
    'data_abertura', 'tempo_para_solucao', 'ultima_atualizacao',
    'tempo_resolucao', 'sla_cumprido'
]

# Manter apenas as colunas que existem no DataFrame
df_final = df[[col for col in colunas_esperadas if col in df.columns]]

# Enviar para o banco
df_final.to_sql('chamados', con=engine, if_exists='replace', index=False)

print("✅ Importação concluída com sucesso.") 

# Converter novamente para timedelta se for string
df['tempo_resolucao'] = pd.to_timedelta(df['tempo_resolucao'], errors='coerce')
media = df['tempo_resolucao'].mean()
print("Tempo médio de resolução:", media)

# Tempo médio e mediano de resolução
tempo_medio = df['tempo_resolução'].mean()
tempo_mediano = df['tempo_resolução'].median()

# MTTR (mean Time To Resolution)
mttr_horas = df['tempo__resolução'].mean().total-seconds() / 3600
print(f"MTTR: {mttr_horas:.2f} horas")

desempenho_tecnico = df.groupby('tecnico')['tempo_resolucao'].mean().sort_values()
desempenho_grupo = df.groupby('grupo_tecnico')['sla_cumprido'].mean().sort_values(ascending=False)
