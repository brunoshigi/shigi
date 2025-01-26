import customtkinter as ctk
from tkinter import messagebox
import requests
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime
import os
import tempfile

# Configurações iniciais
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Tenta importar as lojas do módulo
LOJAS = [
    "AUSTRAL MORUMBI SHOPPING",
    "AUSTRAL JK IGUATEMI",
    "AUSTRAL IGUATEMI SP",
    "AUSTRAL HIGIENÓPOLIS",
    "AUSTRAL ALPHAVILLE",
    "AUSTRAL CATARINA OUTLET"
]

class SistemaEtiquetas(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.configure(fg_color="#0F0F0F")
        
        # Verifica se as lojas foram carregadas corretamente
        if LOJAS == ["ERRO AO CARREGAR LOJAS"]:
            messagebox.showerror("Erro", "O sistema não conseguiu carregar a lista de lojas.")
            self.after(1000, self.destroy)
            return
        
        # Configurações de dimensões da etiqueta
        self.LARGURA_PAPEL = 400
        self.ALTURA_ETIQUETA = 600
        self.LARGURA_IMPRESSAO = 380
        self.MARGEM = 20
        
        # Configurações da janela
        self.title("SISTEMA AUSTRAL - ETIQUETAS")
        self.geometry("600x700")
        self.resizable(False, False)
        
        # Centralização na tela
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width - 600) // 2
        y = (screen_height - 700) // 2
        self.geometry(f"600x700+{x}+{y}")
        
        # Inicialização de variáveis
        self.origem_var = None
        self.destino_var = None
        self.loja_var = None
        self.modo_atual = None
        self.endereco_completo = {}
        
        # Setup da interface
        self.criar_interface()
        
        # Força o foco
        self.lift()
        self.focus_force()

    def criar_interface(self):
        """Cria a interface principal do sistema com layout otimizado"""
        # Frame principal com margens adequadas
        self.main_frame = ctk.CTkFrame(self, corner_radius=15, fg_color="black")
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Frame do cabeçalho para título e subtítulo
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(20, 10))
        
        # Título com tamanho e espaçamento ajustados
        self.label_titulo = ctk.CTkLabel(
            header_frame,
            text="AUSTRAL",
            font=ctk.CTkFont(size=36, weight="bold")
        )
        self.label_titulo.pack(pady=(0, 5))

        # Subtítulo com tamanho proporcional
        self.label_subtitulo = ctk.CTkLabel(
            header_frame,
            text="Sistema de Geração de Etiquetas",
            font=ctk.CTkFont(size=16), fg_color="black"
        )
        self.label_subtitulo.pack(pady=(0, 20))
        
        # Frame para os botões de modo com espaçamento melhorado
        self.frame_modos = ctk.CTkFrame(self.main_frame, fg_color="black")
        self.frame_modos.pack(pady=20)
        
        # Primeiro frame para os dois primeiros botões
        buttons_frame1 = ctk.CTkFrame(self.frame_modos, fg_color="black")
        buttons_frame1.pack(pady=(0, 10))
        
        # Botões da primeira linha
        self.btn_delivery = ctk.CTkButton(
            buttons_frame1,
            text="ETIQUETA PARA CLIENTE",
            width=240,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self.mudar_modo("delivery")
        )
        self.btn_delivery.pack(side="left", padx=10)
        
        self.btn_transfer = ctk.CTkButton(
            buttons_frame1,
            text="ETIQUETA DE TRANSFERÊNCIA",
            width=240,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self.mudar_modo("transfer")
        )
        self.btn_transfer.pack(side="left", padx=10)
        
        # Frame para o botão de reserva
        buttons_frame2 = ctk.CTkFrame(self.frame_modos, fg_color="black")
        buttons_frame2.pack()
        
        # Botão de reserva centralizado
        self.btn_reserve = ctk.CTkButton(
            buttons_frame2,
            text="ETIQUETA DE RESERVA",
            width=240,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=lambda: self.mudar_modo("reserve")
        )
        self.btn_reserve.pack(pady=5)
        
        # Frame para conteúdo dinâmico com margens apropriadas
        self.frame_conteudo = ctk.CTkFrame(
            self.main_frame, corner_radius=15, fg_color="black"
        )
        self.frame_conteudo.pack(pady=20, fill="both", expand=True)
        
        # Rodapé com espaçamento adequado
        self.criar_footer()

    def criar_footer(self):
        """Cria o rodapé com layout melhorado"""
        self.footer = ctk.CTkFrame(self.main_frame, fg_color="black")
        self.footer.pack(side="bottom", fill="x", pady=(20, 10))
        
        # Status e hora com fonte legível
        self.status_label = ctk.CTkLabel(
            self.footer,
            text="",
            font=ctk.CTkFont(size=12), fg_color="black"
        )
        self.status_label.pack(side="left", padx=20)
        
        # Créditos com fonte legível
        self.label_footer = ctk.CTkLabel(
            self.footer,
            text="© 2025 Shigi - GitHub @brunoshigi",
            font=ctk.CTkFont(size=12), fg_color="black"
        )
        self.label_footer.pack(side="right", padx=20)
        # Botão de saída
        self.btn_sair = ctk.CTkButton(
            self.footer,
            text="SAIR",
            command=self.sair_sistema,
            fg_color="red"
        )
        self.btn_sair.pack(side="right", padx=10)
        
        # Inicia atualização do horário
        self.atualizar_hora()

    def sair_sistema(self):
        self.destroy()

    def atualizar_hora(self):
        """Atualiza o horário no rodapé com formato melhorado"""
        agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.status_label.configure(text=f"Online | {agora}")
        self.after(1000, self.atualizar_hora)

    def limpar_frame_conteudo(self):
        """Limpa o frame de conteúdo mantendo suas dimensões"""
        for widget in self.frame_conteudo.winfo_children():
            widget.destroy()

    def mudar_modo(self, modo):
        """Muda o modo de geração de etiquetas"""
        self.limpar_frame_conteudo()
        
        if modo == "delivery":
            self.criar_interface_delivery()
        elif modo == "transfer":
            self.criar_interface_transfer()
        elif modo == "reserve":
            self.criar_interface_reserve()
        
        self.modo_atual = modo # Atualiza o modo atual,
        self.grab_set() # Foca na janela
        self.focus_force() # Força o foco



    def criar_interface_delivery(self):
        """Interface para etiquetas de entrega"""
        # Frame da loja
        loja_frame = ctk.CTkFrame(self.frame_conteudo)
        loja_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(loja_frame, text="FILIAL:").pack(side="left", padx=5)
        self.loja_var = ctk.StringVar(value="")
        loja_combo = ctk.CTkComboBox(
            loja_frame,
            values=LOJAS,
            variable=self.loja_var,
            width=200,
            state="normal"
        )
        loja_combo.pack(side="left", padx=5)
        
        # Frame do cliente
        cliente_frame = ctk.CTkFrame(self.frame_conteudo)
        cliente_frame.pack(fill="x", padx=20, pady=5)
        
        campos = [
            ("CLIENTE:", "cliente"),
            ("CEP:", "cep"),
            ("NÚMERO:", "numero"),
            ("COMPLEMENTO:", "complemento"),
            ("REFERÊNCIA:", "referencia")
        ]
        
        for label, nome in campos:
            frame = ctk.CTkFrame(cliente_frame)
            frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(frame, text=label).pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame, width=200)
            entry.pack(side="left", padx=5)
            
            setattr(self, f"entry_{nome}", entry)
            
            if nome == "cep":
                entry.bind('<FocusOut>', self.consultar_cep)
        
        # Botões
        btn_frame = ctk.CTkFrame(self.frame_conteudo)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="LIMPAR",
            command=self.limpar_campos_delivery,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="GERAR ETIQUETA",
            command=self.gerar_etiqueta_delivery,
            width=100
        ).pack(side="right", padx=5)

    def criar_interface_transfer(self):
        """Interface para etiquetas de transferência"""
        # Frame origem
        origem_frame = ctk.CTkFrame(self.frame_conteudo)
        origem_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(origem_frame, text="FILIAL ORIGEM:").pack(side="left", padx=5)
        self.origem_var = ctk.StringVar(value="")
        origem_combo = ctk.CTkComboBox(
            origem_frame,
            values=LOJAS,
            variable=self.origem_var,
            width=200,
            state="normal"
        )
        origem_combo.pack(side="left", padx=5)
        
        # Frame destino
        destino_frame = ctk.CTkFrame(self.frame_conteudo)
        destino_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(destino_frame, text="FILIAL DESTINO:").pack(side="left", padx=5)
        self.destino_var = ctk.StringVar(value="")
        destino_combo = ctk.CTkComboBox(
            destino_frame,
            values=LOJAS,
            variable=self.destino_var,
            width=200,
            state="normal"
        )
        destino_combo.pack(side="left", padx=5)
        
        # Botões
        btn_frame = ctk.CTkFrame(self.frame_conteudo)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="LIMPAR",
            command=self.limpar_campos_transfer,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="GERAR ETIQUETA",
            command=self.gerar_etiqueta_transfer,
            width=100
        ).pack(side="right", padx=5)

    def criar_interface_reserve(self):
        """Interface para etiquetas de reserva"""
        # Frame da loja
        loja_frame = ctk.CTkFrame(self.frame_conteudo)
        loja_frame.pack(fill="x", padx=20, pady=5)
        
        ctk.CTkLabel(loja_frame, text="FILIAL:").pack(side="left", padx=5)
        self.loja_var = ctk.StringVar(value="")
        loja_combo = ctk.CTkComboBox(
            loja_frame,
            values=LOJAS,
            variable=self.loja_var,
            width=200,
            state="normal"
        )
        loja_combo.pack(side="left", padx=5)
        
        # Frame do cliente e vendedor
        info_frame = ctk.CTkFrame(self.frame_conteudo)
        info_frame.pack(fill="x", padx=20, pady=5)
        
        campos = [
            ("VENDEDOR:", "vendedor"),
            ("CLIENTE:", "cliente_reserva"),
            ("PEÇA:", "peca"),
            ("DATA LIMITE:", "data_limite")
        ]
        
        for label, nome in campos:
            frame = ctk.CTkFrame(info_frame)
            frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(frame, text=label).pack(side="left", padx=5)
            if nome == "data_limite":
                # Criar campos de data separados para facilitar
                data_frame = ctk.CTkFrame(frame)
                data_frame.pack(side="left")
                
                self.dia_var = ctk.StringVar(value=datetime.now().strftime("%d"))
                self.mes_var = ctk.StringVar(value=datetime.now().strftime("%m"))
                self.ano_var = ctk.StringVar(value=datetime.now().strftime("%Y"))
                
                # Dia
                dia_entry = ctk.CTkEntry(data_frame, width=40, textvariable=self.dia_var)
                dia_entry.pack(side="left", padx=2)
                ctk.CTkLabel(data_frame, text="/").pack(side="left")
                
                # Mês
                mes_entry = ctk.CTkEntry(data_frame, width=40, textvariable=self.mes_var)
                mes_entry.pack(side="left", padx=2)
                ctk.CTkLabel(data_frame, text="/").pack(side="left")
                
                # Ano
                ano_entry = ctk.CTkEntry(data_frame, width=60, textvariable=self.ano_var)
                ano_entry.pack(side="left", padx=2)
            else:
                entry = ctk.CTkEntry(frame, width=200)
                entry.pack(side="left", padx=5)
                setattr(self, f"entry_{nome}", entry)
        
        # Botões
        btn_frame = ctk.CTkFrame(self.frame_conteudo)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            btn_frame,
            text="LIMPAR",
            command=self.limpar_campos_reserve,
            width=100
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="GERAR ETIQUETA",
            command=self.gerar_etiqueta_reserve,
            width=100
        ).pack(side="right", padx=5)

    def consultar_cep(self, event=None):
        """Consulta CEP na API ViaCEP e preenche os campos de endereço"""
        cep = self.entry_cep.get().replace('-', '').replace('.', '').strip()
        
        # Validação básica do CEP
        if not cep.isdigit() or len(cep) != 8:
            self.grab_release()
            messagebox.showwarning("Atenção", "CEP inválido!\nDigite apenas números (8 dígitos)")
            self.grab_set()
            self.focus_force()
            return
        
        try:
            # Configura timeout para a requisição
            response = requests.get(
                f'https://viacep.com.br/ws/{cep}/json/',
                timeout=5  # 5 segundos de timeout
            )
            
            if response.status_code == 200:
                dados = response.json()
                
                # Verifica se o CEP existe
                if 'erro' in dados:
                    self.grab_release()
                    messagebox.showerror("Erro", "CEP não encontrado na base de dados.")
                    self.grab_set()
                    self.focus_force()
                    self.endereco_completo = {}
                    return
                
                # Armazena os dados
                self.endereco_completo = dados
                
                # Foca no campo número
                self.entry_numero.focus()
                return
                
            else:
                raise Exception(f"Erro na API: {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.grab_release()
            messagebox.showerror("Erro", "Tempo excedido na consulta.\nTente novamente.")
            self.grab_set()
            self.focus_force()
            
        except requests.exceptions.ConnectionError:
            self.grab_release()
            messagebox.showerror("Erro", "Sem conexão com a internet.\nVerifique sua conexão.")
            self.grab_set()
            self.focus_force()
            
        except Exception as e:
            self.grab_release()
            messagebox.showerror("Erro", f"Erro ao consultar CEP: {str(e)}")
            self.grab_set()
            self.focus_force()
        
        self.endereco_completo = {}

    def criar_imagem_delivery(self):
        """Cria a imagem da etiqueta para entrega usando PIL"""
        try:
            imagem = Image.new("RGB", (self.LARGURA_PAPEL, self.ALTURA_ETIQUETA), "white")
            draw = ImageDraw.Draw(imagem)
            
            # Define as fontes com tamanhos apropriados
            try:
                fonte_titulo = ImageFont.truetype("arial.ttf", 30)
                fonte_cliente = ImageFont.truetype("arial.ttf", 25)
                fonte_endereco = ImageFont.truetype("arial.ttf", 20)
                fonte_info = ImageFont.truetype("arial.ttf", 20)
            except:
                fonte_titulo = fonte_cliente = fonte_endereco = fonte_info = ImageFont.load_default()

            y = self.MARGEM

            # Inserção do logo
            try:
                logo = Image.open("assets/logo.png")
                logo_width = 300
                logo = logo.resize((logo_width, int(logo.height * logo_width / logo.width)))
                x_logo = (self.LARGURA_PAPEL - logo_width) // 2
                imagem.paste(logo, (x_logo, y), logo if 'A' in logo.getbands() else None)
                y += logo.height + 20
            except:
                draw.text((self.MARGEM, y), "Austral", fill="black", font=fonte_titulo)
                y += 40

            # Informações da filial
            draw.text((self.MARGEM, y), "FILIAL:", fill="blue", font=fonte_titulo)
            y += 35
            draw.text((self.MARGEM, y), self.loja_var.get().upper(), fill="black", font=fonte_cliente)
            y += 40

            # Nome do cliente
            draw.text((self.MARGEM, y), "A/C CLIENTE:", fill="blue", font=fonte_titulo)
            y += 35
            cliente = self.entry_cliente.get().strip().upper()
            draw.text((self.MARGEM, y), cliente, fill="black", font=fonte_cliente)
            y += 40

            # Linha divisória
            draw.line([(self.MARGEM, y), (self.LARGURA_IMPRESSAO - self.MARGEM, y)], fill="black", width=1)
            y += 20

            # Informações de endereço
            if self.endereco_completo:
                # Logradouro e número
                endereco = f"{self.endereco_completo.get('logradouro', '').upper()}, {self.entry_numero.get().upper()}"
                draw.text((self.MARGEM, y), endereco, fill="black", font=fonte_endereco)
                y += 25

                # Complemento (se houver)
                if self.entry_complemento.get().strip():
                    complemento = self.entry_complemento.get().strip().upper()
                    draw.text((self.MARGEM, y), complemento, fill="black", font=fonte_endereco)
                    y += 25

                # Bairro
                bairro_cidade = f"{self.endereco_completo.get('bairro', '').upper()}"
                draw.text((self.MARGEM, y), bairro_cidade, fill="black", font=fonte_endereco)
                y += 25

                # Cidade e Estado
                cidade_uf = f"{self.endereco_completo.get('localidade', '').upper()}/{self.endereco_completo.get('uf', '').upper()}"
                draw.text((self.MARGEM, y), cidade_uf, fill="black", font=fonte_endereco)
                y += 25

                # CEP formatado
                cep_formatado = f"CEP {self.endereco_completo.get('cep', '')}"
                draw.text((self.MARGEM, y), cep_formatado, fill="black", font=fonte_endereco)
                y += 25

            # Referência (opcional)
            if self.entry_referencia.get().strip():
                y += 10
                draw.line([(self.MARGEM, y), (self.LARGURA_IMPRESSAO - self.MARGEM, y)], fill="black", width=1)
                y += 20
                draw.text((self.MARGEM, y), "REFERÊNCIA:", fill="blue", font=fonte_titulo)
                y += 35
                referencia = self.entry_referencia.get().strip().upper()
                draw.text((self.MARGEM, y), referencia, fill="black", font=fonte_endereco)
                y += 25

            # Data e hora de geração
            y = self.ALTURA_ETIQUETA - 50
            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
            draw.text((self.MARGEM, y), data_hora, fill="black", font=fonte_info)

            return imagem
        except Exception as e:
            self.grab_release()
            messagebox.showerror("Erro", f"Erro ao criar imagem: {str(e)}")
            self.grab_set()
            self.focus_force()
            return None

    def criar_imagem_reserve(self):
        """Cria a imagem da etiqueta de reserva usando PIL com melhor alinhamento"""
        try:
            imagem = Image.new("RGB", (self.LARGURA_PAPEL, self.ALTURA_ETIQUETA), "white")
            draw = ImageDraw.Draw(imagem)
            
            # Define as fontes
            try:
                fonte_titulo = ImageFont.truetype("arial.ttf", 25)
                fonte_texto = ImageFont.truetype("arial.ttf", 20)
                fonte_data = ImageFont.truetype("arial.ttf", 15)
                fonte_alerta = ImageFont.truetype("arial.ttf", 23)
            except:
                fonte_titulo = fonte_texto = fonte_data = fonte_alerta = ImageFont.load_default()

            y = self.MARGEM

            # Logo Austral
            try:
                logo = Image.open("assets/logo.png")
                logo_width = 300
                logo = logo.resize((logo_width, int(logo.height * logo_width / logo.width)))
                x_logo = (self.LARGURA_PAPEL - logo_width) // 2
                imagem.paste(logo, (x_logo, y), logo if 'A' in logo.getbands() else None)
                y += logo.height + 30
            except:
                draw.text((self.MARGEM, y), "Austral", fill="black", font=fonte_titulo)
                y += 40

            # Título "RESERVA DE PRODUTO" em vermelho e centralizado
            titulo = "RESERVA DE PRODUTO"
            titulo_width = draw.textlength(titulo, fonte_titulo)
            x_titulo = (self.LARGURA_PAPEL - titulo_width) // 2
            draw.text((x_titulo, y), titulo, fill="red", font=fonte_titulo)
            y += 40

            # Linha divisória
            draw.line([(self.MARGEM, y), (self.LARGURA_IMPRESSAO - self.MARGEM, y)], 
                     fill="black", width=1)
            y += 20

            # Informações da filial
            draw.text((self.MARGEM, y), "FILIAL:", fill="blue", font=fonte_titulo)
            y += 23
            draw.text((self.MARGEM, y), self.loja_var.get().upper(), fill="black", font=fonte_texto)
            y += 35

            # Linha divisória
            draw.line([(self.MARGEM, y), (self.LARGURA_IMPRESSAO - self.MARGEM, y)], 
                     fill="black", width=1)
            y += 20

            # Informações principais em formato de tabela
            infos = [
                ("VENDEDOR:", self.entry_vendedor.get().strip().upper()),
                ("CLIENTE:", self.entry_cliente_reserva.get().strip().upper()),
                ("PEÇA:", self.entry_peca.get().strip().upper())
            ]

            for label, valor in infos:
                draw.text((self.MARGEM, y), label, fill="blue", font=fonte_titulo)
                y += 25
                draw.text((self.MARGEM, y), valor, fill="black", font=fonte_texto)
                y += 35

            # Data limite em destaque
            draw.text((self.MARGEM, y), "DATA LIMITE:", fill="red", font=fonte_titulo)
            y += 25
            data_limite = f"{self.dia_var.get()}/{self.mes_var.get()}/{self.ano_var.get()}"
            draw.text((self.MARGEM, y), data_limite, fill="red", font=fonte_texto)
            y += 35

            # Linha divisória antes do aviso
            draw.line([(self.MARGEM, y), (self.LARGURA_IMPRESSAO - self.MARGEM, y)], 
                     fill="black", width=1)
            y += 25

            # Aviso de reserva em destaque
            aviso = "*SUJEITO A PERDA ECOMMERCE*"
            aviso_width = draw.textlength(aviso, fonte_alerta)
            x_aviso = (self.LARGURA_PAPEL - aviso_width) // 2
            draw.text((x_aviso, y), aviso, fill="red", font=fonte_alerta)

            # Data e hora de geração no rodapé
            y = self.ALTURA_ETIQUETA - 35
            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
            draw.text((self.MARGEM, y), f"Gerado em: {data_hora}", fill="black", font=fonte_data)

            return imagem
        except Exception as e:
            self.grab_release()
            messagebox.showerror("Erro", f"Erro ao criar imagem: {str(e)}")
            self.grab_set()
            self.focus_force()
            return None

    def criar_imagem_transfer(self):
        """Cria a imagem para etiqueta de transferência"""
        try:
            imagem = Image.new("RGB", (self.LARGURA_PAPEL, self.ALTURA_ETIQUETA), "white")
            draw = ImageDraw.Draw(imagem)
            
            # Define as fontes
            try:
                fonte_titulo = ImageFont.truetype("arial.ttf", 30)
                fonte_origem = ImageFont.truetype("arial.ttf", 25)
                fonte_destino = ImageFont.truetype("arial.ttf", 25)
                fonte_info = ImageFont.truetype("arial.ttf", 20)
                fonte_alerta = ImageFont.truetype("arial.ttf", 25)
            except:
                fonte_titulo = fonte_origem = fonte_destino = fonte_info = fonte_alerta = ImageFont.load_default()

            y = self.MARGEM
            
            # Informações do destino
            destino_info = self.destino_var.get().upper()
            
            # Box e Interfone (se for estoque)
            if "ESTOQUE" in destino_info or "BOX" in destino_info:
                box_text = "BOX 20011\nTOCAR INTERFONE 0525"
                msg_width = max(draw.textlength("BOX 20011", fonte_alerta),
                              draw.textlength("TOCAR INTERFONE 0525", fonte_alerta))
                msg_height = 60
                rect_x = (self.LARGURA_PAPEL - msg_width - 20) // 2
                rect_y = y
                draw.rectangle([(rect_x, rect_y), 
                              (rect_x + msg_width + 20, rect_y + msg_height)],
                              outline="red", fill=None, width=2)
                
                lines = box_text.split('\n')
                for line in lines:
                    w = draw.textlength(line, fonte_alerta)
                    x = (self.LARGURA_PAPEL - w) // 2
                    draw.text((x, y), line, font=fonte_alerta, fill="red")
                    y += 30
                y += 10

            # Logo Austral
            try:
                logo = Image.open("assets/logo.png")
                logo_width = 300
                logo = logo.resize((logo_width, int(logo.height * logo_width / logo.width)))
                x_logo = (self.LARGURA_PAPEL - logo_width) // 2
                imagem.paste(logo, (x_logo, y), logo if 'A' in logo.getbands() else None)
                y += logo.height + 20
            except:
                draw.text((self.MARGEM, y), "Austral", fill="black", font=fonte_titulo)
                y += 40

            # Origem
            draw.text((self.MARGEM, y), "FILIAL ORIGEM:", fill="blue", font=fonte_titulo)
            y += 35
            draw.text((self.MARGEM, y), self.origem_var.get().upper(), fill="black", font=fonte_origem)
            y += 40

            # Destino
            draw.text((self.MARGEM, y), "FILIAL DESTINO:", fill="blue", font=fonte_titulo)
            y += 35
            draw.text((self.MARGEM, y), self.destino_var.get().upper(), fill="black", font=fonte_destino)
            y += 30
                
            # Linha divisória
            draw.line([(self.MARGEM, y), (self.LARGURA_IMPRESSAO - self.MARGEM, y)], 
                     fill="black", width=1)
            y += 20
                
            # Data e hora
            data_hora = datetime.now().strftime("%d/%m/%Y %H:%M")
            if "ESTOQUE" in destino_info or "BOX" in destino_info:
                y = self.ALTURA_ETIQUETA - 80
                draw.text((self.MARGEM, y), data_hora, fill="red", font=fonte_info)
                y += 30
                msg = "TOCAR INTERFONE 0525"
                msg_width = draw.textlength(msg, fonte_alerta)
                x = (self.LARGURA_PAPEL - msg_width) // 2
                draw.text((x, y), msg, font=fonte_alerta, fill="red")
            else:
                y = self.ALTURA_ETIQUETA - 50
                draw.text((self.MARGEM, y), data_hora, fill="black", font=fonte_info)

            return imagem
        except Exception as e:
            self.grab_release()
            messagebox.showerror("Erro", f"Erro ao criar imagem: {str(e)}")
            self.grab_set()
            self.focus_force()
            return None

    def validar_campos_delivery(self):
        """Valida campos do modo delivery"""
        if not self.loja_var.get():
            self.grab_release()
            messagebox.showwarning("Atenção", "Por favor, selecione uma filial.")
            self.grab_set()
            self.focus_force()
            return False
            
        if not self.entry_cliente.get().strip():
            self.grab_release()
            messagebox.showwarning("Atenção", "Por favor, digite o nome do cliente.")
            self.grab_set()
            self.focus_force()
            return False
            
        if not self.endereco_completo:
            self.grab_release()
            messagebox.showwarning("Atenção", "Por favor, consulte um CEP válido.")
            self.grab_set()
            self.focus_force()
            return False
            
        if not self.entry_numero.get().strip():
            self.grab_release()
            messagebox.showwarning("Atenção", "Por favor, digite o número do endereço.")
            self.grab_set()
            self.focus_force()
            return False
            
        return True

    def validar_campos_transfer(self):
        """Valida campos do modo transfer"""
        origem = self.origem_var.get().strip()
        destino = self.destino_var.get().strip()
        
        if not origem:
            self.grab_release()
            messagebox.showwarning("Atenção", "Por favor, selecione a filial de origem.")
            self.grab_set()
            self.focus_force()
            return False
            
        if not destino:
            self.grab_release()
            messagebox.showwarning("Atenção", "Por favor, selecione a filial de destino.")
            self.grab_set()
            self.focus_force()
            return False
            
        if origem == destino:
            self.grab_release()
            messagebox.showwarning("Atenção", "A filial de origem e destino não podem ser iguais.")
            self.grab_set()
            self.focus_force()
            return False
            
        return True

    def limpar_campos_delivery(self):
        """Limpa campos do modo delivery"""
        self.loja_var.set('')
        for nome in ['cliente', 'cep', 'numero', 'complemento', 'referencia']:
            entry = getattr(self, f'entry_{nome}')
            entry.delete(0, 'end')
        self.endereco_completo = {}

    def limpar_campos_transfer(self):
        """Limpa campos do modo transfer"""
        self.origem_var.set('')
        self.destino_var.set('')

    def abrir_e_deletar_arquivo(self, temp_path):
        """Abre o arquivo e agenda sua deleção após 60 segundos"""
        if os.path.isfile(temp_path):
            self.grab_release()
            
            try:
                os.startfile(temp_path)  # Windows
            except AttributeError:
                try:
                    import subprocess
                    if os.name == 'posix':
                        subprocess.Popen(['xdg-open', temp_path])  # Linux
                    else:
                        subprocess.Popen(['open', temp_path])      # Mac
                except:
                    messagebox.showinfo("Sucesso", f"Etiqueta gerada em: {temp_path}")
                    return False
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir o arquivo: {str(e)}")
                return False

            def deletar_arquivo():
                try:
                    os.remove(temp_path)
                except:
                    pass
            self.after(60000, deletar_arquivo)
            
            messagebox.showinfo("Sucesso", "Etiqueta gerada com sucesso!")
            self.grab_set()
            self.focus_force()
            return True
        return False

    def gerar_etiqueta_delivery(self):
        """Gera etiqueta para entrega"""
        if not self.validar_campos_delivery():
            return
        
        try:
            imagem = self.criar_imagem_delivery()
            if imagem:
                temp_name = f"etiqueta_delivery_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                temp_path = os.path.join(tempfile.gettempdir(), temp_name)
                imagem.save(temp_path, "PNG")
                
                self.grab_release()
                
                if not self.abrir_e_deletar_arquivo(temp_path):
                    messagebox.showinfo("Sucesso", f"Etiqueta gerada em: {temp_path}")
                
                self.grab_set()
                self.focus_force()
        except Exception as e:
            self.grab_release()
            messagebox.showerror("Erro", f"Erro ao gerar etiqueta: {str(e)}")
            self.grab_set()
            self.focus_force()

    def gerar_etiqueta_transfer(self):
        """Gera etiqueta para transferência"""
        if not self.validar_campos_transfer():
            return
        
        try:
            imagem = self.criar_imagem_transfer()
            if imagem:
                temp_name = f"etiqueta_transfer_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                temp_path = os.path.join(tempfile.gettempdir(), temp_name)
                imagem.save(temp_path, "PNG")
                
                self.grab_release()
                
                if not self.abrir_e_deletar_arquivo(temp_path):
                    messagebox.showinfo("Sucesso", f"Etiqueta gerada em: {temp_path}")
                
                self.grab_set()
                self.focus_force()
        except Exception as e:
            self.grab_release()
            messagebox.showerror("Erro", f"Erro ao gerar etiqueta: {str(e)}")
            self.grab_set()
            self.focus_force()

    def validar_campos_reserve(self):
        """Valida campos do modo reserve"""
        campos = [
            (self.loja_var.get(), "Por favor, selecione uma filial."),
            (self.entry_vendedor.get().strip(), "Por favor, digite o nome do vendedor."),
            (self.entry_cliente_reserva.get().strip(), "Por favor, digite o nome do cliente."),
            (self.entry_peca.get().strip(), "Por favor, digite a descrição da peça.")
        ]

        for valor, mensagem in campos:
            if not valor:
                self.grab_release()
                messagebox.showwarning("Atenção", mensagem)
                self.grab_set()
                self.focus_force()
                return False

        # Validação da data
        try:
            dia = int(self.dia_var.get())
            mes = int(self.mes_var.get())
            ano = int(self.ano_var.get())
            data = datetime(ano, mes, dia)
            
            if data < datetime.now():
                self.grab_release()
                messagebox.showwarning("Atenção", "A data limite não pode ser anterior à data atual.")
                self.grab_set()
                self.focus_force()
                return False
        except ValueError:
            self.grab_release()
            messagebox.showwarning("Atenção", "Data inválida.")
            self.grab_set()
            self.focus_force()
            return False

        return True

    def limpar_campos_reserve(self):
        """Limpa campos do modo reserve"""
        self.loja_var.set('')
        for nome in ['vendedor', 'cliente_reserva', 'peca']:
            entry = getattr(self, f'entry_{nome}')
            entry.delete(0, 'end')
        
        # Resetar data para hoje
        hoje = datetime.now()
        self.dia_var.set(hoje.strftime("%d"))
        self.mes_var.set(hoje.strftime("%m"))
        self.ano_var.set(hoje.strftime("%Y"))

    def gerar_etiqueta_reserve(self):
        """Gera etiqueta de reserva"""
        if not self.validar_campos_reserve():
            return
        
        try:
            imagem = self.criar_imagem_reserve()
            if imagem:
                # Gera um nome único para cada arquivo
                temp_name = f"etiqueta_reserva_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                temp_path = os.path.join(tempfile.gettempdir(), temp_name)
                imagem.save(temp_path, "PNG")
                
                self.grab_release()
                
                if not self.abrir_e_deletar_arquivo(temp_path):
                    messagebox.showinfo("Sucesso", f"Etiqueta gerada em: {temp_path}")
                
                self.grab_set()
                self.focus_force()
        except Exception as e:
            self.grab_release()
            messagebox.showerror("Erro", f"Erro ao gerar etiqueta: {str(e)}")
            self.grab_set()
            self.focus_force()

    def __del__(self):
        """Destrutor da classe para garantir limpeza adequada"""
        try:
            self.grab_release()
        except:
            pass


if __name__ == "__main__":
    app = SistemaEtiquetas()
    app.mainloop()