"""Pruebas de memoria y de la tabla de procesos."""
import unittest

from simulador.memoria import Bloque, Memoria, MemoriaInsuficiente
from simulador.procesos import Estado, ProcesoNoEncontrado, TablaProcesos


class TestMemoria(unittest.TestCase):
    def setUp(self):
        # Deja dos huecos: 100 KB en 100-200 y 600 KB en 400-1000
        self.memoria = Memoria(1000)
        for pid, tamano in [(1, 100), (2, 100), (3, 200), (4, 300)]:
            self.memoria.asignar(pid, tamano)
        self.memoria.liberar(2)
        self.memoria.liberar(4)

    def test_mejor_ajuste_elige_el_hueco_mas_pequeno(self):
        bloque = self.memoria.asignar(5, 80)
        self.assertEqual(bloque, Bloque(100, 80, 5))

    def test_liberar_fusiona_huecos_vecinos(self):
        self.memoria.liberar(3)
        self.assertEqual(self.memoria.bloques, [Bloque(0, 100, 1), Bloque(100, 900)])

    def test_sin_espacio_suficiente(self):
        self.memoria.asignar(5, 600)  # quedan 100 KB libres en total
        with self.assertRaisesRegex(MemoriaInsuficiente, "solo quedan"):
            self.memoria.asignar(6, 200)

    def test_fragmentacion_externa(self):
        self.memoria.asignar(5, 550)  # quedan 150 KB libres, repartidos en 100 + 50
        with self.assertRaisesRegex(MemoriaInsuficiente, "fragmentación externa"):
            self.memoria.asignar(6, 120)


class TestTablaProcesos(unittest.TestCase):
    def setUp(self):
        self.memoria = Memoria(500)
        self.tabla = TablaProcesos(self.memoria)

    def test_crear_asigna_memoria_y_queda_listo(self):
        proceso = self.tabla.crear("Reportes", 0, 5, 1, 200)
        self.assertEqual(proceso.estado, Estado.LISTO)
        self.assertEqual(self.memoria.usada, 200)

    def test_finalizar_libera_memoria(self):
        proceso = self.tabla.crear("Reportes", 0, 5, 1, 200)
        self.tabla.finalizar(proceso.pid)
        self.assertEqual(proceso.estado, Estado.TERMINADO)
        self.assertEqual(self.memoria.usada, 0)
        self.assertEqual(self.tabla.activos(), [])

    def test_sin_memoria_no_se_registra(self):
        with self.assertRaises(MemoriaInsuficiente):
            self.tabla.crear("Grande", 0, 5, 1, 600)
        self.assertEqual(self.tabla.listar(), [])

    def test_consultar_inexistente(self):
        with self.assertRaises(ProcesoNoEncontrado):
            self.tabla.consultar(99)

    def test_datos_invalidos(self):
        with self.assertRaises(ValueError):
            self.tabla.crear("", 0, 5, 1, 100)
        with self.assertRaises(ValueError):
            self.tabla.crear("Sin CPU", 0, 0, 1, 100)


if __name__ == "__main__":
    unittest.main()
