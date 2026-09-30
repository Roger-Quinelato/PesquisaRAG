"""Roda o pipeline inteiro na ordem certa (~8 min, deterministico por semente).

Uso:  python experimento/reproduzir.py

Cada script roda em processo proprio: os de figura configuram o estilo do
matplotlib/seaborn ao serem importados, e executa-los no mesmo processo
vazaria esse estilo de um para o outro, mudando os PNGs. Para no primeiro
que falhar.
"""
import os
import subprocess
import sys

ETAPAS = ("varredura.py", "equidade.py", "figuras.py",
          "figuras_relatorio.py", "figuras_poster.py")


def main():
    """Executa cada etapa com o mesmo interpretador; sai com erro se uma falhar."""
    pasta = os.path.dirname(os.path.abspath(__file__))
    for etapa in ETAPAS:
        print(f"\n=== {etapa} ===", flush=True)
        subprocess.run([sys.executable, os.path.join(pasta, etapa)], check=True)


if __name__ == "__main__":
    main()
