"""Testes do experimento de simulacao.

Uso (da raiz do repositorio):  python -m unittest discover tests

Depende de numpy e scikit-learn (versoes em requirements.txt). Os testes
usam amostras pequenas e nao reproduzem a varredura inteira (isso e' feito
rodando experimento/varredura.py duas vezes e comparando os CSVs).
"""
import os
import sys
import unittest

import numpy as np

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "experimento"))

from gerador import Params, gerar, COBERTURA           # noqa: E402
from bracos import BRACOS, calcular                     # noqa: E402
from bracos_ml import BRACOS_ML, FRAC_TREINO, calcular_ml  # noqa: E402
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


class TestBracosFechadosEmSklearn(unittest.TestCase):
    """A, B e C sao BernoulliNB com parametros injetados. Devem coincidir com
    a formula de Fellegi-Sunter escrita direto em numpy."""

    @staticmethod
    def _sigmoid(x):
        return 1.0 / (1.0 + np.exp(-x))

    @staticmethod
    def _llr(E, sens, fpr):
        return np.where(E == 1, np.log(sens / fpr),
                        np.log((1 - sens) / (1 - fpr))).sum(axis=1)

    def test_a_e_b_batem_com_a_formula_direta(self):
        params, _, dados = _amostra(0)
        ra, F, E, f_true = dados
        s = calcular(ra, F, E, f_true, params)
        sens = params.sens_arr
        logit = np.log(params.pi / (1 - params.pi))
        np.testing.assert_allclose(
            s["A"], self._sigmoid(logit + self._llr(E, sens, params.fpr_global())), atol=1e-12)
        np.testing.assert_allclose(
            s["B"], self._sigmoid(logit + self._llr(E, sens, f_true)), atol=1e-12)

    def test_bracos_nao_usam_o_rotulo(self):
        """Embaralhar F nao muda A, B nem C (so o LOOKUP usa o rotulo)."""
        params, _, dados = _amostra(0)
        ra, F, E, f_true = dados
        a = calcular(ra, F, E, f_true, params)
        b = calcular(ra, np.random.default_rng(9).permutation(F), E, f_true, params)
        for nome in ("A", "B", "C"):
            np.testing.assert_array_equal(a[nome], b[nome])
        self.assertFalse(np.array_equal(a["LOOKUP"], b["LOOKUP"]))


class TestBracosTreinados(unittest.TestCase):
    """Os doze bracos de bracos_ml.py (AdaBoost, Naive Bayes, calibrados)."""

    @classmethod
    def setUpClass(cls):
        cls.params, cls.rng0, dados = _amostra(0)
        cls.ra, cls.F, cls.E, _ = dados
        rng = np.random.default_rng(123)
        cls.scores, cls.idx = calcular_ml(cls.ra, cls.F, cls.E, cls.params, rng)
        cls.rng_depois = rng

    def test_nomes_tamanho_e_faixa(self):
        self.assertEqual(tuple(self.scores), BRACOS_ML)
        for nome, s in self.scores.items():
            self.assertEqual(s.shape, (len(self.idx),), nome)
            self.assertFalse(np.isnan(s).any(), nome)
            self.assertTrue(np.all((s >= 0) & (s <= 1)), nome)

    def test_split_aproximadamente_50_50_e_sem_vazamento(self):
        frac_teste = len(self.idx) / len(self.F)
        self.assertAlmostEqual(frac_teste, 1 - FRAC_TREINO, delta=0.02)
        self.assertEqual(len(np.unique(self.idx)), len(self.idx))

    def test_consumo_do_rng_e_fixo(self):
        """1 sorteio de N (split) + 3 inteiros (sementes). Mudar isso muda
        todos os numeros publicados dos bracos treinados."""
        ref = np.random.default_rng(123)
        ref.random(len(self.F))
        for _ in range(3):
            ref.integers(0, 2**32 - 1)
        self.assertEqual(self.rng_depois.random(), ref.random())

    def test_deterministico_por_semente(self):
        again, idx = calcular_ml(self.ra, self.F, self.E, self.params,
                                 np.random.default_rng(123))
        np.testing.assert_array_equal(idx, self.idx)
        for nome in BRACOS_ML:
            np.testing.assert_array_equal(again[nome], self.scores[nome], nome)

    def test_naive_bayes_treinado_e_calibrado_e_adaboost_cru_nao(self):
        y = self.F[self.idx]
        self.assertLess(ece(self.scores["A_NB"], y), 0.02)
        self.assertGreater(ece(self.scores["D_ML"], y), 0.05)

    def test_calibracao_posterior_corrige_o_adaboost(self):
        y = self.F[self.idx]
        for cru, cal in (("D_ML", "D_PL"), ("D_ML", "D_ISO"),
                         ("E_ML", "E_PL"), ("F_ML", "F_ISO")):
            self.assertLess(ece(self.scores[cal], y), ece(self.scores[cru], y), cal)
            self.assertLess(brier(self.scores[cal], y), brier(self.scores[cru], y), cal)

    def test_platt_preserva_a_ordenacao_do_adaboost(self):
        """O Platt e' monotono no decision_function; predict_proba do AdaBoost
        e' monotono nele tambem. A ordem so pode divergir em empates."""
        cru, pl = self.scores["D_ML"], self.scores["D_PL"]
        ordem = np.argsort(cru, kind="stable")
        self.assertTrue(np.all(np.diff(pl[ordem]) >= -1e-12))

    def test_territorio_nao_vaza_no_modelo_sem_ra(self):
        """D_ML e A_NB nao recebem a RA: dois casos com as mesmas evidencias
        recebem o mesmo score, em qualquer RA."""
        for nome in ("D_ML", "A_NB", "D_PL", "D_ISO"):
            s, E, ra = self.scores[nome], self.E[self.idx], self.ra[self.idx]
            codigo = E.astype(int) @ np.array([1, 2, 4])
            for c in range(8):
                m = codigo == c
                if m.any():
                    self.assertEqual(len(np.unique(s[m])), 1, (nome, c))


if __name__ == "__main__":
    unittest.main()
