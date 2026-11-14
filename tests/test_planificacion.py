"""Pruebas de planificación con un caso resuelto a mano."""
import unittest

from simulador.planificacion import Tramo, fcfs, round_robin, sjf
from simulador.procesos import Proceso


def proceso(pid: int, llegada: int, rafaga: int) -> Proceso:
    return Proceso(pid, f"P{pid}", llegada, rafaga, prioridad=1, memoria=10)


# P1 a P5: llegadas 0, 1, 2, 3, 4 y ráfagas 8, 4, 9, 5, 2
CASO = [proceso(1, 0, 8), proceso(2, 1, 4), proceso(3, 2, 9), proceso(4, 3, 5), proceso(5, 4, 2)]


def finalizaciones(resultado) -> list[int]:
    return [m.finalizacion for m in resultado.metricas]


class TestFCFS(unittest.TestCase):
    def test_caso_resuelto(self):
        resultado = fcfs(CASO)
        self.assertEqual(finalizaciones(resultado), [8, 12, 21, 26, 28])
        self.assertAlmostEqual(resultado.retorno_promedio, 17.0)
        self.assertAlmostEqual(resultado.espera_promedio, 11.4)

    def test_cpu_ociosa_hasta_la_primera_llegada(self):
        resultado = fcfs([proceso(1, 3, 2)])
        self.assertEqual(resultado.tramos, [Tramo(None, 0, 3), Tramo(1, 3, 5)])


class TestSJF(unittest.TestCase):
    def test_caso_resuelto(self):
        resultado = sjf(CASO)
        self.assertEqual([t.pid for t in resultado.tramos], [1, 5, 2, 4, 3])
        self.assertEqual(finalizaciones(resultado), [8, 14, 28, 19, 10])
        self.assertAlmostEqual(resultado.retorno_promedio, 13.8)
        self.assertAlmostEqual(resultado.espera_promedio, 8.2)


class TestRoundRobin(unittest.TestCase):
    def test_caso_resuelto_con_quantum_3(self):
        resultado = round_robin(CASO, quantum=3)
        self.assertEqual([t.pid for t in resultado.tramos], [1, 2, 3, 4, 1, 5, 2, 3, 4, 1, 3])
        self.assertEqual(finalizaciones(resultado), [25, 18, 28, 23, 17])
        self.assertAlmostEqual(resultado.retorno_promedio, 20.2)
        self.assertAlmostEqual(resultado.espera_promedio, 14.6)

    def test_quantum_invalido(self):
        with self.assertRaises(ValueError):
            round_robin(CASO, quantum=0)


class TestValidaciones(unittest.TestCase):
    def test_sin_procesos(self):
        for algoritmo in (fcfs, sjf):
            with self.assertRaises(ValueError):
                algoritmo([])


if __name__ == "__main__":
    unittest.main()
