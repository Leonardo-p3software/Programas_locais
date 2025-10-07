import tkinter as tk                                    # Biblioteca para criar interfaces gráficas
from tkinter import ttk, messagebox                     # Biblioteca para widgets avançados e caixas de mensagem
import win32print, win32api                             # Biblioteca para acessar as impressoras no Windows
import json                                             # Biblioteca para manipulação de arquivos JSON
import qrcode                                           # Biblioteca para gerar QR Codes
from PIL import Image, ImageTk, ImageDraw, ImageFont    # Biblioteca para manipulação de imagens
import os                                               # Biblioteca para manipulação de arquivos e diretórios
import tempfile                                         # Biblioteca para criar arquivos temporários   


def listar_impressoras():
    """Retorna uma lista de impressoras disponíveis no sistema tanto local quanto em rede."""
    return [impressora[2] for impressora in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]

def main():
    root = tk.Tk()
    root.title("Impressão de Senhas")
    root.geometry("400x350")

    # Label
    label = tk.Label(root, text="Selecione a impressora:", font=("Arial", 12))
    label.pack(pady=10)

    # Dropdown de impressoras
    impressoras = listar_impressoras()  # Lista de impressoras do sistema
    combo = ttk.Combobox(root, values=impressoras, state="readonly", font=("Arial", 11))
    combo.pack(pady=5)

    # Botão de imprimir
    btn_imprimir = tk.Button(root, text="Imprimir", font=("Arial", 12), width=15)
    btn_imprimir.pack(pady=20)

    # Label para exibir o QR Code
    qr_label = tk.Label(root)
    qr_label.pack(pady=10)

    def imprimir():
        try:
            #verificações iniciais
            impressora_selecionada = combo.get()
            if not impressora_selecionada:
                messagebox.showerror("Erro", "Por favor, selecione uma impressora antes de continuar.")
                return

            # Define a impressora selecionada como impressora padrão do sistema
            try:
                win32print.SetDefaultPrinter(impressora_selecionada)
            except Exception as e:
                messagebox.showerror("Erro ao definir impressora padrão", str(e))
                return

            if not os.path.exists("dados.json"):
                messagebox.showerror("Erro", "Arquivo 'dados.json' não encontrado.")
                return

            # Lê o arquivo JSON
            with open("dados.json", "r", encoding="utf-8") as f:
                dados = json.load(f)

            senha = str(dados.get("senha", "")).strip() # Obtém a senha do JSON e remove espaços em branco
            if not senha: # Verifica se a senha está vazia
                messagebox.showerror("Erro", "Chave 'senha' não encontrada ou está vazia no arquivo JSON.")
                return
            
            link_final = f"http://nuvem.p3software.com.br:8080/ver_posicao/{senha}"

            # gerando QR Code
            qr = qrcode.make(link_final)
            qr = qr.resize((150, 150))

            # exibindo o QR Code na interface
            qr_img = ImageTk.PhotoImage(qr)
            qr_label.config(image=qr_img)
            qr_label.image = qr_img  # Referência para não perder a imagem

            try:
                # cria arquivo temporário para a imagem
                with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                    tmp_path = tmp_file.name
                # salvando o QR Code como PNG
                qr.convert('RGB').save(tmp_path, 'PNG')

                '''
                # envia o arquivo de imagem para impressão usando a impressora padrão
                try:
                    win32api.ShellExecute(0, "print", tmp_path, None, ".", 0)
                    messagebox.showinfo("Impressão enviada", f"Arquivo de imagem gerado em:\n{tmp_path}\nEnviado para impressão na impressora padrão ('{impressora_selecionada}').")
                except Exception as e_print:
                    messagebox.showwarning("Falha ao imprimir", f"Arquivo gerado em:\n{tmp_path}\nFalha ao enviar para a impressora: {e_print}")
                '''

            except Exception as e_build:
                messagebox.showerror("Erro ao preparar imagem para impressão", str(e_build))
                return
        except Exception as e:
            # Exibe a mensagem do erro para facilitar debug
            messagebox.showerror("Erro", str(e))
            return

    btn_imprimir.config(command=imprimir)
    root.mainloop()

if __name__ == "__main__":
    main()
