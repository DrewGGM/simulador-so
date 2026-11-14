"""Punto de entrada del simulador de sistema operativo."""
from simulador.menu import Simulador

if __name__ == "__main__":
    try:
        Simulador().ejecutar()
    except (KeyboardInterrupt, EOFError):
        print("\nSimulador cerrado.")
