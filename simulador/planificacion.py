"""Planificación de CPU: FCFS, SJF no expulsivo y Round Robin, con sus estadísticas.

Desempates: a igual llegada gana el PID menor. En SJF, a igual ráfaga gana el que llegó
primero. En Round Robin, los procesos que llegan durante un quantum entran a la cola antes
que el proceso que acaba de usar la CPU.
"""
from collections import deque
from dataclasses import dataclass

from simulador.procesos import Proceso


@dataclass(frozen=True)
class Tramo:
    pid: int | None  # None significa CPU ociosa
    inicio: int
    fin: int


@dataclass(frozen=True)
class Metricas:
    pid: int
    llegada: int
    rafaga: int
    finalizacion: int

    @property
    def retorno(self) -> int:
        return self.finalizacion - self.llegada

    @property
    def espera(self) -> int:
        return self.retorno - self.rafaga


@dataclass(frozen=True)
class Resultado:
    algoritmo: str
    tramos: list[Tramo]
    metricas: list[Metricas]

    @property
    def retorno_promedio(self) -> float:
        return sum(m.retorno for m in self.metricas) / len(self.metricas)

    @property
    def espera_promedio(self) -> float:
        return sum(m.espera for m in self.metricas) / len(self.metricas)


def fcfs(procesos: list[Proceso]) -> Resultado:
    """Primero en llegar, primero en ser atendido."""
    _validar(procesos)
    reloj, tramos, finalizacion = 0, [], {}
    for proceso in _por_llegada(procesos):
        reloj = _esperar_llegada(tramos, reloj, proceso.llegada)
        reloj = _ejecutar(tramos, proceso, reloj, proceso.rafaga)
        finalizacion[proceso.pid] = reloj
    return _resultado("FCFS", procesos, tramos, finalizacion)


def sjf(procesos: list[Proceso]) -> Resultado:
    """Trabajo más corto primero, sin expulsión: entre los que ya llegaron, la menor ráfaga."""
    _validar(procesos)
    pendientes = _por_llegada(procesos)
    reloj, tramos, finalizacion = 0, [], {}
    while pendientes:
        llegados = [p for p in pendientes if p.llegada <= reloj]
        if not llegados:
            reloj = _esperar_llegada(tramos, reloj, pendientes[0].llegada)
            continue
        proceso = min(llegados, key=lambda p: (p.rafaga, p.llegada, p.pid))
        pendientes.remove(proceso)
        reloj = _ejecutar(tramos, proceso, reloj, proceso.rafaga)
        finalizacion[proceso.pid] = reloj
    return _resultado("SJF no expulsivo", procesos, tramos, finalizacion)


def round_robin(procesos: list[Proceso], quantum: int) -> Resultado:
    """Turnos de a lo sumo `quantum` unidades; si el proceso no termina, vuelve al final de la cola."""
    _validar(procesos)
    if quantum <= 0:
        raise ValueError("El quantum debe ser positivo.")

    por_llegar = deque(_por_llegada(procesos))
    restante = {p.pid: p.rafaga for p in procesos}
    cola: deque[Proceso] = deque()
    reloj, tramos, finalizacion = 0, [], {}

    while cola or por_llegar:
        while por_llegar and por_llegar[0].llegada <= reloj:
            cola.append(por_llegar.popleft())
        if not cola:
            reloj = _esperar_llegada(tramos, reloj, por_llegar[0].llegada)
            continue

        proceso = cola.popleft()
        uso = min(quantum, restante[proceso.pid])
        reloj = _ejecutar(tramos, proceso, reloj, uso)
        restante[proceso.pid] -= uso

        while por_llegar and por_llegar[0].llegada <= reloj:
            cola.append(por_llegar.popleft())
        if restante[proceso.pid]:
            cola.append(proceso)
        else:
            finalizacion[proceso.pid] = reloj

    return _resultado(f"Round Robin (q={quantum})", procesos, tramos, finalizacion)


def _validar(procesos: list[Proceso]) -> None:
    if not procesos:
        raise ValueError("No hay procesos para planificar.")


def _por_llegada(procesos: list[Proceso]) -> list[Proceso]:
    return sorted(procesos, key=lambda p: (p.llegada, p.pid))


def _esperar_llegada(tramos: list[Tramo], reloj: int, llegada: int) -> int:
    """Si la CPU queda sin trabajo, registra el tiempo ocioso hasta la próxima llegada."""
    if llegada > reloj:
        tramos.append(Tramo(None, reloj, llegada))
        return llegada
    return reloj


def _ejecutar(tramos: list[Tramo], proceso: Proceso, reloj: int, duracion: int) -> int:
    """Registra el uso de CPU y une tramos seguidos del mismo proceso."""
    fin = reloj + duracion
    if tramos and tramos[-1].pid == proceso.pid and tramos[-1].fin == reloj:
        tramos[-1] = Tramo(proceso.pid, tramos[-1].inicio, fin)
    else:
        tramos.append(Tramo(proceso.pid, reloj, fin))
    return fin


def _resultado(nombre: str, procesos: list[Proceso], tramos: list[Tramo], finalizacion: dict[int, int]) -> Resultado:
    metricas = [
        Metricas(p.pid, p.llegada, p.rafaga, finalizacion[p.pid])
        for p in sorted(procesos, key=lambda p: p.pid)
    ]
    return Resultado(nombre, tramos, metricas)
