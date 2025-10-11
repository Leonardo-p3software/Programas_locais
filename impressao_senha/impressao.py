import tkinter as tk                                    # Biblioteca para criar interfaces gráficas
from tkinter import ttk, messagebox                     # Biblioteca para widgets avançados e caixas de mensagem
import win32print, win32api                             # Biblioteca para acessar as impressoras no Windows
import json                                             # Biblioteca para manipulação de arquivos JSON
import qrcode                                           # Biblioteca para gerar QR Codes
from PIL import Image, ImageTk, ImageDraw, ImageFont    # Biblioteca para manipulação de imagens
import os                                               # Biblioteca para manipulação de arquivos e diretórios
import tempfile                                         # Biblioteca para criar arquivos temporários   
from reportlab.lib.pagesizes import A4                  # Biblioteca para definir tamanhos de página
from reportlab.pdfgen import canvas                     # Biblioteca para gerar PDFs
from reportlab.lib.units import mm                      # Biblioteca para unidades de medida 
import io                                               # Biblioteca para manipulação de streams de dados
import webbrowser                                       # Biblioteca para abrir URLs no navegador padrão

def listar_impressoras():
    """Retorna uma lista de impressoras disponíveis no sistema tanto local quanto em rede."""
    return [impressora[2] for impressora in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)]


def validar_dados(combo):
    """Valida a impressora selecionada e o arquivo JSON com a senha."""
    impressora_selecionada = combo.get()
    if not impressora_selecionada:
        messagebox.showerror("Erro", "Por favor, selecione uma impressora antes de continuar.")
        return None, None

    # Define a impressora selecionada como padrão
    try:
        win32print.SetDefaultPrinter(impressora_selecionada)
    except Exception as e:
        messagebox.showerror("Erro ao definir impressora padrão", str(e))
        return None, None

    # Verifica existência do arquivo JSON
    if not os.path.exists("dados.json"):
        messagebox.showerror("Erro", "Arquivo 'dados.json' não encontrado.")
        return None, None

    # Lê o arquivo JSON
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
        # Gera QR Code e redimensiona
        qr = qrcode.make(link_final)
        qr = qr.resize((150, 150))

        # Exibe na interface
        qr_img = ImageTk.PhotoImage(qr)
        qr_label.config(image=qr_img)
        qr_label.image = qr_img  # Evita perda de referência da imagem

        # Cria arquivo temporário
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
            tmp_path = tmp_file.name
        # Salva QR Code como PNG
        qr.convert('RGB').save(tmp_path, 'PNG')

        return tmp_path
    except Exception as e:
        messagebox.showerror("Erro ao gerar QR Code", str(e))
        return None


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

def imprimir(combo, qr_label):
    """Função principal que valida, gera QR Code e cria o PDF."""
    try:
        senha, link_final = validar_dados(combo)
        if not senha or not link_final:
            return

        tmp_path = gerar_qr_code(link_final, qr_label)
        if not tmp_path:
            return

        try:
            '''
            base_dir = os.path.dirname(os.path.abspath(__file__)) # apontando para o diretório do script
            nome_arquivo = "relatorio.pdf"
            pdf_path = os.path.join(base_dir, nome_arquivo)
            '''



            # Gera o relatório PDF
            buffer = io.BytesIO()
            custom_page_size = (80 * mm, 297 * mm)
            c = canvas.Canvas(buffer, pagesize=custom_page_size)


            # Texto principal
            text_obj = c.beginText(60, 800)
            text_obj.setFont("Helvetica", 10)
            text_obj.textOut("Sua senha é ")
            text_obj.setFont("Helvetica-Bold", 12)
            text_obj.textOut(senha)
            text_obj.setFont("Helvetica", 10)
            text_obj.textLine(".")
            c.drawText(text_obj)

            # Inserir QR Code no pdf
            qr_x = 65
            qr_y = 690
            qr_width = 100
            qr_height = 100
            c.drawImage(tmp_path, qr_x, qr_y, width=qr_width, height=qr_height)

            # Texto secundário e dunâmico
            texto_abaixo_qr = [
                "Escaneie o QR Code para acessar sua",
                "posição na fila."
            ]

            # calculando a posição da altura do texto abaixo do QR Code
            margem_inferior = 20  # fresta do QR Code e o texto
            text_y = qr_y - margem_inferior

            text_obj = c.beginText(25, text_y)
            text_obj.setFont("Helvetica", 10)
            #for para adicionar cada linha do texto
            for linha in texto_abaixo_qr:
                text_obj.textLine(linha)
            c.drawText(text_obj)

            '''
            text_obj = c.beginText(25, 600)
            text_obj.setFont("Helvetica", 10)
            text_obj.textLine("Escaneie o QR Code para acessar sua")
            text_obj.textLine("posição na fila.")
            '''
            c.save() 

            # Salva o PDF no caminho especificado
            pdf_bytes = buffer.getvalue()

            messagebox.showinfo(
                "Relatório gerado", 
                "O relatório foi gerado com sucesso em memoria"
            )

            visualizar_pdf(pdf_bytes)

        except Exception as e_pdf:
            messagebox.showerror("Erro ao gerar PDF", str(e_pdf))
            return

    except Exception as e:
        messagebox.showerror("Erro", str(e))
        return


def main():
    root = tk.Tk()
    root.title("Impressão de Senhas")
    root.geometry("400x350")

    label = tk.Label(root, text="Selecione a impressora:", font=("Arial", 12))
    label.pack(pady=10)

    impressoras = listar_impressoras()
    combo = ttk.Combobox(root, values=impressoras, state="readonly", font=("Arial", 11))
    combo.pack(pady=5)

    btn_imprimir = tk.Button(root, text="Imprimir", font=("Arial", 12), width=15)
    btn_imprimir.pack(pady=20)

    qr_label = tk.Label(root)
    qr_label.pack(pady=10)

    btn_imprimir.config(command=lambda: imprimir(combo, qr_label))

    root.mainloop()


if __name__ == "__main__":
    main()