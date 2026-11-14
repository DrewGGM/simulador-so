"""Concurrencia: condición de carrera, sección crítica con Lock y cola de mensajes."""
import queue
import threading
import time
from collections.abc import Callable
from contextlib import nullcontext
from dataclasses import dataclass

_FIN = object()  # le avisa al consumidor que no vienen más mensajes


@dataclass(frozen=True)
class ResultadoContador:
    esperado: int
    obtenido: int

    @property
    def perdidos(self) -> int:
        return self.esperado - self.obtenido


def incrementar_contador(usar_lock: bool, hilos: int = 2, incrementos: int = 2000) -> ResultadoContador:
    """Varios hilos suman sobre el mismo contador, con o sin Lock en la sección crítica."""
    valor = 0
    candado = threading.Lock() if usar_lock else nullcontext()

    def trabajar() -> None:
        nonlocal valor
        for _ in range(incrementos):
            with candado:
                leido = valor
                time.sleep(0)  # cede la CPU entre leer y escribir: ahí otro hilo puede colarse
                valor = leido + 1

    _ejecutar_en_paralelo([trabajar] * hilos)
    return ResultadoContador(esperado=hilos * incrementos, obtenido=valor)


def intercambiar_mensajes(mensajes: list[str], capacidad: int = 2) -> list[str]:
    """Un productor envía mensajes por una cola acotada y un consumidor los recibe en orden."""
    cola: queue.Queue = queue.Queue(maxsize=capacidad)
    recibidos: list[str] = []

    def productor() -> None:
        for mensaje in mensajes:
            cola.put(mensaje)  # se bloquea mientras la cola esté llena
        cola.put(_FIN)

    def consumidor() -> None:
        while (mensaje := cola.get()) is not _FIN:  # se bloquea mientras la cola esté vacía
            recibidos.append(mensaje)

    _ejecutar_en_paralelo([productor, consumidor])
    return recibidos


def _ejecutar_en_paralelo(tareas: list[Callable[[], None]]) -> None:
    hilos = [threading.Thread(target=tarea) for tarea in tareas]
    for hilo in hilos:
        hilo.start()
    for hilo in hilos:
        hilo.join()
