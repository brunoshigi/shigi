import os
import sqlite3
from datetime import datetime
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk

# Configurações globais
COLORS = {
    "background": "#0F0F0F",
    "frame_bg": "#1E1E1E",
    "primary": "#00AEEF",
    "secondary": "#2A2D2E",
    "success": "#4CAF50",
    "warning": "#FF9800",
    "danger": "#F44336",
    "text": "#FFFFFF"
}

FONTS = {
    "title": ("Helvetica Bold", 24),
    "subtitle": ("Helvetica Bold", 16),
    "text": ("Helvetica", 14),
    "button": ("Helvetica Bold", 14),
    "small": ("Helvetica", 12)
}

class DefectManagerApp:
    def __init__(self):
        self.setup_main_window()
        self.setup_database()
        self.init_ui()
        self.selected_id = None
        self.selected_item = None
        
    def setup_main_window(self):
        """Configura a janela principal"""
        self.root = ctk.CTk()
        self.root.title("SISTEMA AUSTRAL - GESTÃO DE DEFEITOS")
        self.root.configure(fg_color="#0F0F0F")
        
        # Define um tamanho menor para a janela (80% do tamanho da tela)
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)
        
        # Centraliza a janela
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # Configura grid principal
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)

    def init_ui(self):
        """Inicializa a interface do usuário"""
        self.create_sidebar()
        self.create_main_content()
        self.create_status_bar()

    def create_sidebar(self):
        """Cria a barra lateral com informações e ações rápidas"""
        sidebar = ctk.CTkFrame(
            self.root,
            fg_color="black",
            corner_radius=0
        )
        sidebar.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=(10, 0), pady=10)
        
        # Logo/Título
        ctk.CTkLabel(
            sidebar,
            text="AUSTRAL",
            font=FONTS["title"],
            text_color=COLORS["primary"]
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            sidebar,
            text="Gestão de Defeitos",
            font=FONTS["subtitle"]
        ).pack(pady=(0, 20))
        
        # Estatísticas
        stats_frame = ctk.CTkFrame(sidebar, fg_color=COLORS["secondary"])
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        self.stats_labels = {}
        for stat in ["Total", "Pendentes", "Resolvidos"]:
            label = ctk.CTkLabel(
                stats_frame,
                text=f"{stat}: 0",
                font=FONTS["text"]
            )
            label.pack(pady=5)
            self.stats_labels[stat.lower()] = label
            
        # Ações rápidas
        actions_frame = ctk.CTkFrame(sidebar, fg_color=COLORS["secondary"])
        actions_frame.pack(fill="x", padx=10, pady=20)
        
        ctk.CTkButton(
            actions_frame,
            text="Novo Registro",
            command=self.novo_registro,
            font=FONTS["button"],
            fg_color=COLORS["primary"],
            hover_color="#0099CC"
        ).pack(pady=10, padx=10, fill="x")
        
        ctk.CTkButton(
            actions_frame,
            text="Exportar Relatório",
            command=self.exportar_excel,
            font=FONTS["button"],
            fg_color=COLORS["success"],
            hover_color="#45a049"
        ).pack(pady=10, padx=10, fill="x")

        # Versão e créditos no final da sidebar
        ctk.CTkLabel(
            sidebar,
            text="v2.0.0",
            font=FONTS["small"],
            text_color="#888888"
        ).pack(side="bottom", pady=10)
        
        ctk.CTkLabel(
            sidebar,
            text="© 2025 Shigi",
            font=FONTS["small"],
            text_color="#888888"
        ).pack(side="bottom", pady=5)

    def create_main_content(self):
        """Cria a área principal de conteúdo"""
        main_frame = ctk.CTkFrame(
            self.root,
            fg_color="black",
            corner_radius=15
        )
        main_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        main_frame.grid_rowconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Painel superior com filtros e pesquisa
        self.create_filter_panel(main_frame)
        
        # Container principal dividido em duas partes
        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=10)
        content_frame.grid_columnconfigure(1, weight=1)
        
        # Formulário à esquerda
        self.create_form(content_frame)
        
        # Tabela à direita
        self.create_table(content_frame)

    def create_filter_panel(self, parent):
        """Cria o painel de filtros e pesquisa"""
        filter_frame = ctk.CTkFrame(parent, fg_color="black")
        filter_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Campo de pesquisa
        search_frame = ctk.CTkFrame(filter_frame, fg_color="transparent")
        search_frame.pack(side="left", padx=10, pady=5)
        
        self.search_entry = ctk.CTkEntry(
            search_frame,
            placeholder_text="Pesquisar...",
            width=300,
            font=FONTS["text"]
        )
        self.search_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            search_frame,
            text="Buscar",
            command=self.pesquisar,
            font=FONTS["text"],
            width=100
        ).pack(side="left")
        
        # Filtros
        filter_options = ctk.CTkFrame(filter_frame, fg_color="transparent")
        filter_options.pack(side="right", padx=10)
        
        self.filtro_status = ctk.CTkComboBox(
            filter_options,
            values=["Todos", "Pendentes", "Resolvidos"],
            font=FONTS["text"],
            width=150
        )
        self.filtro_status.pack(side="left", padx=5)
        
        self.filtro_loja = ctk.CTkComboBox(
            filter_options,
            values=["Todas", "Matriz", "Filial 1", "Filial 2"],
            font=FONTS["text"],
            width=150
        )
        self.filtro_loja.pack(side="left", padx=5)

    def create_form(self, parent):
        """Cria o formulário de registro"""
        form_frame = ctk.CTkFrame(parent, fg_color="black")
        form_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        # Título do formulário
        ctk.CTkLabel(
            form_frame,
            text="Registro de Defeito",
            font=FONTS["subtitle"]
        ).pack(pady=10)
        
        # Container para os campos
        fields_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        fields_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Campos do formulário
        self.create_form_fields(fields_frame)
        
        # Botões do formulário
        buttons_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkButton(
            buttons_frame,
            text="Limpar",
            command=self.limpar_campos,
            font=FONTS["button"],
            fg_color=COLORS["warning"],
            hover_color="#FF7043"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            buttons_frame,
            text="Salvar",
            command=self.adicionar_defeito,
            font=FONTS["button"],
            fg_color=COLORS["success"],
            hover_color="#45a049"
        ).pack(side="right", padx=5)

    def create_form_fields(self, parent):
        """Cria os campos do formulário"""
        fields = [
            ("Tipo de Defeito", "tipo_defeito_entry", ["SELECIONE", "GARANTIA", "CLIENTE"]),
            ("Código do Produto", "codigo_produto_entry", None),
            ("Tamanho", "tamanho_entry", ["SELECIONE", "P", "M", "G", "GG"]),
            ("Vendedor", "nome_vendedor_entry", None),
            ("Descrição", "descricao_defeito_entry", ["SELECIONE", "MANCHA", "COSTURA", "FURO"]),
            ("Loja", "loja_entry", ["MATRIZ", "FILIAL 1", "FILIAL 2"])
        ]

        for label_text, entry_name, options in fields:
            container = ctk.CTkFrame(parent, fg_color="transparent")
            container.pack(fill="x", pady=5)
            
            ctk.CTkLabel(
                container,
                text=label_text,
                font=FONTS["text"]
            ).pack(anchor="w")
            
            if options:
                widget = ctk.CTkComboBox(
                    container,
                    values=options,
                    font=FONTS["text"],
                    width=200  # Reduzido de 250 para 200
                )
                widget.set(options[0])
            else:
                widget = ctk.CTkEntry(
                    container,
                    font=FONTS["text"],
                    width=200  # Reduzido de 250 para 200
                )
            
            widget.pack(anchor="w")
            setattr(self, entry_name, widget)
            
        # Campo de observações
        obs_container = ctk.CTkFrame(parent, fg_color="transparent")
        obs_container.pack(fill="x", pady=5)
        
        ctk.CTkLabel(
            obs_container,
            text="Observações",
            font=FONTS["text"]
        ).pack(anchor="w")
        
        self.observacoes_entry = ctk.CTkTextbox(
            obs_container,
            font=FONTS["text"],
            height=80  # Reduzido de 100 para 80
        )
        self.observacoes_entry.pack(fill="x")

    def create_table(self, parent):
        """Cria a tabela de registros"""
        table_frame = ctk.CTkFrame(parent, fg_color="black")
        table_frame.grid(row=0, column=1, sticky="nsew")
        
        # Título da tabela
        header_frame = ctk.CTkFrame(table_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            header_frame,
            text="Registros",
            font=FONTS["subtitle"]
        ).pack(side="left")
        
        actions_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        actions_frame.pack(side="right")
        
        ctk.CTkButton(
            actions_frame,
            text="Resolver Selecionados",
            command=self.marcar_como_resolvido,
            font=FONTS["text"],
            fg_color=COLORS["success"],
            hover_color="#45a049"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            actions_frame,
            text="Excluir Selecionados",
            command=self.excluir_defeito,
            font=FONTS["text"],
            fg_color=COLORS["danger"],
            hover_color="#D32F2F"
        ).pack(side="left", padx=5)
        
        # Configuração da tabela
        style = ttk.Style()
        style.configure(
            "Treeview",
            background=COLORS["secondary"],
            foreground=COLORS["text"],
            fieldbackground=COLORS["secondary"],
            rowheight=35
        )
        style.configure(
            "Treeview.Heading",
            background=COLORS["frame_bg"],
            foreground=COLORS["text"],
            font=FONTS["text"]
        )
        
        # Criação da Treeview
        columns = (
            "DATA", "TIPO", "CÓDIGO", "TAMANHO",
            "VENDEDOR", "LOJA", "STATUS"
        )
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Treeview",
            selectmode="extended"
        )
        
        # Configuração das colunas com larguras menores
        widths = {
            "DATA": 100,      # Reduzido de 120
            "TIPO": 120,      # Reduzido de 150
            "CÓDIGO": 120,    # Reduzido de 150
            "TAMANHO": 80,    # Reduzido de 100
            "VENDEDOR": 150,  # Reduzido de 200
            "LOJA": 120,      # Reduzido de 150
            "STATUS": 100     # Reduzido de 120
        }
        
        for col, width in widths.items():
            self.tree.column(col, width=width, anchor="center")
            self.tree.heading(col, text=col)
        
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Eventos da tabela
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
        self.tree.bind("<Double-1>", self.preencher_campos)

    def create_status_bar(self):
        """Cria a barra de status no rodapé"""
        status_bar = ctk.CTkFrame(
            self.root,
            fg_color="black",
            height=30
        )
        status_bar.grid(row=1, column=1, sticky="ew", padx=10, pady=(0, 10))
        
        # Data e hora atual
        self.time_label = ctk.CTkLabel(
            status_bar,
            text="",
            font=FONTS["small"]
        )
        self.time_label.pack(side="right", padx=10)
        self.update_clock()

    def update_clock(self):
        """Atualiza o relógio na barra de status"""
        self.time_label.configure(
            text=datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        )
        self.root.after(1000, self.update_clock)

    def setup_database(self):
        """Configura o banco de dados SQLite"""
        self.assets_path = os.path.join(os.path.dirname(__file__), "assets")
        if not os.path.exists(self.assets_path):
            os.makedirs(self.assets_path)
        self.db_path = os.path.join(self.assets_path, "austral.db")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS defeitos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_defeito TEXT,
                tipo_defeito TEXT,
                codigo_produto TEXT,
                tamanho TEXT,
                nome_vendedor TEXT,
                descricao_defeito TEXT,
                observacoes TEXT,
                loja TEXT,
                status TEXT DEFAULT 'Pendente'
            )
        ''')
        conn.commit()
        conn.close()

    def novo_registro(self):
        """Limpa os campos para um novo registro"""
        self.limpar_campos()
        # Foca no primeiro campo
        self.tipo_defeito_entry.set("SELECIONE")

    def atualizar_estatisticas(self):
        """Atualiza as estatísticas na sidebar"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total de registros
            cursor.execute("SELECT COUNT(*) FROM defeitos")
            total = cursor.fetchone()[0]
            self.stats_labels["total"].configure(text=f"Total: {total}")
            
            # Registros pendentes
            cursor.execute("SELECT COUNT(*) FROM defeitos WHERE status = 'Pendente'")
            pendentes = cursor.fetchone()[0]
            self.stats_labels["pendentes"].configure(text=f"Pendentes: {pendentes}")
            
            # Registros resolvidos
            cursor.execute("SELECT COUNT(*) FROM defeitos WHERE status = 'Resolvido'")
            resolvidos = cursor.fetchone()[0]
            self.stats_labels["resolvidos"].configure(text=f"Resolvidos: {resolvidos}")
            
        except sqlite3.Error as e:
            print(f"Erro ao atualizar estatísticas: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def pesquisar(self):
        """Realiza a pesquisa com base nos filtros"""
        search_term = self.search_entry.get().strip().upper()
        status_filtro = self.filtro_status.get()
        loja_filtro = self.filtro_loja.get()
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = """
                SELECT data_defeito, tipo_defeito, codigo_produto, 
                       tamanho, nome_vendedor, loja, status
                FROM defeitos
                WHERE 1=1
            """
            params = []
            
            if search_term:
                query += """ AND (
                    codigo_produto LIKE ? OR 
                    nome_vendedor LIKE ? OR 
                    descricao_defeito LIKE ?
                )"""
                params.extend([f"%{search_term}%"] * 3)
            
            if status_filtro != "Todos":
                query += " AND status = ?"
                params.append(status_filtro)
                
            if loja_filtro != "Todas":
                query += " AND loja = ?"
                params.append(loja_filtro)
                
            query += " ORDER BY data_defeito DESC"
            
            cursor.execute(query, params)
            
            # Limpa a tabela atual
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            # Preenche com os resultados
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("ERRO", f"Erro na pesquisa: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def validar_campos(self):
        """Valida os campos obrigatórios"""
        campos = {
            "Tipo de Defeito": (self.tipo_defeito_entry.get(), "SELECIONE"),
            "Código do Produto": (self.codigo_produto_entry.get().strip(), ""),
            "Tamanho": (self.tamanho_entry.get(), "SELECIONE"),
            "Vendedor": (self.nome_vendedor_entry.get().strip(), ""),
            "Descrição": (self.descricao_defeito_entry.get(), "SELECIONE"),
            "Loja": (self.loja_entry.get(), "")
        }

        for campo, (valor, invalido) in campos.items():
            if valor == invalido or not valor:
                messagebox.showwarning(
                    "ATENÇÃO",
                    f"O campo {campo} é obrigatório!",
                    parent=self.root
                )
                return False
        return True

    def adicionar_defeito(self):
        """Adiciona ou atualiza um registro de defeito"""
        if not self.validar_campos():
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            data_atual = datetime.now().strftime('%d/%m/%Y')
            
            if self.selected_id:  # Atualização
                cursor.execute('''
                    UPDATE defeitos SET
                        tipo_defeito = ?,
                        codigo_produto = ?,
                        tamanho = ?,
                        nome_vendedor = ?,
                        descricao_defeito = ?,
                        observacoes = ?,
                        loja = ?
                    WHERE id = ?
                ''', (
                    self.tipo_defeito_entry.get(),
                    self.codigo_produto_entry.get().strip().upper(),
                    self.tamanho_entry.get(),
                    self.nome_vendedor_entry.get().strip().upper(),
                    self.descricao_defeito_entry.get(),
                    self.observacoes_entry.get("1.0", "end-1c").strip(),
                    self.loja_entry.get(),
                    self.selected_id
                ))
                mensagem = "Registro atualizado com sucesso!"
            else:  # Novo registro
                cursor.execute('''
                    INSERT INTO defeitos (
                        data_defeito, tipo_defeito, codigo_produto,
                        tamanho, nome_vendedor, descricao_defeito,
                        observacoes, loja, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data_atual,
                    self.tipo_defeito_entry.get(),
                    self.codigo_produto_entry.get().strip().upper(),
                    self.tamanho_entry.get(),
                    self.nome_vendedor_entry.get().strip().upper(),
                    self.descricao_defeito_entry.get(),
                    self.observacoes_entry.get("1.0", "end-1c").strip(),
                    self.loja_entry.get(),
                    "Pendente"
                ))
                mensagem = "Defeito registrado com sucesso!"
            
            conn.commit()
            messagebox.showinfo("SUCESSO", mensagem)
            self.limpar_campos()
            self.carregar_dados()
            self.atualizar_estatisticas()
            
        except sqlite3.Error as e:
            messagebox.showerror("ERRO", f"Erro ao salvar registro: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def marcar_como_resolvido(self):
        """Marca os registros selecionados como resolvidos"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                "ATENÇÃO",
                "Selecione um ou mais registros para marcar como resolvido.",
                parent=self.root
            )
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in selected_items:
                valores = self.tree.item(item)['values']
                codigo_produto = valores[2]  # Índice do código do produto
                
                cursor.execute('''
                    UPDATE defeitos
                    SET status = 'Resolvido'
                    WHERE codigo_produto = ?
                ''', (codigo_produto,))
            
            conn.commit()
            messagebox.showinfo(
                "SUCESSO",
                "Status atualizado com sucesso!",
                parent=self.root
            )
            self.carregar_dados()
            self.atualizar_estatisticas()
            
        except sqlite3.Error as e:
            messagebox.showerror("ERRO", f"Erro ao atualizar status: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def excluir_defeito(self):
        """Exclui os registros selecionados"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning(
                "ATENÇÃO",
                "Selecione um ou mais registros para excluir.",
                parent=self.root
            )
            return

        if not messagebox.askyesno(
            "CONFIRMAÇÃO",
            "Tem certeza que deseja excluir os registros selecionados?",
            parent=self.root
        ):
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for item in selected_items:
                valores = self.tree.item(item)['values']
                codigo_produto = valores[2]
                cursor.execute(
                    'DELETE FROM defeitos WHERE codigo_produto = ?',
                    (codigo_produto,)
                )
            
            conn.commit()
            messagebox.showinfo(
                "SUCESSO",
                "Registro(s) excluído(s) com sucesso!",
                parent=self.root
            )
            self.carregar_dados()
            self.atualizar_estatisticas()
            
        except sqlite3.Error as e:
            messagebox.showerror("ERRO", f"Erro ao excluir registro(s): {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def exportar_excel(self):
        """Exporta os dados para um arquivo Excel"""
        try:
            conn = sqlite3.connect(self.db_path)
            query = '''
                SELECT 
                    data_defeito as "Data",
                    tipo_defeito as "Tipo",
                    codigo_produto as "Código",
                    tamanho as "Tamanho",
                    nome_vendedor as "Vendedor",
                    descricao_defeito as "Descrição",
                    observacoes as "Observações",
                    loja as "Loja",
                    status as "Status"
                FROM defeitos
                ORDER BY data_defeito DESC
            '''
            
            df = pd.read_sql_query(query, conn)
            
            if df.empty:
                messagebox.showwarning(
                    "ATENÇÃO",
                    "Não há dados para exportar!",
                    parent=self.root
                )
                return
            
            data_atual = datetime.now().strftime("%d%m%Y")
            nome_arquivo = f"defeitos_{data_atual}.xlsx"
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=nome_arquivo,
                title="Salvar arquivo Excel",
                filetypes=[("Excel files", "*.xlsx")],
                parent=self.root
            )
            
            if file_path:
                df.to_excel(file_path, index=False)
                messagebox.showinfo(
                    "SUCESSO",
                    f"Dados exportados para {file_path}",
                    parent=self.root
                )
                
        except Exception as e:
            messagebox.showerror("ERRO", f"Erro ao exportar dados: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def carregar_dados(self):
        """Carrega os dados na tabela"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT data_defeito, tipo_defeito, codigo_produto, tamanho,
                       nome_vendedor, loja, status
                FROM defeitos
                ORDER BY data_defeito DESC
            ''')

            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)

            self.atualizar_estatisticas()

        except sqlite3.Error as e:
            messagebox.showerror("ERRO", f"Erro ao carregar dados: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        self.tipo_defeito_entry.set("SELECIONE")
        self.codigo_produto_entry.delete(0, "end")
        self.tamanho_entry.set("SELECIONE")
        self.nome_vendedor_entry.delete(0, "end")
        self.descricao_defeito_entry.set("SELECIONE")
        self.observacoes_entry.delete("1.0", "end")
        self.loja_entry.set("MATRIZ")
        self.selected_id = None
        self.selected_item = None

    def on_select(self, event=None):
        """Manipula a seleção de item na tabela"""
        selected_items = self.tree.selection()
        if selected_items:
            self.selected_item = selected_items[0]
            valores = self.tree.item(self.selected_item)['values']
            if valores:
                # O código do produto está na posição 2 do valores
                self.selected_id = valores[2]

    def preencher_campos(self, event=None):
        """Preenche os campos com os dados do item selecionado"""
        if not self.selected_item:
            return

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM defeitos
                WHERE codigo_produto = ?
            ''', (self.selected_id,))
            
            row = cursor.fetchone()
            if row:
                # Limpa os campos antes de preencher
                self.limpar_campos()
                
                # Preenche os campos com os dados do banco
                self.tipo_defeito_entry.set(row[2])  # tipo_defeito
                self.codigo_produto_entry.insert(0, row[3])  # codigo_produto
                self.tamanho_entry.set(row[4])  # tamanho
                self.nome_vendedor_entry.insert(0, row[5])  # nome_vendedor
                self.descricao_defeito_entry.set(row[6])  # descricao_defeito
                self.observacoes_entry.insert("1.0", row[7] if row[7] else "")  # observacoes
                self.loja_entry.set(row[8])  # loja
                
        except sqlite3.Error as e:
            messagebox.showerror("ERRO", f"Erro ao carregar dados: {str(e)}")
        finally:
            if 'conn' in locals():
                conn.close()

    def run(self):
        """Inicia a aplicação"""
        self.carregar_dados()  # Carrega os dados iniciais
        self.root.mainloop()

if __name__ == "__main__":
    app = DefectManagerApp()
    app.run()