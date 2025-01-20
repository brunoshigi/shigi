import os
import sqlite3
from datetime import datetime
import pandas as pd
import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Definição de fontes e estilos
FONT_TITLE = ("Arial Bold", 24)
FONT_LABEL = ("Arial Bold", 14)
FONT_ENTRY = ("Arial", 14)
FONT_BUTTON = ("Arial Bold", 14)

class DefectManagerApp:
    def __init__(self):
        self.root = ctk.CTk()
        
        # Configurações da janela
        self.root.title("SISTEMA AUSTRAL - REGISTRO DE DEFEITOS")
        self.center_window()
        
        # Variáveis de controle
        self.selected_item = None
        self.selected_id = None
        
        # Lista de opções
        self.tipos_defeito = ["SELECIONE A ORIGEM", "CLIENTE", "LOJA", "UNIFORME"]
        self.tamanhos = ["SELECIONE O TAMANHO", "ÚNICO", "XPP", "PP", "P", "M", "G", "GG", "XGG",
                      "36", "38", "40", "42", "44", "46", "48",
                      "38-39", "40-41", "42-43", "44-45", "36-37", "34-35"]
        self.lojas_lista = ["SELECIONE A LOJA", "LOJA 1", "LOJA 2"]
        self.defeitos_lista = [
            "SELECIONE O TIPO DE DEFEITO",
            "1. FUROS EM PEÇA NOVA",
            "2. MANCHA EM PEÇA NOVA",
            "3. COSTURA DEFEITUOSA",
            "4. BOTÃO QUEBRADO/FALTANDO",
            "5. ZÍPER QUEBRADO",
            "6. COR MANCHADA",
            "7. TAMANHO ERRADO",
            "8. ETIQUETA ERRADA",
            "9. TECIDO COM DEFEITO",
            "10. ACABAMENTO IRREGULAR"
        ]
        
        self.setup_database()
        self.setup_ui()
        self.carregar_dados()

    def center_window(self):
        """Centraliza a janela principal na tela"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 1400
        window_height = 800
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.minsize(1200, 700)

    def setup_database(self):
        """Configura o banco de dados SQLite"""
        conn = sqlite3.connect('austral.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS defeitos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo_defeito TEXT,
                codigo_produto TEXT,
                descricao TEXT,
                cor TEXT,
                tamanho TEXT,
                nome_cliente TEXT,
                nome_vendedor TEXT,
                data_defeito TEXT,
                descricao_defeito TEXT,
                observacoes TEXT,
                loja TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

    def setup_ui(self):
        """Configura a interface do usuário"""
        # Container principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Título
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="REGISTRO DE DEFEITOS",
            font=FONT_TITLE
        )
        title_label.pack(pady=(0, 20))

        # Frame para campos de entrada
        entry_frame = ctk.CTkFrame(self.main_frame)
        entry_frame.pack(fill="x", padx=10, pady=(0, 10))

        # Divide em duas colunas
        left_frame = ctk.CTkFrame(entry_frame)
        left_frame.pack(side="left", expand=True, fill="both", padx=10)
        
        right_frame = ctk.CTkFrame(entry_frame)
        right_frame.pack(side="left", expand=True, fill="both", padx=10)

        # Configuração dos campos
        self.setup_left_fields(left_frame)
        self.setup_right_fields(right_frame)
        
        # Frame de botões
        self.setup_buttons()
        
        # Frame da tabela
        self.setup_table()

    def setup_left_fields(self, frame):
        """Configura os campos da coluna esquerda"""
        # Origem do Defeito
        ctk.CTkLabel(frame, text="ORIGEM DEFEITO *:", font=FONT_LABEL).grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.tipo_defeito_entry = ctk.CTkComboBox(
            frame, values=self.tipos_defeito, width=300, height=40,
            font=FONT_ENTRY, dropdown_font=FONT_ENTRY
        )
        self.tipo_defeito_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)
        self.tipo_defeito_entry.set(self.tipos_defeito[0])

        # Código do Produto
        ctk.CTkLabel(frame, text="CÓDIGO PRODUTO *:", font=FONT_LABEL).grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.codigo_produto_entry = ctk.CTkEntry(frame, width=300, height=40, font=FONT_ENTRY)
        self.codigo_produto_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        # Descrição
        ctk.CTkLabel(frame, text="NOME PRODUTO:", font=FONT_LABEL).grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.descricao_entry = ctk.CTkEntry(frame, width=300, height=40, font=FONT_ENTRY)
        self.descricao_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5)

        # Cor
        ctk.CTkLabel(frame, text="COR:", font=FONT_LABEL).grid(row=3, column=0, sticky="e", padx=10, pady=5)
        self.cor_entry = ctk.CTkEntry(frame, width=300, height=40, font=FONT_ENTRY)
        self.cor_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

        # Tamanho
        ctk.CTkLabel(frame, text="TAMANHO *:", font=FONT_LABEL).grid(row=4, column=0, sticky="e", padx=10, pady=5)
        self.tamanho_entry = ctk.CTkComboBox(
            frame, values=self.tamanhos, width=300, height=40,
            font=FONT_ENTRY, dropdown_font=FONT_ENTRY
        )
        self.tamanho_entry.grid(row=4, column=1, sticky="ew", padx=10, pady=5)
        self.tamanho_entry.set(self.tamanhos[0])

        # Loja
        ctk.CTkLabel(frame, text="FILIAL:", font=FONT_LABEL).grid(row=5, column=0, sticky="e", padx=10, pady=5)
        self.loja_entry = ctk.CTkComboBox(
            frame, values=self.lojas_lista, width=300, height=40,
            font=FONT_ENTRY, dropdown_font=FONT_ENTRY
        )
        self.loja_entry.grid(row=5, column=1, sticky="ew", padx=10, pady=5)
        self.loja_entry.set(self.lojas_lista[0])

    def setup_right_fields(self, frame):
        """Configura os campos da coluna direita"""
        # Nome do Cliente
        ctk.CTkLabel(frame, text="NOME CLIENTE:", font=FONT_LABEL).grid(row=0, column=0, sticky="e", padx=10, pady=5)
        self.nome_cliente_entry = ctk.CTkEntry(frame, width=300, height=40, font=FONT_ENTRY)
        self.nome_cliente_entry.grid(row=0, column=1, sticky="ew", padx=10, pady=5)

        # Nome do Vendedor
        ctk.CTkLabel(frame, text="NOME VENDEDOR *:", font=FONT_LABEL).grid(row=1, column=0, sticky="e", padx=10, pady=5)
        self.nome_vendedor_entry = ctk.CTkEntry(frame, width=300, height=40, font=FONT_ENTRY)
        self.nome_vendedor_entry.grid(row=1, column=1, sticky="ew", padx=10, pady=5)

        # Tipo de Defeito
        ctk.CTkLabel(frame, text="TIPO DE DEFEITO *:", font=FONT_LABEL).grid(row=2, column=0, sticky="e", padx=10, pady=5)
        self.descricao_defeito_entry = ctk.CTkComboBox(
            frame, values=self.defeitos_lista, width=300, height=40,
            font=FONT_ENTRY, dropdown_font=FONT_ENTRY
        )
        self.descricao_defeito_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=5)
        self.descricao_defeito_entry.set(self.defeitos_lista[0])

        # Observações
        ctk.CTkLabel(frame, text="OBSERVAÇÕES:", font=FONT_LABEL).grid(row=3, column=0, sticky="ne", padx=10, pady=5)
        self.observacoes_entry = ctk.CTkTextbox(frame, width=300, height=120, font=FONT_ENTRY)
        self.observacoes_entry.grid(row=3, column=1, sticky="ew", padx=10, pady=5)

    def setup_buttons(self):
        """Configura os botões de ação"""
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(fill="x", padx=10, pady=10)

        # Botões com cores diferentes
        ctk.CTkButton(
            button_frame,
            text="ADICIONAR",
            command=self.adicionar_defeito,
            font=FONT_BUTTON,
            width=200,
            height=40
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="ATUALIZAR",
            command=self.atualizar_defeito,
            font=FONT_BUTTON,
            width=200,
            height=40,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="EXCLUIR",
            command=self.excluir_defeito,
            font=FONT_BUTTON,
            width=200,
            height=40,
            fg_color="#FF4444",
            hover_color="#CC3333"
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="LIMPAR",
            command=self.limpar_campos,
            font=FONT_BUTTON,
            width=200,
            height=40,
            fg_color="#FFA500",
            hover_color="#FF8C00"
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="EXPORTAR",
            command=self.exportar_excel,
            font=FONT_BUTTON,
            width=200,
            height=40,
            fg_color="#9370DB",
            hover_color="#8A2BE2"
        ).pack(side="left", padx=10)

    def setup_table(self):
        """Configura a tabela de registros"""
        # Frame para a tabela
        tree_frame = ctk.CTkFrame(self.main_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Estilo da tabela
        style = ttk.Style()
        style.configure(
            "Treeview",
            font=('Arial', 12),
            rowheight=30,
            background="#2a2d2e",
            foreground="white",
            fieldbackground="#2a2d2e"
        )
        style.configure("Treeview.Heading", font=('Arial Bold', 13))

        # Criação da tabela
        self.tree = ttk.Treeview(
            tree_frame,
            columns=(
                "id", "tipo_defeito", "codigo_produto", "descricao",
                "nome_vendedor", "data_defeito", "cor", "tamanho",
                "loja", "observacoes"
            ),
            show="headings",
            height=15
        )

        # Configuração das colunas
        colunas_config = {
            "id": ("ID", 60),
            "tipo_defeito": ("ORIGEM", 100),
            "codigo_produto": ("CÓDIGO", 120),
            "descricao": ("NOME PRODUTO", 200),
            "nome_vendedor": ("VENDEDOR", 150),
            "data_defeito": ("DATA", 100),
            "cor": ("COR", 100),
            "tamanho": ("TAM", 80),
            "loja": ("FILIAL", 100),
            "observacoes": ("OBS", 200)
        }

        for col, (heading, width) in colunas_config.items():
            self.tree.heading(col, text=heading, anchor="center")
            self.tree.column(col, width=width, minwidth=width, anchor="center")

        # Scrollbars
        vsb = ctk.CTkScrollbar(tree_frame, command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        
        hsb = ctk.CTkScrollbar(tree_frame, orientation="horizontal", command=self.tree.xview)
        hsb.pack(side="bottom", fill="x")
        
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        
        # Bindings da tabela
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.preencher_campos)

    def limpar_campos(self):
        """Limpa todos os campos do formulário"""
        self.tipo_defeito_entry.set(self.tipos_defeito[0])
        self.codigo_produto_entry.delete(0, 'end')
        self.descricao_entry.delete(0, 'end')
        self.cor_entry.delete(0, 'end')
        self.tamanho_entry.set(self.tamanhos[0])
        self.loja_entry.set(self.lojas_lista[0])
        self.nome_cliente_entry.delete(0, 'end')
        self.nome_vendedor_entry.delete(0, 'end')
        self.descricao_defeito_entry.set(self.defeitos_lista[0])
        self.observacoes_entry.delete("1.0", "end")
        self.selected_item = None
        self.selected_id = None

    def carregar_dados(self):
        """Carrega os dados do banco para a tabela"""
        # Limpa a tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            conn = sqlite3.connect('austral.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, tipo_defeito, codigo_produto, descricao,
                       nome_vendedor, data_defeito, cor, tamanho,
                       loja, observacoes
                FROM defeitos
                ORDER BY id DESC
            """)
            
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
                
        except sqlite3.Error as e:
            messagebox.showerror("ERRO", f"Erro ao carregar dados: {str(e)}")
            
        finally:
            if 'conn' in locals():
                conn.close()

    def validar_campos(self):
        """Valida os campos obrigatórios"""
        campos_obrigatorios = {
            "Origem do Defeito": self.tipo_defeito_entry.get(),
            "Código do Produto": self.codigo_produto_entry.get().strip(),
            "Tamanho": self.tamanho_entry.get(),
            "Nome do Vendedor": self.nome_vendedor_entry.get().strip(),
            "Tipo de Defeito": self.descricao_defeito_entry.get()
        }
        
        for campo, valor in campos_obrigatorios.items():
            if valor in ["", "SELECIONE A ORIGEM", "SELECIONE O TAMANHO", "SELECIONE O TIPO DE DEFEITO"]:
                messagebox.showwarning("ATENÇÃO", f"O campo {campo} é obrigatório!")
                return False
        return True

    def on_select(self, event=None):
        """Manipula a seleção de item na tabela"""
        selected_items = self.tree.selection()
        if selected_items:
            self.selected_item = selected_items[0]
            valores = self.tree.item(self.selected_item)['values']
            if valores:
                self.selected_id = valores[0]

    def preencher_campos(self, event=None):
        """Preenche os campos com os dados do item selecionado"""
        if not self.selected_item:
            return
            
        valores = self.tree.item(self.selected_item)['values']
        if not valores:
            return
            
        # Limpa os campos antes de preencher
        self.limpar_campos()
        
        try:
            conn = sqlite3.connect('austral.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM defeitos WHERE id = ?
            """, (self.selected_id,))
            
            row = cursor.fetchone()
            if row:
                self.selected_id = row[0]
                self.tipo_defeito_entry.set(row[1])
                self.codigo_produto_entry.insert(0, row[2])
                self.descricao_entry.insert(0, row[3])
                self.cor_entry.insert(0, row[4])
                self.tamanho_entry.set(row[5])
                self.nome_cliente_entry.insert(0, row[6])
                self.nome_vendedor_entry.insert(0, row[7])
                self.descricao_defeito_entry.set(row[9])
                self.observacoes_entry.insert("1.0", row[10])
                self.loja_entry.set(row[11])
                
        except sqlite3.Error as e:
            messagebox.showerror("ERRO", f"Erro ao carregar dados do item: {str(e)}")
            
        finally:
            if 'conn' in locals():
                conn.close()

    def adicionar_defeito(self):
        """Adiciona um novo defeito ao banco de dados"""
        if not self.validar_campos():
            return
            
        try:
            conn = sqlite3.connect('austral.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO defeitos (
                    tipo_defeito, codigo_produto, descricao, cor, tamanho,
                    nome_cliente, nome_vendedor, data_defeito,
                    descricao_defeito, observacoes, loja
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.tipo_defeito_entry.get(),
                self.codigo_produto_entry.get().strip(),
                self.descricao_entry.get().strip(),
                self.cor_entry.get().strip(),
                self.tamanho_entry.get(),
                self.nome_cliente_entry.get().strip(),
                self.nome_vendedor_entry.get().strip(),
                datetime.now().strftime('%d/%m/%Y'),
                self.descricao_defeito_entry.get(),
                self.observacoes_entry.get("1.0", "end-1c").strip(),
                self.loja_entry.get()
            ))
            conn.commit()
            messagebox.showinfo("SUCESSO", "Defeito registrado com sucesso!")
            self.limpar_campos()
            self.carregar_dados()
            
        except sqlite3.Error as e:
            messagebox.showerror("ERRO", f"Erro ao adicionar defeito: {str(e)}")
            
        finally:
            if 'conn' in locals():
                conn.close()

    def atualizar_defeito(self):
        """Atualiza um defeito existente"""
        if not self.selected_id:
            messagebox.showwarning("ATENÇÃO", "Selecione um defeito para atualizar!")
            return
            
        if not self.validar_campos():
            return
            
        try:
            conn = sqlite3.connect('austral.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE defeitos SET
                    tipo_defeito = ?,
                    codigo_produto = ?,
                    descricao = ?,
                    cor = ?,
                    tamanho = ?,
                    nome_cliente = ?,
                    nome_vendedor = ?,
                    descricao_defeito = ?,
                    observacoes = ?,
                    loja = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (
                self.tipo_defeito_entry.get(),
                self.codigo_produto_entry.get().strip(),
                self.descricao_entry.get().strip(),
                self.cor_entry.get().strip(),
                self.tamanho_entry.get(),
                self.nome_cliente_entry.get().strip(),
                self.nome_vendedor_entry.get().strip(),
                self.descricao_defeito_entry.get(),
                self.observacoes_entry.get("1.0", "end-1c").strip(),
                self.loja_entry.get(),
                self.selected_id
            ))
            conn.commit()
            messagebox.showinfo("SUCESSO", "Defeito atualizado com sucesso!")
            self.limpar_campos()
            self.carregar_dados()
            
        except sqlite3.Error as e:
            messagebox.showerror("ERRO", f"Erro ao atualizar defeito: {str(e)}")
            
        finally:
            if 'conn' in locals():
                conn.close()

    def excluir_defeito(self):
        """Exclui um defeito do banco de dados"""
        if not self.selected_id:
            messagebox.showwarning("ATENÇÃO", "Selecione um defeito para excluir!")
            return
            
        if not messagebox.askyesno("CONFIRMAR", "Tem certeza que deseja excluir este registro?"):
            return
            
        try:
            conn = sqlite3.connect('austral.db')
            cursor = conn.cursor()
            cursor.execute('DELETE FROM defeitos WHERE id = ?', (self.selected_id,))
            conn.commit()
            messagebox.showinfo("SUCESSO", "Defeito excluído com sucesso!")
            self.limpar_campos()
            self.carregar_dados()
            
        except sqlite3.Error as e:
            messagebox.showerror("ERRO", f"Erro ao excluir defeito: {str(e)}")
            
        finally:
            if 'conn' in locals():
                conn.close()

    def exportar_excel(self):
        """Exporta os dados para um arquivo Excel"""
        try:
            data_atual = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"defeitos_{data_atual}.xlsx"
            
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx")],
                initialfile=filename
            )
            
            if not filepath:
                return
                
            conn = sqlite3.connect('austral.db')
            query = """
                SELECT 
                    tipo_defeito as 'TIPO DE DEFEITO',
                    codigo_produto as 'CÓDIGO DO PRODUTO',
                    descricao as 'DESCRIÇÃO',
                    cor as 'COR',
                    tamanho as 'TAMANHO',
                    nome_cliente as 'NOME DO CLIENTE',
                    nome_vendedor as 'NOME DO VENDEDOR',
                    data_defeito as 'DATA DO DEFEITO',
                    descricao_defeito as 'DESCRIÇÃO DO DEFEITO',
                    observacoes as 'OBSERVAÇÕES',
                    loja as 'LOJA',
                    created_at as 'DATA DE CRIAÇÃO',
                    updated_at as 'ÚLTIMA ATUALIZAÇÃO'
                FROM defeitos
                ORDER BY id DESC
            """
            
            df = pd.read_sql_query(query, conn)
            writer = pd.ExcelWriter(filepath, engine='openpyxl')
            df.to_excel(writer, index=False, sheet_name='DEFEITOS')
            
            # Ajusta largura das colunas
            worksheet = writer.sheets['DEFEITOS']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).apply(len).max(), len(col))
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2
                
            writer.close()
            messagebox.showinfo("SUCESSO", f"Dados exportados com sucesso para:\n{filepath}")
            
        except Exception as e:
            messagebox.showerror("ERRO", f"Erro ao exportar dados: {str(e)}")
            
        finally:
            if 'conn' in locals():
                conn.close()

    def run(self):
        """Inicia a aplicação"""
        self.root.mainloop()

if __name__ == "__main__":
    app = DefectManagerApp()
    app.run()