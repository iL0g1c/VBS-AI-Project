import neat
import visualize
import time

class Game:
    def __init__(self, PlayerA, playerB):
        self.playerA = PlayerA
        self.playerB = playerB
        self.night = 0
        self.winner = None
    def start(self, train=False, verbose=False):
        while self.night < 5:
            self.resolveNight(train, verbose)
        if not train:
            if self.playerA.wins > self.playerB.wins:
                self.winner = "Player A"
            elif self.playerB.wins > self.playerA.wins:
                self.winner = "Player B"
            else:
                if self.playerA.totalCommited > self.playerB.totalCommited:
                    self.winner = "Player A"
                elif self.playerB.totalCommited > self.playerA.totalCommited:
                    self.winner = "Player B"

    def resolveNight(self, train, verbose):
        self.night += 1
        if not train:
            print("Night", self.night)
            print("===================================")
            print("Player A coinage:", self.playerA.coinage)
            print("Player B coinage:", self.playerB.coinage)
            print("Player A cash:", self.playerA.cash)
            print("Player B cash:", self.playerB.cash)
            print("===================================\n")
            
            print("Player A's turn")
            self.playerA.resolveDecision(verbose)
            print("Player B's turn")
            if self.playerB.playerType == "Human":
                self.playerB.resolveDecision(verbose)
            else:
                self.playerB.resolveDecision(verbose, night=self.night, opCoin=self.playerA.coinage, opCash=self.playerA.cash, opCoinCommit=self.playerA.coinCommit, opCashCommit=self.playerA.cashCommit, opWins=self.playerA.wins)

            print("===================================")
            print("Player A commit coins:", self.playerA.coinCommit)
            print("Player B commit coins:", self.playerB.coinCommit)
            print("Player A commit cash:", self.playerA.cashCommit)
            print("Player B commit cash:", self.playerB.cashCommit)
            print("===================================\n")

            bucketA = self.playerA.coinCommit - self.playerB.cashCommit
            bucketB = self.playerB.coinCommit - self.playerA.cashCommit
            if bucketA < 0:
                bucketA = 0
            if bucketB < 0:
                bucketB = 0

            print("===================================")
            if bucketA > bucketB:
                self.playerA.wins += 1
                print("Player A wins night", self.night)
            elif bucketB > bucketA:
                self.playerB.wins += 1
                print("Player B wins night", self.night)
            else:
                print("Draw night", self.night)
            print("===================================\n")
            print("Player A wins:", self.playerA.wins)
            print("Player B wins:", self.playerB.wins)
        else:
            if verbose:
                print("Night", self.night)
                print("===================================")
                print("Player A coinage:", self.playerA.coinage)
                print("Player B coinage:", self.playerB.coinage)
                print("Player A cash:", self.playerA.cash)
                print("Player B cash:", self.playerB.cash)
                print("===================================\n")
            self.playerA.resolveDecision(verbose, night=self.night, opCoin=self.playerB.coinage, opCash=self.playerB.cash, opCoinCommit=self.playerB.coinCommit, opCashCommit=self.playerB.cashCommit, opWins=self.playerB.wins)
            self.playerB.resolveDecision(verbose, night=self.night, opCoin=self.playerA.coinage, opCash=self.playerA.cash, opCoinCommit=self.playerA.coinCommit, opCashCommit=self.playerA.cashCommit, opWins=self.playerA.wins)


            if verbose:
                print("===================================")
                print("Player A commit coins:", self.playerA.coinCommit)
                print("Player B commit coins:", self.playerB.coinCommit)
                print("Player A commit cash:", self.playerA.cashCommit)
                print("Player B commit cash:", self.playerB.cashCommit)
                print("===================================\n")
            bucketA = self.playerA.coinCommit - self.playerB.cashCommit
            bucketB = self.playerB.coinCommit - self.playerA.cashCommit
            if bucketA < 0:
                bucketA = 0
            if bucketB < 0:
                bucketB = 0

            if bucketA > bucketB:
                self.playerA.wins += 1
            elif bucketB > bucketA:
                self.playerB.wins += 1
            if verbose:
                print("Player A wins:", self.playerA.wins)
                print("Player B wins:", self.playerB.wins)