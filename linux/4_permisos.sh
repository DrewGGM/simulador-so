#!/usr/bin/env bash
# Práctica 4: permisos de archivos con chmod, umask y los límites de un usuario sin privilegios.
source "$(dirname "$0")/comun.sh"
rm -rf ~/practica-permisos && mkdir ~/practica-permisos && cd ~/practica-permisos

titulo "Práctica 4: permisos"

comando 'id'
comando 'umask; touch informe.txt; ls -l informe.txt'
comando 'chmod 640 informe.txt; ls -l informe.txt'
comando 'chmod u-w informe.txt; echo "dato" >> informe.txt'
comando "printf 'echo Hola desde un script\n' > saludo.sh; ./saludo.sh"
comando 'chmod u+x saludo.sh; ./saludo.sh'
comando "stat -c '%A %a %U %G %n' informe.txt saludo.sh"
comando 'chown root informe.txt'
