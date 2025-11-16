# proj_raiz/__main__.py
'''
from .main import TelaLogin


if __name__ == "__main__":
    app = TelaLogin()
    app.mainloop()
'''
import os
import sys

# 🔧 Garante que o diretório raiz do projeto esteja no sys.path
if getattr(sys, 'frozen', False):
    base_dir = os.path.dirname(sys.executable)
else:
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

# Agora o import absoluto funciona corretamente
from impressao_senha.main import main


def run():
    """Função de inicialização do app (chamada pelo start.py)"""
    main()


if __name__ == "__main__":
    run()
