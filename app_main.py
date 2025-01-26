import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

# Configurações gerais
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Importações dos módulos de aplicação
from oms import PedidoSinOMSApp
from defeitos import DefectManagerApp
from fechamento import EmailFechamentoApp
from etiquetas import SistemaEtiquetas
from inventario import InventoryApp
from fundo_fixo import GestorFundoFixo

class SistemaAustral(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações da janela principal
        self.title("SISTEMA AUSTRAL - FERRAMENTAS")
        self.geometry("600x700")
        self.resizable(False, False)

        # Centralização na tela
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 750) // 2
        self.geometry(f"600x700+{x}+{y}")

        # Frame principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="black")
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        self.configure(fg_color="#0F0F0F")

        # Cria header, área principal e footer
        self.criar_header()
        self.criar_area_principal()
        self.criar_footer()

        # Atualiza hora no rodapé
        self.atualiza_data_hora()

        # Mapeamento de botões para aplicações
        self.app_mapping = {
            "CONTROLE PEDIDOS OMS": PedidoSinOMSApp,
            "PLANILHA DEFEITOS": DefectManagerApp,
            "E-MAIL FECHAMENTO": EmailFechamentoApp,
            "GERADOR DE ETIQUETAS": SistemaEtiquetas,
            "INVENTÁRIO": InventoryApp,
            "CONTROLE FUNDO CAIXA": GestorFundoFixo
        }

    def criar_header(self):
        """Cria o cabeçalho com título e subtítulo."""
        self.label_titulo = ctk.CTkLabel(
            self.main_frame,
            text="AUSTRAL",
            font=ctk.CTkFont(size=30, weight="bold")
        )
        self.label_titulo.pack(pady=(15, 5))

        self.label_subtitulo = ctk.CTkLabel(
            self.main_frame,
            text="Sistema de Ferramentas Internas",
            font=ctk.CTkFont(size=14)
        )
        self.label_subtitulo.pack(pady=(0, 15))

    def criar_area_principal(self):
        """Cria a área de botões."""
        self.buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.buttons_frame.pack(pady=10)

        botoes = [
            "CONTROLE PEDIDOS OMS",
            "PLANILHA DEFEITOS",
            "E-MAIL FECHAMENTO",
            "GERADOR DE ETIQUETAS",
            "INVENTÁRIO",
            "CONTROLE FUNDO CAIXA",
        ]

        for texto_botao in botoes:
            btn = ctk.CTkButton(
                self.buttons_frame,
                text=texto_botao,
                width=280,
                height=35,
                corner_radius=6,
                font=ctk.CTkFont(size=12, weight="bold"),
                command=lambda t=texto_botao: self.acao_botao(t)
            )
            btn.pack(pady=6)

    def criar_footer(self):
        """Cria o rodapé."""
        self.footer = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.footer.pack(side="bottom", fill="x", pady=10)

        # Status e hora
        self.status_label = ctk.CTkLabel(
            self.footer,
            text="",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="left", padx=10)

        # Botão de saída
        self.sair_button = ctk.CTkButton(
            self.footer,
            text="SAIR",
            command=self.sair_sistema,
            fg_color="red"
        )
        self.sair_button.pack(side="right", padx=10)

        # Créditos do desenvolvedor
        self.label_footer = ctk.CTkLabel(
            self.footer,
            text="© 2025 Shigi - GitHub @brunoshigi",
            font=ctk.CTkFont(size=12)
        )
        self.label_footer.pack(side="right", padx=10)

    def acao_botao(self, nome_botao):
        """Manipula ações dos botões."""
        # Verifica se o botão tem uma aplicação correspondente
        if nome_botao in self.app_mapping:
            try:
                # Cria uma instância da aplicação correspondente
                app = self.app_mapping[nome_botao]()
                
                # Para as aplicações que não herdam de CTk diretamente
                if hasattr(app, 'run'):
                    app.run()
                else:
                    app.mainloop()
                    
            except Exception as e:
                messagebox.showerror(
                    "Erro",
                    f"Erro ao abrir {nome_botao}:\n{str(e)}"
                )
        else:
            messagebox.showinfo(
                "Em Desenvolvimento",
                f"O módulo '{nome_botao}' está em desenvolvimento.\nEm breve estará disponível!"
            )

    def sair_sistema(self):
        """Fecha o sistema com confirmação."""
        if messagebox.askyesno("Confirmação", "Deseja realmente sair do sistema?"):
            self.destroy()

    def atualiza_data_hora(self):
        """Atualiza o horário no rodapé."""
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.status_label.configure(text=f"Online | {agora}")
        self.after(1000, self.atualiza_data_hora)

if __name__ == "__main__":
    app = SistemaAustral()
    app.mainloop()