# Pokémon Red com PPO

Projeto de aprendizado por reforço onde um agente treinado com PPO aprende a jogar Pokémon Red. O jogo roda no emulador PyBoy e o treino usa Stable-Baselines3 com um ambiente Gymnasium personalizado.

## Como funciona

O agente lê a memória do jogo (posição, mapa e insígnias), escolhe um botão a cada passo e recebe uma recompensa. Com o tempo ele aprende a explorar o mapa e a avançar no jogo.

Observação: posição x e y, id do mapa e número de insígnias, todos normalizados entre 0 e 1.

Ações: 8 botões discretos.

## Estrutura do projeto

```
data/
    red.gb              ROM do jogo (não incluída)
    red.state           estado inicial salvo do emulador
src/
    actions.py          ações disponíveis
    game_state.py       estado do jogo (x, y, map_id, badges)
    pokemon_env.py      ambiente Gymnasium
    pokemon_ram.py      leitura da memória do jogo
    pyboy_adapter.py    adaptador do PyBoy
    reward_strategy.py  estratégias de recompensa
    state_builder.py    monta o estado a partir da RAM
train_gin.py            script de treino
```

## Requisitos

Python 3.10 ou superior e as bibliotecas abaixo.

```
pip install pyboy stable-baselines3 gymnasium numpy tensorboard
```

Você precisa fornecer sua própria ROM do Pokémon Red e colocá-la em `data/red.gb`.

## Criando o estado inicial

O ambiente começa sempre a partir de um save state. Abra o jogo, leve o personagem até o ponto desejado e salve:

```python
from pyboy import PyBoy

pyboy = PyBoy("data/red.gb", window="SDL2")
with open("data/re.state", "wb") as f:
    pyboy.save_state(f)
pyboy.stop()
```

## Treinando

```
python train_gin.py
```

O treino usa vários ambientes em paralelo e salva checkpoints na pasta `checkpoints/`. O modelo final é salvo como `ppo_pokemon_red.zip`.

Para acompanhar o treino no TensorBoard:

```
tensorboard --logdir ppo_tensorboard
```

## Rodando o modelo treinado

O script de execução abre o jogo em uma janela e usa o modelo salvo para jogar.

```
python play.py
```

Use `deterministic=False` no `model.predict`. Com a observação atual, o modo determinístico pode repetir a mesma ação quando o agente trava numa parede.

## Recompensas

ProgressReward: bônus por ganhar insígnia e por entrar em um mapa pela primeira vez.

NoveltyReward: bônus por visitar um tile novo.

StagnationPenalty: pequena penalidade quando o agente não sai do lugar.

BacktrackPenalty (opcional): penalidade por voltar rápido ao mapa anterior.

## Problemas comuns

Agente parado: confira se o `NoveltyReward` paga só na primeira visita e rode com `deterministic=False`.

Agente subindo e descendo a escada: o bônus de mapa deve valer só na primeira visita a cada mapa.

Erro "No data" ao carregar o state: o arquivo `re.state` está vazio ou corrompido. Gere de novo usando `with open(...)`.

Erro ao carregar o modelo: se a observação mudou de tamanho, é preciso treinar um modelo novo.

## Aviso

Este projeto é apenas para estudo. A ROM do jogo não é distribuída aqui e deve ser obtida de forma legal.
