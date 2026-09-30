# Imagem mínima para reproduzir o experimento de simulação.
#
#   docker build -t pesquisarag .
#   docker run --rm pesquisarag                     # testes (poucos segundos)
#
# Pipeline completo (~8 min), com as saídas gravadas no diretório local:
#
#   docker run --rm -v "$PWD/resultados:/pesquisa/resultados" \
#       -v "$PWD/figuras:/pesquisa/figuras" pesquisarag python experimento/reproduzir.py
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /pesquisa

# Dependências antes do código: mudar um script não reinstala os pacotes.
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY experimento/ experimento/
COPY tests/ tests/

CMD ["python", "-m", "unittest", "discover", "-v", "tests"]
