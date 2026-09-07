"""Exporta um dataset de casos com o rotulo LATENTE separado das evidencias.

Diferenca essencial para dataset_sintetico_500_casos.csv: ali
ground_truth == OR(evidencias) em 500/500 linhas, o que torna o rotulo
uma funcao deterministica das colunas visiveis e satura qualquer baseline.
Aqui fraude_latente e' a causa, as evidencias sao sinais ruidosos dela, e
as duas coisas discordam numa fracao substancial dos casos.

Uso: python experimento/exportar_dataset.py [n]
"""
import csv, os, sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gerador import Params, gerar, RAS, COBERTURA, EVIDENCIAS  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAIDA = os.path.join(RAIZ, "dataset_sintetico_v2.csv")


def main(n=5000, semente=20260907):
    params = Params()
    ra, F, E, f_true = gerar(n, params, np.random.default_rng(semente))
    with open(SAIDA, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.writer(fh, delimiter=";")
        w.writerow(["case_id", "regiao_administrativa", "cobertura_cadastral"]
                   + [f"evidencia_{e}" for e in EVIDENCIAS]
                   + ["n_evidencias", "fraude_latente"])
        for i in range(n):
            w.writerow([f"CASE-{i+1:05d}", RAS[ra[i]], f"{COBERTURA[ra[i]]:.2f}"]
                       + [int(x) for x in E[i]] + [int(E[i].sum()), int(F[i])])
    obs = E.max(axis=1)
    disc = int((obs != F).sum())
    print(f"-> {SAIDA}  ({n} casos)")
    print(f"   fraude latente: {F.sum()} ({F.mean():.1%})")
    print(f"   alguma evidencia: {obs.sum()} ({obs.mean():.1%})")
    print(f"   OR(evidencias) != fraude_latente em {disc} linhas ({disc/n:.1%})")
    print(f"   -> falso positivo {int(((obs==1)&(F==0)).sum())}, "
          f"falso negativo {int(((obs==0)&(F==1)).sum())}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 5000)
