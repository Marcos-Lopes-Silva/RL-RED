from asyncio import events

from pyboy import PyBoy
from pyboy.utils import WindowEvent
import os

ROM_PATH = "data/red.gb"
STATE_PATH = "states/initial.state"


def main():
    if not os.path.exists(ROM_PATH):
        print(f"ROM não encontrada: {ROM_PATH}")
        return

    os.makedirs("states", exist_ok=True)

    pyboy = PyBoy(ROM_PATH, window="SDL2")
    pyboy.set_emulation_speed(1)  # velocidade normal pra jogar

    print("🎮 Controles:")
    print("Setas = movimento")
    print("Z = botão A")
    print("X = botão B")
    print("ENTER = Start")
    print("BACKSPACE = Select")
    print("F5 = salvar state")
    print("ESC = sair")

    while True:
        pyboy.tick()
        
        with open(STATE_PATH, "wb") as f:
            pyboy.save_state(f)
            print(f"✅ State salvo em: {STATE_PATH}")


if __name__ == "__main__":
    main()
