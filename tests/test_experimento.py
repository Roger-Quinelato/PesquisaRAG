"""Testes do experimento de simulacao.

Uso (da raiz do repositorio):  python -m unittest discover tests

So depende de numpy. Os testes rodam em poucos segundos: usam amostras
pequenas e nao reproduzem a varredura inteira (isso e' feito rodando
experimento/varredura.py duas vezes e comparando os CSVs).
"""
import os
import sys
import unittest

import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "experimento"))

from gerador import Params, gerar, COBERTURA           # noqa: E402
from bracos import BRACOS, calcular                     # noqa: E402
from metricas import brier, ece, topk, fpr_por_ra       # noqa: E402

N = 20_000


def _amostra(semente=0, **kw):
    """Gera N casos com a semente e os parametros dados."""
    params = Params(**kw)
    rng = np.random.default_rng(semente)
    return params, rng, gerar(N, params, rng)


class TestGerador(unittest.TestCase):
    """Propriedades do mecanismo causal que o experimento pressupoe."""

    def test_deterministico_por_semente(self):
        """Mesma semente, mesmos dados: base da reprodutibilidade."""
        _, _, a = _amostra(3)
        _, _, b = _amostra(3)
        for x, y in zip(a, b):
            np.testing.assert_array_equal(x, y)

    def test_sementes_diferentes_geram_dados_diferentes(self):
        """Sementes diferentes nao podem repetir a amostra."""
        _, _, a = _amostra(0)
        _, _, b = _amostra(1)
        self.assertFalse(np.array_equal(a[2], b[2]))

    def test_taxa_de_fraude_igual_entre_ras(self):
        """Controle do experimento: P(F) nao depende da RA."""
        params, _, (ra, F, _, _) = _amostra(0)
        for r in range(len(COBERTURA)):
            self.assertAlmostEqual(F[ra == r].mean(), params.pi, delta=0.03)

    def test_rotulo_latente_nao_e_funcao_das_evidencias(self):
        """Defeito do dataset legado: ground_truth == OR(evidencias) em 100%."""
        _, _, (_, F, E, _) = _amostra(0)
        divergencia = (E.max(axis=1) != F).mean()
        self.assertGreater(divergencia, 0.20)

    def test_so_endereco_depende_da_cobertura(self):
        """So o FP de endereco varia com a RA; status e valor ficam em f_base."""
        params = Params()
        f = params.fpr_por_ra(np.arange(len(COBERTURA)))
        np.testing.assert_allclose(f[:, 0], params.f_base)
        np.testing.assert_allclose(f[:, 2], params.f_base)
        self.assertTrue(np.all(np.diff(f[:, 1]) > 0))  # cobertura decrescente


class TestMetricas(unittest.TestCase):
    """Metricas em casos pequenos com resposta conhecida."""

    def test_brier(self):
        """Brier de um caso calculado a mao."""
        self.assertEqual(brier(np.array([1.0, 0.0]), np.array([1, 0])), 0.0)
        self.assertEqual(brier(np.array([0.0, 1.0]), np.array([1, 0])), 1.0)

    def test_ece_zero_quando_calibrado(self):
        """Se a probabilidade prevista iguala a frequencia observada, ECE = 0."""
        p = np.full(1000, 0.25)
        y = np.array([1] * 250 + [0] * 750)
        self.assertAlmostEqual(ece(p, y), 0.0)

    def test_ece_detecta_descalibracao(self):
        """Prevendo 0,9 onde a frequencia observada e' 0,1, ECE = 0,8."""
        p = np.full(1000, 0.9)
        y = np.array([1] * 100 + [0] * 900)
        self.assertAlmostEqual(ece(p, y), 0.8)

    def test_topk_tamanho_e_desempate_aleatorio(self):
        """topk seleciona k*n casos e desfaz empates pelo rng, nao pela ordem."""
        score = np.zeros(1000)  # empate total
        a = topk(score, 0.1, np.random.default_rng(0))
        b = topk(score, 0.1, np.random.default_rng(1))
        self.assertEqual(len(a), 100)
        self.assertFalse(np.array_equal(np.sort(a), np.sort(b)))

    def test_fpr_por_ra_ignora_fraudes(self):
        """Fraudes selecionadas nao contam como falso positivo da RA."""
        ra = np.array([0, 0, 1, 1])
        y = np.array([0, 1, 0, 0])
        sel = np.array([0, 1, 2])
        np.testing.assert_allclose(fpr_por_ra(sel, ra, y, 2), [1.0, 0.5])


class TestBracos(unittest.TestCase):
    """Os seis bracos e o achado central sobre o prior regional."""

    def test_scores_em_zero_um(self):
        """Todo braco devolve score em [0, 1]."""
        params, _, dados = _amostra(0)
        scores = calcular(*dados, params)
        self.assertEqual(set(scores), set(BRACOS))
        for nome, s in scores.items():
            self.assertTrue(np.all((s >= 0) & (s <= 1)), nome)

    def test_prior_regional_degrada_calibracao(self):
        """Achado (i): C (RA no prior) e' pior que A em Brier e ECE."""
        params, _, dados = _amostra(0)
        F = dados[1]
        s = calcular(*dados, params)
        self.assertGreater(brier(s["C"], F), brier(s["A"], F))
        self.assertGreater(ece(s["C"], F), ece(s["A"], F))


if __name__ == "__main__":
    unittest.main()
