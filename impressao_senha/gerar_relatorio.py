
#================================
# Gerar Relatório
#================================
import os
import io
import time
import webbrowser
import tempfile
from tkinter import messagebox
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from PIL import ImageTk
import qrcode


class GeradorRelatorioQR:
    def __init__(self):
        self.senha = None
        self.link_final = None
        self.qr_path = None

    def gerar_qr_code(self, link_final):
        """Gera o QR Code, exibe na interface e salva como arquivo temporário."""
        try:
            qr = qrcode.make(link_final)
            qr = qr.resize((150, 150))
            
            #qr_img = ImageTk.PhotoImage(qr)
            #qr_label.config(image=qr_img)
            #qr_label.image = qr_img  # Evita garbage collection

            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_file:
                qr_path = tmp_file.name

            
            qr.convert('RGB').save(qr_path, 'PNG')

            return qr_path
        except Exception as e:
            messagebox.showerror("Erro ao gerar QR Code", str(e))
            return False
        

    def visualizar_pdf(self, pdf_bytes):
        """Abre o PDF em memória no visualizador padrão do sistema."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_bytes)
            tmp_path = tmp_file.name

        webbrowser.open(f'file://{tmp_path}')
        time.sleep(3)

        try:
            os.remove(tmp_path)
        except Exception:
            pass  # Arquivo pode estar em uso

    def imprimir_senha(self, impressora, senha, num_senha, nome_fila):
        """Função principal que valida, gera QR Code e cria o PDF."""

        try:
           
            if not impressora or not senha:
                return

            link_final = f"http://nuvem.p3software.com.br:8080/ver_posicao/{num_senha}"
            self.qr_path = self.gerar_qr_code(link_final)
            if not self.qr_path:
                return


            buffer = io.BytesIO()
            custom_page_size = (80 * mm, 297 * mm)
            relatorio = canvas.Canvas(buffer, pagesize=custom_page_size)
            
            # Texto principal
            texto_senha = relatorio.beginText(60, 800)

            texto_senha.setFont("Helvetica", 10)
            texto_senha.textLine("Fila:" + nome_fila)
            texto_senha.textOut("Sua senha é ")
            texto_senha.setFont("Helvetica-Bold", 12)
            texto_senha.textOut(senha)
            texto_senha.setFont("Helvetica", 10)
            texto_senha.textLine(".")
            relatorio.drawText(texto_senha)

            # QR Code
            relatorio.drawImage(self.qr_path, 65, 670, width=100, height=100)
            
            # Texto abaixo do QR Code
            texto_abaixo_qr = ["Escaneie o QR Code para acessar",
            "sua posição na fila."]
            
            text_y = 670 - 20  # margem inferior
            texto_abaixo_qrcode = relatorio.beginText(25, text_y)
            texto_abaixo_qrcode.setFont("Helvetica", 10)
            texto_abaixo_qrcode.textLines(texto_abaixo_qr)
            relatorio.drawText(texto_abaixo_qrcode)

            relatorio.save()
            pdf_bytes = buffer.getvalue()
            if not pdf_bytes:
                messagebox.showerror("Erro", "Falha ao gerar conteúdo do PDF.")
                return



            self.visualizar_pdf(pdf_bytes)

        except Exception as e:
            messagebox.showerror("Erro ao gerar relatório", str(e))

