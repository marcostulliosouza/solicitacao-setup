import tkinter as tk
from tkinter import ttk, messagebox
import socket
import pickle
import threading
import os
import configparser

import bcrypt

from database_setup import DatabaseManager


def ler_config():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config['PATH']['sql_dir']


class RecebimentoApp:
    def __init__(self, root):
        self.sql_path = ler_config()
        self.database_manager = DatabaseManager()
        self.database_manager.criar_banco_dados()
        self.root = root
        self.root.title("Sistema de Solicitações - Recebimento")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")

        # Centraliza a janela
        largura_janela = 900
        altura_janela = 600
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura_janela // 2)
        pos_y = (altura_tela // 2) - (altura_janela // 2)
        self.root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

        # Variáveis para login
        self.usuario_atual = None
        self.nome_login = tk.StringVar()
        self.senha_login = tk.StringVar()

        # Variáveis para gerenciamento de usuários
        self.novo_nome = tk.StringVar()
        self.novo_cracha = tk.StringVar()
        self.nova_senha = tk.StringVar()
        self.novo_tipo = tk.StringVar(value="solicitante")

        # Variáveis para notificações
        self.socket_servidor = None
        self.porta_notificacao = 5000
        self.notificacoes_ativas = False

        # Inicia com a tela de login
        self.criar_tela_login()

    def criar_tela_login(self):
        # Para a thread de notificações se estiver ativa
        self.notificacoes_ativas = False
        if hasattr(self, 'thread_notificacoes') and self.thread_notificacoes.is_alive():
            if self.socket_servidor:
                self.socket_servidor.close()

        # Remove widgets anteriores, se existirem
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame de login com fundo azul claro
        frame_login = tk.Frame(self.root, bg="#e6f2ff", padx=20, pady=20)
        frame_login.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=300)

        # Título
        titulo = tk.Label(frame_login, text="SISTEMA DE SOLICITAÇÕES", font=("Arial", 16, "bold"),
                          bg="#e6f2ff", fg="#003366")
        titulo.pack(pady=10)

        subtitulo = tk.Label(frame_login, text="Login de Recebimento", font=("Arial", 12),
                             bg="#e6f2ff", fg="#003366")
        subtitulo.pack(pady=5)

        # Campo de usuário
        frame_usuario = tk.Frame(frame_login, bg="#e6f2ff")
        frame_usuario.pack(fill="x", pady=5)

        label_usuario = tk.Label(frame_usuario, text="Nome:", font=("Arial", 10),
                                 bg="#e6f2ff", fg="#003366", width=10, anchor="w")
        label_usuario.pack(side=tk.LEFT, padx=5)

        entry_usuario = tk.Entry(frame_usuario, textvariable=self.nome_login, font=("Arial", 10),
                                 width=30)
        entry_usuario.pack(side=tk.LEFT, padx=5)

        # Campo de senha
        frame_senha = tk.Frame(frame_login, bg="#e6f2ff")
        frame_senha.pack(fill="x", pady=5)

        label_senha = tk.Label(frame_senha, text="Senha:", font=("Arial", 10),
                               bg="#e6f2ff", fg="#003366", width=10, anchor="w")
        label_senha.pack(side=tk.LEFT, padx=5)

        entry_senha = tk.Entry(frame_senha, textvariable=self.senha_login, font=("Arial", 10),
                               width=30, show="*")
        entry_senha.pack(side=tk.LEFT, padx=5)

        # Botão de login
        frame_botao = tk.Frame(frame_login, bg="#e6f2ff")
        frame_botao.pack(pady=20)

        botao_login = tk.Button(frame_botao, text="Entrar", font=("Arial", 10, "bold"),
                                bg="#0066cc", fg="white", padx=20, pady=5,
                                command=self.fazer_login)
        botao_login.pack()

        # Rodapé
        rodape = tk.Label(frame_login, text="© 2025 - Sistema de Solicitações",
                          font=("Arial", 8), bg="#e6f2ff", fg="#666666")
        rodape.pack(side=tk.BOTTOM, pady=10)

    def fazer_login(self):
        nome = self.nome_login.get()
        senha = self.senha_login.get()

        if nome and senha:
            try:
                with DatabaseManager() as db:
                    # Busca o usuário sem restrição de tipo
                    usuario = db.buscar_usuario(nome, senha)

                    if usuario:
                        # Verifica se o usuário é administrador ou recebedor
                        if usuario[4] in ["administrador", "recebedor"]:
                            self.usuario_atual = {
                                'id': usuario[0],
                                'nome': usuario[1],
                                'cracha': usuario[2],
                                'tipo': usuario[4]
                            }
                            self.criar_tela_principal()
                            self.iniciar_servidor_notificacoes()
                        else:
                            messagebox.showerror("Erro de Login",
                                                 "Você não tem permissão para acessar esta área.")
                    else:
                        messagebox.showerror("Erro de Login",
                                             "Usuário não encontrado ou senha incorreta.")
            except Exception as e:
                messagebox.showerror("Erro de Banco de Dados", f"Erro ao conectar ao banco de dados: {str(e)}")
        else:
            messagebox.showwarning("Campos Vazios", "Por favor, preencha todos os campos.")
    def criar_tela_principal(self):
        # Remove widgets anteriores
        for widget in self.root.winfo_children():
            widget.destroy()

        # Configuração da tela principal
        self.root.configure(bg="#f0f0f0")

        # Frame do cabeçalho
        frame_cabecalho = tk.Frame(self.root, bg="#0066cc", height=60)
        frame_cabecalho.pack(fill="x")

        label_titulo = tk.Label(frame_cabecalho, text="SISTEMA DE SOLICITAÇÕES - RECEBIMENTO",
                                font=("Arial", 14, "bold"), bg="#0066cc", fg="white")
        label_titulo.pack(side=tk.LEFT, padx=20, pady=15)

        label_usuario = tk.Label(frame_cabecalho,
                                 text=f"Usuário: {self.usuario_atual['nome']} | Tipo: {self.usuario_atual['tipo'].capitalize()}",
                                 font=("Arial", 10), bg="#0066cc", fg="white")
        label_usuario.pack(side=tk.RIGHT, padx=20, pady=15)

        # Criação do notebook (abas)
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=20, pady=20)

        # Aba de Solicitações
        frame_solicitacoes = ttk.Frame(notebook)
        notebook.add(frame_solicitacoes, text="Solicitações")

        # Configuração da aba de solicitações
        self.configurar_aba_solicitacoes(frame_solicitacoes)

        # Aba de Gerenciamento de Usuários (somente para administradores)
        if self.usuario_atual['tipo'] == 'administrador':
            frame_usuarios = ttk.Frame(notebook)
            notebook.add(frame_usuarios, text="Gerenciamento de Usuários")
            self.configurar_aba_usuarios(frame_usuarios)

        # Frame para botões inferiores
        frame_botoes = tk.Frame(self.root, bg="#f0f0f0")
        frame_botoes.pack(fill="x", padx=20, pady=10)

        # Botão de atualizar
        botao_atualizar = tk.Button(frame_botoes, text="Atualizar Lista",
                                    font=("Arial", 10), bg="#0066cc", fg="white",
                                    padx=15, pady=5,
                                    command=lambda: self.carregar_solicitacoes())
        botao_atualizar.pack(side=tk.LEFT, padx=5)

        # Botão de sair
        botao_sair = tk.Button(frame_botoes, text="Sair",
                               font=("Arial", 10), bg="#ff6666", fg="white",
                               padx=15, pady=5,
                               command=self.criar_tela_login)
        botao_sair.pack(side=tk.RIGHT, padx=5)

        # Área de notificações
        frame_notificacoes = tk.Frame(self.root, bg="#e6f2ff", height=30)
        frame_notificacoes.pack(fill="x", side=tk.BOTTOM)

        self.label_notificacao = tk.Label(frame_notificacoes, text="Sem novas notificações",
                                          font=("Arial", 9), bg="#e6f2ff", fg="#666666")
        self.label_notificacao.pack(side=tk.LEFT, padx=10, pady=5)

    def configurar_aba_solicitacoes(self, frame):
        # Frame para filtros
        frame_filtros = tk.Frame(frame, bg="#f0f0f0")
        frame_filtros.pack(fill="x", padx=10, pady=10)

        label_filtro = tk.Label(frame_filtros, text="Filtrar por status:", font=("Arial", 10), bg="#f0f0f0")
        label_filtro.pack(side=tk.LEFT, padx=5)

        self.filtro_status = tk.StringVar(value="todos")
        combo_status = ttk.Combobox(frame_filtros, textvariable=self.filtro_status, width=15,
                                    values=["todos", "pendente", "em análise", "pago"])
        combo_status.pack(side=tk.LEFT, padx=5)

        botao_filtrar = tk.Button(frame_filtros, text="Filtrar",
                                  font=("Arial", 9), bg="#0066cc", fg="white",
                                  command=self.carregar_solicitacoes)
        botao_filtrar.pack(side=tk.LEFT, padx=5)

        # Frame para a tabela
        frame_tabela = tk.Frame(frame)
        frame_tabela.pack(fill="both", expand=True, padx=10, pady=5)

        # Criação da tabela
        colunas = (
        "ID", "Nome", "Crachá", "Descrição", "Data", "Status", "Última Alteração", "Usuário Alteração", "Observações")

        self.tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", height=15)

        # Configuração das colunas
        self.tabela.column("ID", width=50, anchor="center")
        self.tabela.column("Nome", width=150)
        self.tabela.column("Crachá", width=80, anchor="center")
        self.tabela.column("Descrição", width=300)
        self.tabela.column("Data", width=150, anchor="center")
        self.tabela.column("Status", width=100, anchor="center")
        self.tabela.column("Última Alteração", width=150, anchor="center")
        self.tabela.column("Usuário Alteração", width=150, anchor="center")
        self.tabela.column("Observações", width=200)

        # Cabeçalhos
        for col in colunas:
            self.tabela.heading(col, text=col)

        # Barra de rolagem
        scrollbar = ttk.Scrollbar(frame_tabela, orient="vertical", command=self.tabela.yview)
        self.tabela.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tabela.pack(side="left", fill="both", expand=True)

        # Evento de clique na tabela
        self.tabela.bind("<Double-1>", self.mostrar_opcoes_solicitacao)

        # Frame para ações
        frame_acoes = tk.Frame(frame, bg="#f0f0f0")
        frame_acoes.pack(fill="x", padx=10, pady=10)

        # Carregar solicitações
        self.carregar_solicitacoes()

    def configurar_aba_usuarios(self, frame):
        # Frame para adicionar usuários
        frame_adicionar = tk.LabelFrame(frame, text="Adicionar Novo Usuário", padx=10, pady=10)
        frame_adicionar.pack(fill="x", padx=10, pady=10)

        # Campo Nome
        frame_nome = tk.Frame(frame_adicionar)
        frame_nome.pack(fill="x", pady=5)

        tk.Label(frame_nome, text="Nome:", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
        tk.Entry(frame_nome, textvariable=self.novo_nome, width=30).pack(side=tk.LEFT, padx=5)

        # Campo Crachá
        frame_cracha = tk.Frame(frame_adicionar)
        frame_cracha.pack(fill="x", pady=5)

        tk.Label(frame_cracha, text="Crachá:", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
        tk.Entry(frame_cracha, textvariable=self.novo_cracha, width=15).pack(side=tk.LEFT, padx=5)

        # Campo Senha
        frame_senha = tk.Frame(frame_adicionar)
        frame_senha.pack(fill="x", pady=5)

        tk.Label(frame_senha, text="Senha:", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
        tk.Entry(frame_senha, textvariable=self.nova_senha, width=20, show="*").pack(side=tk.LEFT, padx=5)

        # Campo Tipo
        frame_tipo = tk.Frame(frame_adicionar)
        frame_tipo.pack(fill="x", pady=5)

        tk.Label(frame_tipo, text="Tipo:", width=10, anchor="w").pack(side=tk.LEFT, padx=5)

        rb_solicitante = tk.Radiobutton(frame_tipo, text="Solicitante", variable=self.novo_tipo,
                                        value="solicitante")
        rb_solicitante.pack(side=tk.LEFT, padx=5)

        rb_recebedor = tk.Radiobutton(frame_tipo, text="Recebedor", variable=self.novo_tipo,
                                      value="recebedor")
        rb_recebedor.pack(side=tk.LEFT, padx=5)

        rb_admin = tk.Radiobutton(frame_tipo, text="Administrador", variable=self.novo_tipo,
                                  value="administrador")
        rb_admin.pack(side=tk.LEFT, padx=5)

        # Botão Adicionar
        frame_botao = tk.Frame(frame_adicionar)
        frame_botao.pack(fill="x", pady=10)

        tk.Button(frame_botao, text="Adicionar Usuário", bg="#0066cc", fg="white",
                  command=self.adicionar_usuario).pack(side=tk.RIGHT, padx=5)

        # Frame para lista de usuários
        frame_lista = tk.LabelFrame(frame, text="Usuários Cadastrados", padx=10, pady=10)
        frame_lista.pack(fill="both", expand=True, padx=10, pady=10)

        # Tabela de usuários
        colunas = ("ID", "Nome", "Crachá", "Tipo")

        self.tabela_usuarios = ttk.Treeview(frame_lista, columns=colunas, show="headings", height=10)

        # Configuração das colunas
        self.tabela_usuarios.column("ID", width=50, anchor="center")
        self.tabela_usuarios.column("Nome", width=200)
        self.tabela_usuarios.column("Crachá", width=100, anchor="center")
        self.tabela_usuarios.column("Tipo", width=150, anchor="center")

        # Cabeçalhos
        for col in colunas:
            self.tabela_usuarios.heading(col, text=col)

        # Barra de rolagem
        scrollbar = ttk.Scrollbar(frame_lista, orient="vertical", command=self.tabela_usuarios.yview)
        self.tabela_usuarios.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tabela_usuarios.pack(side="left", fill="both", expand=True)

        # Evento de clique na tabela
        self.tabela_usuarios.bind("<Double-1>", self.opcoes_usuario)

        # Botão para atualizar lista
        tk.Button(frame_lista, text="Atualizar Lista", bg="#0066cc", fg="white",
                  command=self.carregar_usuarios).pack(side=tk.RIGHT, padx=5, pady=5)

        # Carregar usuários
        self.carregar_usuarios()

    def carregar_solicitacoes(self):
        # Limpar tabela
        for i in self.tabela.get_children():
            self.tabela.delete(i)

        try:
            with DatabaseManager() as db:
                # Filtro por status
                filtro = self.filtro_status.get()
                if filtro != "todos":
                    solicitacoes = db.buscar_solicitacoes(filtro)
                else:
                    solicitacoes = db.buscar_solicitacoes()

                for s in solicitacoes:
                    # Formatar a data para melhor visualização
                    data_formatada = s[4]
                    data_alteracao_formatada = s[6] if s[6] else "N/A"

                    # Inserir na tabela
                    self.tabela.insert("", "end", values=(
                        s[0], s[1], s[2], s[3], data_formatada, s[5], data_alteracao_formatada, s[7], s[8]
                    ))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar solicitações: {str(e)}")

    def carregar_usuarios(self):
        # Limpar tabela
        for i in self.tabela_usuarios.get_children():
            self.tabela_usuarios.delete(i)

        try:
            with DatabaseManager() as db:
                usuarios = db.buscar_usuarios()

                for u in usuarios:
                    # Inserir na tabela
                    self.tabela_usuarios.insert("", "end", values=u)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar usuários: {str(e)}")

    def mostrar_opcoes_solicitacao(self, event):
        item = self.tabela.selection()[0]
        solicitacao = self.tabela.item(item, "values")

        # Criar janela de opções
        janela_opcoes = tk.Toplevel(self.root)
        janela_opcoes.title("Opções de Solicitação")
        janela_opcoes.geometry("450x300")
        janela_opcoes.configure(bg="#e6f2ff")
        janela_opcoes.transient(self.root)
        janela_opcoes.grab_set()

        # Centralizar a janela
        largura_janela = 550
        altura_janela = 400
        largura_tela = janela_opcoes.winfo_screenwidth()
        altura_tela = janela_opcoes.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura_janela // 2)
        pos_y = (altura_tela // 2) - (altura_janela // 2)
        janela_opcoes.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

        # Cabeçalho
        tk.Label(janela_opcoes, text="Detalhes da Solicitação", font=("Arial", 12, "bold"),
                 bg="#e6f2ff", fg="#003366").pack(pady=10)

        # Informações da solicitação
        frame_info = tk.Frame(janela_opcoes, bg="#e6f2ff")
        frame_info.pack(fill="x", padx=20, pady=5)

        # ID
        tk.Label(frame_info, text=f"ID: {solicitacao[0]}", font=("Arial", 10),
                 bg="#e6f2ff", fg="#333333", anchor="w").pack(fill="x", pady=2)

        # Nome
        tk.Label(frame_info, text=f"Nome: {solicitacao[1]}", font=("Arial", 10),
                 bg="#e6f2ff", fg="#333333", anchor="w").pack(fill="x", pady=2)

        # Crachá
        tk.Label(frame_info, text=f"Crachá: {solicitacao[2]}", font=("Arial", 10),
                 bg="#e6f2ff", fg="#333333", anchor="w").pack(fill="x", pady=2)

        # Data
        tk.Label(frame_info, text=f"Data: {solicitacao[4]}", font=("Arial", 10),
                 bg="#e6f2ff", fg="#333333", anchor="w").pack(fill="x", pady=2)

        # Descrição
        tk.Label(frame_info, text="Descrição:", font=("Arial", 10),
                 bg="#e6f2ff", fg="#333333", anchor="w").pack(fill="x", pady=2)

        texto_descricao = tk.Text(frame_info, font=("Arial", 10), height=4, width=40)
        texto_descricao.insert("1.0", solicitacao[3])
        texto_descricao.config(state="disabled")
        texto_descricao.pack(fill="x", pady=5)

        # Status atual
        frame_status = tk.Frame(janela_opcoes, bg="#e6f2ff")
        frame_status.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_status, text="Status atual:", font=("Arial", 10),
                 bg="#e6f2ff", fg="#333333").pack(side=tk.LEFT, padx=5)

        status_atual = solicitacao[5]
        label_status = tk.Label(frame_status, text=status_atual, font=("Arial", 10, "bold"),
                                bg="#e6f2ff", fg=self.cor_status(status_atual))
        label_status.pack(side=tk.LEFT, padx=5)

        # Campo de Observações
        frame_observacoes = tk.Frame(janela_opcoes, bg="#e6f2ff")
        frame_observacoes.pack(fill="x", padx=20, pady=5)

        tk.Label(frame_observacoes, text="Observações:", font=("Arial", 10),
                 bg="#e6f2ff", fg="#333333").pack(side=tk.LEFT, padx=5)


        self.observacoes_texto = tk.Text(frame_observacoes, font=("Arial", 10), height=4, width=40)
        self.observacoes_texto.insert("1.0", solicitacao[8] if solicitacao[8] else "")
        self.observacoes_texto.pack(fill="x", pady=5)

        # Opções de atualização de status
        frame_atualizacao = tk.Frame(janela_opcoes, bg="#e6f2ff")
        frame_atualizacao.pack(fill="x", padx=20, pady=10)

        tk.Label(frame_atualizacao, text="Atualizar status para:", font=("Arial", 10),
                 bg="#e6f2ff", fg="#333333").pack(side=tk.LEFT, padx=5)

        novo_status = tk.StringVar(value=status_atual)
        combo_status = ttk.Combobox(frame_atualizacao, textvariable=novo_status, width=15,
                                    values=["pendente", "em análise", "pago"])
        combo_status.pack(side=tk.LEFT, padx=5)

        # Botões
        frame_botoes = tk.Frame(janela_opcoes, bg="#e6f2ff")
        frame_botoes.pack(fill="x", padx=20, pady=10)

        # Botão Atualizar
        botao_atualizar = tk.Button(frame_botoes, text="Atualizar Status", bg="#0066cc", fg="white",
                                    command=lambda: self.atualizar_status(solicitacao[0], novo_status.get(),
                                                                          janela_opcoes))
        botao_atualizar.pack(side=tk.LEFT, padx=5)

        # Botão Excluir (apenas para administradores)
        if self.usuario_atual['tipo'] == 'administrador':
            botao_excluir = tk.Button(frame_botoes, text="Excluir Solicitação", bg="#ff6666", fg="white",
                                      command=lambda: self.excluir_solicitacao(solicitacao[0], janela_opcoes))
            botao_excluir.pack(side=tk.RIGHT, padx=5)

        # Botão Fechar
        botao_fechar = tk.Button(frame_botoes, text="Fechar", bg="#cccccc", fg="#333333",
                                 command=janela_opcoes.destroy)
        botao_fechar.pack(side=tk.RIGHT, padx=5)

    def cor_status(self, status):
        if status == "pendente":
            return "#FF6600"  # Laranja
        elif status == "em análise":
            return "#0066CC"  # Azul
        elif status == "pago":
            return "#009900"  # Verde
        else:
            return "#333333"  # Cinza

    def atualizar_status(self, id_solicitacao, novo_status, janela=None):
        observacoes = self.observacoes_texto.get("1.0", "end-1c") if hasattr(self, 'observacoes_texto') else ""
        usuario_alteracao = self.usuario_atual['nome']

        try:
            with DatabaseManager() as db:
                db.atualizar_status_solicitacao(id_solicitacao, novo_status)
                messagebox.showinfo("Sucesso", "Status atualizado com sucesso!")

                # Fechar janela se existir
                if janela:
                    janela.destroy()

                # Atualizar lista de solicitações
                self.carregar_solicitacoes()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar status: {str(e)}")

    def cancelar_solicitacao(self, id_solicitacao, janela=None):
        observacoes = self.observacoes_texto.get("1.0", "end-1c") if hasattr(self, 'observacoes_texto') else ""
        usuario_alteracao = self.usuario_atual['nome']

        try:
            with DatabaseManager() as db:
                db.atualizar_status_solicitacao(id_solicitacao, "cancelado", observacoes, usuario_alteracao)
                messagebox.showinfo("Sucesso", "Solicitação cancelada com sucesso!")

                # Fechar janela se existir
                if janela:
                    janela.destroy()

                # Atualizar lista de solicitações
                self.carregar_solicitacoes()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cancelar solicitação: {str(e)}")

    def opcoes_usuario(self, event):
        item = self.tabela_usuarios.selection()[0]
        usuario = self.tabela_usuarios.item(item, "values")

        # Criar janela de opções
        janela_opcoes = tk.Toplevel(self.root)
        janela_opcoes.title("Opções de Usuário")
        janela_opcoes.geometry("350x200")
        janela_opcoes.configure(bg="#e6f2ff")
        janela_opcoes.transient(self.root)
        janela_opcoes.grab_set()

        # Centralizar a janela
        largura_janela = 350
        altura_janela = 200
        largura_tela = janela_opcoes.winfo_screenwidth()
        altura_tela = janela_opcoes.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura_janela // 2)
        pos_y = (altura_tela // 2) - (altura_janela // 2)
        janela_opcoes.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

        # Cabeçalho
        tk.Label(janela_opcoes, text="Detalhes do Usuário", font=("Arial", 12, "bold"),
                 bg="#e6f2ff", fg="#003366").pack(pady=10)

        # Informações do usuário
        frame_info = tk.Frame(janela_opcoes, bg="#e6f2ff")
        frame_info.pack(fill="x", padx=20, pady=5)

        # ID
        tk.Label(frame_info, text=f"ID: {usuario[0]}", font=("Arial", 10),
                 bg="#e6f2ff", fg="#333333", anchor="w").pack(fill="x", pady=2)

        # Nome
        tk.Label(frame_info, text=f"Nome: {usuario[1]}", font=("Arial", 10),
                 bg="#e6f2ff", fg="#333333", anchor="w").pack(fill="x", pady=2)

        # Crachá
        tk.Label(frame_info, text=f"Crachá: {usuario[2]}", font=("Arial", 10),
                 bg="#e6f2ff", fg="#333333", anchor="w").pack(fill="x", pady=2)

        # Tipo
        tk.Label(frame_info, text=f"Tipo: {usuario[3]}", font=("Arial", 10),
                 bg="#e6f2ff", fg="#333333", anchor="w").pack(fill="x", pady=2)

        # Botões
        frame_botoes = tk.Frame(janela_opcoes, bg="#e6f2ff")
        frame_botoes.pack(fill="x", padx=20, pady=15)

        # Botão Cancelar
        botao_cancelar = tk.Button(frame_botoes, text="Cancelar Solicitação", bg="#ff6666", fg="white",
                                   command=lambda: self.cancelar_solicitacao(solicitacao[0], janela_opcoes))
        botao_cancelar.pack(side=tk.RIGHT, padx=5)

        # Botão Fechar
        botao_fechar = tk.Button(frame_botoes, text="Fechar", bg="#cccccc", fg="#333333",
                                 command=janela_opcoes.destroy)
        botao_fechar.pack(side=tk.RIGHT, padx=5)

    def adicionar_usuario(self):
        nome = self.novo_nome.get()
        cracha = self.novo_cracha.get()
        senha = self.nova_senha.get()
        tipo = self.novo_tipo.get()

        # Validar campos
        if not nome or not cracha or not senha:
            messagebox.showwarning("Campos Vazios", "Por favor, preencha todos os campos.")
            return

        try:
            with DatabaseManager() as db:
                # Verificar se o crachá já existe
                if db.buscar_usuario_por_cracha(cracha):
                    messagebox.showwarning("Crachá Já Existe", "Este número de crachá já está cadastrado.")
                    return

                # Gerar hash da senha
                senha_hash = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())

                # Inserir novo usuário
                db.inserir_usuario(nome, cracha, senha_hash, tipo)
                messagebox.showinfo("Sucesso", "Usuário cadastrado com sucesso!")

                # Limpar campos
                self.novo_nome.set("")
                self.novo_cracha.set("")
                self.nova_senha.set("")
                self.novo_tipo.set("solicitante")

                # Atualizar lista
                self.carregar_usuarios()

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao cadastrar usuário: {str(e)}")

    def excluir_usuario(self, id_usuario, janela=None):
        # Confirmação
        resposta = messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir este usuário?")

        if resposta:
            try:
                with DatabaseManager() as db:
                    # Verificar se é o administrador padrão
                    if db.buscar_usuario_por_id(id_usuario)['cracha'] == '0000':
                        messagebox.showwarning("Operação Não Permitida",
                                               "Não é possível excluir o administrador padrão.")
                        return

                    db.excluir_usuario(id_usuario)
                    messagebox.showinfo("Sucesso", "Usuário excluído com sucesso!")

                    # Fechar janela se existir
                    if janela:
                        janela.destroy()

                    # Atualizar lista de usuários
                    self.carregar_usuarios()

            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao excluir usuário: {str(e)}")

    def iniciar_servidor_notificacoes(self):
        # Iniciar o servidor de notificações em uma thread separada
        self.notificacoes_ativas = True
        self.thread_notificacoes = threading.Thread(target=self.servidor_notificacoes)
        self.thread_notificacoes.daemon = True
        self.thread_notificacoes.start()

    def servidor_notificacoes(self):
        try:
            # Criar socket servidor
            self.socket_servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_servidor.bind(('localhost', self.porta_notificacao))
            self.socket_servidor.listen(5)

            # Timeout para permitir verificação de notificacoes_ativas
            self.socket_servidor.settimeout(1)

            while self.notificacoes_ativas:
                try:
                    cliente, endereco = self.socket_servidor.accept()

                    # Receber dados
                    dados = cliente.recv(1024)
                    notificacao = pickle.loads(dados)

                    # Processar notificação
                    if notificacao['tipo'] == 'nova_solicitacao':
                        self.mostrar_notificacao(notificacao)

                    cliente.close()
                except socket.timeout:
                    # Timeout normal, continuar loop
                    pass
                except Exception as e:
                    # Ignorar outros erros durante o loop
                    pass

            # Fechar socket ao finalizar
            if self.socket_servidor:
                self.socket_servidor.close()

        except Exception as e:
            # Erro ao iniciar o servidor
            pass

    def mostrar_notificacao(self, notificacao):
        # Atualizar a informação de notificação na interface
        def atualizar_notificacao():
            self.label_notificacao.config(
                text=f"Nova solicitação recebida de {notificacao['nome']} às {notificacao['data']}",
                fg="#0066cc",
                font=("Arial", 9, "bold")
            )
            # Atualizar a lista de solicitações
            self.carregar_solicitacoes()

            # Criar uma janela de notificação
            janela_notif = tk.Toplevel(self.root)
            janela_notif.title("Nova Solicitação")
            janela_notif.geometry("300x150")
            janela_notif.configure(bg="#e6f2ff")

            # Centralizar a janela
            largura_janela = 300
            altura_janela = 150
            largura_tela = self.root.winfo_screenwidth()
            altura_tela = self.root.winfo_screenheight()
            pos_x = (largura_tela // 2) - (largura_janela // 2)
            pos_y = (altura_tela // 2) - (altura_janela // 2)
            janela_notif.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

            tk.Label(janela_notif, text="Nova Solicitação Recebida!", font=("Arial", 12, "bold"),
                     bg="#e6f2ff", fg="#0066cc").pack(pady=10)

            tk.Label(janela_notif, text=f"De: {notificacao['nome']} (Crachá: {notificacao['cracha']})",
                     bg="#e6f2ff", fg="#333333").pack(pady=5)

            tk.Label(janela_notif, text=f"Data/Hora: {notificacao['data']}",
                     bg="#e6f2ff", fg="#333333").pack(pady=5)

            tk.Button(janela_notif, text="OK", command=janela_notif.destroy,
                      bg="#0066cc", fg="white", width=10).pack(pady=10)

            # Auto-fechar após 5 segundos
            janela_notif.after(5000, janela_notif.destroy)

        # Executar na thread da interface
        self.root.after(0, atualizar_notificacao)


if __name__ == "__main__":
    # Verifica se o banco de dados existe, se não, cria
    sql_path = ler_config()
    if not os.path.exists(sql_path):
        from database_setup import criar_banco_dados

        criar_banco_dados()

    root = tk.Tk()
    app = RecebimentoApp(root)
    root.mainloop()