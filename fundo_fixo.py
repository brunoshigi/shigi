import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3

# Configurações da aplicação
APPEARANCE_MODE = "Dark"
COLOR_THEME = "blue"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
DB_PATH = "austral.db"
FONT = {"family": "Arial", "size": {"title": 16, "subtitle": 14}}
CORES = {
    "bg_primary": "#2b2b2b",
    "bg_secondary": "#333333",
    "text_primary": "#ffffff"
}

def criar_tabelas(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS config_fundo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            valor_fundo REAL NOT NULL,
            depositos_pendentes REAL NOT NULL,
            reposicoes_pendentes REAL NOT NULL,
            ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data TEXT NOT NULL,
            tipo TEXT NOT NULL,
            valor REAL NOT NULL,
            responsavel TEXT,
            descricao TEXT,
            saldo REAL NOT NULL
        )
    """)

class GestorFundoFixo(ctk.CTk):
    def __init__(self):
        super().__init__()  # Agora herda de CTk, a janela principal
        
        # Configurações da janela
        self.title("Fundo Fixo - Saldo Real em Caixa")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)

        # Centralizar em relação à tela
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

        # Configuração do tema do CustomTkinter
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

        # Inicialização de variáveis
        self.saldo = 1000.00
        self.root = self  # Agora 'root' é a própria instância da janela principal

        # Conecta ao banco de dados e carrega dados existentes
        self.conectar_banco()
        self.carregar_dados()

        # Frame principal que conterá todos os elementos
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=CORES["bg_primary"]
        )
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Criação dos componentes principais
        self.criar_painel_info(self.main_frame)
        self.criar_area_movimentacao(self.main_frame)
        self.criar_lista_movimentacoes(self.main_frame)
        self.criar_botao_resumo_periodo(self.main_frame)

    def conectar_banco(self):
        """Conecta ao banco e cria tabela se necessário."""
        self.conn = sqlite3.connect(DB_PATH)
        cursor = self.conn.cursor()
        criar_tabelas(cursor)
        self.conn.commit()

    def carregar_dados(self):
        """Carrega dados do banco."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT valor_fundo, depositos_pendentes, reposicoes_pendentes 
            FROM config_fundo 
            ORDER BY id DESC LIMIT 1
        """)
        cfg = cursor.fetchone()
        if cfg:
            self.dados = {
                "valor_fundo": cfg[0],
                "saldo_atual": cfg[0],  # Inicia com valor_fundo se não houver movimentações
                "depositos_pendentes": cfg[1],
                "reposicoes_pendentes": cfg[2],
                "movimentacoes": []
            }
        else:
            # Insere configuração padrão no banco se não existir
            cursor.execute("""
                INSERT INTO config_fundo (valor_fundo, depositos_pendentes, reposicoes_pendentes)
                VALUES (?, ?, ?)
            """, (1000.00, 0.00, 0.00))
            self.conn.commit()
            self.dados = {
                "valor_fundo": 1000.00,
                "saldo_atual": 1000.00,
                "depositos_pendentes": 0.00,
                "reposicoes_pendentes": 0.00,
                "movimentacoes": []
            }
        
        # Carrega movimentações existentes
        cursor.execute("""
            SELECT data, tipo, valor, responsavel, descricao, saldo 
            FROM movimentacoes 
            ORDER BY id ASC
        """)
        movs = cursor.fetchall()
        for row in movs:
            self.dados["movimentacoes"].append({
                "data": row[0],
                "tipo": row[1],
                "valor": row[2],
                "responsavel": row[3],
                "descricao": row[4],
                "saldo": row[5]
            })
        self.after(100, self.atualizar_interface)

    def salvar_dados(self):
        """Salva dados atuais no banco."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE config_fundo
            SET valor_fundo = ?,
                depositos_pendentes = ?,
                reposicoes_pendentes = ?,
                ultima_atualizacao = CURRENT_TIMESTAMP
            WHERE id = (SELECT id FROM config_fundo ORDER BY id DESC LIMIT 1)
        """, (
            self.dados["valor_fundo"],
            self.dados["depositos_pendentes"],
            self.dados["reposicoes_pendentes"]
        ))
        self.conn.commit()

    def criar_painel_info(self, parent):
        """
        Cria o painel superior que mostra as informações principais:
        valor do fundo, saldo atual e valores pendentes.
        """
        self.info_frame = ctk.CTkFrame(parent, fg_color=CORES["bg_secondary"])
        self.info_frame.pack(fill="x", pady=(0, 10))

        titulo_label = ctk.CTkLabel(
            self.info_frame,
            text="Informações do Fundo Fixo",
            font=(FONT["family"], FONT["size"]["title"]),
            text_color=CORES["text_primary"]
        )
        titulo_label.pack(pady=5)

        # Linha superior com valor do fundo e saldo atual
        linha1 = ctk.CTkFrame(self.info_frame)
        linha1.pack(fill="x", pady=5)

        self.label_valor_fundo = ctk.CTkLabel(
            linha1,
            text="Valor do Fundo:",
            font=("Arial", 14, "bold")
        )
        self.label_valor_fundo.pack(side="left", expand=True)

        self.label_saldo_atual = ctk.CTkLabel(
            linha1,
            text="Saldo Atual:",
            font=("Arial", 14, "bold")
        )
        self.label_saldo_atual.pack(side="left", expand=True)

        # Linha inferior com depósitos e reposições pendentes
        linha2 = ctk.CTkFrame(self.info_frame)
        linha2.pack(fill="x", pady=5)

        self.label_depositos = ctk.CTkLabel(
            linha2,
            text="Depósitos Pendentes: R$ 0.00",
            font=("Arial", 13)
        )
        self.label_depositos.pack(side="left", expand=True)

        self.label_reposicoes = ctk.CTkLabel(
            linha2,
            text="Reposições Pendentes: R$ 0.00",
            font=("Arial", 13)
        )
        self.label_reposicoes.pack(side="left", expand=True)

    def criar_area_movimentacao(self, parent):
        """
        Cria a área onde são registradas as movimentações,
        com campos para tipo, valor, responsável e descrição.
        """
        self.mov_frame = ctk.CTkFrame(
            parent,
            fg_color=CORES["bg_secondary"]
        )
        self.mov_frame.pack(fill="x", pady=(0, 10))

        mov_titulo = ctk.CTkLabel(
            self.mov_frame,
            text="Registrar Movimentação",
            font=(FONT["family"], FONT["size"]["subtitle"]),
            text_color=CORES["text_primary"]
        )
        mov_titulo.pack(pady=5)

        linha_mov = ctk.CTkFrame(self.mov_frame)
        linha_mov.pack(fill="x", padx=5, pady=5)

        # Tipo de movimentação (Entrada/Saída)
        label_tipo = ctk.CTkLabel(linha_mov, text="Tipo:")
        label_tipo.pack(side="left", padx=(0, 5))

        self.tipo_var = tk.StringVar(value="Entrada")
        self.tipo_om = ctk.CTkOptionMenu(
            linha_mov,
            values=["Entrada", "Saída"],
            variable=self.tipo_var,
            width=100
        )
        self.tipo_om.pack(side="left", padx=(0, 15))

        # Campo de valor
        label_valor = ctk.CTkLabel(linha_mov, text="Valor R$:") 
        label_valor.pack(side="left", padx=(0, 5))

        self.valor_var = tk.StringVar()
        self.valor_entry = ctk.CTkEntry(
            linha_mov,
            textvariable=self.valor_var,
            width=100
        )
        self.valor_entry.pack(side="left", padx=(0, 15))

        # Campo de responsável
        label_resp = ctk.CTkLabel(linha_mov, text="Responsável:")
        label_resp.pack(side="left", expand=True)

        self.resp_var = tk.StringVar()
        self.resp_entry = ctk.CTkEntry(
            linha_mov,
            textvariable=self.resp_var,
            width=120
        )
        self.resp_entry.pack(side="left", expand=True)

        # Campo de descrição
        label_desc = ctk.CTkLabel(linha_mov, text="Descrição:")
        label_desc.pack(side="left", expand=True)

        self.desc_var = tk.StringVar()
        self.desc_entry = ctk.CTkEntry(
            linha_mov,
            textvariable=self.desc_var,
            width=200
        )
        self.desc_entry.pack(side="left", expand=True)

        # Botão de registrar
        registrar_btn = ctk.CTkButton(
            linha_mov,
            text="Registrar",
            command=self.registrar_movimentacao
        )
        registrar_btn.pack(side="left", padx=(0, 5))

    def criar_lista_movimentacoes(self, parent):
        """
        Cria a área que mostra o histórico de movimentações
        em formato de tabela.
        """
        self.lista_frame = ctk.CTkFrame(parent)
        self.lista_frame.pack(fill="both", expand=True)

        lista_titulo = ctk.CTkLabel(
            self.lista_frame,
            text="Histórico de Movimentações",
            font=("Arial", 15, "bold")
        )
        lista_titulo.pack(pady=5)

        tv_frame = ctk.CTkFrame(self.lista_frame)
        tv_frame.pack(fill="both", expand=True)

        # Configuração da tabela
        self.tree = ttk.Treeview(
            tv_frame,
            columns=("data", "tipo", "valor", "responsavel", "descricao", "saldo"),
            show="headings",
            selectmode="browse"
        )
        
        # Configuração das colunas
        self.tree.heading("data", text="Data/Hora")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("valor", text="Valor")
        self.tree.heading("responsavel", text="Responsável")
        self.tree.heading("descricao", text="Descrição")
        self.tree.heading("saldo", text="Saldo")

        # Largura das colunas
        self.tree.column("data", width=140)
        self.tree.column("tipo", width=70)
        self.tree.column("valor", width=90)
        self.tree.column("responsavel", width=110)
        self.tree.column("descricao", width=220)
        self.tree.column("saldo", width=90)

        # Adiciona barra de rolagem
        vsb = ttk.Scrollbar(tv_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

        # Menu de contexto para editar/excluir
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(
            label="Excluir Movimentação",
            command=self.excluir_movimentacao
        )
        self.context_menu.add_command(
            label="Editar Descrição",
            command=self.editar_descricao
        )
        self.tree.bind("<Button-3>", self.mostrar_menu_contexto)

    def mostrar_menu_contexto(self, event):
        """
        Exibe o menu de contexto ao clicar com botão direito
        em uma movimentação.
        """
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def criar_botao_resumo_periodo(self, parent):
        """
        Cria o botão para gerar relatório de resumo por período.
        """
        resumo_frame = ctk.CTkFrame(parent)
        resumo_frame.pack(fill="x", pady=10)

        btn_resumo = ctk.CTkButton(
            resumo_frame,
            text="Resumo por Período",
            command=self.mostrar_resumo_periodo
        )
        btn_resumo.pack(pady=5)

    def logica_entrada(self, valor):
        """
        Aplica a lógica de entrada de dinheiro mantendo o controle do saldo real.
        """
        # 1) Se houver reposições pendentes, abate primeiro
        if self.dados["reposicoes_pendentes"] > 0:
            if valor >= self.dados["reposicoes_pendentes"]:
                valor -= self.dados["reposicoes_pendentes"]
                self.dados["reposicoes_pendentes"] = 0.0
            else:
                self.dados["reposicoes_pendentes"] -= valor
                valor = 0.0
    
        # 2) Sempre atualiza o saldo real primeiro
        self.dados["saldo_atual"] += valor
        
        # 3) Se o saldo ficou acima do valor do fundo, adiciona a diferença em depósitos pendentes
        if self.dados["saldo_atual"] > self.dados["valor_fundo"]:
            excesso = self.dados["saldo_atual"] - self.dados["valor_fundo"]
            self.dados["depositos_pendentes"] += excesso

    def logica_saida(self, valor):
        """
        Aplica a lógica de saída de dinheiro mantendo o fundo fixo constante.
        """
        # 1) Primeiro tenta abater de depósitos pendentes
        if self.dados["depositos_pendentes"] > 0:
            if valor <= self.dados["depositos_pendentes"]:
                self.dados["depositos_pendentes"] -= valor
                return  # Não afeta o saldo do fundo
            else:
                valor -= self.dados["depositos_pendentes"]
                self.dados["depositos_pendentes"] = 0.0
        
        # 2) Se ainda há valor para saída, subtrai do saldo
        self.dados["saldo_atual"] -= valor
        
        # 3) Se o saldo ficou abaixo do fundo fixo, registra como reposição pendente
        if self.dados["saldo_atual"] < self.dados["valor_fundo"]:
            falta = self.dados["valor_fundo"] - self.dados["saldo_atual"]
            self.dados["reposicoes_pendentes"] += falta

    def registrar_movimentacao(self):
        """
        Registra uma nova movimentação no sistema.
        """
        try:
            tipo = self.tipo_var.get()
            valor = float(self.valor_var.get().replace(',', '.'))
            responsavel = self.resp_var.get().strip()
            descricao = self.desc_var.get().strip()

            if valor <= 0:
                raise ValueError("O valor deve ser maior que zero")

            if tipo == "Entrada":
                self.logica_entrada(valor)
            else:
                self.logica_saida(valor)

            # Registra a movimentação
            movimentacao = {
                "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "tipo": tipo,
                "valor": valor,
                "responsavel": responsavel,
                "descricao": descricao,
                "saldo": self.dados["saldo_atual"]
            }
            self.dados["movimentacoes"].append(movimentacao)

            # Salva a movimentação no banco de dados
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO movimentacoes(data, tipo, valor, responsavel, descricao, saldo)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                movimentacao["data"], tipo, valor, responsavel, descricao, self.dados["saldo_atual"]
            ))
            self.conn.commit()

            # Salva os dados e atualiza a interface
            self.salvar_dados()
            self.atualizar_interface()
            self.limpar_campos()

        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def mostrar_resumo_periodo(self):
        """
        Abre uma janela para o usuário selecionar o período
        do qual deseja ver o resumo das movimentações.
        """
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Resumo por Período")
        dialog.geometry("400x300")

        # Instruções para o usuário
        instr_label = ctk.CTkLabel(
            dialog,
            text="Digite as datas no formato dd/mm/yyyy",
            font=("Arial", 14)
        )
        instr_label.pack(pady=5)

        # Frame para os campos de data
        frame_datas = ctk.CTkFrame(dialog)
        frame_datas.pack(pady=5)

        # Campo de data inicial
        ctk.CTkLabel(frame_datas, text="Data Inicial:").grid(
            row=0, column=0, padx=5, pady=5
        )
        data_inicial_var = tk.StringVar()
        data_inicial_entry = ctk.CTkEntry(
            frame_datas,
            textvariable=data_inicial_var,
            width=110
        )
        data_inicial_entry.grid(row=0, column=1, padx=5, pady=5)

        # Campo de data final
        ctk.CTkLabel(frame_datas, text="Data Final:").grid(
            row=0, column=2, padx=5, pady=5
        )
        data_final_var = tk.StringVar()
        data_final_entry = ctk.CTkEntry(
            frame_datas,
            textvariable=data_final_var,
            width=110
        )
        data_final_entry.grid(row=0, column=3, padx=5, pady=5)

        # Função interna para processar as datas e gerar o resumo
        def gerar_resumo():
            di = data_inicial_var.get().strip()
            df = data_final_var.get().strip()
            self.gerar_resumo_periodo(dialog, di, df)

        # Botão para gerar o resumo
        gerar_btn = ctk.CTkButton(
            dialog,
            text="Gerar Resumo",
            command=gerar_resumo
        )
        gerar_btn.pack(pady=5)

    def gerar_resumo_periodo(self, parent_dialog, data_ini_str, data_fim_str):
        """
        Gera um relatório detalhado das movimentações no período especificado.
        """
        try:
            # Converte as strings de data para objetos datetime
            formato = "%d/%m/%Y"
            data_ini = datetime.strptime(data_ini_str, formato).date()
            data_fim = datetime.strptime(data_fim_str, formato).date()

            # Filtra as movimentações do período
            movs_periodo = []
            for mov in self.dados["movimentacoes"]:
                dt = datetime.strptime(mov["data"], "%d/%m/%Y %H:%M").date()
                if data_ini <= dt <= data_fim:
                    movs_periodo.append(mov)

            # Calcula totais
            total_entrada = sum(m["valor"] for m in movs_periodo if m["tipo"] == "Entrada")
            total_saida = sum(m["valor"] for m in movs_periodo if m["tipo"] == "Saída")

            # Cria uma nova janela para mostrar o resumo
            resumo_toplevel = ctk.CTkToplevel(parent_dialog)
            resumo_toplevel.title("Resumo do Período")
            resumo_toplevel.geometry("400x400")

            # Área de texto para o relatório
            text_box = tk.Text(resumo_toplevel, height=20, width=50)
            text_box.pack(padx=10, pady=10, fill="both", expand=True)

            # Insere as informações no relatório
            text_box.insert("end", f"RESUMO DE {data_ini_str} ATÉ {data_fim_str}\n\n")
            text_box.insert("end", f"Quantidade de Movimentações: {len(movs_periodo)}\n")
            text_box.insert("end", f"Total Entradas: R$ {total_entrada:.2f}\n")
            text_box.insert("end", f"Total Saídas:   R$ {total_saida:.2f}\n\n")

            text_box.insert("end", "MOVIMENTAÇÕES:\n\n")
            for mov in movs_periodo:
                text_box.insert(
                    "end",
                    f"- {mov['data']} | {mov['tipo']} | R${mov['valor']:.2f} | "
                    f"{mov.get('responsavel','')} | {mov['descricao']}\n"
                )

            # Desabilita a edição do texto
            text_box.configure(state="disabled")

        except ValueError:
            messagebox.showerror(
                "Erro",
                "Datas inválidas! Use o formato dd/mm/yyyy."
            )

    def excluir_movimentacao(self):
        """
        Remove uma movimentação selecionada e recalcula os saldos.
        """
        selecionado = self.tree.selection()
        if not selecionado:
            return

        if messagebox.askyesno(
            "Confirmar",
            "Deseja realmente excluir esta movimentação?"
        ):
            item = selecionado[0]
            # O índice na lista é invertido em relação à exibição
            idx = len(self.dados["movimentacoes"]) - self.tree.index(item) - 1
            
            self.dados["movimentacoes"].pop(idx)
            # Exclui do banco (busca movimento pela ordem inserida)
            cursor = self.conn.cursor()
            cursor.execute("SELECT id FROM movimentacoes ORDER BY id ASC")
            all_ids = [x[0] for x in cursor.fetchall()]
            if idx < len(all_ids):
                registro_id = all_ids[idx]
                cursor.execute("DELETE FROM movimentacoes WHERE id = ?", (registro_id,))
                self.conn.commit()
            self.recalcular_saldos()
            self.salvar_dados()
            self.atualizar_interface()

    def editar_descricao(self):
        """
        Permite editar a descrição de uma movimentação selecionada.
        """
        selecionado = self.tree.selection()
        if not selecionado:
            return

        item = selecionado[0]
        idx = len(self.dados["movimentacoes"]) - self.tree.index(item) - 1

        # Cria uma janela para edição
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Editar Descrição")
        dialog.geometry("400x150")

        ctk.CTkLabel(dialog, text="Nova descrição:").pack(pady=5)

        nova_desc_var = tk.StringVar(
            value=self.dados["movimentacoes"][idx]["descricao"]
        )
        entry_desc = ctk.CTkEntry(dialog, textvariable=nova_desc_var, width=300)
        entry_desc.pack(pady=5)

        def salvar():
            self.dados["movimentacoes"][idx]["descricao"] = nova_desc_var.get().strip()
            self.salvar_dados()
            self.atualizar_interface()
            dialog.destroy()

        ctk.CTkButton(dialog, text="Salvar", command=salvar).pack(pady=5)

    def recalcular_saldos(self):
        """
        Recalcula todos os saldos e valores pendentes após modificações.
        """
        # Reinicia os valores para o padrão
        self.dados["saldo_atual"] = self.dados["valor_fundo"]
        self.dados["depositos_pendentes"] = 0.0
        self.dados["reposicoes_pendentes"] = 0.0

        # Recalcula cada movimentação
        for mov in self.dados["movimentacoes"]:
            tipo = mov["tipo"]
            valor = mov["valor"]
            
            if tipo == "Entrada":
                self.logica_entrada(valor)
            else:  # "Saída"
                self.logica_saida(valor)

            mov["saldo"] = self.dados["saldo_atual"]

    def atualizar_interface(self):
        """
        Atualiza todos os elementos visuais da interface.
        """
        # Atualiza os labels de informação
        self.label_valor_fundo.configure(
            text=f"Valor do Fundo: R$ {self.dados['valor_fundo']:.2f}"
        )
        self.label_saldo_atual.configure(
            text=f"Saldo Atual: R$ {self.dados['saldo_atual']:.2f}"
        )
        self.label_depositos.configure(
            text=f"Depósitos Pendentes: R$ {self.dados['depositos_pendentes']:.2f}"
        )
        self.label_reposicoes.configure(
            text=f"Reposições Pendentes: R$ {self.dados['reposicoes_pendentes']:.2f}"
        )
        
        # Atualiza a lista de movimentações
        self.atualizar_lista_movimentacoes()

    def atualizar_lista_movimentacoes(self):
        """
        Atualiza a tabela de movimentações com os dados mais recentes.
        """
        # Limpa a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insere as movimentações na ordem reversa (mais recente no topo)
        for mov in reversed(self.dados["movimentacoes"]):
            self.tree.insert(
                "",
                "end",
                values=(
                    mov["data"],
                    mov["tipo"],
                    f"R$ {mov['valor']:.2f}",
                    mov.get("responsavel", ""),
                    mov["descricao"],
                    f"R$ {mov['saldo']:.2f}"
                )
            )

    def limpar_campos(self):
        """
        Limpa os campos de entrada após registrar uma movimentação.
        """
        self.valor_var.set("")
        self.resp_var.set("")
        self.desc_var.set("")
        self.tipo_var.set("Entrada")

    def run(self):
        self.mainloop()

if __name__ == "__main__":
    app = GestorFundoFixo()
    app.run()
