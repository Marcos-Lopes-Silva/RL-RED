import os
import queue
import sys
import threading

from pyboy import PyBoy

from src.pyboy_adapter import PyBoyAdapter
from src.pokemon_ram import MemoryService
from src.state_builder import StateBuilder

ROM_PATH = "data/red.gb"
STATES_DIR = "data"

AJUDA = """
Comandos (digite no terminal e aperte Enter):
  s nome      salva o estado em data/nome.state
  c nome      carrega data/nome.state
  i           mostra mapa, posição, insígnias e time
  v N         muda a velocidade do emulador (1 = normal)
  ajuda       mostra esta lista
  sair        fecha o emulador

Teclas do jogo: setas, A = A, S = B, Enter = Start, Backspace = Select
"""

comandos = queue.Queue()


def ler_terminal():
    while True:
        try:
            linha = input().strip()
        except EOFError:
            break
        if linha:
            comandos.put(linha)


def caminho_state(nome):
    return os.path.join(STATES_DIR, f"{os.path.basename(nome)}.state")


def salvar(pyboy, nome):
    os.makedirs(STATES_DIR, exist_ok=True)
    caminho = caminho_state(nome)
    with open(caminho, "wb") as f:
        pyboy.save_state(f)
    print(f"Salvo: {caminho} ({os.path.getsize(caminho)} bytes)")


def carregar(pyboy, nome):
    caminho = caminho_state(nome)
    if not os.path.exists(caminho):
        print(f"Arquivo não encontrado: {caminho}")
        return
    with open(caminho, "rb") as f:
        pyboy.load_state(f)
    print(f"Carregado: {caminho}")


def mostrar_info(state_builder):
    x, y, map_id, badges, party_size, species = state_builder.build()
    print(f"mapa={map_id} pos=({x}, {y}) insignias={badges} time={party_size} primeiro={species}")


def processar(pyboy, state_builder, linha):
    partes = linha.split()
    cmd = partes[0].lower()

    if cmd == "s" and len(partes) > 1:
        salvar(pyboy, partes[1])
    elif cmd == "c" and len(partes) > 1:
        carregar(pyboy, partes[1])
    elif cmd == "i":
        mostrar_info(state_builder)
    elif cmd == "v" and len(partes) > 1:
        try:
            pyboy.set_emulation_speed(int(partes[1]))
            print(f"Velocidade: {partes[1]}x")
        except ValueError:
            print("Use um número inteiro, ex: v 2")
    elif cmd == "ajuda":
        print(AJUDA)
    elif cmd == "sair":
        return False
    else:
        print("Comando inválido. Digite 'ajuda'.")

    return True


def main():
    if not os.path.exists(ROM_PATH):
        print(f"Erro: ROM não encontrada em {ROM_PATH}")
        sys.exit(1)

    pyboy = PyBoy(ROM_PATH, window="SDL2")
    pyboy.set_emulation_speed(1)

    adapter = PyBoyAdapter(pyboy)
    state_builder = StateBuilder(MemoryService(adapter.pyboy))

    if len(sys.argv) > 1:
        carregar(pyboy, sys.argv[1])

    threading.Thread(target=ler_terminal, daemon=True).start()
    print(AJUDA)

    frame = 0
    ultimo_mapa = None
    rodando = True

    while rodando and pyboy.tick():
        frame += 1

        while rodando and not comandos.empty():
            rodando = processar(pyboy, state_builder, comandos.get())

        if frame % 30 == 0:
            mapa = state_builder.build()[2]
            if mapa != ultimo_mapa:
                print(f"Mapa atual: {mapa}")
                ultimo_mapa = mapa

    pyboy.stop()


if __name__ == "__main__":
    main()