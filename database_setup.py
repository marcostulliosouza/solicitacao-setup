import sqlite3
import os
import configparser
import bcrypt
from datetime import datetime

# Constantes
CONFIG_FILE = 'config.ini'
DATABASE_NAME = 'solicitacoes.db'
ADMIN_USER = ('Admin', '0000', 'admin123', 'administrador')
EXAMPLE_USERS = [
    ('João Silva', '1234', 'senha123', 'solicitante'),
    ('Maria Oliveira', '5678', 'senha456', 'recebedor'),
]
EXAMPLE_REQUESTS = [
    ('João Silva', '1234', 'Solicitação de reembolso de viagem', 'pendente')
]

# Dados dos insumos
INSUMOS = [
    ("1403468", "AGULHA PLASTICA PINK #20"),
    ("1403799", "ALICATE DE BICO 05POL PNE01NB"),
    ("1404992", "BICO PLASTICO OLIVA 14GA"),
    ("1400011", "CAMISINHA P/ SUGADOR DE SOLDA"),
    ("1401300", "CANETA ESFER AZL"),
    ("1401298", "CANETA MARC TX VRD"),
    ("1401291", "CANETA RETROP AZL"),
    ("1401290", "CANETA RETROP PRT"),
    ("1401293", "CANETA RETROP VRM"),
    ("1403304", "EMBOLO 30/50CC P/ SERINGA DE FLUID"),
    ("1400019", "ESCOVA DURA 3X7 P/ LIMP DE PLACAS"),
    ("1401264", "ETQ COUCHE VRD LIMA 85X40MM"),
    ("1405153", "FIO DE SOLDA LEAD FREE 0.8MM"),
    ("1404580", "FIO DE SOLDA TIN LEAD 0.55MM"),
    ("1404579", "FIO DE SOLDA TIN LEAD 0.75MM"),
    ("1404092", "FITA ADES PLAST SIMBOLO ESD 3/4 50M"),
    ("1404732", "FITA CREPE PAPEL AUTOMOTIVA 18MMX40M"),
    ("1401288", "FITA DE KAPTON ESD 13X33M"),
    ("1403473", "FRASCO ALMOTOLIA PLASTICO"),
    ("1404764", "LUVA NYLON ESD REVEST C/PU M"),
    ("1401167", "MALHA DESOLDADORA 2MMX1.5M"),
    ("1401169", "MARC INDUSTRIAL VRD"),
    ("1401168", "MARCADOR INDUSTRIAL AMARELO"),
    ("1400455", "PINCA ADS SERRIL 120MM"),
    ("1400047", "PINCA TS10 GOOT PONTI 120MM"),
    ("1400048", "PINCA TS11 GOOT PONTI 140MM"),
    ("1400050", "PINCEL TIGRE 1/2POL REF 815 -CERDA 0.5"),
    ("1404385", "PONTA FER SOLDA FACA T18-K"),
    ("1400055", "PONTE FER SOLDA CONIC RX-80HRT-LB GOOT"),
    ("1401190", "PULSEIRA 80V ANTI-ESTATICA"),
    ("1401669", "Ribbon cera"),
    ("1405628", "RIBBON RESINA PRT 110MMX74M R1880 ATRITO"),
    ("1403303", "SERINGA 50 CC P/ FLUID DISPENSER"),
    ("1401638", "SPUDGER (ESPATULA DE FD)155MM"),
    ("1400067", "ALICATE DE CORTE 05POL TER-03-NB"),
    ("1401119", "BATERIA 9V"),
    ("1405260", "CANETA DE FLUXO ALPHA EF-6100R (10G)"),
    ("1403285", "CANETA ESF BIC CRISTAL PRETA"),
    ("1401299", "CANETA MARC TX AMR"),
    ("1401292", "CANETA RETROP VRD"),
    ("1401304", "CLIPS 3/0"),
    ("1405321", "COLA P/FIXA 75396 - COLA QUENTE"),
    ("1400017", "COLA SUPER BONDER 416 100ML QUIMICO"),
    ("1404621", "ESPONJA REFIL P/LIMPEZA FERRO DE SOLDA"),
    ("1405261", "ESTANHO CHUMBO Sn63/Pb37 P1 1.00MM"),
    ("1405492", "ETQ COUCHE 85X40MM GELO COLINA"),
    ("1402942", "FIO DE SOLDA LEAD FREE 0.5MM"),
    ("1400156", "FITA ADES PLAST TRANSP 48MMX50M"),
    ("1405235", "FITA GOMADA 60MM/PAPEL KRAFT"),
    ("1403521", "FITA PET VRD DE ARQUEAR 16X0.8MM"),
    ("1402925", "FLUXO EM CANETA RMA-0801 QUIMICO"),
    ("1404765", "LUVA NYLON ESD REVEST C/PU G"),
    ("1404766", "LUVA NYLON ESD REVEST C/PU P"),
    ("1401492", "MARC QUADRO BCO VRD"),
    ("1404762", "PANO DE LIMPEZA ESD SGS"),
    ("1404113", "PINCEL CERDA 13MM REF 300X1/2"),
    ("1405089", "PONTA P/ESTACAO RX-80-HRT-55K"),
    ("1401485", "PONTE FER SOLDA FACA RX-80HRT-4.5K GOOT"),
    ("1401195", "SERINGAS DESCARTAVEIS 10ML"),
    ("1400140", "SUGADOR DE SOLDA AFR201"),
]


