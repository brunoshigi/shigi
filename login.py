import customtkinter as ctk
from PIL import Image
import os

class TelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configuração inicial do CustomTkinter
        ctk.set_appearance_mode("dark")  # Modo escuro
        ctk.set_default_color_theme("blue")  # Tema azul mas pode ser alterado para "green" ou "red" 

        # Configuração da janela
        self.title("Austral - Login")
        self.geometry("600x700")
        self.center_window()
        self.resizable(False, False)

        # Interface principal
        self.setup_ui()

    def center_window(self):
        """Centraliza a janela na tela"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 700) // 2
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="black")
        self.main_frame.pack(padx=50, pady=50, fill="both", expand=True)
        self.configure(fg_color="#0F0F0F")

        

        # Título e subtítulo
        self.create_header()

        # Área de login
        self.create_login_frame()

        # Rodapé
        self.create_footer()

    def create_header(self):
        """Cria o cabeçalho com título e subtítulo"""
        ctk.CTkLabel(self.main_frame, text="AUSTRAL", font=("Helvetica", 32, "bold")).pack(pady=(40, 10))
        ctk.CTkLabel(self.main_frame, text="Sistema de Ferramentas Internas", font=("Helvetica", 16)).pack(pady=(0, 30))

    def create_login_frame(self):
        """Cria o frame com os campos de login"""
        login_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        login_frame.pack(padx=40, pady=20)

        # Campo de usuário
        ctk.CTkEntry(login_frame, placeholder_text="Digite seu usuário").pack(pady=(0, 15))

        # Campo de senha
        ctk.CTkEntry(login_frame, placeholder_text="Digite sua senha", show="•").pack(pady=(0, 10))

        # Botão de login
        ctk.CTkButton(login_frame, text="ENTRAR").pack(pady=(10, 15))

    def create_footer(self):
        """Cria o rodapé"""
        ctk.CTkLabel(
            self.main_frame,
            text="© 2025 Shigi - GitHub @brunoshigi",
            font=("Helvetica", 11),
            text_color="gray"
        ).pack(side="bottom", pady=15)


if __name__ == "__main__":
    app = TelaLogin()
    app.mainloop()
