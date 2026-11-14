"""Procesos: bloque de control (PCB) y tabla de procesos del simulador."""
from dataclasses import dataclass
from enum import Enum

from simulador.memoria import Memoria


class Estado(Enum):
    NUEVO = "Nuevo"
    LISTO = "Listo"
    TERMINADO = "Terminado"


class ProcesoNoEncontrado(LookupError):
    def __init__(self, pid: int) -> None:
        super().__init__(f"No existe un proceso con PID {pid}.")


@dataclass
class Proceso:
    pid: int
    nombre: str
    llegada: int
    rafaga: int  # tiempo de CPU requerido
    prioridad: int  # 1 es la más alta
    memoria: int  # en KB
    estado: Estado = Estado.NUEVO

    def __post_init__(self) -> None:
        if not self.nombre.strip():
            raise ValueError("El proceso necesita un nombre.")
        if self.llegada < 0:
            raise ValueError("La llegada no puede ser negativa.")
        if self.rafaga <= 0 or self.prioridad <= 0 or self.memoria <= 0:
            raise ValueError("La ráfaga, la prioridad y la memoria deben ser positivas.")


class TablaProcesos:
    """Registra los procesos y les asigna o libera memoria al crearlos o finalizarlos."""

    def __init__(self, memoria: Memoria) -> None:
        self._memoria = memoria
        self._procesos: dict[int, Proceso] = {}
        self._siguiente_pid = 1

    def crear(self, nombre: str, llegada: int, rafaga: int, prioridad: int, memoria: int) -> Proceso:
        proceso = Proceso(self._siguiente_pid, nombre.strip(), llegada, rafaga, prioridad, memoria)
        self._memoria.asignar(proceso.pid, proceso.memoria)
        proceso.estado = Estado.LISTO
        self._procesos[proceso.pid] = proceso
        self._siguiente_pid += 1
        return proceso

    def consultar(self, pid: int) -> Proceso:
        try:
            return self._procesos[pid]
        except KeyError:
            raise ProcesoNoEncontrado(pid) from None

    def listar(self) -> list[Proceso]:
        return list(self._procesos.values())

    def activos(self) -> list[Proceso]:
        return [p for p in self._procesos.values() if p.estado is not Estado.TERMINADO]

    def finalizar(self, pid: int) -> Proceso:
        proceso = self.consultar(pid)
        if proceso.estado is Estado.TERMINADO:
            raise ValueError(f"El proceso {pid} ya había terminado.")
        self._memoria.liberar(pid)
        proceso.estado = Estado.TERMINADO
        return proceso
