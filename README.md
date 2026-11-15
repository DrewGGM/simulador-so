# Simulador de sistema operativo

Simulador de consola en Python que representa funciones básicas de un sistema operativo. Administra procesos, planifica la CPU con FCFS, SJF no expulsivo y Round Robin, demuestra concurrencia con hilos, comunica hilos con una cola de mensajes, asigna memoria y opera archivos dentro de una carpeta de pruebas.

Solo usa la biblioteca estándar de Python, así que no hay nada que instalar.

## Requisitos

Python 3.10 o superior.

## Uso

```bash
python main.py
```

Para ver todo funcionando rápido, entre a **Procesos** y elija **Cargar caso de prueba**. Eso crea cinco procesos con los que se pueden probar la planificación y el mapa de memoria.

## Pruebas

```bash
python -m unittest
```

## Prácticas en Linux

Cada práctica muestra sus comandos con el prompt y su salida real. Se corren desde la raíz del repositorio en una terminal de Linux o WSL:

```bash
bash linux/1_procesos.sh     # estados, árbol de procesos, señales y un zombie
bash linux/2_prioridades.sh  # nice, renice y dos procesos que compiten por un núcleo
bash linux/3_hilos.sh        # hilos de un proceso y la condición de carrera del simulador
bash linux/4_permisos.sh     # umask, chmod y límites de un usuario sin privilegios
bash linux/5_memoria.sh      # tamaño de página y asignación bajo demanda
```

## Documentos

En `docs/` están los entregables en PDF y Word, las capturas reales en `docs/evidencias/` y los diagramas con su fuente Mermaid en `docs/diagramas/`.

| Documento | Contenido |
|---|---|
| Proyecto SO - 1 Documento de diseño | Problema, objetivos, arquitectura, módulos, diagramas y pseudocódigo |
| Proyecto SO - 2 Evidencias Linux y comparación | Capturas y explicación de las prácticas, y tabla de diferencias con el simulador |
| Proyecto SO - 3 Informe final | Pruebas, resultados, dificultades y conclusiones |
| Proyecto SO - Guía de estudio y sustentación | Conceptos, recorrido del código, guion de la demostración y preguntas probables |

## Estructura

| Archivo | Responsabilidad |
|---|---|
| `main.py` | Punto de entrada |
| `simulador/menu.py` | Menú de consola que integra los módulos |
| `simulador/procesos.py` | Bloque de control de cada proceso y tabla de procesos para crear, consultar y finalizar |
| `simulador/planificacion.py` | FCFS, SJF no expulsivo, Round Robin y estadísticas de finalización, retorno y espera |
| `simulador/concurrencia.py` | Contador compartido sin Lock y con Lock, y cola de mensajes entre productor y consumidor |
| `simulador/memoria.py` | Memoria contigua con asignación por mejor ajuste y liberación que une huecos vecinos |
| `simulador/archivos.py` | Crear, listar, leer, modificar y eliminar archivos en `carpeta_pruebas` |
| `tests/` | Pruebas unitarias |
| `linux/` | Scripts de las prácticas en Linux |
| `docs/` | Entregables, capturas y diagramas |

## Decisiones del modelo

- **Al crear un proceso** se le asigna su memoria y queda en estado Listo. Si no hay espacio, no se registra. **Al finalizarlo** libera su memoria y queda Terminado.
- **La planificación** usa los procesos activos y no los modifica. Así los tres algoritmos se comparan sobre el mismo conjunto.
- **Desempates.** A igual llegada gana el PID menor. En SJF, a igual ráfaga gana el que llegó primero. En Round Robin, los procesos que llegan durante un quantum entran a la cola antes que el proceso que acaba de usar la CPU.
- **Retorno** es finalización menos llegada. **Espera** es retorno menos ráfaga.
- **Memoria.** Cuando un proceso no cabe, el mensaje distingue entre falta de espacio y fragmentación externa, que es cuando el espacio libre total alcanza pero ningún hueco contiguo sirve.
- **Condición de carrera.** Cada hilo lee el contador, cede la CPU y luego escribe. Sin Lock otro hilo se cuela entre la lectura y la escritura y se pierden sumas. Con Lock el resultado siempre es exacto.
