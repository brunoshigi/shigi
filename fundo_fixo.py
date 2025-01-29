import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sqlite3
import os

# Configurações iniciais
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Configuração dos caminhos
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)
DB_PATH = os.path.join(ASSETS_DIR, "austral.db")

class GestorFundoFixo(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da janela principal
        self.title("SISTEMA AUSTRAL - FUNDO FIXO")
        self.geometry("1400x780")
        self.center_window()
        self.resizable(False, False)
        self.configure(fg_color="#0F0F0F")

        # Inicializações
        self.dados = {
            "valor_fundo": 1000.00,
            "saldo_atual": 1000.00,
            "depositos_pendentes": 0.00,
            "reposicoes_pendentes": 0.00,
            "movimentacoes": []
        }

        # Conecta ao banco e cria interface
        self.conectar_banco()
        self.carregar_dados()
        self.criar_interface()

    def center_window(self):
        """Centraliza a janela na tela"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 1400) // 2
        y = (screen_height - 720) // 2
        self.geometry(f"+{x}+{y}")

    def criar_interface(self):
        """Cria a interface principal"""
        # Frame principal com padding ajustado
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="black")
        self.main_frame.pack(padx=10, pady=(10, 15), fill="both", expand=True)

        # Container para conteúdo principal (tudo exceto footer)
        self.content_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.content_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

        # Cabeçalho
        ctk.CTkLabel(
            self.content_frame,
            text="CONTROLE DE FUNDO FIXO",
            font=("Helvetica", 20, "bold")
        ).pack(pady=(5, 10))

        # Área de informações
        self.criar_area_info()

        # Área de movimentação
        self.criar_area_movimentacao()

        # Lista de movimentações
        self.criar_lista_movimentacoes()

        # Rodapé (agora fora do content_frame)
        self.criar_footer()

    def criar_area_info(self):
        """Cria área de informações do fundo"""
        info_frame = ctk.CTkFrame(self.content_frame, fg_color="#1A1A1A")
        info_frame.pack(fill="x", padx=20, pady=10)

        # Botão para configurar valor do fundo
        config_btn = ctk.CTkButton(
            info_frame,
            text="CONFIGURAR VALOR DO FUNDO",
            command=self.configurar_valor_fundo,
            width=200,
            fg_color="#4B0082",  # Cor índigo
            hover_color="#483D8B"
        )
        config_btn.pack(pady=5)

        # Grid para informações
        grid = ctk.CTkFrame(info_frame, fg_color="transparent")
        grid.pack(pady=10)

        # Primeira linha
        self.label_valor_fundo = ctk.CTkLabel(
            grid,
            text="VALOR DO FUNDO",
            font=("Helvetica", 14, "bold")
        )
        self.label_valor_fundo.grid(row=0, column=0, padx=20)

        self.label_saldo_atual = ctk.CTkLabel(
            grid,
            text="SALDO ATUAL",
            font=("Helvetica", 14, "bold")
        )
        self.label_saldo_atual.grid(row=0, column=1, padx=20)

        # Segunda linha
        self.label_depositos = ctk.CTkLabel(
            grid,
            text="DEPÓSITOS PENDENTES",
            font=("Helvetica", 12)
        )
        self.label_depositos.grid(row=1, column=0, padx=20, pady=10)

        self.label_reposicoes = ctk.CTkLabel(
            grid,
            text="REPOSIÇÕES PENDENTES",
            font=("Helvetica", 12)
        )
        self.label_reposicoes.grid(row=1, column=1, padx=20, pady=10)

    def criar_area_movimentacao(self):
        """Cria área de registro de movimentações"""
        mov_frame = ctk.CTkFrame(self.content_frame, fg_color="#1A1A1A")
        mov_frame.pack(fill="x", padx=20, pady=10)

        # Form frame
        form_frame = ctk.CTkFrame(mov_frame, fg_color="transparent")
        form_frame.pack(pady=10, padx=20)

        # Campos de entrada
        # Tipo de movimentação
        ctk.CTkLabel(form_frame, text="TIPO:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.tipo_var = tk.StringVar(value="Entrada")
        self.tipo_om = ctk.CTkOptionMenu(
            form_frame,
            values=["Entrada", "Saída"],
            variable=self.tipo_var,
            width=150
        )
        self.tipo_om.grid(row=0, column=1, sticky="w", padx=5, pady=5)

        # Valor
        ctk.CTkLabel(form_frame, text="VALOR R$:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.valor_var = tk.StringVar()
        self.valor_entry = ctk.CTkEntry(form_frame, textvariable=self.valor_var, width=150)
        self.valor_entry.grid(row=0, column=3, sticky="w", padx=5, pady=5)

        # Responsável
        ctk.CTkLabel(form_frame, text="RESPONSÁVEL:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.resp_var = tk.StringVar()
        self.resp_entry = ctk.CTkEntry(form_frame, textvariable=self.resp_var, width=150)
        self.resp_entry.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        # Descrição
        ctk.CTkLabel(form_frame, text="DESCRIÇÃO:").grid(row=1, column=2, sticky="w", padx=5, pady=5)
        self.desc_var = tk.StringVar()
        self.desc_entry = ctk.CTkEntry(form_frame, textvariable=self.desc_var, width=400)
        self.desc_entry.grid(row=1, column=3, columnspan=2, sticky="w", padx=5, pady=5)

        # Botões
        btn_frame = ctk.CTkFrame(mov_frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="REGISTRAR",
            command=self.registrar_movimentacao,
            width=120
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="LIMPAR",
            command=self.limpar_campos,
            width=120,
            fg_color="#FFA500",
            hover_color="#FF8C00"
        ).pack(side="left", padx=5)

    def criar_footer(self):
        """Cria o rodapé."""
        self.footer = ctk.CTkFrame(self.main_frame, height=40, fg_color="#1A1A1A")
        self.footer.pack(side="bottom", fill="x", padx=10, pady=(0, 10))
        # Força a altura mínima do footer e impede que seja redimensionado
        self.footer.pack_propagate(False)
        self.footer.grid_propagate(False)

        # Container esquerdo para status
        status_container = ctk.CTkFrame(self.footer, fg_color="transparent")
        status_container.pack(side="left", fill="y", padx=10)
        
        # Status com fonte ajustada
        self.status_label = ctk.CTkLabel(
            status_container,
            text="Sistema pronto",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", pady=8)

        # Container direito para botões e créditos
        right_container = ctk.CTkFrame(self.footer, fg_color="transparent")
        right_container.pack(side="right", fill="y", padx=10)

        # Créditos do desenvolvedor
        self.label_footer = ctk.CTkLabel(
            right_container,
            text="© 2025 Shigi - GitHub @brunoshigi",
            font=ctk.CTkFont(size=12)
        )
        self.label_footer.pack(side="right", padx=10, pady=8)

        # Botão de saída
        self.btn_sair = ctk.CTkButton(
            right_container,
            text="SAIR",
            width=70,
            height=30,
            corner_radius=5,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.sair_sistema,
            fg_color="red",
            hover_color="#CC0000"
        )
        self.btn_sair.pack(side="right", padx=5, pady=5)

    def sair_sistema(self):
        """Fecha a aplicação"""
        self.quit()
        self.destroy()

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

    def criar_lista_movimentacoes(self):
        """Cria a área que mostra o histórico de movimentações"""
        self.lista_frame = ctk.CTkFrame(self.content_frame)
        self.lista_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Header frame
        header_frame = ctk.CTkFrame(self.lista_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(5, 10))

        # Título alinhado à esquerda
        ctk.CTkLabel(
            header_frame,
            text="HISTÓRICO DE MOVIMENTAÇÕES",
            font=("Arial", 15, "bold")
        ).pack(side="left", padx=10)

        # Botões de ação alinhados à direita
        btn_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        btn_frame.pack(side="right", padx=10)

        # Botões com tamanhos padronizados
        button_width = 120
        button_height = 32

        ctk.CTkButton(
            btn_frame,
            text="EXCLUIR",
            command=self.excluir_movimentacao,
            width=button_width,
            height=button_height,
            fg_color="#FF4444",
            hover_color="#CC3333"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="EDITAR",
            command=self.editar_descricao,
            width=button_width,
            height=button_height,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="RESUMO",
            command=self.mostrar_resumo_periodo,
            width=button_width,
            height=button_height,
            fg_color="#9370DB",
            hover_color="#8A2BE2"
        ).pack(side="left", padx=5)

        # Frame da tabela
        tv_frame = ctk.CTkFrame(self.lista_frame)
        tv_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

        # Configuração da tabela com proporções ajustadas
        self.tree = ttk.Treeview(
            tv_frame,
            columns=("data", "tipo", "valor", "responsavel", "descricao", "saldo"),
            show="headings",
            selectmode="browse"
        )
        
        # Configuração das colunas com proporções melhores
        self.tree.heading("data", text="Data/Hora")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("valor", text="Valor")
        self.tree.heading("responsavel", text="Responsável")
        self.tree.heading("descricao", text="Descrição")
        self.tree.heading("saldo", text="Saldo")

        # Larguras proporcionais
        self.tree.column("data", width=150)
        self.tree.column("tipo", width=100)
        self.tree.column("valor", width=120)
        self.tree.column("responsavel", width=150)
        self.tree.column("descricao", width=300)
        self.tree.column("saldo", width=120)

        # Scrollbars
        vsb = ttk.Scrollbar(tv_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tv_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Grid da tabela e scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        # Configurar expansão do grid
        tv_frame.grid_columnconfigure(0, weight=1)
        tv_frame.grid_rowconfigure(0, weight=1)

    def configurar_valor_fundo(self):
        """Abre janela para configurar novo valor do fundo fixo"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Configurar Valor do Fundo")
        dialog.geometry("400x200")
        dialog.resizable(False, False)
        
        # Força a janela a ficar na frente
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()

        # Frame principal
        frame = ctk.CTkFrame(dialog)
        frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Label informativo
        ctk.CTkLabel(
            frame,
            text="Digite o novo valor do fundo fixo:",
            font=("Helvetica", 14)
        ).pack(pady=10)

        # Entry para o valor
        valor_var = tk.StringVar(value=str(self.dados["valor_fundo"]))
        valor_entry = ctk.CTkEntry(
            frame,
            textvariable=valor_var,
            width=200,
            placeholder_text="Ex: 1000.00"
        )
        valor_entry.pack(pady=10)

        def salvar_valor():
            try:
                novo_valor = float(valor_var.get().replace(',', '.'))
                if novo_valor <= 0:
                    raise ValueError("O valor deve ser maior que zero")

                # Atualiza o valor do fundo
                self.dados["valor_fundo"] = novo_valor
                
                # Se o saldo atual for maior que o novo valor, ajusta os depósitos pendentes
                if self.dados["saldo_atual"] > novo_valor:
                    self.dados["depositos_pendentes"] += (self.dados["saldo_atual"] - novo_valor)
                # Se for menor, ajusta as reposições pendentes
                elif self.dados["saldo_atual"] < novo_valor:
                    self.dados["reposicoes_pendentes"] = novo_valor - self.dados["saldo_atual"]

                # Salva no banco e atualiza interface
                self.salvar_dados()
                self.atualizar_interface()
                dialog.destroy()
                messagebox.showinfo("Sucesso", "Valor do fundo atualizado com sucesso!")

            except ValueError as e:
                messagebox.showerror("Erro", str(e))

        # Botões
        btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
        btn_frame.pack(pady=10)

        ctk.CTkButton(
            btn_frame,
            text="SALVAR",
            command=salvar_valor,
            width=100
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            btn_frame,
            text="CANCELAR",
            command=dialog.destroy,
            width=100,
            fg_color="gray"
        ).pack(side="left", padx=5)

    def logica_entrada(self, valor):
        """
        Aplica a lógica de entrada de dinheiro mantendo o controle do saldo real.
        """
        # 1) Atualiza o saldo real primeiro
        self.dados["saldo_atual"] += valor
        
        # 2) Se houver reposições pendentes, abate primeiro
        if self.dados["reposicoes_pendentes"] > 0:
            if self.dados["saldo_atual"] >= self.dados["valor_fundo"]:
                # Se o saldo atual cobriu o valor do fundo, zera as reposições pendentes
                self.dados["reposicoes_pendentes"] = 0.0
            else:
                # Caso contrário, reduz proporcionalmente as reposições pendentes
                self.dados["reposicoes_pendentes"] = self.dados["valor_fundo"] - self.dados["saldo_atual"]
        
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
        
        # 3) Atualiza reposições pendentes baseado no saldo atual
        if self.dados["saldo_atual"] < self.dados["valor_fundo"]:
            self.dados["reposicoes_pendentes"] = self.dados["valor_fundo"] - self.dados["saldo_atual"]

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
        """Abre janela para seleção do período"""
        dialog = ctk.CTkToplevel(self)  # Corrigido: self.root -> self
        dialog.title("Resumo por Período")
        dialog.geometry("500x300")
        dialog.resizable(False, False)
        
        # Força a janela a ficar na frente
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()

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
            
            # Força a janela a ficar na frente
            resumo_toplevel.transient(parent_dialog)
            resumo_toplevel.grab_set()
            resumo_toplevel.focus_force()

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
            messagebox.showwarning("Atenção", "Selecione uma movimentação para editar!")
            return

        item = selecionado[0]
        idx = len(self.dados["movimentacoes"]) - self.tree.index(item) - 1

        # Cria uma janela para edição
        dialog = ctk.CTkToplevel(self)  # Corrigido: self.root -> self
        dialog.title("Editar Descrição")
        dialog.geometry("500x200")
        dialog.resizable(False, False)
        
        # Força a janela a ficar na frente
        dialog.transient(self)
        dialog.grab_set()
        dialog.focus_force()

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

def criar_tabelas(cursor):
    """Cria as tabelas necessárias se não existirem"""
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

if __name__ == "__main__":
    app = GestorFundoFixo()
    app.run()
