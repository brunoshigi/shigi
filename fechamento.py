import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from lojas import lojas 

# Configurações iniciais
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class EmailFechamentoApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da janela principal
        self.title("E-MAIL DE FECHAMENTO AUSTRAL")
        self.geometry("600x700")
        self.center_window()
        self.resizable(False, False)
        self.configure(fg_color="#0F0F0F")  # Cor da borda externa

        # Variáveis
        self.filial_var = ctk.StringVar()
        self.valor_var = ctk.StringVar()
        self.nome_var = ctk.StringVar()

        # Configuração da interface
        self.criar_interface()

    def center_window(self):
        """Centraliza a janela na tela"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 700) // 2
        self.geometry(f"+{x}+{y}")

    def criar_interface(self):
        """Cria a interface principal"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="black")
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Cabeçalho
        ctk.CTkLabel(self.main_frame, text="E-MAIL DE FECHAMENTO", font=("Helvetica", 20, "bold")).pack(pady=(10, 20))

        # Formulário
        form_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        form_frame.pack(pady=20, padx=20, fill="x")

        # Campo Filial
        ctk.CTkLabel(form_frame, text="FILIAL:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        filial_combo = ctk.CTkComboBox(form_frame, values=[x["loja"] for x in lojas], variable=self.filial_var)
        filial_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)

        # Campo Valor Total
        ctk.CTkLabel(form_frame, text="VALOR TOTAL:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        valor_entry = ctk.CTkEntry(form_frame, textvariable=self.valor_var, placeholder_text="Ex: 15000,00")
        valor_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        # Campo Nome
        ctk.CTkLabel(form_frame, text="SEU NOME:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        nome_entry = ctk.CTkEntry(form_frame, textvariable=self.nome_var, placeholder_text="Digite seu nome")
        nome_entry.grid(row=2, column=1, sticky="ew", padx=5, pady=5)

        # Botão para gerar e-mail
        ctk.CTkButton(
            self.main_frame, text="GERAR E-MAIL", command=self.gerar_email, width=150
        ).pack(pady=(10, 20))

        # Área para exibir o e-mail
        self.email_text = ctk.CTkTextbox(self.main_frame, wrap="word", font=("Helvetica", 12), height=200)
        self.email_text.pack(padx=20, pady=10, fill="both", expand=True)
        self.email_text.configure(state="disabled")

        # Botão para copiar o e-mail
        ctk.CTkButton(
            self.main_frame, text="COPIAR E-MAIL", command=self.copiar_email, width=150
        ).pack(pady=(10, 20))

        # Rodapé
        self.criar_footer()

    def criar_footer(self):
        """Cria o rodapé."""
        self.footer = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.footer.pack(side="bottom", fill="x", pady=10)

        # Status e hora
        self.status_label = ctk.CTkLabel(self.footer, text="", font=ctk.CTkFont(size=10))
        self.status_label.pack(side="left", padx=10)

        # Botão de saída
        self.btn_sair = ctk.CTkButton(
            self.footer,
            text="SAIR",
            width=70,
            height=28,
            corner_radius=6,
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.destroy,
            fg_color="red"
        )
        self.btn_sair.pack(side="right", padx=10)

        # Créditos do desenvolvedor
        self.label_footer = ctk.CTkLabel(
            self.footer, text="© 2025 Shigi - GitHub @brunoshigi", font=ctk.CTkFont(size=12)
        )
        self.label_footer.pack(side="right", padx=10)

    def validar_campos(self):
        """Valida os campos antes de gerar o e-mail"""
        if not self.filial_var.get():
            messagebox.showwarning("Atenção", "Selecione uma filial!")
            return False
        if not self.valor_var.get():
            messagebox.showwarning("Atenção", "Digite o valor total!")
            return False
        if not self.nome_var.get().strip():
            messagebox.showwarning("Atenção", "Digite seu nome!")
            return False
        return True

    def gerar_email(self):
        """Gera o e-mail de fechamento"""
        if not self.validar_campos():
            return

        try:
            filial = self.filial_var.get()
            valor = self.valor_var.get().replace(",", ".")
            nome = self.nome_var.get().strip().upper()
            data_atual = datetime.now().strftime("%d/%m/%Y")

            # Formatação do valor
            try:
                valor_formatado = f"R$ {float(valor):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except ValueError:
                messagebox.showerror("Erro", "Valor inválido! Use apenas números e vírgula.")
                return

            # Corpo do e-mail
            email_body = (
                f"Boa noite,\n\n"
                f"Segue o resumo do fechamento do dia {data_atual} da filial {filial}:\n\n"
                f"VALOR TOTAL VENDIDO: {valor_formatado}\n\n"
                "Em anexo, você encontrará o fechamento detalhado e o acumulado diário, ambos referentes ao dia.\n\n"
                "Atenciosamente,\n"
                f"{nome}"
            )

            # Exibe o e-mail gerado
            self.email_text.configure(state="normal")
            self.email_text.delete("1.0", "end")
            self.email_text.insert("1.0", email_body)
            self.email_text.configure(state="disabled")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao gerar o e-mail: {str(e)}")

    def copiar_email(self):
        """Copia o e-mail para a área de transferência"""
        email_body = self.email_text.get("1.0", "end").strip()
        if not email_body:
            messagebox.showwarning("Atenção", "Nenhum e-mail para copiar!")
            return

        self.clipboard_clear()
        self.clipboard_append(email_body)
        messagebox.showinfo("Sucesso", "E-mail copiado para a área de transferência!")

def create_app():
    return EmailFechamentoApp()

if __name__ == "__main__":
    app = create_app()
    app.mainloop()
