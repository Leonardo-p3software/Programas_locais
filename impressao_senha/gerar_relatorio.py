import qrcode
from PIL import Image, ImageDraw, ImageFont, ImageWin
import win32print
import tempfile, os
import win32ui


class GeradorRelatorioQR:
    def imprimir_senha(self, impressora, senha, num_senha, nome_fila):

        # === QR CODE ===
        link = f"http://nuvem.p3software.com.br:8080/ver_posicao/{num_senha}"
        qr = qrcode.make(link).resize((240, 240))

        # === CRIA IMAGEM ===
        largura = 580   # 80mm em 203dpi
        altura = 600
        imagem = Image.new("RGB", (largura, altura), "white")
        draw = ImageDraw.Draw(imagem)

        # fonte segura
        try:
            fonte_titulo = ImageFont.truetype("arial.ttf", 32)
            fonte_texto = ImageFont.truetype("arial.ttf", 32)
        except:
            fonte_titulo = ImageFont.load_default()
            fonte_texto = ImageFont.load_default()

        draw.text((20, 00), f"=========================", fill="black", font=fonte_texto)
        draw.text((20, 30), f"Fila: {nome_fila}", fill="black", font=fonte_texto)
        draw.text((20, 80), f"Sua senha: {senha}", fill="black", font=fonte_titulo)

        imagem.paste(qr, (165, 150))

        draw.text((20, 430), "             Escaneie o QR Code", fill="black", font=fonte_texto)
        draw.text((20, 465), "            para ver sua posição.", fill="black", font=fonte_texto)

        # === CONVERTER PARA 1-BIT (ESSENCIAL PARA IMPRESSORAS USB TERMO) ===
        imagem = imagem.convert("1")  # preto e branco puro!

        # === SALVAR TEMP ===
        temp_path = os.path.join(tempfile.gettempdir(), "ticket_print.bmp")
        imagem.save(temp_path, "BMP")

        # === IMPRIMIR ===
        self.imprimir_imagem_direto(temp_path, impressora)

        # remover arquivo depois
        try:
            os.remove(temp_path)
        except:
            pass
  
    def imprimir_imagem_direto(self, caminho_imagem, impressora=None):
        # Seleciona impressora padrão se não fornecida
        if not impressora:
            impressora = win32print.GetDefaultPrinter()

        # Abre a imagem
        imagem = Image.open(caminho_imagem)

        # Cria DC da impressora
        hPrinter = win32print.OpenPrinter(impressora)
        try:
            hDC = win32ui.CreateDC()
            hDC.CreatePrinterDC(impressora)

            # Inicia impressão
            hDC.StartDoc("Ticket")
            hDC.StartPage()

            # Cria objeto ImageWin compatível
            dib = ImageWin.Dib(imagem)

            # Determina área de impressão (em pixels)
            largura, altura = imagem.size
            # Define a posição de impressão sem esticar (0,0 até largura/altura originais)
            dib.draw(hDC.GetHandleOutput(), (0, 0, largura, altura))

            hDC.EndPage()
            hDC.EndDoc()
            hDC.DeleteDC()
        finally:
            win32print.ClosePrinter(hPrinter)


