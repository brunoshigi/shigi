# sistema_austral.py
"""
Sistema Austral - Ferramentas de Gestão
Refatorado para melhor modularidade e clareza.
"""

import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

# Importações de módulos de aplicação
from oms import PedidoSinOMSApp
from defeitos import DefectManagerApp
from fechamento import EmailFechamentoApp
from etiquetas import SistemaEtiquetas
from inventario import InventoryApp
from fundo_fixo import GestorFundoFixo


class SistemaAustral(ctk.CTk):
    """Classe principal do Sistema Austral."""

    def __init__(self):
        super().__init__()
        self.app_mapping = self._mapear_aplicacoes()  # Defina o mapeamento primeiro
        self._configurar_janela()
        self._criar_componentes()

    def _configurar_janela(self):
        """Configurações da janela principal."""
        self.title("SISTEMA AUSTRAL - FERRAMENTAS")
        self.geometry("600x700")
        self.resizable(False, False)
        self._centralizar_janela(600, 700)

    def _centralizar_janela(self, largura, altura):
        """Centraliza a janela na tela."""
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - largura) // 2
        y = (screen_height - altura) // 2
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def _mapear_aplicacoes(self):
        """Mapeia botões às respectivas aplicações."""
        return {
            "CONTROLE PEDIDOS OMS": PedidoSinOMSApp,
            "PLANILHA DEFEITOS": DefectManagerApp,
            "E-MAIL FECHAMENTO": EmailFechamentoApp,
            "GERADOR DE ETIQUETAS": SistemaEtiquetas,
            "INVENTÁRIO": InventoryApp,
            "CONTROLE FUNDO CAIXA": GestorFundoFixo,
        }

    def _criar_componentes(self):
        """Cria os componentes principais da interface."""
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="black")
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        self.configure(fg_color="#0F0F0F")

        self._criar_header()
        self._criar_area_principal()
        self._criar_footer()
        self._atualizar_data_hora()

    def _criar_header(self):
        """Cria o cabeçalho com título e subtítulo."""
        ctk.CTkLabel(
            self.main_frame,
            text="AUSTRAL",
            font=ctk.CTkFont(size=30, weight="bold")
        ).pack(pady=(15, 5))

        ctk.CTkLabel(
            self.main_frame,
            text="Sistema de Ferramentas Internas",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(0, 15))

    def _criar_area_principal(self):
        """Cria a área principal com botões."""
        buttons_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        buttons_frame.pack(pady=10)

        for texto_botao in self.app_mapping.keys():
            self._adicionar_botao(buttons_frame, texto_botao)

    def _adicionar_botao(self, parent, texto_botao):
        """Adiciona um botão ao frame fornecido."""
        ctk.CTkButton(
            parent,
            text=texto_botao,
            width=280,
            height=35,
            corner_radius=6,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=lambda: self._acao_botao(texto_botao)
        ).pack(pady=6)

    def _criar_footer(self):
        """Cria o rodapé."""
        footer = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        footer.pack(side="bottom", fill="x", pady=10)

        self.status_label = ctk.CTkLabel(footer, text="", font=ctk.CTkFont(size=10))
        self.status_label.pack(side="left", padx=10)

        ctk.CTkButton(
            footer,
            text="SAIR",
            command=self._sair_sistema,
            fg_color="red"
        ).pack(side="right", padx=10)

        ctk.CTkLabel(
            footer,
            text="© 2025 Shigi - GitHub @brunoshigi",
            font=ctk.CTkFont(size=12)
        ).pack(side="right", padx=10)

    def _acao_botao(self, nome_botao):
        """Executa a ação associada ao botão."""
        app_cls = self.app_mapping.get(nome_botao)
        if app_cls:
            self._iniciar_aplicacao(app_cls, nome_botao)
        else:
            self._notificar_em_desenvolvimento(nome_botao)

    def _iniciar_aplicacao(self, app_cls, nome_botao):
        """Inicializa a aplicação correspondente ao botão."""
        try:
            app = app_cls()
            if hasattr(app, 'run'):
                app.run()
            else:
                app.mainloop()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir {nome_botao}:\n{e}")

    def _notificar_em_desenvolvimento(self, nome_botao):
        """Notifica que o módulo está em desenvolvimento."""
        messagebox.showinfo(
            "Em Desenvolvimento",
            f"O módulo '{nome_botao}' está em desenvolvimento.\nEm breve estará disponível!"
        )

    def _sair_sistema(self):
        """Confirmação para fechar o sistema."""
        if messagebox.askyesno("Confirmação", "Deseja realmente sair do sistema?"):
            self.destroy()

    def _atualizar_data_hora(self):
        """Atualiza o horário no rodapé."""
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.status_label.configure(text=f"Online | {agora}")
        self.after(1000, self._atualizar_data_hora)


if __name__ == "__main__":
    app = SistemaAustral()
    app.mainloop()
