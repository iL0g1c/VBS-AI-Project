from game import Game
from player import Player

def getGamemode():
    while True:
        print("""
            1. Play yourself
            2. Play the best AI
            3. Train AI
            Select a gamemode (1-3): 
        """)
        gamemode = input()
        if gamemode in ["1", "2", "3"]:
            return int(gamemode)
        else:
            print("Invalid input. Please try again.")
    

def main():
    gamemode = getGamemode()
    print("You selected gamemode", gamemode)
    if gamemode == 1:
        playerA = Player(300, 300, "Human")
        playerB = Player(300, 300, "Human")
    if gamemode == 2:
        pass
    if gamemode == 3:
        playerA = Player(300, 300, "AI")
        playerB = Player(300, 300, "AI")
    game = Game(playerA, playerB)
    game.start()
    print("The winner is", game.winner)


if __name__ == "__main__":
    main()