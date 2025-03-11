import sqlite3
import os
import configparser
import bcrypt

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


class DatabaseManager:
    """ Classe para gerenciar o banco"""

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
        """ Fecha a conexão com o banco de dados"""
        if self.connection:
            self.connection.commit()
            self.connection.close()

    def criar_tabelas(self):
        """ Cria as tabelas no banco"""
        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                cracha TEXT NOT NULL UNIQUE,
                senha TEXT NOT NULL,
                tipo TEXT NOT NULL
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
                usuario_alteracao TEXT
            )
            '''
        )

        self.cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS insumos  (
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
                FOREIGN KEY (solicitacao_id) REFERENCES solicitacoes(id),
                FOREIGN KEY (insumo_id) REFERENCES insumos(id)
            )
            '''
        )

    def inserir_usuario(self, nome, cracha, senha, tipo):
        """ Insere um usuário na tabela usuários"""
        senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
        self.cursor.execute(
            '''
            INSERT INTO usuarios (nome, cracha, senha, tipo)
            VALUES (?, ?, ?, ?)
            '''
            , (nome, cracha, senha_hash, tipo))

    def inserir_solicitacao(self, nome, cracha, descricao, data_atual, status):
        """ Insere uma solicitação na tabela de solicatações"""
        self.cursor.execute(
            '''
            INSERT INTO solicitacoes (nome, cracha, descricao, data, status)
            VALUES (?, ?, ?, ?, ?)
            '''
            , (nome, cracha, descricao, data_atual, status)
        )

    def adicionar_insumo(self, cod_sap, nome, descricao=None, quantidade_disponivel=0):
        """Adiciona um novo insumo ao banco de dados."""
        self.cursor.execute(
            '''
            INSERT INTO insumos (cod_sap, nome, descricao, quantidade_disponivel)
            VALUES (?, ?, ?, ?)
            ''',
            (cod_sap, nome, descricao, quantidade_disponivel)
        )

    def remover_insumo(self, insumo_id):
        """Remove um insumo do banco de dados."""
        self.cursor.execute(
            '''
            DELETE FROM insumos WHERE id = ?
            ''',
            (insumo_id,)
        )

    def atualizar_insumo(self, insumo_id, cod_sap=None, nome=None, descricao=None, quantidade_disponivel=None):
        """Atualiza as informações de um insumo."""
        query = "UPDATE insumos SET "
        params = []
        if cod_sap:
            query += "cod_sap = ?, "
            params.append(cod_sap)
        if nome:
            query += "nome = ?, "
            params.append(nome)
        if descricao:
            query += "descricao = ?, "
            params.append(descricao)
        if quantidade_disponivel is not None:
            query += "quantidade_disponivel = ?, "
            params.append(quantidade_disponivel)
        query = query.rstrip(", ") + " WHERE id = ?"
        params.append(insumo_id)
        self.cursor.execute(query, tuple(params))

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

    def adicionar_insumo_a_solicitacao(self, solicitacao_id, insumo_id, quantidade):
        """Adiciona um insumo a uma solicitação."""
        self.cursor.execute(
            '''
            INSERT INTO solicitacoes_insumos (solicitacao_id, insumo_id, quantidade)
            VALUES (?, ?, ?)
            ''',
            (solicitacao_id, insumo_id, quantidade)
        )

    def remover_insumo_de_solicitacao(self, solicitacao_id, insumo_id):
        """Remove um insumo de uma solicitação."""
        self.cursor.execute(
            '''
            DELETE FROM solicitacoes_insumos WHERE solicitacao_id = ? AND insumo_id = ?
            ''',
            (solicitacao_id, insumo_id)
        )

    def atualizar_quantidade_insumo_em_solicitacao(self, solicitacao_id, insumo_id, quantidade):
        """Atualiza a quantidade de um insumo em uma solicitação."""
        self.cursor.execute(
            '''
            UPDATE solicitacoes_insumos SET quantidade = ?
            WHERE solicitacao_id = ? AND insumo_id = ?
            ''',
            (quantidade, solicitacao_id, insumo_id)
        )

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

    def popular_dados_iniciais(self):
        """Popula o banco de dados com dados iniciais."""
        self.inserir_usuario(*ADMIN_USER)
        for usuario in EXAMPLE_USERS:
            self.inserir_usuario(*usuario)
        for solicitacao in EXAMPLE_REQUESTS:
            self.inserir_solicitacao(*solicitacao)

    def criar_banco_dados(self):
        """ Cria o banco de dados e popula com dados iniciais"""
        # Cria o diretório se não existir
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


def ler_config():
    """ Lê o aruqivo de configuração e retorna o diretório do banco de dados."""
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config['PATH']['sql_dir']

