#!/usr/bin/env bash
# Práctica 5: memoria virtual paginada, tamaño de página y asignación bajo demanda.
source "$(dirname "$0")/comun.sh"

titulo "Práctica 5: memoria"

comando 'free -h'
comando 'getconf PAGESIZE'

segundo_plano "python3 -c 'import mmap, time; m = mmap.mmap(-1, 200 * 2**20); time.sleep(30)'"
RESERVA=$!
segundo_plano "python3 -c 'import mmap, time; m = mmap.mmap(-1, 200 * 2**20); m[::4096] = bytes(51200); time.sleep(30)'"
USADA=$!
sleep 1
comando "ps -o pid,vsz,rss,cmd -p $RESERVA,$USADA"

kill "$RESERVA" "$USADA"
