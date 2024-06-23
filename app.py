from game import Game
from player import Player
import neat
import visualize
import time

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
    

def eval_genomes(genomes, config):
    print(f"Number of genomes: {len(genomes)}")  # Debug statement to print the number of genomes
    for i in range(0, len(genomes), 2):
        playerA = Player(300, 300, "AI", Genome=genomes[i][1], Config=config)
        
        if i + 1 < len(genomes):
            playerB = Player(300, 300, "AI", Genome=genomes[i+1][1], Config=config)
            game = Game(playerA, playerB)

            genomes[i][1].fitness = 0.0
            genomes[i+1][1].fitness = 0.0
            print(i)
            if i > 46:
                game.start(train=True, verbose=True)
            else:
                game.start(train=True)
            
            game.playerA.genome.fitness += game.playerA.wins
            game.playerA.genome.fitness -= game.playerB.wins
            game.playerB.genome.fitness += game.playerB.wins
            game.playerB.genome.fitness -= game.playerA.wins
        else:
            # If there is no pair, the genome cannot be evaluated in a game
            # Optionally, assign a default fitness score or handle accordingly
            print(f"Unpaired genome index: {i}")  # Debug statement for unpaired genome
            genomes[i][1].fitness = 0.0


def run(config_file):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                            neat.DefaultSpeciesSet, neat.DefaultStagnation,
                            config_file)
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(300))

    winner = p.run(eval_genomes, 300)

    print('\nBest genome:\n{!s}'.format(winner))
    node_names = {-1: 'Coinage', -2: 'Cash', -3: 'Night', -4: 'Opponent Coinage', -5: 'Opponent Cash', -6: 'Coinage Commit', -7: 'Cash Commit', -8: 'Opponent Coinage Commit', -9: 'Opponent Coin Commit', -10: 'Wins', -11: 'Losses'}
    visualize.draw_net(config, winner, True, node_names=node_names)
    visualize.draw_net(config, winner, True, node_names=node_names, prune_unused=True)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

def main():
    gamemode = getGamemode()
    print("You selected gamemode", gamemode)
    if gamemode == 1:
        playerA = Player(300, 300, "Human")
        playerB = Player(300, 300, "Human")
        game = Game(playerA, playerB)
        game.start()
        print("The winner is", game.winner)
    if gamemode == 2:
        pass
    if gamemode == 3:
        run("config-feedforward.txt")


if __name__ == "__main__":
    main()