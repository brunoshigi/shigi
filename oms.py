import os
import sqlite3
from datetime import datetime
import pandas as pd
import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog, ttk

# Configuração do tema e aparência
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PedidoSinOMSApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("SISTEMA AUSTRAL - CONTROLE DE ENVIO DE PEDIDOS SINOMS")
        self.root.minsize(1200, 700)  # Tamanho mínimo da janela
        self.center_window()  # Centraliza a janela logo após criar
        
        # Configuração do grid principal
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.setup_database()
        self.setup_ui()
        self.carregar_dados()

    def center_window(self):
        """Centraliza a janela principal na tela"""
        # Obtém as dimensões da tela
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Define o tamanho da janela
        window_width = 1400
        window_height = 800
        
        # Calcula a posição para centralizar
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        
        # Aplica a geometria
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')

    def setup_database(self):
        """Configura o banco de dados SQLite"""
        conn = sqlite3.connect('austral.db')
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
        # Frame superior para entrada de dados
        entry_frame = ctk.CTkFrame(self.root)
        entry_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Labels e Entradas
        ctk.CTkLabel(entry_frame, text="RESPONSÁVEL:", font=("Arial Bold", 14)).grid(row=0, column=0, padx=10, pady=10)
        self.responsavel_entry = ctk.CTkEntry(entry_frame, font=("Arial", 14), width=300, height=35)
        self.responsavel_entry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(entry_frame, text="NÚMERO DO PEDIDO:", font=("Arial Bold", 14)).grid(row=0, column=2, padx=10, pady=10)
        self.numero_pedido_entry = ctk.CTkEntry(entry_frame, font=("Arial", 14), width=300, height=35)
        self.numero_pedido_entry.grid(row=0, column=3, padx=10, pady=10)

        # Botão Registrar
        ctk.CTkButton(
            entry_frame, 
            text="REGISTRAR PEDIDO",
            font=("Arial Bold", 14),
            command=self.adicionar_pedido,
            height=45,
            width=250
        ).grid(row=1, column=0, columnspan=4, pady=20)

        # Frame para a tabela
        table_frame = ctk.CTkFrame(self.root)
        table_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Configuração da Treeview com estilo personalizado
        style = ttk.Style()
        style.configure(
            "Treeview",
            background="#2a2d2e",
            foreground="white",
            fieldbackground="#2a2d2e",
            rowheight=30
        )
        style.configure("Treeview.Heading", font=('Arial Bold', 14))
        style.configure("Treeview", font=('Arial', 12))
        
        self.tree = ttk.Treeview(
            table_frame,
            columns=("DATA", "RESPONSÁVEL", "PEDIDO", "STATUS", "ENVIO", "RESPONSÁVEL ENVIO"),
            show="headings",
            style="Treeview"
        )

        # Configuração das colunas
        for col in self.tree["columns"]:
            self.tree.column(col, anchor="center", width=200, minwidth=150)
            self.tree.heading(col, text=col, anchor="center")

        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Scrollbar
        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Frame inferior para botões de ação
        action_frame = ctk.CTkFrame(self.root)
        action_frame.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Botões de Ação
        ctk.CTkButton(
            action_frame,
            text="MARCAR COMO ENVIADO",
            font=("Arial Bold", 14),
            command=self.marcar_como_enviado,
            width=200
        ).grid(row=0, column=0, padx=10, pady=10)

        ctk.CTkButton(
            action_frame,
            text="EXCLUIR PEDIDO",
            font=("Arial Bold", 14),
            command=self.excluir_pedido,
            width=200,
            fg_color="#FF4444",
            hover_color="#CC3333"
        ).grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkButton(
            action_frame,
            text="EXPORTAR PARA EXCEL",
            font=("Arial Bold", 14),
            command=self.exportar_excel,
            width=200,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).grid(row=0, column=2, padx=10, pady=10)

    def adicionar_pedido(self):
        """Adiciona um novo pedido ao banco de dados"""
        data_faturamento = datetime.now().strftime('%d/%m/%Y')
        responsavel = self.responsavel_entry.get().upper()
        numero_pedido = self.numero_pedido_entry.get().upper()

        if not responsavel or not numero_pedido:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return

        conn = sqlite3.connect('austral.db')
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO pedidos (data_faturamento, responsavel_faturamento, numero_pedido)
                VALUES (?, ?, ?)
            ''', (data_faturamento, responsavel, numero_pedido))
            conn.commit()
            self.carregar_dados()
            # Limpar campos após adicionar
            self.responsavel_entry.delete(0, 'end')
            self.numero_pedido_entry.delete(0, 'end')
        except sqlite3.IntegrityError:
            messagebox.showwarning("Erro", "Número de pedido já existe.")
        finally:
            conn.close()

    def carregar_dados(self):
        """Carrega os dados do banco para a tabela"""
        for row in self.tree.get_children():
            self.tree.delete(row)

        conn = sqlite3.connect('austral.db')
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
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um pedido.")
            return

        pedido = self.tree.item(selected_item)["values"][2]
        
        # Dialog personalizado para entrada do responsável
        dialog = ctk.CTkInputDialog(
            text="Digite o nome do responsável pelo envio:",
            title="Responsável pelo Envio"
        )
        responsavel_envio = dialog.get_input()

        if responsavel_envio:
            data_envio = datetime.now().strftime("%d/%m/%Y")
            conn = sqlite3.connect('austral.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE pedidos 
                SET status="Enviado", data_envio=?, responsavel_envio=? 
                WHERE numero_pedido=?
            ''', (data_envio, responsavel_envio.upper(), pedido))
            conn.commit()
            conn.close()
            self.carregar_dados()

    def excluir_pedido(self):
        """Exclui um pedido selecionado"""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Atenção", "Selecione um pedido para excluir.")
            return

        pedido = self.tree.item(selected_item)["values"][2]
        if messagebox.askyesno("Confirmar Exclusão", f"Deseja realmente excluir o pedido {pedido}?"):
            conn = sqlite3.connect('austral.db')
            cursor = conn.cursor()
            try:
                cursor.execute('DELETE FROM pedidos WHERE numero_pedido=?', (pedido,))
                conn.commit()
                messagebox.showinfo("Sucesso", "Pedido excluído com sucesso!")
                self.carregar_dados()
            except sqlite3.Error as e:
                messagebox.showerror("Erro", f"Erro ao excluir pedido: {str(e)}")
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
            conn = sqlite3.connect('austral.db')
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