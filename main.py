import customtkinter as ctk
from login import TelaLogin
from configuracoes import config

# Configuração inicial de aparência
ctk.set_appearance_mode(config.APPEARANCE_MODE)
ctk.set_default_color_theme(config.COLOR_THEME)

if __name__ == "__main__":
    from app_main import SistemaAustral
    app = TelaLogin()
    app.mainloop()
