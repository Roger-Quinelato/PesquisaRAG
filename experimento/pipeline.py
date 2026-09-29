"""Nucleo do experimento: metricas de uma semente, cache por familia e pool.

- `rodar_semente` calcula, para UMA (configuracao, semente), as metricas de
  cada braco das familias pedidas. Toda a aleatoriedade vem de fluxos.fluxos,
  entao o resultado de uma familia nao depende de quais outras rodaram.
- O cache guarda um registro por (configuracao, semente, braco) em
  resultados/cache/<familia>.csv, com floats em repr (ida e volta exata).
  Cada familia tem uma chave: o SHA-256 do codigo de que ela depende, das
  versoes de numpy/scikit-learn e de N e K. Chave diferente = familia
  recalculada inteira. As linhas sao gravadas assim que cada tarefa termina,
  entao uma rodada interrompida retoma de onde parou.
- `executar` distribui as tarefas que faltam num pool de processos.
  executor.map preserva a ordem, e a agregacao por semente e' feita sempre na
  ordem das sementes: o resultado nao depende do numero de processos.
"""
import csv
import hashlib
import os
import sys
from concurrent.futures import ProcessPoolExecutor

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerador import Params                                            # noqa: E402
from bracos import BRACOS, calcular                                   # noqa: E402
from bracos_ml import BRACOS_ML, FAMILIAS_ML, calcular_ml             # noqa: E402
from fluxos import fluxos                                             # noqa: E402
from metricas import brier, ece, precisao_topk_desempate, fpr_por_ra  # noqa: E402

AQUI = os.path.dirname(os.path.abspath(__file__))
FAMILIAS = {"fechados": BRACOS, **FAMILIAS_ML}
# Codigo de que cada familia depende. Conservador de proposito: qualquer
# mudanca no modulo invalida a familia inteira.
FONTES_COMUNS = ("gerador.py", "metricas.py", "fluxos.py", "pipeline.py")
FONTES = {"fechados": ("bracos.py",), "nb": ("bracos_ml.py",),
          "adaboost": ("bracos_ml.py",), "calibrados": ("bracos_ml.py",)}
N_RAS = 8
CAMPOS = (["f_base", "beta", "pi", "semente", "braco", "prec", "brier", "ece", "n"]
          + [f"fpr_{r}" for r in range(N_RAS)])


# --------------------------------------------------------------------------
# uma semente
# --------------------------------------------------------------------------
def _registro(s, y, ra, u, k):
    """Exatamente o que varredura.uma_config calculava por braco: topk sobre o
    score cru, Brier e ECE sobre o score cortado em [0, 1]."""
    p = np.clip(s, 0.0, 1.0)
    prec, sel = precisao_topk_desempate(s, y, k, u)
    return {"prec": prec, "brier": brier(p, y), "ece": ece(p, y), "n": len(y),
            "fpr": fpr_por_ra(sel, ra, y, len(y), N_RAS)}


def rodar_semente(f_base, beta, pi, semente, familias, n, k, n_jobs=-1):
    """{braco: registro} de uma (configuracao, semente), so para `familias`."""
    params = Params(pi=pi, f_base=f_base, beta=beta)
    fx = fluxos(semente, params, n)
    out = {}
    if "fechados" in familias:
        for b, s in calcular(fx.ra, fx.F, fx.E, fx.f_true, params).items():
            out[b] = _registro(s, fx.F, fx.ra, fx.desempate[b], k)
    treinadas = [f for f in familias if f != "fechados"]
    if treinadas:
        scores, idx = calcular_ml(fx.ra, fx.F, fx.E, params, fx.treino, fx.sementes,
                                  treinadas, n_jobs)
        F_t, ra_t = fx.F[idx], fx.ra[idx]
        for b, s in scores.items():
            out[b] = _registro(s, F_t, ra_t, fx.desempate[b], k)
    return out


# --------------------------------------------------------------------------
# cache
# --------------------------------------------------------------------------
def chave(familia, n, k):
    import sklearn
    h = hashlib.sha256()
    for nome in FONTES_COMUNS + FONTES[familia]:
        with open(os.path.join(AQUI, nome), "rb") as fh:
            h.update(nome.encode() + b"\0" + fh.read())
    h.update(f"numpy={np.__version__};sklearn={sklearn.__version__};n={n};k={k!r}".encode())
    return h.hexdigest()


def _cfg(f_base, beta, pi):
    # repr de float nativo: '0.07', nunca 'np.float64(0.07)'.
    return (repr(float(f_base)), repr(float(beta)), repr(float(pi)))


