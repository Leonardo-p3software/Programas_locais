import tkinter as tk
from tkinter import messagebox
from .servidor_impressao import TelaImpressao
from conecta_api.chamar_api import ChamarFusionAPI


import sys, os

class TelaLogin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Impressão de senhas")
        # Barra de status
        self.status_bar = tk.Label(self, text="Sistema Fusion - P3 Software", bd=1,relief="sunken",anchor="w")
        self.status_bar.pack(side="bottom", fill="x")
        self.geometry("300x180")
        self.resizable(False, False)
        self.centralizar_tela()
        self.criar_widgets()

    def centralizar_tela(self):
        self.update_idletasks()
        largura = 300
        altura = 180
        x = (self.winfo_screenwidth() // 2) - (largura // 2)
        y = (self.winfo_screenheight() // 2) - (altura // 2)
        self.geometry(f"{largura}x{altura}+{x}+{y}")

    def criar_widgets(self):
        # Frame para os campos
        frame = tk.Frame(self)
        frame.pack(pady=20)

        # Usuário
        tk.Label(frame, text="Usuário:").grid(row=0, column=0, sticky="e")
        self.entry_usuario = tk.Entry(frame)
        self.entry_usuario.grid(row=0, column=1)

        # Senha
        tk.Label(frame, text="Senha:").grid(row=1, column=0, sticky="e")
        self.entry_senha = tk.Entry(frame, show="*")
        self.entry_senha.grid(row=1, column=1)

        # Botões
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        btn_login = tk.Button(btn_frame, text="Login", command=self.verificar_login)
        btn_login.grid(row=0, column=0, padx=5)

        btn_sair = tk.Button(btn_frame, text="Sair", command=self.quit)
        btn_sair.grid(row=0, column=1, padx=5)

    def verificar_login(self):
        usuario = self.entry_usuario.get()
        senha = self.entry_senha.get()

        '''if usuario.upper() == "LEO" and senha == "1234":
            self.abrir_tela_impressao()
        else:
            messagebox.showerror("Erro de login", "Usuário ou senha incorretos.") '''

        api_client = ChamarFusionAPI()

        # Tente autenticar com usuário e senha
        if api_client.autenticar(usuario, senha):
            print("Autenticado com sucesso!")
            self.abrir_tela_impressao(api_client)
        else:
            print("Falha na autenticação.")
            messagebox.showerror("Erro de login", "Usuário ou senha incorretos.")

    def abrir_tela_impressao(self, api_client):
        self.withdraw()  # Oculta a tela de login
        tela = TelaImpressao(api_client, self)  # Abre a tela de impressão
        # A tela de impressão é um Toplevel. Quando ela for fechada, a tela de login volta a aparecer.
        self.wait_window(tela)  # Espera a tela de impressão ser fechada
        self.deiconify()    # Mostra novamente a tela de login

def main():
    app = TelaLogin()
    app.mainloop()

if __name__ == "__main__":
    main()


