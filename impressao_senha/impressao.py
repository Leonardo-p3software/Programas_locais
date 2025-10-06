import tkinter as tk                                    # Biblioteca para criar interfaces gráficas
from tkinter import ttk, messagebox                     # Biblioteca para widgets avançados e caixas de mensagem
import win32print, win32api                              # Biblioteca para acessar as impressoras no Windows
import json                                             # Biblioteca para manipulação de arquivos JSON
import qrcode                                           # Biblioteca para gerar QR Codes
from PIL import Image, ImageTk, ImageDraw, ImageFont    # Biblioteca para manipulação de imagens
import os                                               # Biblioteca para manipulação de arquivos e diretórios


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

            # Monta o link usando a senha que está no arquivo JSON
            link_final = f"http://nuvem.p3software.com.br:8080/ver_posicao/{senha}"

            # gerando QR Code
            qr = qrcode.make(link_final)
            qr = qr.resize((150, 150))

            # exibindo o QR Code na interface
            qr_img = ImageTk.PhotoImage(qr)
            qr_label.config(image=qr_img)
            qr_label.image = qr_img  # Referência para não perder a imagem

            '''
            # montando a imagem para impressão
            img_final = Image.new("RGB", (300, 400), "white")
            draw = ImageDraw.Draw(img_final)
            try:
                fonte_titulo = ImageFont.truetype("arial.ttf", 22)
                fonte_sub = ImageFont.truetype("arial.ttf", 18)
                fonte_pequena = ImageFont.truetype("arial.ttf", 14)
            except:
                fonte_titulo = fonte_sub = fonte_pequena = ImageFont.load_default()

            # Adiciona textos e QR Code na imagem
            draw.text((90, 20), "Fila", font=fonte_titulo, fill="black")
            draw.text((70, 50), "Direção", font=fonte_sub, fill="black")
            draw.text((40, 80), f"Sua Senha é: {senha}", font=fonte_sub, fill="black")
            img_final.paste(qr, (75, 120))
            draw.text((20, 290), "Escaneie o QRCode para\nacompanhar sua posição na fila", font=fonte_pequena, fill="black")

            # Salva imagem temporária
            temp_path = "temp_print.bmp"
            img_final.save(temp_path)

            # Imprime usando método simplificado
            win32print.SetDefaultPrinter(impressora_selecionada)
            win32api.ShellExecute(0, "print", temp_path, None, ".", 0)

            # Remove imagem temporária
            if os.path.exists(temp_path):
                os.remove(temp_path)

            '''
            # mensagem de sucesso
            messagebox.showinfo("QR Code gerado", f"QR Code gerado para o link:\n{link_final} e sua impressão foi enviada para a impressora '{impressora_selecionada}' com a senha '{senha}'.")
        except Exception as e:
            messagebox.showerror("Erro")
            return

    btn_imprimir.config(command=imprimir)
    root.mainloop()

if __name__ == "__main__":
    main()
