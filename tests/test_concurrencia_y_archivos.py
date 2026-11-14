"""Pruebas de concurrencia, cola de mensajes y archivos."""
import tempfile
import unittest
from pathlib import Path

from simulador.archivos import GestorArchivos
from simulador.concurrencia import incrementar_contador, intercambiar_mensajes


class TestConcurrencia(unittest.TestCase):
    def test_con_lock_no_se_pierde_ninguna_suma(self):
        resultado = incrementar_contador(usar_lock=True)
        self.assertEqual(resultado.obtenido, resultado.esperado)

    def test_sin_lock_nunca_supera_lo_esperado(self):
        resultado = incrementar_contador(usar_lock=False)
        self.assertLessEqual(resultado.obtenido, resultado.esperado)

    def test_la_cola_entrega_todo_en_orden(self):
        mensajes = [f"mensaje {i}" for i in range(20)]
        self.assertEqual(intercambiar_mensajes(mensajes, capacidad=2), mensajes)


class TestArchivos(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.gestor = GestorArchivos(Path(self.temporal.name) / "pruebas")

    def tearDown(self):
        self.temporal.cleanup()

    def test_ciclo_completo(self):
        self.gestor.crear("notas.txt", "hola")
        self.assertEqual(self.gestor.listar(), ["notas.txt"])
        self.gestor.modificar("notas.txt", "chao")
        self.assertEqual(self.gestor.leer("notas.txt"), "chao")
        self.gestor.eliminar("notas.txt")
        self.assertEqual(self.gestor.listar(), [])

    def test_no_duplica_ni_lee_inexistentes(self):
        self.gestor.crear("a.txt")
        with self.assertRaises(FileExistsError):
            self.gestor.crear("a.txt")
        with self.assertRaises(FileNotFoundError):
            self.gestor.leer("b.txt")

    def test_no_sale_de_la_carpeta(self):
        for nombre in ["../fuera.txt", "sub/archivo.txt", "..", ""]:
            with self.assertRaises(ValueError):
                self.gestor.crear(nombre)


if __name__ == "__main__":
    unittest.main()
