"""Memoria: asignación contigua con mejor ajuste y liberación con fusión de huecos."""
from dataclasses import dataclass


class MemoriaInsuficiente(Exception):
    """No hay un hueco libre donde quepa la solicitud."""


@dataclass(frozen=True)
class Bloque:
    inicio: int
    tamano: int
    pid: int | None = None  # None significa que el bloque está libre

    @property
    def fin(self) -> int:
        return self.inicio + self.tamano

    @property
    def libre(self) -> bool:
        return self.pid is None


class Memoria:
    def __init__(self, capacidad: int) -> None:
        if capacidad <= 0:
            raise ValueError("La capacidad de la memoria debe ser positiva.")
        self.capacidad = capacidad
        self._bloques = [Bloque(0, capacidad)]

    @property
    def bloques(self) -> list[Bloque]:
        return list(self._bloques)

    @property
    def libre(self) -> int:
        return sum(bloque.tamano for bloque in self._bloques if bloque.libre)

    @property
    def usada(self) -> int:
        return self.capacidad - self.libre

    def asignar(self, pid: int, tamano: int) -> Bloque:
        """Ubica el proceso en el hueco libre más pequeño donde quepa (mejor ajuste)."""
        if tamano <= 0:
            raise ValueError("El tamaño solicitado debe ser positivo.")
        if any(bloque.pid == pid for bloque in self._bloques):
            raise ValueError(f"El proceso {pid} ya tiene memoria asignada.")

        huecos = [(i, b) for i, b in enumerate(self._bloques) if b.libre and b.tamano >= tamano]
        if not huecos:
            if self.libre >= tamano:
                raise MemoriaInsuficiente(
                    f"Hay {self.libre} KB libres pero ningún hueco contiguo de {tamano} KB "
                    "(fragmentación externa)."
                )
            raise MemoriaInsuficiente(f"Se piden {tamano} KB y solo quedan {self.libre} KB libres.")

        indice, hueco = min(huecos, key=lambda par: par[1].tamano)
        asignado = Bloque(hueco.inicio, tamano, pid)
        sobrante = [Bloque(asignado.fin, hueco.tamano - tamano)] if hueco.tamano > tamano else []
        self._bloques[indice:indice + 1] = [asignado, *sobrante]
        return asignado

    def liberar(self, pid: int) -> None:
        indice = next((i for i, b in enumerate(self._bloques) if b.pid == pid), None)
        if indice is None:
            raise ValueError(f"El proceso {pid} no tiene memoria asignada.")
        bloque = self._bloques[indice]
        self._bloques[indice] = Bloque(bloque.inicio, bloque.tamano)
        self._fusionar_huecos()

    def _fusionar_huecos(self) -> None:
        """Une los huecos libres vecinos para que vuelvan a formar uno solo."""
        fusionados: list[Bloque] = []
        for bloque in self._bloques:
            if fusionados and bloque.libre and fusionados[-1].libre:
                anterior = fusionados.pop()
                bloque = Bloque(anterior.inicio, anterior.tamano + bloque.tamano)
            fusionados.append(bloque)
        self._bloques = fusionados
