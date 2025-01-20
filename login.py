import customtkinter as ctk
import sqlite3
from PIL import Image
import os

# Configurações
APPEARANCE = {
    "mode": "dark",
    "theme": "blue",
    "corner_radius": 10
}

CORES = {
    "bg_primary": "#1a1a1a",
    "accent": "#0066cc",
    "accent_hover": "#0052a3",
    "error": "#ff4444",
    "success": "#4CAF50"
}

FONT = {
    "title": ("Helvetica", 32, "bold"),
    "subtitle": ("Helvetica", 16, "normal"),
    "input": ("Helvetica", 14, "normal"),
    "button": ("Helvetica", 14, "bold"),
    "message": ("Helvetica", 13, "normal"),
    "footer": ("Helvetica", 11, "normal")
}

DIMENSIONS = {
    "window": {
        "width": 600,
        "height": 700
    },
    "input": {
        "width": 300,
        "height": 45
    },
    "button": {
        "width": 200,
        "height": 45
    }
}

DB_PATH = "austral.db"

class TelaLogin(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurações iniciais do CustomTkinter
        ctk.set_appearance_mode(APPEARANCE["mode"])
        ctk.set_default_color_theme(APPEARANCE["theme"])

        # Configuração da janela
        self.title("Austral - Login")
        self.geometry(f"{DIMENSIONS['window']['width']}x{DIMENSIONS['window']['height']}")
        self.center_window()
        self.resizable(False, False)

        # Variáveis
        self.mostrar_senha = ctk.BooleanVar(value=False)
        self.setup_ui()
        
        # Bindings
        self.bind("<Return>", lambda event: self.realizar_login())
        self.entry_usuario.focus()

    def center_window(self):
        """Centraliza a janela na tela"""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - DIMENSIONS['window']['width']) // 2
        y = (screen_height - DIMENSIONS['window']['height']) // 2
        self.geometry(f"+{x}+{y}")

    def setup_ui(self):
        """Configura a interface do usuário"""
        # Frame principal com gradiente
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=CORES["bg_primary"],
            corner_radius=15
        )
        self.main_frame.pack(padx=30, pady=30, fill="both", expand=True)

        # Logo e Título
        try:
            logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
            if os.path.exists(logo_path):
                logo = ctk.CTkImage(Image.open(logo_path), size=(100, 100))
                logo_label = ctk.CTkLabel(self.main_frame, image=logo, text="")
                logo_label.pack(pady=(30, 0))
        except Exception:
            pass

        # Título e Subtítulo
        self.create_header()
        
        # Frame de login
        self.create_login_frame()
        
        # Rodapé
        self.create_footer()

    def create_header(self):
        """Cria o cabeçalho com título e subtítulo"""
        ctk.CTkLabel(
            self.main_frame,
            text="AUSTRAL",
            font=ctk.CTkFont(*FONT["title"])
        ).pack(pady=(40, 10))

        ctk.CTkLabel(
            self.main_frame,
            text="Sistema de Ferramentas Internas",
            font=ctk.CTkFont(*FONT["subtitle"])
        ).pack(pady=(0, 30))

    def create_login_frame(self):
        """Cria o frame com os campos de login"""
        login_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color="transparent"
        )
        login_frame.pack(padx=40, pady=20)

        # Campo de usuário
        self.entry_usuario = ctk.CTkEntry(
            login_frame,
            placeholder_text="Digite seu usuário",
            width=DIMENSIONS["input"]["width"],
            height=DIMENSIONS["input"]["height"],
            font=ctk.CTkFont(*FONT["input"]),
            corner_radius=APPEARANCE["corner_radius"]
        )
        self.entry_usuario.pack(pady=(0, 15))

        # Campo de senha
        self.entry_senha = ctk.CTkEntry(
            login_frame,
            placeholder_text="Digite sua senha",
            show="•",
            width=DIMENSIONS["input"]["width"],
            height=DIMENSIONS["input"]["height"],
            font=ctk.CTkFont(*FONT["input"]),
            corner_radius=APPEARANCE["corner_radius"]
        )
        self.entry_senha.pack(pady=(0, 10))

        # Checkbox mostrar senha
        ctk.CTkCheckBox(
            login_frame,
            text="Mostrar senha",
            variable=self.mostrar_senha,
            command=self.toggle_senha,
            font=ctk.CTkFont(*FONT["message"]),
            checkbox_width=20,
            checkbox_height=20
        ).pack(pady=(0, 20))

        # Botão de login
        ctk.CTkButton(
            login_frame,
            text="ENTRAR",
            command=self.realizar_login,
            width=DIMENSIONS["button"]["width"],
            height=DIMENSIONS["button"]["height"],
            corner_radius=APPEARANCE["corner_radius"],
            font=ctk.CTkFont(*FONT["button"]),
            fg_color=CORES["accent"],
            hover_color=CORES["accent_hover"]
        ).pack(pady=(10, 15))

        # Label para mensagens de erro/sucesso
        self.label_mensagem = ctk.CTkLabel(
            login_frame,
            text="",
            font=ctk.CTkFont(*FONT["message"])
        )
        self.label_mensagem.pack(pady=(0, 10))

    def create_footer(self):
        """Cria o rodapé"""
        ctk.CTkLabel(
            self.main_frame,
            text="© 2025 Shigi - GitHub @brunoshigi",
            font=ctk.CTkFont(*FONT["footer"]),
            text_color="gray"
        ).pack(side="bottom", pady=15)

    def toggle_senha(self):
        """Alterna a visibilidade da senha"""
        self.entry_senha.configure(show="" if self.mostrar_senha.get() else "•")

    def realizar_login(self):
        """Realiza a autenticação do usuário"""
        usuario = self.entry_usuario.get().strip()
        senha = self.entry_senha.get().strip()

        if not usuario or not senha:
            self.mostrar_mensagem("Por favor, preencha todos os campos", "error")
            return

        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT * FROM usuarios WHERE usuario = ? AND senha = ?",
                (usuario, senha)
            )
            
            if cursor.fetchone():
                self.mostrar_mensagem("Login realizado com sucesso!", "success")
                self.after(1000, self.abrir_sistema_principal)
            else:
                self.mostrar_mensagem("Usuário ou senha incorretos", "error")
                
        except sqlite3.Error as e:
            self.mostrar_mensagem("Erro ao conectar ao banco de dados", "error")
        finally:
            conn.close()

    def mostrar_mensagem(self, mensagem, tipo):
        """Exibe mensagem de erro ou sucesso"""
        cor = CORES["success"] if tipo == "success" else CORES["error"]
        self.label_mensagem.configure(text=mensagem, text_color=cor)

    def abrir_sistema_principal(self):
        """Abre o sistema principal"""
        self.destroy()
        try:
            from app_main import SistemaAustral
            app_principal = SistemaAustral()
            app_principal.mainloop()
        except ImportError:
            print("Erro ao importar o sistema principal")

if __name__ == "__main__":
    app = TelaLogin()
    app.mainloop()