import tkinter as tk
from tkinter import messagebox
import json
import qrcode
from PIL import Image, ImageTk
import os
import tempfile
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
import webbrowser

def validar_dados():
    """Valida a existência do arquivo JSON com a senha."""
    if not os.path.exists("dados.json"):
        messagebox.showerror("Erro", "Arquivo 'dados.json' não encontrado.")
        return None, None

    with open("dados.json", "r", encoding="utf-8") as f:
        dados = json.load(f)

    senha = str(dados.get("senha", "")).strip()
    if not senha:
        messagebox.showerror("Erro", "Chave 'senha' não encontrada ou está vazia no arquivo JSON.")
        return None, None

    link_final = f"http://nuvem.p3software.com.br:8080/ver_posicao/{senha}"
    return senha, link_final

def gerar_qr_code(link_final, qr_label):
    """Gera o QR Code, exibe na interface e salva como arquivo temporário."""
    try:
        qr = qrcode.make(link_final)
        qr = qr.resize((200, 200))

        qr_img = ImageTk.PhotoImage(qr)
        qr_label.config(image=qr_img)
        qr_label.image = qr_img  # Evita perda de referência

        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_path = tmp_file.name
        qr.convert('RGB').save(tmp_path, 'PNG')

        return tmp_path
    except Exception as e:
        messagebox.showerror("Erro ao gerar QR Code", str(e))
        return None


def imprimir(qr_label):
    """Função principal que valida, gera QR Code e cria o PDF."""
    try:
        # Valida o JSON e obtém senha + link final
        senha, link_final = validar_dados()
        if not senha or not link_final:
            return

        # Gera o QR Code e exibe na interface
        tmp_path = gerar_qr_code(link_final, qr_label)
        if not tmp_path:
            return

        try:
            base_dir = os.path.dirname(os.path.abspath(__file__)) # apontando para a pasta do script
            nome_arquivo = "relatorio.pdf"
            pdf_path = os.path.join(base_dir, nome_arquivo) 
            
            # Gera o relatório PDF
            custom_page_size = (80 * mm, 297 * mm)
            c = canvas.Canvas(pdf_path, pagesize=custom_page_size)

            # Texto principal
            text_obj = c.beginText(60, 800)
            text_obj.setFont("Helvetica", 10)
            text_obj.textOut("Sua senha é ")
            text_obj.setFont("Helvetica-Bold", 12)
            text_obj.textOut(senha)
            text_obj.setFont("Helvetica", 10)
            text_obj.textLine(".")
            c.drawText(text_obj)

            # Inserir QR Code no PDF
            qr_x = 65
            qr_y = 690
            qr_width = 100
            qr_height = 100
            c.drawImage(tmp_path, qr_x, qr_y, width=qr_width, height=qr_height)

            # Texto secundário e dinâmico abaixo do QR Code
            texto_abaixo_qr = [
                "Escaneie o QR Code para acessar sua",
                "posição na fila."
            ]

            # Calculando a posição do texto abaixo do QR Code
            margem_inferior = 20  # fresta do QR Code e o texto
            text_y = qr_y - margem_inferior

            text_obj = c.beginText(25, text_y)
            text_obj.setFont("Helvetica", 10)
            # For para adicionar cada linha do texto
            for linha in texto_abaixo_qr:
                text_obj.textLine(linha)
            c.drawText(text_obj)

            # Salva o PDF
            c.save()

            # Exibe mensagem de sucesso
            messagebox.showinfo(
                "Relatório gerado",
                f"O Relatório foi gerado com sucesso. \nEle será aberto para visualização."
            )

            # Abre PDF no visualizador padrão
            #webbrowser.open(f'file://{pdf_path}')

        except Exception as e_pdf:
            messagebox.showerror("Erro ao gerar PDF", str(e_pdf))
            return

    except Exception as e:
        messagebox.showerror("Erro", str(e))
        return


'''
def visualizar_pdf(pdf_bytes):
    """
    Abre um PDF em memória no visualizador padrão do sistema.
    Cria um arquivo temporário que pode ser apagado depois.
    """
    # Cria arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_bytes)
        tmp_path = tmp_file.name

    # Abre no visualizador padrão
    webbrowser.open(f'file://{tmp_path}')
'''


def main():
    root = tk.Tk()
    root.title("Impressão de Senhas")
    root.geometry("400x350")

    btn_imprimir = tk.Button(root, text="Imprimir", font=("Arial", 12), width=15)
    btn_imprimir.pack(pady=20)

    qr_label = tk.Label(root)
    qr_label.pack(pady=10)

    btn_imprimir.config(command=lambda: imprimir(qr_label))

    root.mainloop()


if __name__ == "__main__":
    main()