#!/usr/bin/env bash
# Práctica 1: creación de procesos, árbol padre-hijo, estados y señales.
source "$(dirname "$0")/comun.sh"

titulo "Práctica 1: procesos, estados y señales"

comando "ps -o pid,ppid,stat,cmd -p $$ --ppid $$"

segundo_plano 'sleep 300'
DORMIDO=$!
comando "pstree -p $$"

comando "kill -STOP $DORMIDO; ps -o pid,stat,cmd -p $DORMIDO"

segundo_plano "python3 -c 'import os, time; os.fork() or os._exit(0); time.sleep(60)'"
PADRE=$!
sleep 0.5
comando "ps -o pid,ppid,stat,cmd --ppid $PADRE"

comando 'top -b -n 1 | head -2 | tail -1'

comando "kill -CONT $DORMIDO; ps -o pid,stat,cmd -p $DORMIDO"
comando "kill $DORMIDO $PADRE; sleep 0.3; ps -p $DORMIDO,$PADRE > /dev/null || echo 'Los dos procesos terminaron'"
