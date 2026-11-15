# Funciones compartidas por las prácticas: muestran cada comando con su prompt antes de ejecutarlo.

titulo() {
    printf '\e[1;33m== %s ==\e[0m\n' "$*"
}

_prompt() {
    printf '\n\e[1;32m%s@%s\e[0m:\e[1;34m%s\e[0m$ %s\n' "$USER" "$(hostname)" "${PWD/#$HOME/\~}" "$*"
}

comando() {
    _prompt "$*"
    bash -c "$*"
}

# Deja el proceso en segundo plano; quien llama lee su PID en $!
segundo_plano() {
    _prompt "$* &"
    eval "$* &"
}
