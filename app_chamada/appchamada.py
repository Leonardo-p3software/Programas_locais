import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import threading
import time
from datetime import datetime
import pyttsx3 #biblitoteca para voz do windows

class TelaChamada(tk.Toplevel):
    def __init__(self, api_client=None, master=None):
        super().__init__(master)
        self.title("Chamada Eletrônica")
        self.api_client = api_client
        # Controle de atualização automática
        self.executando = False   # status inicial = parado
        self.after_id = None      # guardará o ID do after() para cancelamento


        # Abre a janela maximizada sem loop infinito
        self.bind("<Map>", self.maximize_once)

        # Controle de vídeo
        self.cap = None
        self.video_running = False
        self.video_thread = None
        self.frame_lock = threading.Lock()
        self.current_frame = None

        self.video_ativado = False
        self.video_timer_id = None  # guardará o after que aguarda 20 segundos

        self.create_widgets()
       
       

    def maximize_once(self, event=None):
        """Maximiza apenas uma vez, sem loop."""
        self.state("zoomed")
        self.unbind("<Map>")  # evita loop infinito

    def create_widgets(self):
        # Cabeçalho
        header_frame = tk.Frame(self, bg="white")
        header_frame.pack(fill="x", pady=5)

        logo = tk.Label(header_frame, text="🌀 FUSION", font=("Arial Black", 32), fg="green", bg="white")
        logo.pack(side="left", padx=20)

        self.btn_parar = tk.Button(header_frame, text="Iniciar", width=10, command=self.Iniciar_parar)
        self.btn_parar.pack(side="right", padx=20)


        # Abas
        #notebook = ttk.Notebook(self)
        #notebook.pack(expand=True, fill="both")

        # === BARRA DE STATUS ===
        status_frame = tk.Frame(self, bg="#f0f0f0", height=25)
        status_frame.pack(side="bottom", fill="x")
        
        status_frame.pack_propagate(False)  # garante que a altura seja respeitada

        #self.status_label = tk.Label(status_frame, text="Pronto", anchor="w", bg="#f0f0f0")
        #self.status_label.pack(fill="both", padx=10)
        # Parte esquerda: mensagens
        self.status_label = tk.Label(status_frame, text="Pronto", anchor="w", bg="#f0f0f0")
        self.status_label.pack(side="left", fill="x", expand=True, padx=10)

        # Parte direita: status de execução
        self.status_execucao = tk.Label(status_frame, text="⏹ Parado", anchor="e", bg="#f0f0f0", fg="red")
        self.status_execucao.pack(side="right", padx=10)

        # Notebook
        notebook = ttk.Notebook(self)
        notebook.pack(side="top", expand=True, fill="both")  # adicionado side="top"
        
        self.notebook = notebook  # salva referência para poder alternar abas

        # === ABA CHAMADA ===
        frame_chamada = tk.Frame(notebook, bg="white")
        notebook.add(frame_chamada, text="Chamada")

        tk.Label(frame_chamada, text="Chamando", font=("Arial", 18, "bold"), bg="white").pack(pady=(10, 0))
        self.label_chamando = tk.Label(frame_chamada, text=" ", font=("Arial", 24), bg="white")
        self.label_chamando.pack(pady=20)

        tk.Label(frame_chamada, text="Últimas chamadas", font=("Arial", 16, "bold"), bg="white").pack()

        # Frame contendo Text + Scrollbar
        text_frame = tk.Frame(frame_chamada, bg="white")
        text_frame.pack(pady=10, fill="both", expand=True)

        # Barra de rolagem vertical
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        # Widget Text com rolagem
        self.text_ultimas = tk.Text(
            text_frame,
            font=("Arial", 20),
            bg="white",
            bd=0,
            wrap="word",
            yscrollcommand=scrollbar.set
        )
        self.text_ultimas.insert("end", "")
        self.text_ultimas.config(state="disabled")
        self.text_ultimas.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self.text_ultimas.yview)

        # === ABA VÍDEO ===
        frame_video = tk.Frame(notebook, bg="black")
        notebook.add(frame_video, text="Vídeo")

        self.video_label = tk.Label(frame_video, bg="black")
        self.video_label.pack(expand=True, fill="both")

        btn_frame = tk.Frame(frame_video, bg="black")
        btn_frame.pack(pady=10)

        # self.btn_video = tk.Button(btn_frame, text="▶ Reproduzir Vídeo", command=self.play_video)
        # self.btn_video.pack(side="left", padx=5)
        # self.btn_stop = tk.Button(btn_frame, text="⏹ Parar", command=self.stop_video)
        # self.btn_stop.pack(side="left", padx=5)
        self.agendar_video_automatico()



        # Inicia atualização automática das chamadas
        #self.after(2000, self.atualizar_periodicamente)


    # -------------------------
    # CONTROLE DE VÍDEO
    # -------------------------
    def play_video(self):
        video_path = "app_chamada/video.mp4"
        self.cap = cv2.VideoCapture(video_path)

        if not self.cap.isOpened():
            messagebox.showerror("Erro", f"Não foi possível abrir o vídeo: {video_path}")
            return

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_interval = 1.0 / fps if fps > 0 else 1 / 30

        self.video_running = True
        self.video_thread = threading.Thread(target=self.video_loop, daemon=True)
        self.video_thread.start()
        self.update_gui_frame()

    def stop_video(self):
        self.video_running = False
        if self.cap:
            self.cap.release()
            self.cap = None
        self.video_label.config(image="", bg="black")

    def video_loop(self):
        """Thread que lê os frames do vídeo na velocidade correta."""
        while self.video_running and self.cap.isOpened():
            start = time.time()
            ret, frame = self.cap.read()
            if not ret:
                # Reinicia o vídeo automaticamente
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            with self.frame_lock:
                self.current_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Espera o tempo exato do FPS real
            elapsed = time.time() - start
            time.sleep(max(0, self.frame_interval - elapsed))

    def update_gui_frame(self):
        """Atualiza o frame na interface (Tkinter) sem travar."""
        if not self.video_running:
            return

        with self.frame_lock:
            frame = self.current_frame

        if frame is not None:
            # Redimensionar frame para caber na área do label
            label_width = max(1, self.video_label.winfo_width())
            label_height = max(1, self.video_label.winfo_height())
            resized = cv2.resize(frame, (label_width, label_height), interpolation=cv2.INTER_AREA)

            img = Image.fromarray(resized)
            imgtk = ImageTk.PhotoImage(image=img)
            self.video_label.imgtk = imgtk
            self.video_label.config(image=imgtk)

        # Atualiza a imagem a cada 15 ms (~60 fps possíveis)
        self.after(15, self.update_gui_frame)



    # -------------------------
    # MODO VÍDEO AUTOMÁTICO
    # -------------------------
    def agendar_video_automatico(self):
        """Agenda a troca automática para o vídeo em 20 segundos se não houver chamadas."""
        # Cancela qualquer agendamento anterior
        if self.video_timer_id:
            self.after_cancel(self.video_timer_id)

        # Agenda execução para daqui a 20 segundos
        self.video_timer_id = self.after(20000, self.tocar_video_automaticamente)

    def tocar_video_automaticamente(self):
        """Muda para a aba de vídeo e inicia a reprodução."""
        if not hasattr(self, "notebook") or self.notebook is None:
            print("Notebook ainda não está disponível — adiando vídeo automático.")
            # tenta novamente em 2 segundos
            self.video_timer_id = self.after(2000, self.tocar_video_automaticamente)
            return

        if self.video_ativado:
            return

        self.video_ativado = True
        self.notebook.select(1)
        self.play_video()
        self._atualizar_status("Nenhuma chamada — vídeo iniciado automaticamente.")


    def voltar_para_chamada(self):
        """Retorna para a aba de chamada quando houver dados."""
        # Cancela agendamento do vídeo se existir
        if self.video_timer_id:
            self.after_cancel(self.video_timer_id)
            self.video_timer_id = None

        # Se o vídeo estiver rodando, para
        if self.video_ativado:
            self.stop_video()
            self.video_ativado = False
            self.notebook.select(0)  # volta para aba chamada
            self._atualizar_status("Chamadas encontradas — voltando para tela de chamadas.")
    

    # -------------------------
    # ATUALIZAÇÃO DE CHAMADAS
    # -------------------------
    def atualizar_chamadas(self):
        """Busca chamadas da API e atualiza os widgets de tela."""
        def tarefa():
            try:
                self._atualizar_status("Atualizando chamadas...")

                dados = []
                if self.api_client:
                    dados = self.api_client.buscar_chamadas()

                '''if not dados:
                    self._atualizar_status("Nenhum dado retornado da API.")
                    return

                textos = [item.get("texto", "") for item in dados if item.get("texto")]
                if not textos:
                    self._atualizar_status("Nenhum texto válido recebido.")
                    return '''
                
                if not dados:
                    self._atualizar_status("Nenhum dado retornado da API.")
                    # Agenda vídeo automático em 20 segundos
                    self.after(0, self.agendar_video_automatico)
                    return

                textos = [item.get("texto", "") for item in dados if item.get("texto")]
                if not textos:
                    self._atualizar_status("Nenhum texto válido recebido.")
                    self.after(0, self.agendar_video_automatico)
                    return

                # Se chegou aqui, há dados — cancela vídeo e volta para aba chamada
                self.after(0, self.voltar_para_chamada)


                # Atualiza GUI no thread principal

                self.after(0, lambda: self._atualizar_widgets_chamada(dados))

                self._atualizar_status(f"Última atualização: {datetime.now().strftime('%H:%M:%S')}")

            except Exception as e:
                erro_msg = str(e)

                self.after(0, lambda e=e: messagebox.showerror("Erro", f"Falha ao atualizar chamadas:\n{e}"))
                
                self._atualizar_status("Erro ao atualizar chamadas.")

        # Executa em thread separada
        threading.Thread(target=tarefa, daemon=True).start()

    def _atualizar_widgets_chamada(self, dados):
        """Atualiza label_chamando e adiciona chamadas ao histórico rapidamente, sem after."""
        
        MAX_LINHAS = 30
        REMOVER_LINHAS = 15

        for item in dados:
            texto = item.get("texto", "")
            chamada_id = item.get("id")
            origem = item.get("origem", "fila_senhas")

            # Atualiza label principal (fica no último item)
            self.label_chamando.config(text=texto)
            # Atualiza GUI após processar todos
            self.label_chamando.update_idletasks()
            # Fala o nome do paciente 2 vezes
            
            for _ in range(2):  # 2 vezes
                self.falar_texto(texto)


            
            # Executa atualizar_realizado
            self.executar_atualizar_realizado(chamada_id, origem)

            # Atualiza histórico no Text (mais recentes no topo)
            self.text_ultimas.config(state="normal")
            self.text_ultimas.insert("1.0", f"{texto}\n")
            # Atualiza GUI após processar todos
            self.text_ultimas.update_idletasks()

            total_linhas = int(self.text_ultimas.index('end-1c').split('.')[0])
            if total_linhas > MAX_LINHAS:
                idx_inicio = f"{total_linhas - REMOVER_LINHAS + 1}.0"
                idx_fim = f"{total_linhas}.end"
                self.text_ultimas.delete(idx_inicio, idx_fim)

            self.text_ultimas.yview_moveto(0)
            self.text_ultimas.config(state="disabled")

        # Atualiza GUI após processar todos
        self.text_ultimas.update_idletasks()



    def _atualizar_status(self, mensagem):
        """Atualiza texto da barra de status."""
        self.status_label.config(text=mensagem)
        self.status_label.update_idletasks()


    def atualizar_periodicamente(self):
        """Executa atualização automática apenas quando em modo 'executando'."""
        if not self.executando:
            return  # sai se estiver parado

        self.atualizar_chamadas()
        # agenda próxima execução
        self.after_id = self.after(20000, self.atualizar_periodicamente)


    def executar_atualizar_realizado(self, chamada_id: int, origem: str):
        """
        Executa a função atualizar_realizado e trata a resposta.
        
        :param chamada_id: ID da SenhaChamada ou número Fusion
        :param origem: "fila_senhas" ou "fusion"
        """
        resultado = self.api_client.atualizar_realizado(chamada_id, origem)

        if 'erro' in resultado:
            # Tratar erro: pode exibir pop-up ou log
            print(f"[ERRO] Falha ao atualizar realizado: {resultado['erro']}")
            if 'detalhes' in resultado:
                print(f"Detalhes: {resultado['detalhes']}")
            if 'status_code' in resultado:
                print(f"Status code: {resultado['status_code']}")
            # Se estiver no Tkinter, poderia usar:
            # messagebox.showerror("Erro", f"{resultado['erro']}\nDetalhes: {resultado.get('detalhes','')}")
        else:
            # Atualização realizada com sucesso
            print(f"[OK] Chamada {chamada_id} atualizada com sucesso: {resultado}")
            # Se quiser exibir no Tkinter:
            # messagebox.showinfo("Sucesso", f"Chamada {chamada_id} atualizada com sucesso")

    ###################
    # Função que usa fala do windows.
    ################
    def falar_texto(self, texto: str, voz: str = None, velocidade: int = 150):
        """
        Lê o texto em voz humana usando o TTS do Windows.

        :param texto: Texto a ser falado
        :param voz: Nome da voz disponível no sistema (opcional)
        :param velocidade: Velocidade da fala (padrão 150)
        """
        engine = pyttsx3.init()
        
        # Configura velocidade
        engine.setProperty('rate', velocidade)
        
        # Configura voz (se fornecida)
        if voz:
            vozes = engine.getProperty('voices')
            for v in vozes:
                if voz.lower() in v.name.lower():
                    engine.setProperty('voice', v.id)
                    break

        engine.say(texto)
        
        engine.runAndWait()

    ###################
    # Função do Botão Iniciar/Parar
    ################
    def Iniciar_parar(self):
        """Alterna entre iniciar e parar a atualização automática."""
        if self.executando:
            # Parar execução
            self.executando = False
            self.btn_parar.config(text="Iniciar")
            self.status_execucao.config(text="⏹ Parado", fg="red")

            # Cancela o after pendente se houver
            if self.after_id:
                self.after_cancel(self.after_id)
                self.after_id = None

            self._atualizar_status("Atualização automática parada.")
        else:
            # Iniciar execução
            self.executando = True
            self.btn_parar.config(text="Parar")
            self.status_execucao.config(text="▶ Executando", fg="green")

            self._atualizar_status("Atualização automática iniciada.")
            # Chama a função imediatamente e agenda próximas
            self.atualizar_periodicamente()
