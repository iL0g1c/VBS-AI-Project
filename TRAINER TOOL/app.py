import neat
import visualize
import pickle
import random
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

def getStartingBalance():
    while True:
        print("Enter the starting COIN balance for both players: ")
        coin = input()
        if coin.isdigit():
            coin = int(coin)
            break
        else:
            print("Invalid input. Please try again.")
    while True:
        print("Enter the starting CASH balance for both players: ")
        cash = input()
        if cash.isdigit():
            cash = int(cash)
            break
        else:
            print("Invalid input. Please try again.")
    return coin, cash

# ──────────────────────────────────────────────────────────────────────────────
# 2. Classic absolute-reward fitness (used only for human-vs-AI mode)
# ──────────────────────────────────────────────────────────────────────────────
def calculateFitness(player, opponent, playerOverCash):
    fitness = 0
    fitness += (player.wins / 5) * (50 if player.wins > opponent.wins else 25)
    fitness += ((5 - opponent.wins) / 5) * (50 if player.wins > opponent.wins else 25)
    fitness += (player.totalCommited / (player.startingCoinage + player.startingCash)) * 20
    fitness += (1 - playerOverCash / player.startingCash) * 20
    return fitness

# ──────────────────────────────────────────────────────────────────────────────
# 3. Hall-of-Fame + Elo rating globals
# ──────────────────────────────────────────────────────────────────────────────
HOF_SIZE      = 10
hall_of_fame = {}                 # list of (genome, config) tuples
ELO_DEFAULT   = 1000
ELO_K         = 32
elo_ratings   = {}                 # genome.key → current Elo
generation_idx = 0

def _ensure_elo(genome):
    """Give a new genome an initial rating if it doesn’t have one yet."""
    if genome.key not in elo_ratings:
        elo_ratings[genome.key] = ELO_DEFAULT

def _elo_update(genome_a, genome_b, score_a):
    """Update global elo_ratings dict in-place and return new ratings."""
    _ensure_elo(genome_a)
    _ensure_elo(genome_b)
    ra, rb = elo_ratings[genome_a.key], elo_ratings[genome_b.key]

    ea = 1 / (1 + 10 ** ((rb - ra) / 400))
    eb = 1 - ea
    sb = 1 - score_a

    ra += ELO_K * (score_a - ea)
    rb += ELO_K * (sb      - eb)

    elo_ratings[genome_a.key] = ra
    elo_ratings[genome_b.key] = rb
    return ra, rb

def dump_hof(gen_idx: int, top_k: int = 10, file: str | None = None):
    ranked = sorted(
        hall_of_fame.values(),                       # ← dict → values
        key=lambda t: elo_ratings.get(t[0].key, ELO_DEFAULT),
        reverse=True
    )[:top_k]

    lines = [f"\n=== Hall-of-Fame after generation {gen_idx} ==="]
    for rank, (g, _) in enumerate(ranked, 1):
        rating = elo_ratings.get(g.key, ELO_DEFAULT)
        lines.append(f"{rank:2d}. key={g.key:<6}  Elo={rating:6.1f}")
    output = "\n".join(lines)
    print(output)

    if file is not None:
        with open(file, "a") as fh:
            fh.write(output + "\n")


def add_to_hof(genome, cfg):
    _ensure_elo(genome)                     # ← make sure Elo exists
    hall_of_fame[genome.key] = (genome, cfg)

    if len(hall_of_fame) > HOF_SIZE:
        # drop the key with the worst Elo
        worst_key = min(
            hall_of_fame,
            key=lambda k: elo_ratings.get(k, ELO_DEFAULT)
        )
        del hall_of_fame[worst_key]

# ──────────────────────────────────────────────────────────────────────────────
# 4. Self-play evaluation with HoF sampling + Elo fitness
# ──────────────────────────────────────────────────────────────────────────────
def eval_genomes(genomes, config, coinBalance, cashBalance):
    """
    • Randomly pairs genomes each generation.
    • 30 % of the time, swaps the opponent with a random Hall-of-Fame entry.
    • Best genome of the generation is pushed into the Hall-of-Fame.
    """
    global generation_idx

    random.shuffle(genomes)
    best_genome = None
    best_fitness = float('-inf')

    for i in range(0, len(genomes), 2):
        _, genome_a = genomes[i]

        # --- pick opponent -------------------------------------------------
        use_hof = (random.random() < 0.30) and bool(hall_of_fame)

        if use_hof:
            genome_b, _ = random.choice(list(hall_of_fame.values()))  # dict → list
            hof_opponent = True
        elif i + 1 < len(genomes):
            genome_b = genomes[i + 1][1]
            hof_opponent = False
        else:                              # lonely last genome
            if hall_of_fame:
                genome_b, _ = random.choice(list(hall_of_fame.values()))
                hof_opponent = True
            else:
                genome_a.fitness = 0.0
                continue


        # --- play one game --------------------------------------------------
        playerA = Player(coinBalance, cashBalance, "AI", Genome=genome_a, Config=config)
        playerB = Player(coinBalance, cashBalance, "AI", Genome=genome_b, Config=config)
        game = Game(playerA, playerB)
        game.start(train=True, saveVerbose=True)

        # Determine win/draw/loss for Elo
        if game.playerA.wins > game.playerB.wins:
            score_a = 1.0
        elif game.playerA.wins < game.playerB.wins:
            score_a = 0.0
        else:
            score_a = 0.5

        new_ra, new_rb = _elo_update(genome_a, genome_b, score_a)

        genome_a.fitness = new_ra
        if not hof_opponent: # don’t overwrite HoF genome’s stored fitness
            genome_b.fitness = new_rb

        # Track best live genome of this generation
        if new_ra > best_fitness:
            best_fitness, best_genome = new_ra, genome_a
        if (not hof_opponent) and new_rb > best_fitness:
            best_fitness, best_genome = new_rb, genome_b

    # --- update Hall-of-Fame -----------------------------------------------
    if best_genome is not None:
        add_to_hof(best_genome, config)

    # guarantee every genome has numeric fitness
    for _, genome in genomes:
        _ensure_elo(genome)
        genome.fitness = elo_ratings[genome.key]

    # ----- dump HoF for this generation ------------------------------
    dump_hof(generation_idx, top_k=10, file="hall_of_fame.log")
    generation_idx += 1

def run(config_file, coinBalance, cashBalance):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)
    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)
    pop.add_reporter(neat.Checkpointer(500))

    # Pass the balances to eval_genomes
    winner = pop.run(lambda g, c: eval_genomes(g, c, coinBalance, cashBalance), 1000)
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
        playerAFitness = calculateFitness(game.playerA, game.playerB, game.playerAOverCash)
        playerBFitness = calculateFitness(game.playerB, game.playerA, game.playerBOverCash)


    if gamemode == 3:
        coinBalance, cashBalance = getStartingBalance()
        run("config-feedforward.txt", coinBalance, cashBalance)

if __name__ == "__main__":
    main()