class DatabaseManager:
    """ Classe para gerenciar o banco de dados """

    def __init__(self):
        self.connection = None
        self.cursor = None
        self.sql_dir = ler_config()
        self.db_path = os.path.join(self.sql_dir, DATABASE_NAME)

    def __enter__(self):
        """ Abre a conexão com o banco de dados """
        self.connection = sqlite3.connect(self.db_path)
        self.cursor = self.connection.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """ Fecha a conexão com o banco de dados """
        if self.connection:
            self.connection.commit()
            self.connection.close()

    def criar_tabelas(self):
        """ Cria as tabelas no banco de dados """
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cracha TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                tipo TEXT NOT NULL,
                limite_solicitacao INTEGER DEFAULT 0
            )
            '''
        )

        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS solicitacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cracha TEXT NOT NULL,
                descricao_solicitacao TEXT NOT NULL,
                data_solicitacao TEXT NOT NULL,
                status TEXT NOT NULL,
                observacoes_recebimento TEXT,
                data_alteracao TEXT,
                usuario_alteracao TEXT,
                status_pagamento TEXT DEFAULT 'pendente'
            )
            '''
        )

        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS insumos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cod_sap TEXT NOT NULL UNIQUE,
                nome TEXT NOT NULL,
                descricao TEXT,
                quantidade_disponivel INTEGER NOT NULL DEFAULT 0
            )
            '''
        )

        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS solicitacoes_insumos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                solicitacao_id INTEGER NOT NULL,
                insumo_id INTEGER NOT NULL,
                quantidade INTEGER NOT NULL,
                usuario_id INTEGER,
                FOREIGN KEY (solicitacao_id) REFERENCES solicitacoes(id),
                FOREIGN KEY (insumo_id) REFERENCES insumos(id),
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            '''
        )

    def inserir_usuario(self, nome, cracha, senha, tipo):
        """ Insere um usuário na tabela de usuários """
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        self.cursor.execute(
            '''
            INSERT INTO usuarios (nome, cracha, senha, tipo)
            VALUES (?, ?, ?, ?)
            ''', (nome, cracha, senha_hash, tipo))

    def inserir_solicitacao(self, nome, cracha, descricao, data_atual, status):
        """ Insere uma solicitação na tabela de solicitações """
        self.cursor.execute(
            '''
            INSERT INTO solicitacoes (nome, cracha, descricao_solicitacao, data_solicitacao, status)
            VALUES (?, ?, ?, ?, ?)
            ''', (nome, cracha, descricao, data_atual, status))

    def adicionar_insumo(self, cod_sap, nome, descricao=None, quantidade_disponivel=0):
        """ Adiciona um novo insumo ao banco de dados """
        self.cursor.execute(
            '''
            INSERT INTO insumos (cod_sap, nome, descricao, quantidade_disponivel)
            VALUES (?, ?, ?, ?)
            ''', (cod_sap, nome, descricao, quantidade_disponivel))

    def popular_insumos(self):
        """ Popula a tabela de insumos com os dados fornecidos """
        for cod_sap, nome in INSUMOS:
            self.adicionar_insumo(cod_sap, nome)

    def popular_dados_iniciais(self):
        """ Popula o banco de dados com dados iniciais """
        self.inserir_usuario(*ADMIN_USER)
        for usuario in EXAMPLE_USERS:
            self.inserir_usuario(*usuario)
        for solicitacao in EXAMPLE_REQUESTS:
            self.inserir_solicitacao(*solicitacao, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'pendente')
        self.popular_insumos()

    def criar_banco_dados(self):
        """ Cria o banco de dados e popula com dados iniciais """
        if not os.path.exists(self.sql_dir):
            os.makedirs(self.sql_dir)
            print(f"Diretório {self.sql_dir} criado.")

        db_path = os.path.join(self.sql_dir, DATABASE_NAME)

        if os.path.exists(db_path):
            print("Banco de dados já existe!")
            return

        with DatabaseManager() as db:
            db.criar_tabelas()
            db.popular_dados_iniciais()
            print("Banco de dados criado e populado com sucesso!")

    def verificar_limite_usuario(self, usuario_id, quantidade):
        """Verifica se o usuário tem limite disponível para solicitar insumos."""
        self.cursor.execute('''
        SELECT limite_solicitacao FROM usuarios WHERE id = ?
        ''', (usuario_id,))
        limite = self.cursor.fetchone()[0]

        self.cursor.execute('''
        SELECT SUM(quantidade) FROM solicitacoes_insumos WHERE usuario_id = ?
        ''', (usuario_id,))
        total_solicitado = self.cursor.fetchone()[0] or 0

        return (total_solicitado + quantidade) <= limite

    def adicionar_insumo_a_solicitacao_com_limite(self, solicitacao_id, insumo_id, quantidade, usuario_id):
        """Adiciona um insumo a uma solicitação, verificando o limite do usuário."""
        if not self.verificar_limite_usuario(usuario_id, quantidade):
            raise ValueError("Limite de solicitação excedido para o usuário.")

        self.cursor.execute(
            '''
            INSERT INTO solicitacoes_insumos (solicitacao_id, insumo_id, quantidade, usuario_id)
            VALUES (?, ?, ?, ?)
            ''',
            (solicitacao_id, insumo_id, quantidade, usuario_id)
        )

    def atualizar_status_pagamento(self, solicitacao_id, status_pagamento):
        """Atualiza o status de pagamento de uma solicitação."""
        self.cursor.execute('''
        UPDATE solicitacoes SET status_pagamento = ? WHERE id = ?
        ''', (status_pagamento, solicitacao_id))

    def buscar_solicitacoes_por_status_pagamento(self, status_pagamento):
        """Busca solicitações no banco de dados com base no status de pagamento."""
        self.cursor.execute('''
        SELECT * FROM solicitacoes WHERE status_pagamento = ? ORDER BY id DESC
        ''', (status_pagamento,))
        return self.cursor.fetchall()

    def buscar_insumos(self):
        """Busca todos os insumos no banco de dados."""
        self.cursor.execute('''
        SELECT * FROM insumos ORDER BY id
        ''')
        return self.cursor.fetchall()

    def buscar_insumo_por_nome(self, nome):
        """Busca um insumo pelo nome."""
        self.cursor.execute('''
        SELECT * FROM insumos WHERE nome = ?
        ''', (nome,))
        return self.cursor.fetchone()

    def buscar_insumo_por_id(self, insumo_id):
        """Busca um insumo pelo ID."""
        self.cursor.execute('''
        SELECT * FROM insumos WHERE id = ?
        ''', (insumo_id,))
        return self.cursor.fetchone()

    def buscar_insumo_por_cod_sap(self, cod_sap):
        """Busca um insumo pelo código SAP."""
        self.cursor.execute('''
        SELECT * FROM insumos WHERE cod_sap = ?
        ''', (cod_sap,))
        return self.cursor.fetchone()

    def buscar_insumos_por_solicitacao(self, solicitacao_id):
        """Busca todos os insumos associados a uma solicitação."""
        self.cursor.execute('''
        SELECT i.id, i.cod_sap, i.nome, i.descricao, si.quantidade
        FROM solicitacoes_insumos si
        JOIN insumos i ON si.insumo_id = i.id
        WHERE si.solicitacao_id = ?
        ''', (solicitacao_id,))
        return self.cursor.fetchall()

    def buscar_usuario(self, nome, senha, tipo=None):
        """Busca um usuário no banco de dados."""
        try:
            # Busca o usuário pelo nome
            self.cursor.execute('''
            SELECT * FROM usuarios WHERE nome = ?
            ''', (nome,))
            usuario = self.cursor.fetchone()

            # Verifica se o usuário foi encontrado e se a senha está correta
            if usuario and bcrypt.checkpw(senha.encode('utf-8'), usuario[3]):
                # Verifica o tipo, se fornecido
                if tipo and usuario[4] != tipo:
                    return None
                return usuario
            return None
        except Exception as e:
            print(f"Erro ao buscar usuário: {e}")
            return None

    def buscar_solicitacoes(self, status=None):
        """Busca solicitações no banco de dados."""
        if status:
            self.cursor.execute('''
            SELECT * FROM solicitacoes WHERE status = ? ORDER BY id DESC
            ''', (status,))
        else:
            self.cursor.execute('''
            SELECT * FROM solicitacoes ORDER BY id DESC
            ''')
        return self.cursor.fetchall()

    def buscar_solicitacoes_por_usuario(self, id_usuario):
        """Busca todas as solicitações de um usuário pelo ID."""
        self.cursor.execute('''
        SELECT * FROM solicitacoes WHERE cracha = (
            SELECT cracha FROM usuarios WHERE id = ?
        ) ORDER BY id DESC
        ''', (id_usuario,))
        return self.cursor.fetchall()

    def atualizar_status_solicitacao(self, id_solicitacao, novo_status):
        """Atualiza o status de uma solicitação."""
        self.cursor.execute('''
        UPDATE solicitacoes SET status = ? WHERE id = ?
        ''', (novo_status, id_solicitacao))

    def excluir_solicitacao(self, id_solicitacao):
        """Exclui uma solicitação do banco de dados."""
        self.cursor.execute('''
        DELETE FROM solicitacoes WHERE id = ?
        ''', (id_solicitacao,))

    def buscar_usuarios(self):
        """Busca todos os usuários no banco de dados."""
        self.cursor.execute('''
        SELECT id, nome, cracha, tipo FROM usuarios ORDER BY id
        ''')
        return self.cursor.fetchall()

    def excluir_usuario(self, id_usuario):
        """Exclui um usuário do banco de dados."""
        self.cursor.execute('''
        DELETE FROM usuarios WHERE id = ?
        ''', (id_usuario,))


def ler_config():
    """ Lê o arquivo de configuração e retorna o diretório do banco de dados """
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config['PATH']['sql_dir']