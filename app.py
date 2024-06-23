from game import Game
from player import Player
import neat
import visualize
import time
import pickle

coinBalance = 0
cashBalance = 0

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

def getStartingBalance():
    while True:
        print("Enter the starting COIN balance for both players: ")
        startingBalance = input()
        if startingBalance.isdigit():
            coinBalance = int(startingBalance)
            break
        else:
            print("Invalid input. Please try again.")
    while True:
        print("Enter the starting CASH balance for both players: ")
        startingBalance = input()
        if startingBalance.isdigit():
            cashBalance = int(startingBalance)
            break
        else:
            print("Invalid input. Please try again.")
    return coinBalance, cashBalance

def calculateFitness(playerA, playerB, playerAOverCash, playerBOverCash):
    playerAWinBonus = playerA.wins * 5
    playerATieBonus = (playerA.wins == playerB.wins) * (playerA.totalCommited / 100.0)
    playerAFitness = playerAWinBonus + playerATieBonus
    if playerA.totalCommited != 0:
        playerAFitness *= 1.25 - playerAOverCash / playerA.totalCommited # Penalize for wasting cash
    playerAFitness += (5 - playerA.wins) * -6 # Penalize for losing nights
    playerAFitness += playerA.wins / 5.0 # Consistency reward
    playerAFitness += 30 * ((playerA.startingCoinage + playerA.startingCash - playerA.totalCommited) / (playerA.startingCoinage + playerA.startingCash)) # Manage resources efficiently over the week

    playerBWinBonus = playerB.wins * 5
    playerBTieBonus = (playerA.wins == playerB.wins) * (playerB.totalCommited / 100.0)
    playerBFitness = playerBWinBonus + playerBTieBonus
    if playerB.totalCommited != 0:
        playerBFitness *= 1.25 - playerBOverCash / playerB.totalCommited
    playerBFitness += (5 - playerB.wins) * -6
    playerBFitness += playerB.wins / 5.0
    playerBFitness += 20 * ((playerB.startingCoinage + playerB.startingCash - playerB.totalCommited) / (playerB.startingCoinage + playerB.startingCash))
    return playerAFitness, playerBFitness

def eval_genomes(genomes, config, coinBalance, cashBalance):
    for i in range(0, len(genomes), 2):
        playerA = Player(coinBalance, cashBalance, "AI", Genome=genomes[i][1], Config=config)
        
        if i + 1 < len(genomes):
            playerB = Player(coinBalance, cashBalance, "AI", Genome=genomes[i+1][1], Config=config)
            game = Game(playerA, playerB)

            genomes[i][1].fitness = 0.0
            genomes[i+1][1].fitness = 0.0
            if i > 97:
                game.start(train=True, verbose=True)
            else:
                game.start(train=True)
            
            playerAFitness, playerBFitness = calculateFitness(game.playerA, game.playerB, game.playerAOverCash, game.playerBOverCash)
            genomes[i][1].fitness = playerAFitness
            genomes[i+1][1].fitness = playerBFitness
        else:
            # If there is no pair, the genome cannot be evaluated in a game
            # Optionally, assign a default fitness score or handle accordingly
            genomes[i][1].fitness = 0.0

def run(config_file, coinBalance, cashBalance):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(500))

    # Pass the balances to eval_genomes
    winner = p.run(lambda genomes, config: eval_genomes(genomes, config, coinBalance, cashBalance), 400)
    with open("winner.pkl", "wb") as f:
        pickle.dump(winner, f)
        f.close()

    print('\nBest genome:\n{!s}'.format(winner))
    node_names = {-1: 'Coinage', -2: 'Cash', -3: 'Night', -4: 'Opponent Coinage', -5: 'Opponent Cash', -6: 'Coinage Commit', -7: 'Cash Commit', -8: 'Opponent Coinage Commit', -9: 'Opponent Coin Commit', -10: 'Wins', -11: 'Losses'}
    visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

def main():
    gamemode = getGamemode()
    print("You selected gamemode", gamemode)
    if gamemode == 1:
        coinBalance, cashBalance = getStartingBalance()
        playerA = Player(coinBalance, cashBalance, "Human")
        playerB = Player(coinBalance, cashBalance, "Human")
        game = Game(playerA, playerB)
        game.start()
        print("The winner is", game.winner)
    if gamemode == 2:
        coinBalance, cashBalance = getStartingBalance()
        playerA = Player(coinBalance, cashBalance, "Human")
        playerB = Player(coinBalance, cashBalance, "AI", train=False, Config=neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            "config-feedforward.txt"))
        game = Game(playerA, playerB)
        game.start()
        playerAFitness, playerBFitness = calculateFitness(game.playerA, game.playerB, game.playerAOverCash, game.playerBOverCash)
        print("Player A fitness:", playerAFitness)
        print("Player B fitness:", playerBFitness)

    if gamemode == 3:
        coinBalance, cashBalance = getStartingBalance()
        run("config-feedforward.txt", coinBalance, cashBalance)

if __name__ == "__main__":
    main()
