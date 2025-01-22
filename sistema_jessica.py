import os
from datetime import datetime
from decimal import Decimal
import json
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from dataclasses import dataclass
from typing import List, Dict, Optional

# Configurações básicas de fonte
FONT_TITLE = ("Arial", 19, "bold")
FONT_LABEL = ("Arial", 12)
FONT_ENTRY = ("Arial", 12)
FONT_SECTION = ("Arial", 14, "bold")

class ConfigManager:
    def __init__(self):
        self.config = {'database.path': 'austral.db'}
    def get(self, key, default=None):
        return self.config.get(key, default)

@dataclass
class Venda:
    """Representa uma venda individual com todos os seus detalhes."""
    vendedor: str
    tipo_pagamento: str
    detalhes_pagamento: str
    bandeira: str
    valor: Decimal
    numero_boleta: str
    troca: bool
    data: str = None

    def __post_init__(self):
        if self.data is None:
            self.data = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.valor = Decimal(str(self.valor)).quantize(Decimal('0.01'))

    def to_dict(self) -> dict:
        return {
            'vendedor': self.vendedor,
            'tipo_pagamento': self.tipo_pagamento,
            'detalhes_pagamento': self.detalhes_pagamento,
            'bandeira': self.bandeira,
            'valor': str(self.valor),
            'numero_boleta': self.numero_boleta,
            'troca': self.troca,
            'data': self.data
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Venda':
        return cls(
            vendedor=data['vendedor'],
            tipo_pagamento=data['tipo_pagamento'],
            detalhes_pagamento=data['detalhes_pagamento'],
            bandeira=data['bandeira'],
            valor=Decimal(data['valor']),
            numero_boleta=data['numero_boleta'],
            troca=data['troca'],
            data=data['data']
        )

class SistemaCaixa:
    """Sistema de gerenciamento de vendas com interface gráfica"""

    VENDEDORES = ["João", "Maria", "Pedro", "Ana"]
    PAGAMENTOS_COMPLETOS = [
        "Dinheiro", "PIX", "Troca",
        "Visa - Débito", "Visa - Crédito",
        "Mastercard - Débito", "Mastercard - Crédito",
        "Elo - Débito", "Elo - Crédito",
        "American Express - Débito", "American Express - Crédito",
        "Hipercard - Débito", "Hipercard - Crédito"
    ]
    OBSERVACOES_OPCOES = [
        "PDV", "POS Rede", "POS PagSeguro",
        "POS Getnet", "Link Rede", "Outro"
    ]

    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("Sistema de Caixa - Austral")
        self.master.geometry("1200x800")  # Aumentado para melhor visualização
        self.config = ConfigManager()
        self.ARQUIVO_BACKUP = f"vendas_{datetime.now().strftime('%Y%m%d')}.json"
        self.vendas: List[Venda] = []
        self.selected_item = None
        self.selected_id = None

        self._criar_interface()
        self._configurar_atalhos()
        self.carregar_vendas()
        self.atualizar_resumo()

    def _criar_interface(self):
        # Criar o frame principal com uma cor de fundo
        self.main_frame = ctk.CTkFrame(self.master)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Adicionar título principal
        titulo = ctk.CTkLabel(self.main_frame, text="Sistema de Vendas", font=FONT_TITLE)
        titulo.pack(pady=(0, 20))

        # Criar os componentes da interface
        self._criar_campos_entrada()
        self._criar_botoes()
        self._criar_area_principal()

    def _criar_campos_entrada(self):
        # Frame principal para os campos de entrada
        frame_campos = ctk.CTkFrame(self.main_frame)
        frame_campos.pack(fill=tk.X, padx=10, pady=10)

        # Frame esquerdo para dados da venda
        frame_esquerdo = ctk.CTkFrame(frame_campos)
        frame_esquerdo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Frame direito para dados do pagamento
        frame_direito = ctk.CTkFrame(frame_campos)
        frame_direito.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Título para dados da venda
        ctk.CTkLabel(frame_esquerdo, text="Dados da Venda", font=FONT_SECTION).pack(pady=5)
        
        # Campos do lado esquerdo (dados da venda)
        campos_esquerda = [
            ("Vendedor:", "vendedor_cb", self.VENDEDORES, False),
            ("Nº Boleta/Recibo:", "boleta_entry", None, False),
            ("Valor (R$):", "valor_entry", None, False),
        ]
        
        # Título para dados do pagamento
        ctk.CTkLabel(frame_direito, text="Dados do Pagamento", font=FONT_SECTION).pack(pady=5)
        
        # Campos do lado direito (dados do pagamento)
        campos_direita = [
            ("Forma de Pagamento:", "pagamento_cb", self.PAGAMENTOS_COMPLETOS, False),
            ("Observações:", "observacoes_cb", self.OBSERVACOES_OPCOES, True),
        ]

        self.widgets_entrada = []

        # Criar campos do lado esquerdo
        for i, (label, var_name, values, editable) in enumerate(campos_esquerda):
            frame_campo = ctk.CTkFrame(frame_esquerdo)
            frame_campo.pack(fill=tk.X, padx=10, pady=8)
            
            ctk.CTkLabel(frame_campo, text=label, anchor="w", width=120).pack(side=tk.LEFT, padx=5)
            
            if values is not None:
                widget = ctk.CTkOptionMenu(frame_campo, values=values, width=250)
                widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                if values:
                    widget.set(values[0])
            else:
                widget = ctk.CTkEntry(frame_campo, width=250)
                widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            setattr(self, var_name, widget)
            self.widgets_entrada.append(widget)

        # Criar campos do lado direito
        for i, (label, var_name, values, editable) in enumerate(campos_direita):
            frame_campo = ctk.CTkFrame(frame_direito)
            frame_campo.pack(fill=tk.X, padx=10, pady=8)
            
            ctk.CTkLabel(frame_campo, text=label, anchor="w", width=120).pack(side=tk.LEFT, padx=5)
            
            if values is not None:
                widget = ctk.CTkOptionMenu(frame_campo, values=values, width=250)
                widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
                if values:
                    widget.set(values[0])
            else:
                widget = ctk.CTkEntry(frame_campo, width=250)
                widget.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
            
            setattr(self, var_name, widget)
            self.widgets_entrada.append(widget)

        # Configurar navegação por Tab e Enter
        for idx, widget in enumerate(self.widgets_entrada[:-1]):
            widget.bind("<Return>", lambda e, nxt=self.widgets_entrada[idx+1]: nxt.focus_set())
            widget.bind("<Tab>", lambda e, nxt=self.widgets_entrada[idx+1]: nxt.focus_set())
        self.widgets_entrada[-1].bind("<Return>", lambda e: self.adicionar_venda())

    def _criar_botoes(self):
        frame_botoes = ctk.CTkFrame(self.main_frame)
        frame_botoes.pack(fill=tk.X, padx=10, pady=10)

        # Lista de botões com seus textos, comandos e atalhos
        botoes_info = [
            ("Adicionar Venda (Alt+A)", self.adicionar_venda, "<Alt-a>"),
            ("Excluir Venda (Alt+E)", self.excluir_venda, "<Alt-e>"),
            ("Gerar Relatório (Alt+R)", self.gerar_relatorio, "<Alt-r>"),
            ("Limpar Campos (Alt+L)", self.limpar_campos, "<Alt-l>")
        ]

        # Criar os botões com espaçamento uniforme
        for texto, comando, atalho in botoes_info:
            btn = ctk.CTkButton(
                frame_botoes,
                text=texto,
                command=comando,
                width=200,
                height=35
            )
            btn.pack(side=tk.LEFT, padx=10, pady=5)
            self.master.bind(atalho, lambda e, cmd=comando: cmd())

    def _criar_area_principal(self):
        # Frame para conter a tabela e o resumo
        frame_principal = ctk.CTkFrame(self.main_frame)
        frame_principal.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Frame para a tabela (lado esquerdo)
        frame_tabela = ttk.Frame(frame_principal)
        frame_tabela.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Criar Treeview com colunas
        colunas = [
            ("Vendedor", 100),
            ("Tipo", 100),
            ("Detalhes", 150),
            ("Bandeira", 100),
            ("Valor", 100),
            ("Boleta", 100),
            ("Troca", 60),
            ("Data", 150)
        ]

        self.tree = ttk.Treeview(frame_tabela, columns=[col[0] for col in colunas], show='headings')
        
        # Configurar colunas
        for col, width in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')

        # Adicionar scrollbar
        scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        # Posicionar elementos
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Criar frame de resumo (lado direito)
        frame_resumo = ctk.CTkFrame(frame_principal)
        frame_resumo.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))

        # Título do resumo
        ctk.CTkLabel(frame_resumo, text="Resumo de Vendas", font=FONT_SECTION).pack(pady=10)

        # Área de texto do resumo
        self.resumo_text = ctk.CTkTextbox(frame_resumo, width=300, height=400)
        self.resumo_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Configurar eventos da tabela
        self.tree.bind('<<TreeviewSelect>>', self.on_select)
        self.tree.bind('<Double-1>', self.on_double_click)
        self.tree.bind('<Delete>', lambda e: self.excluir_venda())

    def adicionar_venda(self):
        try:
            dados_venda = self._coletar_dados_venda()
            if not dados_venda:
                return

            venda = Venda(**dados_venda)
            self.vendas.append(venda)
            self._adicionar_venda_treeview(venda)
            self.atualizar_resumo()
            self.salvar_vendas()
            self.limpar_campos()

            messagebox.showinfo("Sucesso", "Venda registrada com sucesso!")
        except ValueError as e:
            messagebox.showerror("Erro", str(e))

    def _coletar_dados_venda(self) -> Optional[Dict]:
        vendedor = self.vendedor_cb.get()
        pagamento_escolhido = self.pagamento_cb.get()

        if not vendedor or not pagamento_escolhido:
            messagebox.showerror("Erro", "Selecione o vendedor e o tipo de pagamento.")
            return None

        try:
            valor = Decimal(self.valor_entry.get().replace(',', '.'))
            if pagamento_escolhido != "Troca" and valor <= 0:
                raise ValueError
        except:
            if pagamento_escolhido == "Troca":
                valor = Decimal('0.00')
            else:
                messagebox.showerror("Erro", "Valor inválido. Digite um número válido maior que zero.")
                return None

        tipo_pagamento, bandeira, detalhes_pagamento, troca = self._processar_pagamento(pagamento_escolhido)

        numero_boleta = self.boleta_entry.get().strip()
        if not numero_boleta:
            messagebox.showerror("Erro", "Número da Boleta/Recibo é obrigatório.")
            return None

        return {
            'vendedor': vendedor,
            'tipo_pagamento': tipo_pagamento,
            'detalhes_pagamento': detalhes_pagamento or self.observacoes_cb.get(),
            'bandeira': bandeira,
            'valor': valor,
            'numero_boleta': numero_boleta,
            'troca': troca
        }
    
    def _processar_pagamento(self, pagamento_escolhido: str) -> tuple:
        if pagamento_escolhido == "Dinheiro":
            return "Dinheiro", "", "", False
        elif pagamento_escolhido == "PIX":
            return "PIX", "", "", False
        elif pagamento_escolhido == "Troca":
            return "Troca", "", "", True
        else:
            partes = pagamento_escolhido.split(" - ")
            if len(partes) == 2:
                return "Cartão", partes[0], partes[1], False
            else:
                return pagamento_escolhido, "", "", False

    def _adicionar_venda_treeview(self, venda: Venda):
        self.tree.insert('', tk.END, values=(
            venda.vendedor,
            venda.tipo_pagamento,
            venda.detalhes_pagamento,
            venda.bandeira,
            f"R$ {venda.valor:.2f}",
            venda.numero_boleta,
            "Sim" if venda.troca else "Não",
            venda.data
        ))

    def excluir_venda(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showerror("Erro", "Nenhuma venda selecionada para excluir.")
            return

        if messagebox.askyesno("Confirmação", "Tem certeza que deseja excluir a venda selecionada?"):
            index = self.tree.index(selected_item)
            self.tree.delete(selected_item)
            del self.vendas[index]
            self.atualizar_resumo()
            self.salvar_vendas()
            messagebox.showinfo("Sucesso", "Venda excluída com sucesso!")

    def limpar_campos(self):
        self.vendedor_cb.set(self.VENDEDORES[0])
        self.pagamento_cb.set(self.PAGAMENTOS_COMPLETOS[0])
        self.observacoes_cb.set(self.OBSERVACOES_OPCOES[0])
        self.valor_entry.delete(0, tk.END)
        self.boleta_entry.delete(0, tk.END)
        self.vendedor_cb.focus_set()

    def gerar_relatorio(self):
        if not self.vendas:
            messagebox.showinfo("Relatório", "Nenhuma venda registrada.")
            return

        relatorio_window = ctk.CTkToplevel(self.master)
        relatorio_window.title("Relatório Detalhado de Vendas")
        relatorio_window.geometry("800x600")

        # Criar área de texto com scroll
        text_area = ctk.CTkTextbox(relatorio_window, wrap="word", font=FONT_ENTRY)
        text_area.pack(expand=True, fill='both', padx=10, pady=10)

        # Gerar conteúdo do relatório
        vendas_por_vendedor = self._agrupar_vendas_por_vendedor()
        self._gerar_conteudo_relatorio(text_area, vendas_por_vendedor)

        # Frame para botões
        frame_botoes = ttk.Frame(relatorio_window)
        frame_botoes.pack(pady=5)

        # Botões do relatório
        ttk.Button(
            frame_botoes,
            text="Salvar Relatório",
            command=lambda: self._salvar_relatorio(text_area.get("1.0", tk.END))
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            frame_botoes,
            text="Fechar",
            command=relatorio_window.destroy
        ).pack(side=tk.LEFT, padx=5)

    def _agrupar_vendas_por_vendedor(self) -> Dict[str, List[Venda]]:
        vendas_por_vendedor = {}
        for venda in self.vendas:
            if venda.vendedor not in vendas_por_vendedor:
                vendas_por_vendedor[venda.vendedor] = []
            vendas_por_vendedor[venda.vendedor].append(venda)
        return dict(sorted(vendas_por_vendedor.items()))

    def _gerar_conteudo_relatorio(self, text_area: ctk.CTkTextbox, vendas_por_vendedor: Dict[str, List[Venda]]):
        data_atual = datetime.now().strftime("%d/%m/%Y")
        text_area.insert(tk.END, f"RELATÓRIO DE VENDAS - {data_atual}\n")
        text_area.insert(tk.END, "="*50 + "\n\n")

        total_geral = Decimal('0.00')

        for vendedor, lista_vendas in vendas_por_vendedor.items():
            text_area.insert(tk.END, f"\nVendedor: {vendedor}\n")
            text_area.insert(tk.END, "-"*50 + "\n\n")

            total_vendedor = Decimal('0.00')
            resumo_pagamentos = {}
            resumo_bandeiras = {}
            trocas = []

            # Detalhamento das vendas
            text_area.insert(tk.END, "DETALHAMENTO DAS VENDAS:\n\n")
            for venda in lista_vendas:
                total_vendedor += venda.valor
                self._atualizar_resumos(venda, resumo_pagamentos, resumo_bandeiras, trocas)
                self._inserir_detalhes_venda(text_area, venda)

            total_geral += total_vendedor
            self._inserir_resumos(text_area, total_vendedor, resumo_pagamentos, resumo_bandeiras, trocas)
            text_area.insert(tk.END, "\n" + "-"*50 + "\n")

        # Resumo geral
        text_area.insert(tk.END, f"\nTOTAL GERAL DE VENDAS: R$ {total_geral:.2f}\n")

    def _atualizar_resumos(self, venda: Venda, resumo_pagamentos: dict, resumo_bandeiras: dict, trocas: list):
        key_pagamento = venda.tipo_pagamento
        if venda.detalhes_pagamento and venda.tipo_pagamento not in ["Dinheiro", "PIX", "Troca"]:
            key_pagamento += f" - {venda.detalhes_pagamento}"

        resumo_pagamentos[key_pagamento] = resumo_pagamentos.get(key_pagamento, Decimal('0.00')) + venda.valor

        if venda.bandeira:
            resumo_bandeiras[venda.bandeira] = resumo_bandeiras.get(venda.bandeira, Decimal('0.00')) + venda.valor

        if venda.troca:
            trocas.append(venda)

    def _inserir_detalhes_venda(self, text_area: ctk.CTkTextbox, venda: Venda):
        text_area.insert(tk.END, f"Data/Hora: {venda.data}\n")
        text_area.insert(tk.END, f"Boleta Nº: {venda.numero_boleta}\n")
        text_area.insert(tk.END, f"Pagamento: {venda.tipo_pagamento}\n")
        
        if venda.detalhes_pagamento:
            text_area.insert(tk.END, f"Detalhes: {venda.detalhes_pagamento}\n")
        if venda.bandeira:
            text_area.insert(tk.END, f"Bandeira: {venda.bandeira}\n")
            
        text_area.insert(tk.END, f"Valor: R$ {venda.valor:.2f}\n")
        text_area.insert(tk.END, f"Troca: {'Sim' if venda.troca else 'Não'}\n\n")

    def _inserir_resumos(self, text_area: ctk.CTkTextbox, total_vendas: Decimal, 
                         resumo_pagamentos: dict, resumo_bandeiras: dict, trocas: list):
        text_area.insert(tk.END, f"\nTOTAL DE VENDAS: R$ {total_vendas:.2f}\n\n")
        
        text_area.insert(tk.END, "RESUMO POR TIPO DE PAGAMENTO:\n")
        for tipo, valor in sorted(resumo_pagamentos.items()):
            text_area.insert(tk.END, f"- {tipo}: R$ {valor:.2f}\n")

        if resumo_bandeiras:
            text_area.insert(tk.END, "\nRESUMO POR BANDEIRA:\n")
            for bandeira, valor in sorted(resumo_bandeiras.items()):
                text_area.insert(tk.END, f"- {bandeira}: R$ {valor:.2f}\n")

        if trocas:
            total_trocas = sum(troca.valor for troca in trocas)
            text_area.insert(tk.END, "\nTROCAS REALIZADAS:\n")
            for troca in trocas:
                text_area.insert(tk.END, f"- Boleta {troca.numero_boleta}: R$ {troca.valor:.2f}\n")
            text_area.insert(tk.END, f"\nTotal de Trocas: R$ {total_trocas:.2f}\n")

    def _salvar_relatorio(self, conteudo: str):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"relatorio_{timestamp}.txt"
            with open(nome_arquivo, "w", encoding="utf-8") as file:
                file.write(conteudo)
            messagebox.showinfo("Sucesso", f"Relatório salvo como '{nome_arquivo}'")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar relatório: {str(e)}")

    def atualizar_resumo(self):
        """Atualiza o resumo de vendas na interface"""
        self.resumo_text.configure(state='normal')
        self.resumo_text.delete("1.0", tk.END)

        if not self.vendas:
            self.resumo_text.insert(tk.END, "Nenhuma venda registrada.\n")
            self.resumo_text.configure(state='disabled')
            return

        total_geral = Decimal('0.00')
        resumo_por_tipo = {}
        resumo_por_bandeira = {}
        trocas = []

        for venda in self.vendas:
            self._atualizar_resumos(venda, resumo_por_tipo, resumo_por_bandeira, trocas)
            total_geral += venda.valor

        self._inserir_resumo_geral(total_geral, resumo_por_tipo, resumo_por_bandeira, trocas)
        self.resumo_text.configure(state='disabled')

    def _inserir_resumo_geral(self, total_geral: Decimal, resumo_por_tipo: dict, 
                              resumo_por_bandeira: dict, trocas: list):
        self.resumo_text.insert(tk.END, f"Total Geral: R$ {total_geral:.2f}\n\n")
        
        self.resumo_text.insert(tk.END, "Por Tipo de Pagamento:\n")
        for tipo, valor in sorted(resumo_por_tipo.items()):
            self.resumo_text.insert(tk.END, f"- {tipo}: R$ {valor:.2f}\n")

        if resumo_por_bandeira:
            self.resumo_text.insert(tk.END, "\nPor Bandeira:\n")
            for bandeira, valor in sorted(resumo_por_bandeira.items()):
                self.resumo_text.insert(tk.END, f"- {bandeira}: R$ {valor:.2f}\n")

        if trocas:
            total_trocas = sum(troca.valor for troca in trocas)
            self.resumo_text.insert(tk.END, f"\nTotal de Trocas: R$ {total_trocas:.2f}\n")

    def carregar_vendas(self):
        """Carrega vendas salvas do arquivo de backup do dia atual"""
        try:
            if os.path.exists(self.ARQUIVO_BACKUP):
                with open(self.ARQUIVO_BACKUP, 'r', encoding='utf-8') as file:
                    dados = json.load(file)
                    self.vendas = [Venda.from_dict(venda_dict) for venda_dict in dados]
                    for venda in self.vendas:
                        self._adicionar_venda_treeview(venda)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar vendas: {str(e)}")

    def salvar_vendas(self):
        """Salva as vendas no arquivo de backup do dia atual"""
        try:
            dados = [venda.to_dict() for venda in self.vendas]
            with open(self.ARQUIVO_BACKUP, 'w', encoding='utf-8') as file:
                json.dump(dados, file, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao salvar vendas: {str(e)}")

    def on_select(self, event):
        pass

    def on_double_click(self, event):
        pass

    def _configurar_atalhos(self):
        """Configura os atalhos de teclado do sistema"""
        self.master.bind('<Alt-a>', lambda e: self.adicionar_venda())
        self.master.bind('<Alt-e>', lambda e: self.excluir_venda())
        self.master.bind('<Alt-r>', lambda e: self.gerar_relatorio())
        self.master.bind('<Alt-l>', lambda e: self.limpar_campos())

if __name__ == "__main__":
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    app = SistemaCaixa(root)
    root.mainloop()