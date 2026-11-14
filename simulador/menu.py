"""Menú de consola que integra todos los módulos del simulador."""
from collections.abc import Callable
from pathlib import Path

from simulador import concurrencia, planificacion
from simulador.archivos import GestorArchivos
from simulador.memoria import Memoria, MemoriaInsuficiente
from simulador.planificacion import Resultado, Tramo
from simulador.procesos import Proceso, TablaProcesos

CAPACIDAD_MEMORIA_KB = 1024
CARPETA_PRUEBAS = Path("carpeta_pruebas")

# nombre, llegada, ráfaga, prioridad, memoria en KB
CASO_DE_PRUEBA = [
    ("Procesamiento", 0, 8, 2, 200),
    ("Almacenamiento", 1, 4, 1, 120),
    ("Comunicación", 2, 9, 3, 300),
    ("Reportes", 3, 5, 2, 150),
    ("Respaldo", 4, 2, 1, 80),
]
MENSAJES_DE_EJEMPLO = ["Leer ventas", "Calcular totales", "Generar reporte", "Enviar correo"]

ERRORES_ESPERADOS = (ValueError, LookupError, MemoriaInsuficiente, OSError)
Opciones = dict[str, tuple[str, Callable[[], None]]]


class Simulador:
    def __init__(self) -> None:
        self.memoria = Memoria(CAPACIDAD_MEMORIA_KB)
        self.procesos = TablaProcesos(self.memoria)
        self.archivos = GestorArchivos(CARPETA_PRUEBAS)

    def ejecutar(self) -> None:
        _menu("Simulador de sistema operativo", {
            "1": ("Procesos", self._menu_procesos),
            "2": ("Planificación de CPU", self._menu_planificacion),
            "3": ("Concurrencia y sincronización", self._demostrar_concurrencia),
            "4": ("Cola de mensajes", self._demostrar_cola),
            "5": ("Mapa de memoria", self._mostrar_memoria),
            "6": ("Archivos", self._menu_archivos),
        }, salir="Salir")

    # Procesos

    def _menu_procesos(self) -> None:
        _menu("Procesos", {
            "1": ("Crear proceso", self._crear_proceso),
            "2": ("Listar procesos", lambda: print(_tabla_procesos(self.procesos.listar()))),
            "3": ("Consultar proceso", self._consultar_proceso),
            "4": ("Finalizar proceso", self._finalizar_proceso),
            "5": ("Cargar caso de prueba", self._cargar_caso_de_prueba),
        })

    def _crear_proceso(self) -> None:
        proceso = self.procesos.crear(
            nombre=input("Nombre: "),
            llegada=_leer_entero("Llegada: ", minimo=0),
            rafaga=_leer_entero("CPU requerida (ráfaga): ", minimo=1),
            prioridad=_leer_entero("Prioridad (1 es la más alta): ", minimo=1),
            memoria=_leer_entero("Memoria en KB: ", minimo=1),
        )
        print(f"Proceso {proceso.pid} creado en estado {proceso.estado.value}.")

    def _consultar_proceso(self) -> None:
        print(_tabla_procesos([self.procesos.consultar(_leer_entero("PID: "))]))

    def _finalizar_proceso(self) -> None:
        proceso = self.procesos.finalizar(_leer_entero("PID: "))
        print(f"Proceso {proceso.pid} terminado. Liberó {proceso.memoria} KB.")

    def _cargar_caso_de_prueba(self) -> None:
        for datos in CASO_DE_PRUEBA:
            self.procesos.crear(*datos)
        print(_tabla_procesos(self.procesos.listar()))

    # Planificación

    def _menu_planificacion(self) -> None:
        _menu("Planificación de CPU", {
            "1": ("FCFS", lambda: _mostrar_resultado(planificacion.fcfs(self._activos()))),
            "2": ("SJF no expulsivo", lambda: _mostrar_resultado(planificacion.sjf(self._activos()))),
            "3": ("Round Robin", lambda: _mostrar_resultado(
                planificacion.round_robin(self._activos(), _leer_entero("Quantum: ", minimo=1)))),
            "4": ("Comparar los tres", self._comparar_algoritmos),
        })

    def _activos(self) -> list[Proceso]:
        activos = self.procesos.activos()
        if not activos:
            raise ValueError("No hay procesos activos. Cree procesos o cargue el caso de prueba.")
        return activos

    def _comparar_algoritmos(self) -> None:
        activos = self._activos()
        quantum = _leer_entero("Quantum para Round Robin: ", minimo=1)
        resultados = [
            planificacion.fcfs(activos),
            planificacion.sjf(activos),
            planificacion.round_robin(activos, quantum),
        ]
        for resultado in resultados:
            print(f"\n{resultado.algoritmo}\n{_gantt(resultado.tramos)}")
        print(f"\n{'Algoritmo':<24}{'Retorno prom.':>15}{'Espera prom.':>15}")
        for resultado in resultados:
            print(f"{resultado.algoritmo:<24}{resultado.retorno_promedio:>15.2f}{resultado.espera_promedio:>15.2f}")
        mejor = min(resultados, key=lambda r: r.espera_promedio)
        print(f"\nMenor espera promedio: {mejor.algoritmo}.")

    # Concurrencia y comunicación

    def _demostrar_concurrencia(self) -> None:
        for usar_lock in (False, True):
            resultado = concurrencia.incrementar_contador(usar_lock)
            titulo = "Con Lock" if usar_lock else "Sin Lock"
            print(f"{titulo}: esperado {resultado.esperado}, obtenido {resultado.obtenido}, "
                  f"perdidos {resultado.perdidos}.")
        print("Sin Lock, dos hilos leen el mismo valor antes de que el otro escriba y una suma se pierde.\n"
              "Con Lock, solo un hilo a la vez entra a la sección crítica y el total es exacto.")

    def _demostrar_cola(self) -> None:
        texto = input("Mensajes separados por coma (Enter para usar los de ejemplo): ")
        mensajes = [m.strip() for m in texto.split(",") if m.strip()] or MENSAJES_DE_EJEMPLO
        recibidos = concurrencia.intercambiar_mensajes(mensajes)
        print(f"Productor envió:   {mensajes}")
        print(f"Consumidor recibió: {recibidos}")

    # Memoria

    def _mostrar_memoria(self) -> None:
        print(f"Capacidad {self.memoria.capacidad} KB, usada {self.memoria.usada} KB, "
              f"libre {self.memoria.libre} KB")
        print(f"{'Inicio':>7}{'Fin':>7}{'Tamaño':>9}  Dueño")
        for bloque in self.memoria.bloques:
            dueno = "libre" if bloque.libre else f"P{bloque.pid}"
            print(f"{bloque.inicio:>7}{bloque.fin:>7}{bloque.tamano:>6} KB  {dueno}")

    # Archivos

    def _menu_archivos(self) -> None:
        _menu(f"Archivos en {self.archivos.carpeta}", {
            "1": ("Crear archivo", self._crear_archivo),
            "2": ("Listar archivos", lambda: print("\n".join(self.archivos.listar()) or "(carpeta vacía)")),
            "3": ("Leer archivo", lambda: print(self.archivos.leer(input("Nombre: ")))),
            "4": ("Modificar archivo", self._modificar_archivo),
            "5": ("Eliminar archivo", self._eliminar_archivo),
        })

    def _crear_archivo(self) -> None:
        nombre = input("Nombre: ")
        self.archivos.crear(nombre, input("Contenido: "))
        print(f"Archivo {nombre} creado.")

    def _modificar_archivo(self) -> None:
        nombre = input("Nombre: ")
        self.archivos.modificar(nombre, input("Nuevo contenido: "))
        print(f"Archivo {nombre} modificado.")

    def _eliminar_archivo(self) -> None:
        nombre = input("Nombre: ")
        self.archivos.eliminar(nombre)
        print(f"Archivo {nombre} eliminado.")


