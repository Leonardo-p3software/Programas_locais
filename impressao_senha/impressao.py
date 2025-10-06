import tkinter as tk
from tkinter import ttk, messagebox
import win32print  # Biblioteca para acessar as impressoras no Windows
import json
import qrcode
from PIL import Image, ImageTk

def listar_impressoras():
    """Retorna uma lista de impressoras disponíveis no sistema."""
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
            # Lê o arquivo JSON
            with open("dados.json", "r", encoding="utf-8") as f:
                dados = json.load(f)
            senha = str(dados["senha"]) # Extrai a senha do JSON
            # Monta o link usando a senha que está no arquivo JSON
            link_final = f"http://nuvem.p3software.com.br:8080/ver_posicao/{senha}"

            # gerando QR Code
            qr = qrcode.make(link_final)
            qr = qr.resize((150, 150))
            qr_img = ImageTk.PhotoImage(qr)

            # exibindo o QR Code na interface
            qr_label.config(image=qr_img)
            qr_label.image = qr_img  # Referência para não perder a imagem

            # Opcional: mensagem de sucesso
            messagebox.showinfo("QR Code gerado", f"QR Code gerado para o link:\n{link_final}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler o arquivo JSON ou gerar QR Code: {e}")
            return

    btn_imprimir.config(command=imprimir)

    root.mainloop()

if __name__ == "__main__":
    main()
