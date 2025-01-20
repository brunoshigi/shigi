import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

# Configurações da aplicação
APPEARANCE_MODE = "Dark"
COLOR_THEME = "blue"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700

# Lista de lojas físicas
LOJAS = {
    "AUSTRAL MORUMBI": {
        "endereco": "Shopping Morumbi, Av. Roque Petroni Júnior, 1089",
        "bairro_cidade_estado_cep": "Morumbi, São Paulo - SP, 04707-000",
        "piso": "Piso Lazer",
        "telefone": "(11) 5181-5181"
    },
    "AUSTRAL JK IGUATEMI": {
        "endereco": "Shopping JK Iguatemi, Av. Pres. Juscelino Kubitschek, 2041",
        "bairro_cidade_estado_cep": "Vila Olímpia, São Paulo - SP, 04543-011",
        "piso": "Piso Térreo",
        "telefone": "(11) 3152-6000"
    },
    "AUSTRAL IGUATEMI SP": {
        "endereco": "Shopping Iguatemi, Av. Brig. Faria Lima, 2232",
        "bairro_cidade_estado_cep": "Jardim Paulistano, São Paulo - SP, 01489-900",
        "piso": "Piso Faria Lima",
        "telefone": "(11) 3816-6116"
    },
    "AUSTRAL HIGIENÓPOLIS": {
        "endereco": "Shopping Pátio Higienópolis, Av. Higienópolis, 618",
        "bairro_cidade_estado_cep": "Higienópolis, São Paulo - SP, 01238-000",
        "piso": "Piso Higienópolis",
        "telefone": "(11) 3823-2300"
    },
    "AUSTRAL ALPHAVILLE": {
        "endereco": "Shopping Iguatemi Alphaville, Alameda Rio Negro, 111",
        "bairro_cidade_estado_cep": "Alphaville, Barueri - SP, 06454-000",
        "piso": "Piso Rio Negro",
        "telefone": "(11) 2078-8000"
    },
    "AUSTRAL CATARINA OUTLET": {
        "endereco": "Catarina Fashion Outlet, Rod. Pres. Castello Branco, Km 60",
        "bairro_cidade_estado_cep": "São Roque - SP, 18132-000",
        "piso": "Piso Térreo",
        "telefone": "(11) 4136-7000"
    }
}