class Cache:
    def __init__(self, pasta, n, k):
        self.pasta, self.n, self.k = pasta, n, k
        os.makedirs(pasta, exist_ok=True)

    def _arq(self, familia, ext):
        return os.path.join(self.pasta, f"{familia}.{ext}")

    def chave_valida(self, familia):
        try:
            with open(self._arq(familia, "chave"), encoding="utf-8") as fh:
                return fh.read().strip() == chave(familia, self.n, self.k)
        except OSError:
            return False

    def ler(self, familia):
        """{(cfg, semente): {braco: registro}} com o que estiver gravado."""
        out = {}
        try:
            fh = open(self._arq(familia, "csv"), encoding="utf-8", newline="")
        except OSError:
            return out
        with fh:
            for L in csv.DictReader(fh):
                reg = {"prec": float(L["prec"]), "brier": float(L["brier"]),
                       "ece": float(L["ece"]), "n": int(L["n"]),
                       "fpr": np.array([float(L[f"fpr_{r}"]) for r in range(N_RAS)])}
                cfg = (L["f_base"], L["beta"], L["pi"])
                out.setdefault((cfg, int(L["semente"])), {})[L["braco"]] = reg
        # Uma tarefa so conta como feita se todos os bracos da familia estao la
        # (uma escrita interrompida pode ter deixado so parte deles).
        return {t: r for t, r in out.items() if set(r) == set(FAMILIAS[familia])}

    def zerar(self, familia):
        with open(self._arq(familia, "csv"), "w", encoding="utf-8", newline="") as fh:
            csv.writer(fh).writerow(CAMPOS)
        with open(self._arq(familia, "chave"), "w", encoding="utf-8") as fh:
            fh.write(chave(familia, self.n, self.k) + "\n")

    def gravar(self, familia, cfg, semente, registros):
        with open(self._arq(familia, "csv"), "a", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            for b in FAMILIAS[familia]:
                r = registros[b]
                w.writerow([*cfg, semente, b, repr(r["prec"]), repr(r["brier"]),
                            repr(r["ece"]), r["n"], *(repr(float(x)) for x in r["fpr"])])


# --------------------------------------------------------------------------
# execucao
# --------------------------------------------------------------------------
def _inicializar_worker():
    for var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
        os.environ[var] = "1"


def _tarefa(args):
    f_base, beta, pi, semente, familias, n, k = args
    # Dentro do pool, a validacao cruzada nao abre outro pool (n_jobs=1).
    return rodar_semente(f_base, beta, pi, semente, familias, n, k, n_jobs=1)


def executar(combos, sementes, n, k, pasta_cache, forcar=(), aceitar_velho=(),
             workers=None, progresso=None):
    """Garante no cache todas as (configuracao, semente) de todas as familias
    e devolve {(cfg, semente): {braco: registro}} com os bracos de todas elas.

    forcar: familias recalculadas mesmo com cache valido.
    aceitar_velho: familias cujo cache e' usado mesmo com a chave desatualizada
    (o usuario declara que a mudanca nao as afeta; ha aviso)."""
    cache = Cache(pasta_cache, n, k)
    feitos = {}
    for fam in FAMILIAS:
        valida = cache.chave_valida(fam)
        if fam in forcar or not (valida or fam in aceitar_velho):
            cache.zerar(fam)
            feitos[fam] = {}
        else:
            if not valida:
                print(f"AVISO: usando o cache de '{fam}' com a chave desatualizada "
                      f"(--aceitar-cache). Os numeros dessa familia podem estar velhos.")
            feitos[fam] = cache.ler(fam)

    # Uma tarefa por (configuracao, semente), com as familias que faltam nela.
    tarefas = []
    for f_base, beta, pi in combos:
        cfg = _cfg(f_base, beta, pi)
        for s in sementes:
            faltam = tuple(f for f in FAMILIAS if (cfg, s) not in feitos[f])
            if faltam:
                tarefas.append((float(f_base), float(beta), float(pi), s, faltam, n, k))
    total = len(combos) * len(sementes)
    por_familia = {f: sum(f in t[4] for t in tarefas) for f in FAMILIAS}
    print(f"(configuracao, semente) a calcular: {len(tarefas)}/{total}  ["
          + ", ".join(f"{f} {c}" for f, c in por_familia.items()) + "]")

    def registrar(args, res):
        f_base, beta, pi, s, faltam = args[:5]
        cfg = _cfg(f_base, beta, pi)
        for fam in faltam:
            regs = {b: res[b] for b in FAMILIAS[fam]}
            cache.gravar(fam, cfg, s, regs)
            feitos[fam][(cfg, s)] = regs

    if tarefas:
        if workers == 1:
            resultados = map(_tarefa, tarefas)
            for i, (args, res) in enumerate(zip(tarefas, resultados), 1):
                registrar(args, res)
                if progresso:
                    progresso(i, len(tarefas))
        else:
            with ProcessPoolExecutor(max_workers=workers,
                                     initializer=_inicializar_worker) as ex:
                for i, (args, res) in enumerate(zip(tarefas, ex.map(_tarefa, tarefas)), 1):
                    registrar(args, res)
                    if progresso:
                        progresso(i, len(tarefas))

    tudo = {}
    for fam in FAMILIAS:
        for t, regs in feitos[fam].items():
            tudo.setdefault(t, {}).update(regs)
    return tudo
