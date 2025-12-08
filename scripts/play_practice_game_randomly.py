import random

from oecraft.practice_environment import PracticeCraftingGame

game = PracticeCraftingGame()
game.reset()

for game_num in range(10):
    for i in range(10):
        game.render()
        items = random.sample(game.inventory, 2)
        action = items[0]["name"], items[1]["name"]
        game.step(action)

    game.reset()
