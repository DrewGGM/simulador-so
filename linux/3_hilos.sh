#!/usr/bin/env bash
# Práctica 3: hilos de un proceso vistos desde Linux y la condición de carrera del simulador.
source "$(dirname "$0")/comun.sh"
cd "$(dirname "$0")/.."

titulo "Práctica 3: hilos"

segundo_plano "python3 -c 'import threading, time; [threading.Thread(target=time.sleep, args=(60,)).start() for _ in range(4)]; time.sleep(60)'"
PROCESO=$!
sleep 0.5
comando "ps -o pid,nlwp,comm -p $PROCESO"
comando "ps -T -o pid,spid,stat,comm -p $PROCESO"
comando "ls /proc/$PROCESO/task"

comando "python3 -c 'from simulador.concurrencia import incrementar_contador as f; print(f(usar_lock=False)); print(f(usar_lock=True))'"

kill "$PROCESO"
