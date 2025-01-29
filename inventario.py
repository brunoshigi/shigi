import os
import csv
from datetime import datetime
import customtkinter as ctk
from tkinter import ttk, filedialog, messagebox

# Configuração do tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Definição de fontes e estilos
FONT_TITLE = ("Arial Bold", 24)
FONT_LABEL = ("Arial Bold", 14)
FONT_ENTRY = ("Arial", 14)

class InventoryApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("SISTEMA AUSTRAL - CONTROLE DE INVENTÁRIO")
        self.root.geometry("1400x800")
        self.root.resizable(False, False)
        self.root.configure(fg_color="#0F0F0F")
        self.center_window()

        # Frame principal
        self.main_frame = ctk.CTkFrame(
            self.root,
            corner_radius=15,
            fg_color="black"
        )
        self.main_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Título
        ctk.CTkLabel(
            self.main_frame,
            text="CONTROLE DE INVENTÁRIO",
            font=("Helvetica", 20, "bold")
        ).grid(row=0, column=0, pady=(10, 20))

        # Setup
        self.setup_variables()
        self.setup_ui()
        self.entry_codigo.focus()

    def center_window(self):
        """Centraliza a janela principal na tela"""
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 1000  # Reduzido de 1400
        window_height = 600  # Reduzido de 800
        center_x = int((screen_width - window_width) / 2)
        center_y = int((screen_height - window_height) / 2)
        self.root.geometry(f'{window_width}x{window_height}+{center_x}+{center_y}')
        self.root.minsize(900, 500)  # Reduzido de 1200, 700

    def setup_ui(self):
        # Frame de local
        location_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        location_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkLabel(
            location_frame,
            text="LOCAL DA CONTAGEM:",
            font=("Arial Bold", 14)
        ).pack(side="left", padx=20)

        for text, value in [('LOJA', 'loja'), ('ESTOQUE', 'estoque'), ('QUARTINHO', 'quartinho_escada')]:
            ctk.CTkRadioButton(
                location_frame,
                text=text,
                value=value,
                variable=self.local_atual,
                font=("Arial", 14)
            ).pack(side="left", padx=20)

        # Frame de entrada
        input_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        input_frame.grid(row=2, column=0, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(
            input_frame, 
            text="CÓDIGO:",
            font=("Arial Bold", 14)
        ).pack(side="left", padx=10)

        self.entry_codigo = ctk.CTkEntry(
            input_frame,
            textvariable=self.codigo,
            width=300,
            height=35,
            font=("Arial", 14)
        )
        self.entry_codigo.pack(side="left", padx=10)
        self.entry_codigo.bind('<Return>', self.registrar_codigo)

        ctk.CTkButton(
            input_frame,
            text="REGISTRAR",
            command=self.registrar_codigo,
            width=200,
            height=35,
            font=("Arial Bold", 14),
            fg_color="#00AEEF",
            hover_color="#1976D2"
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            input_frame,
            text="DESFAZER",
            command=self.desfazer_ultimo,
            width=200,
            height=35,
            font=("Arial Bold", 14),
            fg_color="red",
            hover_color="#CC3333"
        ).pack(side="left", padx=10)

        # Frame da tabela
        table_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        table_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nsew")
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

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
            columns=('Local', 'Código', 'Quantidade'),
            show='headings',
            style="Treeview"
        )

        for col, width in [('Local', 200), ('Código', 200), ('Quantidade', 100)]:
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=width, anchor="center")

        self.tree.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(table_frame, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Frame de ações
        action_frame = ctk.CTkFrame(self.main_frame, corner_radius=10)
        action_frame.grid(row=4, column=0, padx=20, pady=10, sticky="ew")

        self.totais_label = ctk.CTkLabel(
            action_frame,
            text="TOTAL DE ITENS: 0",
            font=("Arial Bold", 14)
        )
        self.totais_label.pack(side="left", padx=20)

        ctk.CTkButton(
            action_frame,
            text="FINALIZAR INVENTÁRIO",
            command=self.finalizar_inventario,
            width=250,
            height=40,
            font=("Arial Bold", 14),
            fg_color="green",
            hover_color="#45a049"
        ).pack(side="right", padx=20)

        # Footer
        self.footer = ctk.CTkFrame(self.main_frame, fg_color="black")
        self.footer.grid(row=5, column=0, sticky="ew", padx=20, pady=10)
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

        # Configurar expansão
        self.main_frame.grid_rowconfigure(3, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

    def setup_variables(self):
        """Configura as variáveis"""
        self.local_atual = ctk.StringVar(value="loja")
        self.codigo = ctk.StringVar()
        self.inventario = {
            'loja': {},
            'estoque': {},
            'quartinho_escada': {}
        }
        self.historico_codigos = []

    def registrar_codigo(self, event=None):
        """Registra um código no inventário"""
        codigo = self.codigo.get().strip()
        if not codigo:
            return
        
        local = self.local_atual.get()
        self.historico_codigos.append((local, codigo))
        
        if codigo in self.inventario[local]:
            self.inventario[local][codigo] += 1
        else:
            self.inventario[local][codigo] = 1

        self.atualizar_historico()
        self.atualizar_totais()
        self.codigo.set('')  # Limpa o campo
        self.entry_codigo.focus()

    def desfazer_ultimo(self):
        """Desfaz a última leitura"""
        if not self.historico_codigos:
            messagebox.showwarning("Aviso", "Não há códigos para desfazer!")
            return

        local, codigo = self.historico_codigos.pop()
        self.inventario[local][codigo] -= 1
        
        if self.inventario[local][codigo] == 0:
            del self.inventario[local][codigo]

        self.atualizar_historico()
        self.atualizar_totais()

    def atualizar_historico(self):
        """Atualiza a visualização do histórico"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for local in self.inventario:
            for codigo, qtd in self.inventario[local].items():
                self.tree.insert('', 'end', values=(local.upper(), codigo, qtd))

    def atualizar_totais(self):
        """Atualiza o total de itens no label"""
        total_geral = sum(sum(local.values()) for local in self.inventario.values())
        self.totais_label.configure(text=f"TOTAL DE ITENS: {total_geral}")

    def finalizar_inventario(self):
        """Finaliza o inventário e gera os arquivos"""
        if not any(self.inventario.values()):
            messagebox.showwarning("Aviso", "Nenhum item registrado!")
            return

        diretorio = filedialog.askdirectory(
            title="Selecione onde salvar os arquivos do inventário"
        )
        
        if not diretorio:
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Arquivo detalhado
            caminho_detalhado = os.path.join(
                diretorio,
                f'inventario_{timestamp}_detalhado.csv'
            )
            with open(caminho_detalhado, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Local', 'Código', 'Quantidade'])
                for local in self.inventario:
                    for codigo, qtd in self.inventario[local].items():
                        writer.writerow([local.upper(), codigo, qtd])

            # Arquivo consolidado
            caminho_consolidado = os.path.join(
                diretorio,
                f'inventario_{timestamp}_consolidado.csv'
            )
            with open(caminho_consolidado, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Código', 'Quantidade Total'])
                
                codigos_totais = {}
                for local in self.inventario:
                    for codigo, qtd in self.inventario[local].items():
                        codigos_totais[codigo] = codigos_totais.get(codigo, 0) + qtd
                
                for codigo, qtd in sorted(codigos_totais.items()):
                    writer.writerow([codigo, qtd])

            # Lista completa
            caminho_lista = os.path.join(
                diretorio,
                f'inventario_{timestamp}_lista_completa.csv'
            )
            with open(caminho_lista, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Código'])
                for local in self.inventario:
                    for codigo, qtd in self.inventario[local].items():
                        for _ in range(qtd):
                            writer.writerow([codigo])

            self.mostrar_resumo(
                caminho_detalhado,
                caminho_consolidado,
                caminho_lista
            )
            
        except Exception as e:
            messagebox.showerror(
                "Erro",
                "Ocorreu um erro ao salvar os arquivos do inventário!"
            )

    def mostrar_resumo(self, caminho_detalhado, caminho_consolidado, caminho_lista):
        """Mostra o resumo do inventário"""
        total_geral = 0
        resumo = "Resumo do Inventário:\n\n"
        
        for local in self.inventario:
            total_local = sum(self.inventario[local].values())
            qtd_itens = len(self.inventario[local])
            resumo += f"{local.upper()}:\n"
            resumo += f"Total de itens únicos: {qtd_itens}\n"
            resumo += f"Total de peças: {total_local}\n\n"
            total_geral += total_local
        
        resumo += f"TOTAL GERAL DE PEÇAS: {total_geral}\n\n"
        resumo += f"Arquivos salvos como:\n"
        resumo += f"- {caminho_detalhado}\n"
        resumo += f"- {caminho_consolidado}\n"
        resumo += f"- {caminho_lista}"

        messagebox.showinfo("Inventário Finalizado", resumo)
        self.root.destroy()

    def run(self):
        """Inicia o loop principal da aplicação"""
        self.root.mainloop()


if __name__ == '__main__':
    app = InventoryApp()
    app.run()
