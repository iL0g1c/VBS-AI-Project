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
    # FITNESS MODIFICAATIONS
    # NO NEGATIVE FITNESS VALUES
    fitnessLogs = "Fitness Logs\n"
    playerAWinBonus = playerA.wins * 5
    playerATieBonus = (playerA.wins == playerB.wins) * (playerA.totalCommited / 100.0)
    playerAFitness = playerAWinBonus + playerATieBonus
    fitnessLogs += f"Player A win bonus: {playerAWinBonus}\n"
    fitnessLogs += f"Player A tie bonus: {playerATieBonus}\n"
    if playerA.totalCommited != 0:
        penalty = (1 - playerAOverCash / playerA.totalCommited) * 15
    else:
        penalty = 1
    playerAFitness += penalty
    fitnessLogs += f"Player A over cash penalty: {penalty}\n"
    penalty = (5 - playerA.wins) * -6 # Penalize for losing nights
    playerAFitness += penalty
    fitnessLogs += f"Player A loss penalty: {penalty}\n"
    bonus = playerA.wins / 5.0 # Consistency reward
    playerAFitness += bonus
    fitnessLogs += f"Player A consistency bonus: {bonus}\n"
    bonus = 30 * (playerA.totalCommited / (playerA.startingCoinage + playerA.startingCash)) # Manage resources efficiently over the week
    playerAFitness += bonus
    fitnessLogs += f"Player A resource efficiency: {bonus}\n"
    fitnessLogs += f"Player A fitness: {playerAFitness}\n"

    playerBWinBonus = playerB.wins * 5
    playerBTieBonus = (playerB.wins == playerA.wins) * (playerB.totalCommited / 100.0)
    playerBFitness = playerBWinBonus + playerBTieBonus
    fitnessLogs += f"Player B win bonus: {playerBWinBonus}\n"
    fitnessLogs += f"Player B tie bonus: {playerBTieBonus}\n"
    if playerB.totalCommited != 0:
        penalty = (1 - playerBOverCash / playerB.totalCommited) * 15
    else:
        penalty = 1
    playerBFitness += penalty
    fitnessLogs += f"Player B over cash penalty: {penalty}\n"
    penalty = (5 - playerB.wins) * -6
    playerBFitness += penalty
    fitnessLogs += f"Player B loss penalty: {penalty}\n"
    bonus = playerB.wins / 5.0
    playerBFitness += bonus
    fitnessLogs += f"Player B consistency bonus: {bonus}\n"
    bonus = 30 * (playerB.totalCommited / (playerB.startingCoinage + playerB.startingCash))
    playerBFitness += bonus
    fitnessLogs += f"Player B resource efficiency: {bonus}\n"
    fitnessLogs += f"Player B fitness: {playerBFitness}\n"
    return playerAFitness, playerBFitness, fitnessLogs

def eval_genomes(genomes, config, coinBalance, cashBalance):
    highestFitness = 0
    bestLog = ""
    for i in range(0, len(genomes), 2):
        playerA = Player(coinBalance, cashBalance, "AI", Genome=genomes[i][1], Config=config)
        
        if i + 1 < len(genomes):
            playerB = Player(coinBalance, cashBalance, "AI", Genome=genomes[i+1][1], Config=config)
            game = Game(playerA, playerB)

            genomes[i][1].fitness = 0.0
            genomes[i+1][1].fitness = 0.0
            game.logs = "=======================\n"
            game.start(train=True, saveVerbose=True)
            
            playerAFitness, playerBFitness, fitnessLogs = calculateFitness(game.playerA, game.playerB, game.playerAOverCash, game.playerBOverCash)
            game.logs += fitnessLogs
            genomes[i][1].fitness = playerAFitness
            genomes[i+1][1].fitness = playerBFitness
            if (playerAFitness + playerBFitness) / 2 > highestFitness:
                highestFitness = (playerAFitness + playerBFitness) / 2
                bestLog += game.logs
        else:
            # If there is no pair, the genome cannot be evaluated in a game
            # Optionally, assign a default fitness score or handle accordingly
            genomes[i][1].fitness = 0.0
    with open("bestLog.txt", "a") as f:
        f.write(bestLog)
        f.close()

def run(config_file, coinBalance, cashBalance):
    with open("bestLog.txt", "w") as f:
        f.write("")
        f.close()
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(500))

    # Pass the balances to eval_genomes
    winner = p.run(lambda genomes, config: eval_genomes(genomes, config, coinBalance, cashBalance), 500)
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
        playerAFitness, playerBFitness, fitnessLogs = calculateFitness(game.playerA, game.playerB, game.playerAOverCash, game.playerBOverCash)
        print(fitnessLogs)

    if gamemode == 3:
        coinBalance, cashBalance = getStartingBalance()
        run("config-feedforward.txt", coinBalance, cashBalance)

if __name__ == "__main__":
    main()
