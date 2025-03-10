from Assets.scripts.classes.Game_Class import Game
from Assets.scripts.settings import *

def  main():
    while True:
        game = Game()
        game.start_screen()
        game.play()
        q = game.end_screen()
        if q == "quit":
            break
    pg.quit() 
if __name__ == '__main__': 
    main() 