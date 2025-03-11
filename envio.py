import sqlite3
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import datetime
import socket
import pickle
import configparser
import csv
from database_setup import DatabaseManager

# Constantes
CONFIG_FILE = 'config.ini'
PORTA_NOTIFICACAO = 5000


# Função para ler o arquivo de configuração
def ler_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config['PATH']['sql_dir']


class EnvioApp:
    def __init__(self, root):
        self.sql_path = ler_config()
        self.database_manager = DatabaseManager()
        self.database_manager.criar_banco_dados()
        self.root = root
        self.root.title("Sistema de Solicitações - Envio")
        self.root.geometry("900x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#f0f0f0")

        # Centraliza a janela
        self.centralizar_janela()

        # Variáveis para login
        self.usuario_atual = None
        self.nome_login = tk.StringVar()
        self.senha_login = tk.StringVar()

        # Variáveis para a solicitação
        self.descricao = tk.StringVar()

        # Inicia com a tela de login
        self.criar_tela_login()

    def centralizar_janela(self):
        """Centraliza a janela na tela."""
        largura_janela = 900
        altura_janela = 600
        largura_tela = self.root.winfo_screenwidth()
        altura_tela = self.root.winfo_screenheight()
        pos_x = (largura_tela // 2) - (largura_janela // 2)
        pos_y = (altura_tela // 2) - (altura_janela // 2)
        self.root.geometry(f"{largura_janela}x{altura_janela}+{pos_x}+{pos_y}")

    def criar_tela_login(self):
        """Cria a tela de login."""
        for widget in self.root.winfo_children():
            widget.destroy()

        frame_login = tk.Frame(self.root, bg="#e6f2ff", padx=20, pady=20)
        frame_login.place(relx=0.5, rely=0.5, anchor=tk.CENTER, width=400, height=300)

        # Título
        tk.Label(frame_login, text="SISTEMA DE SOLICITAÇÕES", font=("Arial", 16, "bold"),
                 bg="#e6f2ff", fg="#003366").pack(pady=10)
        tk.Label(frame_login, text="Login de Acesso", font=("Arial", 12),
                 bg="#e6f2ff", fg="#003366").pack(pady=5)

        # Campo de usuário
        frame_usuario = tk.Frame(frame_login, bg="#e6f2ff")
        frame_usuario.pack(fill="x", pady=5)
        tk.Label(frame_usuario, text="Nome:", font=("Arial", 10),
                 bg="#e6f2ff", fg="#003366", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
        tk.Entry(frame_usuario, textvariable=self.nome_login, font=("Arial", 10),
                 width=30).pack(side=tk.LEFT, padx=5)

        # Campo de senha
        frame_senha = tk.Frame(frame_login, bg="#e6f2ff")
        frame_senha.pack(fill="x", pady=5)
        tk.Label(frame_senha, text="Senha:", font=("Arial", 10),
                 bg="#e6f2ff", fg="#003366", width=10, anchor="w").pack(side=tk.LEFT, padx=5)
        tk.Entry(frame_senha, textvariable=self.senha_login, font=("Arial", 10),
                 width=30, show="*").pack(side=tk.LEFT, padx=5)

        # Botão de login
        frame_botao = tk.Frame(frame_login, bg="#e6f2ff")
        frame_botao.pack(pady=20)
        tk.Button(frame_botao, text="Entrar", font=("Arial", 10, "bold"),
                  bg="#0066cc", fg="white", padx=20, pady=5,
                  command=self.fazer_login).pack()

        # Rodapé
        tk.Label(frame_login, text="© 2025 - Sistema de Solicitações",
                 font=("Arial", 8), bg="#e6f2ff", fg="#666666").pack(side=tk.BOTTOM, pady=10)

    def fazer_login(self):
        """Realiza o login do usuário."""
        nome = self.nome_login.get()
        senha = self.senha_login.get()

        if nome and senha:
            try:
                with self.database_manager as db:
                    usuario = db.buscar_usuario(nome, senha)
                    if usuario:
                        self.usuario_atual = {
                            'id': usuario[0],
                            'nome': usuario[1],
                            'cracha': usuario[2],
                            'tipo': usuario[4]
                        }
                        self.criar_tela_solicitacao()
                    else:
                        messagebox.showerror("Erro de Login", "Usuário não encontrado ou não é um solicitante.")
            except Exception as e:
                messagebox.showerror("Erro de Banco de Dados", f"Erro ao conectar ao banco de dados: {str(e)}")
        else:
            messagebox.showwarning("Campos Vazios", "Por favor, preencha todos os campos.")

    def criar_tela_solicitacao(self):
        """Cria a tela de solicitação."""
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame do cabeçalho
        frame_cabecalho = tk.Frame(self.root, bg="#0066cc", height=60)
        frame_cabecalho.pack(fill="x")

        tk.Label(frame_cabecalho, text="SISTEMA DE SOLICITAÇÕES",
                 font=("Arial", 14, "bold"), bg="#0066cc", fg="white").pack(side=tk.LEFT, padx=20, pady=15)
        tk.Label(frame_cabecalho,
                 text=f"Usuário: {self.usuario_atual['nome']} | Crachá: {self.usuario_atual['cracha']}",
                 font=("Arial", 10), bg="#0066cc", fg="white").pack(side=tk.RIGHT, padx=20, pady=15)

        # Frame do formulário
        frame_formulario = tk.Frame(self.root, bg="#e6f2ff", padx=20, pady=20)
        frame_formulario.pack(fill="both", expand=True, padx=20, pady=20)

        tk.Label(frame_formulario, text="Nova Solicitação",
                 font=("Arial", 12, "bold"), bg="#e6f2ff", fg="#003366").pack(pady=10)

        # Dados do usuário
        frame_dados = tk.Frame(frame_formulario, bg="#e6f2ff")
        frame_dados.pack(fill="x", pady=5)

        tk.Label(frame_dados, text="Nome:", font=("Arial", 10),
                 bg="#e6f2ff", fg="#003366", width=10, anchor="w").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        entry_nome = tk.Entry(frame_dados, font=("Arial", 10), width=40)
        entry_nome.insert(0, self.usuario_atual['nome'])
        entry_nome.config(state="readonly")
        entry_nome.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        tk.Label(frame_dados, text="Crachá:", font=("Arial", 10),
                 bg="#e6f2ff", fg="#003366", width=10, anchor="w").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        entry_cracha = tk.Entry(frame_dados, font=("Arial", 10), width=15)
        entry_cracha.insert(0, self.usuario_atual['cracha'])
        entry_cracha.config(state="readonly")
        entry_cracha.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        # Frame para seleção de insumos
        frame_insumos = tk.Frame(frame_formulario, bg="#e6f2ff")
        frame_insumos.pack(fill="x", pady=10)

        tk.Label(frame_insumos, text="Insumos:", font=("Arial", 10),
                 bg="#e6f2ff", fg="#003366").pack(anchor="w", pady=5)

        # Lista de insumos disponíveis
        self.lista_insumos = ttk.Combobox(frame_insumos, font=("Arial", 10), width=30)
        self.lista_insumos.pack(side=tk.LEFT, padx=5)

        # Campo para quantidade
        self.quantidade_insumo = tk.Entry(frame_insumos, font=("Arial", 10), width=10)
        self.quantidade_insumo.pack(side=tk.LEFT, padx=5)

        # Botão para adicionar insumo
        botao_adicionar_insumo = tk.Button(frame_insumos, text="Adicionar Insumo",
                                           font=("Arial", 9), bg="#0066cc", fg="white",
                                           command=self.adicionar_insumo_a_solicitacao)
        botao_adicionar_insumo.pack(side=tk.LEFT, padx=5)

        # Lista de insumos adicionados
        self.lista_insumos_adicionados = tk.Listbox(frame_insumos, font=("Arial", 10), height=5)
        self.lista_insumos_adicionados.pack(fill="x", pady=5)

        # Carregar insumos disponíveis
        self.carregar_insumos_disponiveis()

        # Campo de descrição
        frame_descricao = tk.Frame(frame_formulario, bg="#e6f2ff")
        frame_descricao.pack(fill="x", pady=10)

        tk.Label(frame_descricao, text="Descrição da Solicitação:",
                 font=("Arial", 10), bg="#e6f2ff", fg="#003366").pack(anchor="w", pady=5)
        self.texto_descricao = tk.Text(frame_descricao, font=("Arial", 10), height=6, width=50)
        self.texto_descricao.pack(fill="x", pady=5)

        # Rótulo de status
        self.rotulo_status = tk.Label(frame_formulario, text="", font=("Arial", 10), bg="#e6f2ff", fg="#ff0000")
        self.rotulo_status.pack(pady=5)

        # Botões
        frame_botoes = tk.Frame(frame_formulario, bg="#e6f2ff")
        frame_botoes.pack(fill="x", pady=15)

        tk.Button(frame_botoes, text="Enviar Solicitação",
                  font=("Arial", 10, "bold"), bg="#0066cc", fg="white",
                  padx=15, pady=5,
                  command=lambda: self.enviar_solicitacao(self.texto_descricao.get("1.0", "end-1c"))).pack(side=tk.RIGHT,
                                                                                                      padx=5)
        tk.Button(frame_botoes, text="Limpar",
                  font=("Arial", 10), bg="#cccccc", fg="#333333",
                  padx=15, pady=5,
                  command=lambda: self.texto_descricao.delete("1.0", "end")).pack(side=tk.RIGHT, padx=5)
        tk.Button(frame_botoes, text="Ver Status",
                  font=("Arial", 10), bg="#009933", fg="white",
                  padx=15, pady=5,
                  command=self.criar_tela_status).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_botoes, text="Sair",
                  font=("Arial", 10), bg="#ff6666", fg="white",
                  padx=15, pady=5,
                  command=self.criar_tela_login).pack(side=tk.LEFT, padx=5)

    def criar_tela_status(self):
        """Cria a tela de status das solicitações com barra de rolagem."""
        for widget in self.root.winfo_children():
            widget.destroy()

        # Frame do cabeçalho
        frame_cabecalho = tk.Frame(self.root, bg="#0066cc", height=60)
        frame_cabecalho.pack(fill="x")

        tk.Label(frame_cabecalho, text="SISTEMA DE SOLICITAÇÕES",
                 font=("Arial", 14, "bold"), bg="#0066cc", fg="white").pack(side=tk.LEFT, padx=20, pady=15)
        tk.Label(frame_cabecalho,
                 text=f"Usuário: {self.usuario_atual['nome']} | Crachá: {self.usuario_atual['cracha']}",
                 font=("Arial", 10), bg="#0066cc", fg="white").pack(side=tk.RIGHT, padx=20, pady=15)

        # Frame principal para a lista de solicitações e barra de rolagem
        frame_principal = tk.Frame(self.root, bg="#e6f2ff")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)

        # Canvas para conter a lista de solicitações
        canvas = tk.Canvas(frame_principal, bg="#e6f2ff", highlightthickness=0)
        canvas.pack(side="left", fill="both", expand=True)

        # Barra de rolagem vertical
        scrollbar = tk.Scrollbar(frame_principal, orient="vertical", command=canvas.yview)
        scrollbar.pack(side="right", fill="y")

        # Configurar o canvas para usar a barra de rolagem
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # Frame interno para conter os widgets da lista de solicitações
        frame_lista = tk.Frame(canvas, bg="#e6f2ff")
        canvas.create_window((0, 0), window=frame_lista, anchor="nw")

        tk.Label(frame_lista, text="Status das Solicitações",
                 font=("Arial", 12, "bold"), bg="#e6f2ff", fg="#003366").pack(pady=10)

        # Lista de solicitações
        try:
            with self.database_manager as db:
                solicitacoes = db.buscar_solicitacoes_por_usuario(self.usuario_atual['id'])

            if solicitacoes:
                for solicitacao in solicitacoes:
                    frame_solicitacao = tk.Frame(frame_lista, bg="#e6f2ff", padx=10, pady=10)
                    frame_solicitacao.pack(fill="x", pady=5)

                    tk.Label(frame_solicitacao, text=f"Data/Hora Solicitação: {solicitacao[4]}",
                             font=("Arial", 10), bg="#e6f2ff", fg="#003366").pack(anchor="w")
                    tk.Label(frame_solicitacao, text=f"Descrição: {solicitacao[3]}",
                             font=("Arial", 10), bg="#e6f2ff", fg="#003366").pack(anchor="w")

                    # Busca os insumos associados à solicitação
                    with self.database_manager as db:
                        insumos = db.buscar_insumos_por_solicitacao(solicitacao[0])
                        if insumos:
                            for insumo in insumos:
                                tk.Label(frame_solicitacao, text=f"Insumo: {insumo[1]} - Quantidade: {insumo[3]}",
                                         font=("Arial", 10), bg="#e6f2ff", fg="#003366").pack(anchor="w")

                    # Define a cor do status com base no valor
                    status = solicitacao[5].lower()
                    if status == "pago":
                        cor_status = "green"
                    elif status == "em análise":
                        cor_status = "blue"
                    elif status == "pendente":
                        cor_status = "orange"
                    elif status == "cancelado":
                        cor_status = "red"
                    else:
                        cor_status = "black"

                    tk.Label(frame_solicitacao, text=f"Status: {solicitacao[5]}",
                             font=("Arial", 10, "bold"), bg="#e6f2ff", fg=cor_status).pack(anchor="w")
            else:
                tk.Label(frame_lista, text="Nenhuma solicitação encontrada.",
                         font=("Arial", 10), bg="#e6f2ff", fg="#003366").pack(pady=10)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao buscar solicitações: {str(e)}")

        # Botões
        frame_botoes = tk.Frame(self.root, bg="#e6f2ff", padx=20, pady=10)
        frame_botoes.pack(fill="x", pady=10)

        tk.Button(frame_botoes, text="Gerar Relatório",
                  font=("Arial", 10), bg="#009933", fg="white",
                  padx=15, pady=5,
                  command=self.gerar_relatorio).pack(side="left", padx=5)

        # Botão de atualizar
        botao_atualizar = tk.Button(frame_botoes, text="Atualizar Lista",
                                    font=("Arial", 10), bg="#0066cc", fg="white",
                                    padx=15, pady=5,
                                    command=self.criar_tela_status)  # Chama o método criar_tela_status novamente
        botao_atualizar.pack(side="left", padx=5)

        tk.Button(frame_botoes, text="Voltar",
                  font=("Arial", 10), bg="#cccccc", fg="#333333",
                  padx=15, pady=5,
                  command=self.criar_tela_solicitacao).pack(side="right", padx=5)

    def carregar_insumos_disponiveis(self):
        """Carrega os insumos disponíveis no combobox."""
        with DatabaseManager() as db:
            insumos = db.buscar_insumos()
            self.lista_insumos['values'] = [f"{i[1]} - {i[2]}" for i in insumos]

    def adicionar_insumo_a_solicitacao(self):
        """Adiciona um insumo à lista de insumos da solicitação."""
        insumo_selecionado = self.lista_insumos.get()
        quantidade = self.quantidade_insumo.get()

        if insumo_selecionado and quantidade:
            cod_sap = insumo_selecionado.split(" - ")[0]
            with DatabaseManager() as db:
                insumo = db.buscar_insumo_por_cod_sap(cod_sap)
                if insumo:
                    self.lista_insumos_adicionados.insert(tk.END, f"{insumo[2]} - Quantidade: {quantidade}")
                    self.quantidade_insumo.delete(0, tk.END)
                else:
                    messagebox.showwarning("Insumo não encontrado", "Insumo não encontrado no banco de dados.")
        else:
            messagebox.showwarning("Campos Vazios", "Selecione um insumo e insira a quantidade.")

    def gerar_relatorio(self):
        """Gera um relatório das solicitações do usuário em formato CSV, incluindo insumos."""
        try:
            with self.database_manager as db:
                solicitacoes = db.buscar_solicitacoes_por_usuario(self.usuario_atual['id'])

            if solicitacoes:
                arquivo = filedialog.asksaveasfilename(defaultextension=".csv",
                                                       filetypes=[("Arquivos CSV", "*.csv"),
                                                                  ("Todos os Arquivos", "*.*")])
                if arquivo:
                    with open(arquivo, mode="w", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        # Escreve o cabeçalho
                        writer.writerow(["Data", "Descrição", "Status", "Insumos"])

                        # Escreve as solicitações
                        for solicitacao in solicitacoes:
                            with self.database_manager as db:
                                insumos = db.buscar_insumos_por_solicitacao(solicitacao[0])
                                insumos_str = ", ".join([f"{i[1]} ({i[3]})" for i in insumos]) if insumos else "Nenhum"
                            writer.writerow([solicitacao[4], solicitacao[3], solicitacao[5], insumos_str])

                    messagebox.showinfo("Sucesso", "Relatório gerado com sucesso!")
            else:
                messagebox.showwarning("Sem Dados", "Nenhuma solicitação encontrada para gerar relatório.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar relatório: {str(e)}")

    def enviar_solicitacao(self, descricao):
        """Envia uma nova solicitação com insumos."""
        if not descricao.strip():
            messagebox.showwarning("Campo Vazio", "Por favor, preencha a descrição da solicitação.")
            return

        try:
            data_atual = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            with self.database_manager as db:
                # Insere a solicitação no banco de dados
                db.inserir_solicitacao(self.usuario_atual['nome'], self.usuario_atual['cracha'],
                                       descricao, data_atual, 'pendente')

                # Obtém o ID da última solicitação inserida
                solicitacao_id = db.cursor.lastrowid

                # Adiciona os insumos à solicitação
                for item in self.lista_insumos_adicionados.get(0, tk.END):
                    insumo_info = item.split(" - Quantidade: ")
                    insumo_nome = insumo_info[0]
                    quantidade = int(insumo_info[1])

                    # Busca o ID do insumo pelo nome
                    insumo = db.buscar_insumo_por_nome(insumo_nome)
                    if insumo:
                        db.adicionar_insumo_a_solicitacao(solicitacao_id, insumo[0], quantidade)

            self.enviar_notificacao()
            messagebox.showinfo("Sucesso", "Solicitação enviada com sucesso!")
            # Limpa a lista de insumos adicionados
            self.lista_insumos_adicionados.delete(0, tk.END)
            self.criar_tela_solicitacao()
        except sqlite3.Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao acessar ao banco de dados: {str(e)}")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro inesperado: {str(e)}")

    def enviar_notificacao(self):
        """Envia uma notificação via socket."""
        try:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.connect(('localhost', PORTA_NOTIFICACAO))

            mensagem = {
                'tipo': 'nova_solicitacao',
                'nome': self.usuario_atual['nome'],
                'cracha': self.usuario_atual['cracha'],
                'data': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            cliente.send(pickle.dumps(mensagem))
            cliente.close()
        except:
            pass


if __name__ == "__main__":
    root = tk.Tk()
    app = EnvioApp(root)
    root.mainloop()