class SistemaEmailFechamento(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração da janela
        self.title("Sistema Austral - Gerador de E-mail")
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.resizable(False, False)

        # Configurações de tema
        ctk.set_appearance_mode(APPEARANCE_MODE)
        ctk.set_default_color_theme(COLOR_THEME)

        # Variáveis de controle
        self.filial_var = ctk.StringVar(value="")
        self.valor_var = ctk.StringVar(value="")
        self.nome_var = ctk.StringVar(value="")
        self.preview_var = ctk.StringVar(value="")
        self.detalhes_var = ctk.StringVar()

        # Inicialização da interface
        self.criar_interface()
        self.center_window()

        # Bindings para atualização automática do preview
        self.filial_var.trace_add("write", self.atualizar_preview)
        self.valor_var.trace_add("write", self.atualizar_preview)
        self.nome_var.trace_add("write", self.atualizar_preview)

    def criar_interface(self):
        """Cria a interface do sistema."""
        # Container principal
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(padx=20, pady=20, fill="both", expand=True)

        # Header
        self.criar_header()

        # Seção de entrada de dados
        self.criar_secao_entrada()

        # Seção de preview do email
        self.criar_secao_preview()

        # Botões
        self.criar_area_botoes()

        # Footer
        self.criar_footer()

    def criar_header(self):
        """Cria o cabeçalho."""
        header = ctk.CTkFrame(self.main_container)
        header.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            header,
            text="AUSTRAL",
            font=ctk.CTkFont(size=32, weight="bold")
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            header,
            text="Sistema de Geração de E-mails",
            font=ctk.CTkFont(size=14)
        ).pack()

    def criar_secao_entrada(self):
        """Cria a seção de entrada de dados."""
        entrada_frame = ctk.CTkFrame(self.main_container)
        entrada_frame.pack(fill="x", pady=(0, 15))

        # Seleção de Filial
        self.criar_campo_entrada(
            entrada_frame,
            "Loja:",
            lambda parent: ctk.CTkComboBox(
                parent,
                values=list(LOJAS.keys()),
                variable=self.filial_var,
                width=300,
                height=35,
                font=ctk.CTkFont(size=14),
                command=self.atualizar_detalhes
            )
        )

        # Campo Valor
        self.criar_campo_entrada(
            entrada_frame,
            "Valor Total (R$):",
            lambda parent: ctk.CTkEntry(
                parent,
                textvariable=self.valor_var,
                width=300,
                height=35,
                font=ctk.CTkFont(size=14),
                placeholder_text="Digite o valor total"
            )
        )

        # Campo Nome
        self.criar_campo_entrada(
            entrada_frame,
            "Seu Nome:",
            lambda parent: ctk.CTkEntry(
                parent,
                textvariable=self.nome_var,
                width=300,
                height=35,
                font=ctk.CTkFont(size=14),
                placeholder_text="Digite seu nome"
            )
        )

    def criar_campo_entrada(self, parent, label_text, widget_creator):
        """Cria um campo de entrada com label."""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="x", padx=15, pady=8)

        ctk.CTkLabel(
            frame,
            text=label_text,
            font=ctk.CTkFont(size=14),
            width=100,
            anchor="w"
        ).pack(side="left")

        widget = widget_creator(frame)
        widget.pack(side="left", padx=(5, 0))

    def criar_secao_preview(self):
        """Cria a seção de preview do email."""
        preview_frame = ctk.CTkFrame(self.main_container)
        preview_frame.pack(fill="both", expand=True, pady=(0, 15))

        # Título do preview
        ctk.CTkLabel(
            preview_frame,
            text="PRÉVIA DO E-MAIL",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)

        # Campo de texto para o preview
        self.preview_text = ctk.CTkTextbox(
            preview_frame,
            font=ctk.CTkFont(size=14),
            wrap="word",
            height=200
        )
        self.preview_text.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    def criar_area_botoes(self):
        """Cria a área de botões."""
        botoes_frame = ctk.CTkFrame(self.main_container)
        botoes_frame.pack(fill="x", pady=(0, 15))

        # Botão de copiar
        ctk.CTkButton(
            botoes_frame,
            text="COPIAR PARA ÁREA DE TRANSFERÊNCIA",
            command=self.copiar_email,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#4CAF50",
            hover_color="#45a049"
        ).pack(side="left", padx=5, expand=True)

        # Botão de limpar
        ctk.CTkButton(
            botoes_frame,
            text="LIMPAR",
            command=self.limpar_campos,
            font=ctk.CTkFont(size=14),
            height=40,
            fg_color="#FF4444",
            hover_color="#CC3333"
        ).pack(side="left", padx=5, expand=True)

    def criar_footer(self):
        """Cria o rodapé."""
        footer = ctk.CTkFrame(self.main_container)
        footer.pack(fill="x")

        ctk.CTkLabel(
            footer,
            text="© 2024 Shigi - GitHub @brunoshigi",
            font=ctk.CTkFont(size=12)
        ).pack(pady=10)

    def atualizar_preview(self, *args):
        """Atualiza o preview do email."""
        if not all([self.filial_var.get(), self.valor_var.get(), self.nome_var.get()]):
            return

        data_atual = datetime.now().strftime("%d/%m/%Y")
        valor_formatado = self.formatar_moeda(self.valor_var.get())

        corpo_email = (
            f"Boa noite,\n\n"
            f"Segue o resumo do fechamento do dia {data_atual} da filial {self.filial_var.get()}:\n\n"
            f"VALOR TOTAL VENDIDO: {valor_formatado}\n\n"
            f"Em anexo você encontrará:\n"
            f"- FECHAMENTO DETALHADO\n"
            f"- ACUMULADO DIÁRIO\n\n"
            f"Atenciosamente,\n"
            f"{self.nome_var.get()}"
        )

        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", corpo_email)

    def atualizar_detalhes(self, selection=None):
        """Atualiza os detalhes do local selecionado."""
        local = self.filial_var.get()
        if local in LOJAS:
            detalhes = LOJAS[local]
            texto_detalhes = (
                f"Endereço: {detalhes['endereco']}\n"
                f"Local: {detalhes['bairro_cidade_estado_cep']}\n"
                f"Complemento: {detalhes['piso']}\n"
                f"Telefone: {detalhes['telefone']}"
            )
            self.detalhes_var.set(texto_detalhes)
        else:
            self.detalhes_var.set("")
            data_atual = datetime.now().strftime("%d/%m/%Y")
            valor_formatado = self.formatar_moeda(self.valor_var.get())
            local = self.filial_var.get()
            nome = self.nome_var.get()

    def copiar_email(self):
        """Copia o email para a área de transferência."""
        if not self.validar_campos():
            return

        email = self.preview_text.get("1.0", "end-1c")
        self.clipboard_clear()
        self.clipboard_append(email)
        messagebox.showinfo("Sucesso", "E-mail copiado para a área de transferência!")

    def center_window(self):
        """Centraliza a janela na tela do usuário."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - WINDOW_WIDTH) // 2
        y = (screen_height - WINDOW_HEIGHT) // 2
        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def gerar_email(self):
        """Gera o corpo do e-mail."""
        if not self.validar_campos():
            return
        self.detalhes_var.set("")
        data_atual = datetime.now().strftime("%d/%m/%Y")
        local = self.filial_var.get()
        valor_formatado = self.formatar_moeda(self.valor_var.get())
        nome = self.nome_var.get()
        corpo_email = (
            f"Boa noite,\n\n"
            f"Segue o resumo do fechamento do dia {data_atual} da filial {local}:\n\n"
            f"VALOR TOTAL VENDIDO: {valor_formatado}\n\n"
            f"Em anexo você encontrará:\n"
            f"- FECHAMENTO DETALHADO\n"
            f"- ACUMULADO DIÁRIO\n\n"
            f"Atenciosamente,\n"
            f"{nome}"
        )

        self.exibir_preview(corpo_email)

    def exibir_preview(self, corpo_email):
        """Exibe o preview do e-mail."""
        preview = ctk.CTkToplevel(self)
        preview.title("Pré-visualização do E-mail")
        preview.geometry("600x500")
        
        # Centraliza a janela de preview
        preview.update_idletasks()
        width = preview.winfo_width()
        height = preview.winfo_height()
        x = (preview.winfo_screenwidth() // 2) - (width // 2)
        y = (preview.winfo_screenheight() // 2) - (height // 2)
        preview.geometry(f"+{x}+{y}")
        preview.resizable(False, False)

        # Frame principal do preview
        frame_conteudo = ctk.CTkFrame(preview)
        frame_conteudo.pack(padx=20, pady=20, fill="both", expand=True)

        # Título do preview
        ctk.CTkLabel(
            frame_conteudo,
            text="PRÉ-VISUALIZAÇÃO DO E-MAIL",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(15, 20))

        # Campo de texto com o conteúdo do email
        texto = ctk.CTkTextbox(
            frame_conteudo,
            wrap="word",
            font=ctk.CTkFont(size=14),
            height=300
        )
        texto.pack(padx=15, pady=(0, 20), fill="both", expand=True)
        texto.insert("1.0", corpo_email)
        texto.configure(state="disabled")

        # Frame para os botões
        frame_botoes = ctk.CTkFrame(frame_conteudo, fg_color="transparent")
        frame_botoes.pack(fill="x", padx=15, pady=(0, 15))

        # Botões
        ctk.CTkButton(
            frame_botoes,
            text="COPIAR PARA ÁREA DE TRANSFERÊNCIA",
            command=lambda: self.copiar_para_area(corpo_email),
            font=ctk.CTkFont(size=14),
            fg_color="#4CAF50",
            hover_color="#45a049",
            height=40
        ).pack(side="left", padx=5, expand=True)

        ctk.CTkButton(
            frame_botoes,
            text="FECHAR",
            command=preview.destroy,
            font=ctk.CTkFont(size=14),
            fg_color="#FF4444",
            hover_color="#CC3333",
            height=40
        ).pack(side="left", padx=5, expand=True)

    def copiar_para_area(self, texto):
        """Copia o texto para a área de transferência."""
        self.clipboard_clear()
        self.clipboard_append(texto)
        messagebox.showinfo("Sucesso", "E-mail copiado para a área de transferência!")

    def limpar_campos(self):
        """Limpa os campos do formulário."""
        self.filial_var.set("")
        self.valor_var.set("")
        self.nome_var.set("")
        self.detalhes_var.set("")

    def validar_campos(self):
        """Valida os campos obrigatórios."""
        if not self.filial_var.get():
            messagebox.showwarning("Campo Obrigatório", "Por favor, selecione um local.")
            return False
        if not self.valor_var.get():
            messagebox.showwarning("Campo Obrigatório", "Por favor, digite o valor total.")
            return False
        if not self.nome_var.get():
            messagebox.showwarning("Campo Obrigatório", "Por favor, digite seu nome.")
            return False

        # Validação do formato do valor
        try:
            valor = self.valor_var.get().replace(".", "").replace(",", ".")
            float(valor)
        except ValueError:
            messagebox.showwarning("Valor Inválido", "Por favor, digite um valor numérico válido.")
            return False

        return True

    def formatar_moeda(self, valor):
        """Formata o valor como moeda brasileira."""
        try:
            # Remove formatação existente
            valor = valor.replace(".", "").replace(",", ".")
            valor_float = float(valor)
            
            # Formata para o padrão brasileiro
            return f"R$ {valor_float:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
        except ValueError:
            return "R$ 0,00"

if __name__ == "__main__":
    app = SistemaEmailFechamento()
    app.mainloop()