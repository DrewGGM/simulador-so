"""Archivos: crear, listar, leer, modificar y eliminar dentro de una carpeta de pruebas."""
from pathlib import Path


class GestorArchivos:
    def __init__(self, carpeta: Path) -> None:
        self.carpeta = Path(carpeta)
        self.carpeta.mkdir(parents=True, exist_ok=True)

    def crear(self, nombre: str, contenido: str = "") -> None:
        ruta = self._ruta(nombre)
        if ruta.exists():
            raise FileExistsError(f"Ya existe el archivo {nombre}.")
        ruta.write_text(contenido, encoding="utf-8")

    def listar(self) -> list[str]:
        return sorted(ruta.name for ruta in self.carpeta.iterdir() if ruta.is_file())

    def leer(self, nombre: str) -> str:
        return self._existente(nombre).read_text(encoding="utf-8")

    def modificar(self, nombre: str, contenido: str) -> None:
        self._existente(nombre).write_text(contenido, encoding="utf-8")

    def eliminar(self, nombre: str) -> None:
        self._existente(nombre).unlink()

    def _ruta(self, nombre: str) -> Path:
        """Solo acepta nombres simples, para no salir de la carpeta de pruebas."""
        nombre = nombre.strip()
        if not nombre or nombre in {".", ".."} or Path(nombre).name != nombre:
            raise ValueError(f"Nombre de archivo no válido: {nombre!r}.")
        return self.carpeta / nombre

    def _existente(self, nombre: str) -> Path:
        ruta = self._ruta(nombre)
        if not ruta.is_file():
            raise FileNotFoundError(f"No existe el archivo {nombre}.")
        return ruta