def _menu(titulo: str, opciones: Opciones, salir: str = "Volver") -> None:
    while True:
        print(f"\n=== {titulo} ===")
        for clave, (texto, _) in opciones.items():
            print(f"{clave}. {texto}")
        print(f"0. {salir}")

        eleccion = input("> ").strip()
        if eleccion == "0":
            return
        if eleccion not in opciones:
            print("Opción no válida.")
            continue
        try:
            opciones[eleccion][1]()
        except ERRORES_ESPERADOS as error:
            print(f"Error: {error}")


def _leer_entero(mensaje: str, minimo: int = 1) -> int:
    while True:
        texto = input(mensaje).strip()
        if texto.isdigit() and int(texto) >= minimo:
            return int(texto)
        print(f"Escriba un número entero mayor o igual a {minimo}.")


def _tabla_procesos(procesos: list[Proceso]) -> str:
    if not procesos:
        return "No hay procesos registrados."
    filas = [f"{'PID':>4}  {'Nombre':<16}{'Llegada':>8}{'Ráfaga':>8}{'Prioridad':>10}{'Memoria':>9}  Estado"]
    filas += [
        f"{p.pid:>4}  {p.nombre:<16}{p.llegada:>8}{p.rafaga:>8}{p.prioridad:>10}{p.memoria:>6} KB  {p.estado.value}"
        for p in procesos
    ]
    return "\n".join(filas)


def _mostrar_resultado(resultado: Resultado) -> None:
    print(f"\n{resultado.algoritmo}\n{_gantt(resultado.tramos)}\n")
    print(f"{'PID':>4}{'Llegada':>9}{'Ráfaga':>8}{'Fin':>6}{'Retorno':>9}{'Espera':>8}")
    for m in resultado.metricas:
        print(f"{m.pid:>4}{m.llegada:>9}{m.rafaga:>8}{m.finalizacion:>6}{m.retorno:>9}{m.espera:>8}")
    print(f"Promedios: retorno {resultado.retorno_promedio:.2f}, espera {resultado.espera_promedio:.2f}")


def _gantt(tramos: list[Tramo]) -> str:
    """Diagrama de Gantt en texto: cada unidad de tiempo ocupa dos columnas."""
    barra, tiempos = "|", str(tramos[0].inicio)
    for tramo in tramos:
        etiqueta = f"P{tramo.pid}" if tramo.pid is not None else "--"
        barra += etiqueta.center(max(4, 2 * (tramo.fin - tramo.inicio))) + "|"
        tiempos = tiempos.ljust(len(barra) - 1) + str(tramo.fin)
    return f"{barra}\n{tiempos}"
