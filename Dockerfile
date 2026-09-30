# Imagem mínima para reproduzir o experimento de simulação.
#
#   docker build -t pesquisarag .
#   docker run --rm pesquisarag                     # testes (poucos segundos)
#
# Pipeline completo (~8 min), com as saídas gravadas no diretório local:
#
#   docker run --rm -v "$PWD/resultados:/pesquisa/resultados" \
#       -v "$PWD/figuras:/pesquisa/figuras" pesquisarag \
#       sh -c "python experimento/varredura.py && python experimento/equidade.py \
#              && python experimento/figuras.py && python experimento/figuras_relatorio.py \
#              && python experimento/figuras_poster.py"
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    MPLBACKEND=Agg \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /pesquisa

# Dependências antes do código: mudar um script não reinstala os pacotes.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY experimento/ experimento/
COPY tests/ tests/
RUN mkdir -p resultados figuras

CMD ["python", "-m", "unittest", "discover", "-v", "tests"]
