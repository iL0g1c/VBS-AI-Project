import neat
import time

class Player:
    def __init__(self, Coinage, Cash, PlayerType, Genome=None, Config=None):
        self.coinage = Coinage
        self.cash = Cash
        self.startingCoinage = Coinage
        self.startingCash = Cash
        self.wins = 0
        self.playerType = PlayerType
        self.totalCommited = 0
        self.coinCommit = 0
        self.cashCommit = 0

        self.genome = Genome
        self.config = Config
        if self.genome is not None and self.config is not None:
            self.net = neat.nn.FeedForwardNetwork.create(self.genome, self.config)
    def resolveDecision(self, verbose, night=None, opCoin=None, opCash=None, opCoinCommit=None, opCashCommit=None, opWins=None):
        if self.playerType == "Human":
            while True:
                coinResponse = input("How much coin would you like to spend? ")
                if coinResponse.isdigit():
                    coinResponse = int(coinResponse)
                    if coinResponse <= self.coinage:
                        self.coinCommit = coinResponse
                        break
                    else:
                        print("You don't have enough coin.")
                else:
                    print("Invalid input. Please try again.")
            while True:
                cashResponse = input("How much cash would you like to spend? ")
                if cashResponse.isdigit():
                    cashResponse = int(cashResponse)
                    if cashResponse <= self.cash:
                        self.cashCommit = cashResponse
                        break
                    else:
                        print("You don't have enough cash.")
                else:
                    print("Invalid input. Please try again.")
            self.coinage -= self.coinCommit
            self.cash -= self.cashCommit
            self.totalCommited += self.coinCommit + self.cashCommit
            if self.coinage < 0:
                self.coinage = 0
            if self.cash < 0:
                self.cash = 0
        elif (self.playerType == "AI"):
            input = [
                self.coinage / self.startingCoinage,
                self.cash / self.startingCash,
                night / 5,
                opCoin / self.startingCoinage,
                opCash / self.startingCash,
                self.coinCommit / self.startingCoinage,
                self.cashCommit / self.startingCash,
                opCoinCommit / self.startingCoinage,
                opCashCommit / self.startingCash,
                self.wins / 5,
                opWins / 5
            ]
            output = self.net.activate(input)
            self.coinCommit = int(output[0] * self.coinage)
            self.cashCommit = int(output[1] * self.cash)

            self.coinage -= self.coinCommit
            self.cash -= self.cashCommit
            self.totalCommited += self.coinCommit + self.cashCommit
            if self.coinage < 0:
                self.coinage = 0
            if self.cash < 0:
                self.cash = 0

        else:
            return "ERROR NOT VALID PLAYER TYPE"

