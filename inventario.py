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
        
        # Configurações da janela
        self.root.title("INVENTÁRIO - CONTAGEM DE ESTOQUE")
        self.center_window()
        
        # Variáveis
        self.local_atual = ctk.StringVar(value="loja")
        self.codigo = ctk.StringVar()
        self.inventario = {
            'loja': {},
            'estoque': {},
            'quartinho_escada': {}
        }
        self.historico_codigos = []
        
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
        """Configura a interface do usuário"""
        # Container principal
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)  # Reduzido de 20, 20

        # Título
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="SISTEMA DE INVENTÁRIO",
            font=FONT_TITLE
        )
        title_label.pack(pady=(0, 20))

        # Frame de seleção de local
        self.create_location_frame()
        
        # Frame de entrada
        self.create_input_frame()
        
        # Frame de histórico
        self.create_history_frame()
        
        # Frame de ações e status
        self.create_status_frame()
        self.create_action_frame()

    def create_location_frame(self):
        """Cria o frame de seleção de local"""
        location_frame = ctk.CTkFrame(self.main_frame)
        location_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(
            location_frame,
            text="LOCAL DA CONTAGEM:",
            font=FONT_LABEL
        ).pack(side="left", padx=20)

        locations = [
            ('LOJA', 'loja'),
            ('ESTOQUE', 'estoque'),
            ('QUARTINHO ESCADA', 'quartinho_escada')
        ]

        for text, value in locations:
            ctk.CTkRadioButton(
                location_frame,
                text=text,
                value=value,
                variable=self.local_atual,
                font=FONT_LABEL
            ).pack(side="left", padx=20)

    def create_input_frame(self):
        """Cria o frame de entrada de códigos"""
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(fill="x", padx=10, pady=10)

        # Label código
        ctk.CTkLabel(
            input_frame,
            text="CÓDIGO:",
            font=FONT_LABEL
        ).pack(side="left", padx=10)

        # Entry código
        self.entry_codigo = ctk.CTkEntry(
            input_frame,
            textvariable=self.codigo,
            width=200,  # Reduzido de 300
            height=35,  # Reduzido de 40
            font=FONT_ENTRY
        )
        self.entry_codigo.pack(side="left", padx=10)
        self.entry_codigo.bind('<Return>', self.registrar_codigo)

        # Botões
        ctk.CTkButton(
            input_frame,
            text="REGISTRAR",
            command=self.registrar_codigo,
            width=120,  # Reduzido de 150
            height=35,  # Reduzido de 40
            font=FONT_LABEL
        ).pack(side="left", padx=5)  # Reduzido padding

        ctk.CTkButton(
            input_frame,
            text="DESFAZER",
            command=self.desfazer_ultimo,
            width=120,  # Reduzido de 150
            height=35,  # Reduzido de 40
            font=FONT_LABEL,
            fg_color="#FF4444",
            hover_color="#CC3333"
        ).pack(side="left", padx=5)  # Reduzido padding

    def create_history_frame(self):
        """Cria o frame de histórico"""
        history_frame = ctk.CTkFrame(self.main_frame)
        history_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            history_frame,
            text="HISTÓRICO DE LEITURAS",
            font=FONT_LABEL
        ).pack(pady=10)

        # Frame para o Treeview e Scrollbar
        tree_frame = ctk.CTkFrame(history_frame)
        tree_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Estilo para o Treeview
        style = ttk.Style()
        style.configure(
            "Treeview",
            font=('Arial', 12),
            rowheight=30,
            background="#2a2d2e",
            foreground="white",
            fieldbackground="#2a2d2e"
        )
        style.configure("Treeview.Heading", font=('Arial Bold', 14))

        # Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('Local', 'Código', 'Quantidade'),
            show='headings',
            height=15
        )

        # Configuração das colunas
        self.tree.heading('Local', text='LOCAL', anchor="w")
        self.tree.heading('Código', text='CÓDIGO', anchor="w")
        self.tree.heading('Quantidade', text='QUANTIDADE', anchor="e")

        self.tree.column('Local', width=200, anchor="w")     # Reduzido de 300
        self.tree.column('Código', width=200, anchor="w")    # Reduzido de 300
        self.tree.column('Quantidade', width=100, anchor="e") # Reduzido de 200

        # Scrollbars
        vsb = ctk.CTkScrollbar(tree_frame, command=self.tree.yview)
        vsb.pack(side="right", fill="y")
        
        hsb = ctk.CTkScrollbar(history_frame, orientation="horizontal", command=self.tree.xview)
        hsb.pack(fill="x", padx=10)
        
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.tree.pack(side="left", fill="both", expand=True)

    def create_status_frame(self):
        """Cria o frame de status"""
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.pack(fill="x", padx=10, pady=10)
        
        self.status_var = ctk.StringVar()
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            textvariable=self.status_var,
            font=FONT_LABEL
        )
        self.status_label.pack(side="left", padx=10)

    def create_action_frame(self):
        """Cria o frame de ações finais"""
        action_frame = ctk.CTkFrame(self.main_frame)
        action_frame.pack(fill="x", padx=10, pady=10)

        # Totais
        self.totais_var = ctk.StringVar()
        ctk.CTkLabel(
            action_frame,
            textvariable=self.totais_var,
            font=FONT_LABEL
        ).pack(side="left", padx=10)

        # Botão finalizar
        ctk.CTkButton(
            action_frame,
            text="FINALIZAR INVENTÁRIO",
            command=self.finalizar_inventario,
            width=250,
            height=40,
            font=FONT_LABEL,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side="right", padx=10)

        self.atualizar_totais()

    def atualizar_totais(self):
        """Atualiza os totais mostrados na interface"""
        total_geral = sum(sum(local.values()) for local in self.inventario.values())
        self.totais_var.set(f"TOTAL DE ITENS: {total_geral}")

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
        self.status_var.set(
            f'Código {codigo} registrado no {local.upper()}. '
            f'Total: {self.inventario[local][codigo]}'
        )
        self.codigo.set('')
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
        self.status_var.set(f'Última leitura desfeita: {codigo} do {local.upper()}')

    def atualizar_historico(self):
        """Atualiza a visualização do histórico"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for local in self.inventario:
            for codigo, qtd in self.inventario[local].items():
                self.tree.insert('', 'end', values=(local.upper(), codigo, qtd))

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
