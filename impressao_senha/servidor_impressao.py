import tkinter as tk
from tkinter import ttk, messagebox
import win32print
from chamar_api import ChamarFusionAPI
from gerar_relatorio import GeradorRelatorioQR


def listar_impressoras():
    """Retorna uma lista de impressoras disponíveis no sistema tanto local quanto em rede."""
    return [
        impressora[2]
        for impressora in win32print.EnumPrinters(
            win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS
        )
    ]


class TelaImpressao(tk.Toplevel):
    def __init__(self,  api_client, master=None ):
        super().__init__(master)
        self.title("Impressão de Senhas")
        self.geometry("800x400")

        self.api_client = api_client
        '''self.api_client = ChamarFusionAPI(
            base_url="http://localhost:8000/api/fusion",
            token=token_api or "26560e2073ff37e22c44869a4d6674cb4641301e"
        )'''
        self.build_interface()
        self.protocol("WM_DELETE_WINDOW", self.fechar_tudo)

        self.servico_ativo = False  # Por padrão, o serviço inicia parado

        # 👉 Carrega automaticamente as senhas ao abrir
        # self.carregar_senhas()
        # 🕒 Inicia o timer que executa algo a cada 5 segundos
        self.executar_periodicamente()


    def fechar_tudo(self):
        self.servico_ativo = False  # Para garantir que o timer pare ao fechar
        self.destroy()
        #self.master.destroy()  # Isso encerra o `Tk` principal (TelaLogin)

    def executar_periodicamente(self):
        if self.servico_ativo:
            # 👉 Carrega automaticamente as senhas
            self.status_bar.config(text=f"entrou em executar periodicamente.")
            self.update_idletasks()
            print("entrou em executar periodicamente.")
            self.carregar_senhas()
            self.on_btn_imprimir_click()
            self.after(15000, self.executar_periodicamente)  # Agenda novamente para 5s depois
        else :
            self.status_bar.config(text=f" NÃO entrou em executar periodicamente.")
            print("nao entrou em executar periodicamente.")
            self.update_idletasks()

    def iniciar_servico(self):
        impressora_selecionada = self.cb_impressora.get()
        if not impressora_selecionada:
            messagebox.showerror("Erro", "Por favor, selecione uma impressora antes de continuar.")
            return None

        if not self.servico_ativo:
            self.servico_ativo = True
            self.lbl_status_value.config(text="Ativo", fg="green")
            self.executar_periodicamente()

    def parar_servico(self):
        self.servico_ativo = False
        self.lbl_status_value.config(text="Parado", fg="red")

    
    def on_btn_imprimir_click(self):
        impressora_selecionada = self.cb_impressora.get()
        if not impressora_selecionada:
            messagebox.showerror("Erro", "Por favor, selecione uma impressora antes de continuar.")
            return None

        try:
            win32print.SetDefaultPrinter(impressora_selecionada)
        except Exception as e:
            messagebox.showerror("Erro ao definir impressora padrão", str(e))
            return None
        
         # Verifica se há dados no grid
        itens = self.tree.get_children()
        if itens:
            # messagebox.showerror("Erro", "Não há senhas carregadas para imprimir.")
            #return None

            try:
                relatorio_ready = GeradorRelatorioQR()

                # Loop pelos itens do Treeview
                for item in itens:
                    valores = self.tree.item(item)["values"]
                    if valores:  # garante que existe algum valor
                        num_senha = valores[0]
                        senha = valores[1]  # no seu grid, a senha é a primeira coluna
                        nome_fila = valores[2]
                        if senha:
                            relatorio_ready.imprimir_senha(impressora_selecionada, senha, num_senha, nome_fila)
                            resultado = self.api_client.atualizar_impresso(num_senha, True)
                                                # opcional: validar resposta da API
                            if "erro" in resultado:
                                print(f"Erro ao atualizar {num_senha}: {resultado['erro']}")
                            else:
                                print(f"Senha {num_senha} marcada como impressa.")

            except Exception as e:
                messagebox.showerror("Erro ao imprimir senhas", str(e))              
        
    # ====================================================
    # Função: carregar senhas do endpoint na Treeview
    # ====================================================
    def carregar_senhas(self):
        """Busca senhas via API e preenche o Treeview."""
        try:
            self.status_bar.config(text="Carregando senhas da API...")
            self.update_idletasks()

            dados = self.api_client.buscar_senhas()
            if not isinstance(dados, list):
                messagebox.showerror("Erro", "Formato inesperado de resposta da API.")
                return

            # Limpa o grid antes de preencher
            for i in self.tree.get_children():
                self.tree.delete(i)

            # Insere as linhas
            for item in dados:
                num_senha = item.get("num_senha", "")  
                senha = item.get("senha", "") 
                nome_fila = item.get("nome_fila","")
           
                self.tree.insert("", "end", values=(num_senha, senha, nome_fila))

            self.status_bar.config(text=f"{len(dados)} senhas carregadas com sucesso.")
            # Garante que a interface foi atualizada antes de imprimir:
            self.update_idletasks()
        except Exception as e:
            messagebox.showerror("Erro ao carregar senhas", str(e))
            self.status_bar.config(text="Erro ao carregar dados da API.")

    def build_interface(self):
        # =====================
        # Frame Superior: Botões e status
        # =====================
        top_frame = tk.Frame(self)
        top_frame.pack(pady=10, padx=10, fill='x')
        # Botão Iniciar Serviço
        btn_iniciar = tk.Button(top_frame, text="Iniciar Serviço", command=self.iniciar_servico)
        btn_iniciar.pack(side='left', padx=5)

        # Botão Parar Serviço
        btn_parar = tk.Button(top_frame, text="Parar Serviço", command=self.parar_servico)
        btn_parar.pack(side='left', padx=5)


        # Label de Status
        lbl_status_text = tk.Label(top_frame, text="Status:")
        lbl_status_text.pack(side='left', padx=(20, 5))

        # Label de status dinâmico
        self.lbl_status_value = tk.Label(top_frame, text="Parado", fg="red")
        self.lbl_status_value.pack(side='left', padx=5)

        # Botão Imprimir
        btn_imprimir = tk.Button(top_frame, text="Imprimir", command=self.on_btn_imprimir_click)
        btn_imprimir.pack(side='right', padx=5)

        # Combobox de impressoras
        impressoras = listar_impressoras()
        self.cb_impressora = ttk.Combobox(top_frame, values=impressoras, state="readonly", width=30)
        self.cb_impressora.pack(side='right', padx=5)

        lb_impressora = tk.Label(top_frame, text="Selecione a impressora:")
        lb_impressora.pack(side='right', padx=5)

        # =====================
        # Frame Central: Grid (Tabela)
        # =====================
        grid_frame = tk.Frame(self)
        grid_frame.pack(padx=10, pady=10, fill='both', expand=True)

        columns = ("num_senha", "senha", "nome_fila")
        self.tree = ttk.Treeview(grid_frame, columns=columns, show="headings")
        self.tree.heading("num_senha", text="ID Senha")
        self.tree.heading("senha", text="Senha")
        self.tree.heading("nome_fila", text="Nome fila")

        self.tree.column("num_senha", width=100)
        self.tree.column("senha", width=100)
        self.tree.column("nome_fila", width=100)

        scrollbar = ttk.Scrollbar(grid_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # =====================
        # Frame Inferior: Barra de status
        # =====================
        self.status_bar = tk.Label(self, text="Pronto", bd=1, relief="sunken", anchor="w")
        self.status_bar.pack(side='bottom', fill='x')


