#!/usr/bin/env bash
# Práctica 2: prioridades con nice y renice, y reparto de CPU entre dos procesos que compiten.
source "$(dirname "$0")/comun.sh"

titulo "Práctica 2: prioridades"

segundo_plano 'nice -n 10 sleep 300'
DORMIDO=$!
comando "ps -o pid,ni,pri,cmd -p $DORMIDO"
comando "renice -n 15 -p $DORMIDO"
comando "renice -n 5 -p $DORMIDO"

segundo_plano "taskset -c 0 python3 -c 'while True: pass'"
NORMAL=$!
segundo_plano "taskset -c 0 nice -n 19 python3 -c 'while True: pass'"
AMABLE=$!
comando "sleep 3; top -b -n 2 -d 3 -p $NORMAL,$AMABLE | tail -3"

comando 'chrt -p $$; chrt -m'

kill "$DORMIDO" "$NORMAL" "$AMABLE"
