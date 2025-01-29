import os
import sqlite3
from datetime import datetime
import pandas as pd
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk

# Configuração do tema e aparência
ctk.set_appearance_mode("dark")  # Modo escuro
ctk.set_default_color_theme("blue")  # Tema azul

class PedidoSinOMSApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("SISTEMA AUSTRAL - CONTROLE DE ENVIO DE PEDIDOS SINOMS")
        self.root.geometry("1400x700")
        self.root.resizable(False, False)
        self.root.configure(fg_color="#0F0F0F")
        self.center_window()  # Abre janela centralizada

        # Frame principal para agrupar a interface
        self.main_frame = ctk.CTkFrame(
            self.root,
            corner_radius=15,
            fg_color="black"
        )
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.main_frame,
            text="CONTROLE DE PEDIDOS SINOMS",
            font=("Helvetica", 20, "bold")
        ).grid(row=0, column=0, pady=(10, 20))

        # Caminho para a pasta assets
        self.assets_path = os.path.join(os.path.dirname(__file__), "assets")

        # Verifica se a pasta assets existe, se não, cria
        if not os.path.exists(self.assets_path):
            os.makedirs(self.assets_path)

        # Caminho completo para o banco de dados
        self.db_path = os.path.join(self.assets_path, "austral.db")

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

    def setup_database(self):
        """Configura o banco de dados SQLite"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data_faturamento TEXT,
                responsavel_faturamento TEXT,
                numero_pedido TEXT UNIQUE,
                status TEXT DEFAULT 'Faturado',
                data_envio TEXT,
                responsavel_envio TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def setup_ui(self):
        """Configura a interface gráfica"""
        # Frame superior para entrada de dados
        entry_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        entry_frame.grid(row=1, column=0, padx=20, pady=20, sticky="ew")

        # Labels e Entradas
        ctk.CTkLabel(entry_frame, text="RESPONSÁVEL:", font=("Arial Bold", 14)).grid(row=0, column=0, padx=10, pady=10)
        self.responsavel_entry = ctk.CTkEntry(entry_frame, font=("Arial", 14), width=300, height=35)
        self.responsavel_entry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(entry_frame, text="NÚMERO DO PEDIDO:", font=("Arial Bold", 14)).grid(row=0, column=2, padx=10, pady=10)
        self.numero_pedido_entry = ctk.CTkEntry(entry_frame, font=("Arial", 14), width=300, height=35)
        self.numero_pedido_entry.grid(row=0, column=3, padx=10, pady=10)
        self.numero_pedido_entry.bind("<Return>", lambda e: self.adicionar_pedido())

        # Botão Registrar
        ctk.CTkButton(
            entry_frame,
            text="REGISTRAR PEDIDO",
            font=("Arial Bold", 14),
            command=self.adicionar_pedido,
            height=45,
            width=250,
            fg_color="#00AEEF",
            hover_color="#1976D2"
        ).grid(row=1, column=0, columnspan=4, pady=20)

        # Frame para a tabela
        table_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        table_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Configuração da Treeview com estilo personalizado
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#2a2d2e",
            foreground="white",
            fieldbackground="#2a2d2e",
            rowheight=32
        )
        style.configure("Treeview.Heading", font=('Arial Bold', 13))
        style.configure("Treeview", font=('Arial', 12))

        self.tree = ttk.Treeview(
            table_frame,
            columns=("DATA", "RESPONSÁVEL", "PEDIDO", "STATUS", "ENVIO", "RESPONSÁVEL ENVIO"),
            show="headings",
            style="Treeview",
            selectmode="extended"  # Permite seleção múltipla
        )

        # Configuração das colunas
        for col in self.tree["columns"]:
            self.tree.column(col, anchor="center", stretch=True, minwidth=150)
            self.tree.heading(col, text=col, anchor="center")

        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Frame inferior para botões de ação
        action_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        action_frame.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Botões de Ação
        ctk.CTkButton(
            action_frame,
            text="MARCAR COMO ENVIADO",
            font=("Arial Bold", 14),
            command=self.marcar_como_enviado,
            width=200,
            fg_color="#00AEEF",
            hover_color="#1976D2"
        ).grid(row=0, column=0, padx=10, pady=10)

        ctk.CTkButton(
            action_frame,
            text="EXCLUIR PEDIDO",
            font=("Arial Bold", 14),
            command=self.excluir_pedido,
            width=200,
            fg_color="red",
            hover_color="#CC3333"
        ).grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkButton(
            action_frame,
            text="EXPORTAR PARA EXCEL",
            font=("Arial Bold", 14),
            command=self.exportar_excel,
            width=200,
            fg_color="green",
            hover_color="#45a049"
        ).grid(row=0, column=2, padx=10, pady=10)

        # Footer com botão SAIR e créditos
        self.footer = ctk.CTkFrame(self.main_frame, fg_color="black")
        self.footer.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 10))
        self.footer.grid_columnconfigure(0, weight=1)

        self.btn_sair = ctk.CTkButton(
            self.footer,
            text="SAIR",
            width=70,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.root.destroy,
            fg_color="red"
        )
        self.btn_sair.pack(side="right", padx=10)

        self.label_footer = ctk.CTkLabel(
            self.footer,
            text="© 2025 Shigi - GitHub @brunoshigi",
            font=ctk.CTkFont(size=12)
        )
        self.label_footer.pack(side="right", padx=10)

        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def adicionar_pedido(self):
        """Adiciona um novo pedido ao banco de dados"""
        data_faturamento = datetime.now().strftime('%d/%m/%Y')
        responsavel = self.responsavel_entry.get().strip().upper()
        numero_pedido = self.numero_pedido_entry.get().strip().upper()

        if not responsavel or not numero_pedido:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO pedidos (data_faturamento, responsavel_faturamento, numero_pedido)
                VALUES (?, ?, ?)
            ''', (data_faturamento, responsavel, numero_pedido))
            conn.commit()
            self.carregar_dados()
            self.numero_pedido_entry.delete(0, 'end')
        except sqlite3.IntegrityError:
            messagebox.showwarning("Erro", "Número de pedido já existe.")
        finally:
            conn.close()

    def carregar_dados(self):
        """Carrega os dados do banco para a tabela"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT data_faturamento, responsavel_faturamento, numero_pedido, 
                   status, data_envio, responsavel_envio 
            FROM pedidos
            ORDER BY data_faturamento DESC
        ''')

        for row in cursor.fetchall():
            valores = list(row)
            # Formatação de datas
            for i in [0, 4]:  # índices das colunas de data
                if valores[i]:
                    try:
                        data = datetime.strptime(valores[i], '%Y-%m-%d').strftime('%d/%m/%Y')
                        valores[i] = data
                    except ValueError:
                        pass

            self.tree.insert("", "end", values=[str(v).upper() if v is not None else "" for v in valores])
        conn.close()

    def marcar_como_enviado(self):
        """Marca um pedido como enviado"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Atenção", "Selecione um ou mais pedidos.")
            return

        responsavel_envio_dialog = ctk.CTkInputDialog(
            text="Digite o nome do responsável pelo envio:",
            title="Responsável pelo Envio"
        )
        responsavel_envio_dialog.geometry("450x200+600+300")  # Centraliza e define tamanho
        responsavel_envio = responsavel_envio_dialog.get_input()

        if responsavel_envio:
            data_envio = datetime.now().strftime("%d/%m/%Y")
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            for item in selected_items:
                pedido = self.tree.item(item)["values"][2]
                cursor.execute('''
                    UPDATE pedidos 
                    SET status="Enviado", data_envio=?, responsavel_envio=? 
                    WHERE numero_pedido=?
                ''', (data_envio, responsavel_envio.upper(), pedido))
            conn.commit()
            conn.close()
            self.carregar_dados()
            messagebox.showinfo("Sucesso", "Pedido(s) marcado(s) como enviado(s)!")

    def excluir_pedido(self):
        """Exclui um pedido selecionado"""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Atenção", "Selecione um ou mais pedidos para excluir.")
            return

        if messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir os {len(selected_items)} pedidos selecionados?"):
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            try:
                for item in selected_items:
                    pedido = self.tree.item(item)["values"][2]
                    cursor.execute('DELETE FROM pedidos WHERE numero_pedido=?', (pedido,))
                conn.commit()
                messagebox.showinfo("Sucesso", "Pedido(s) excluído(s) com sucesso!")
                self.carregar_dados()
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir pedido(s): {str(e)}")
            finally:
                conn.close()

    def exportar_excel(self):
        """Exporta os dados para um arquivo Excel"""
        data_atual = datetime.now().strftime("%d%m%Y")
        nome_arquivo = f"sinoms_{data_atual}.xlsx"

        export_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=nome_arquivo,
            title="Salvar arquivo Excel",
            filetypes=[("Excel files", "*.xlsx")]
        )

        if export_path:
            conn = sqlite3.connect(self.db_path)
            try:
                df = pd.read_sql_query('''
                    SELECT 
                        data_faturamento as "Data Faturamento",
                        responsavel_faturamento as "Responsável Faturamento",
                        numero_pedido as "Número Pedido",
                        status as "Status",
                        data_envio as "Data Envio",
                        responsavel_envio as "Responsável Envio"
                    FROM pedidos
                    ORDER BY data_faturamento DESC
                ''', conn)

                df.to_excel(export_path, index=False)
                messagebox.showinfo("Sucesso", f"Dados exportados para {export_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao exportar dados: {str(e)}")
            finally:
                conn.close()

    def run(self):
        """Inicia a aplicação"""
        self.root.mainloop()

if __name__ == "__main__":
    app = PedidoSinOMSApp()
    app.run()