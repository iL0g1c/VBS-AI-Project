import neat
import visualize
import time

class Game:
    def __init__(self, PlayerA, playerB):
        self.playerA = PlayerA
        self.playerB = playerB
        self.night = 0
        self.winner = None
        self.logs = ""

        self.playerAOverCash = 0
        self.playerBOverCash = 0
    def start(self, train=False, saveVerbose=False):
        while self.night < 5:
            self.resolveNight(train, saveVerbose)
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

    def resolveNight(self, train, saveVerbose):
        playerAOverCash = 0
        playerBOverCash = 0
        self.night += 1
        if not train:
            print("Night", self.night)
            print("===================================")
            print("Player A coinage:", self.playerA.coinage)
            print("Player A cash:", self.playerA.cash)
            print("Player B coinage:", self.playerB.coinage)
            print("Player B cash:", self.playerB.cash)
            print("===================================\n")
            
            print("Player A's turn")
            self.playerA.resolveDecision(saveVerbose)
            print("Player B's turn")
            if self.playerB.playerType == "Human":
                self.playerB.resolveDecision(saveVerbose)
            else:
                self.playerB.resolveDecision(saveVerbose, night=self.night, opCoin=self.playerA.coinage, opCash=self.playerA.cash, opCoinCommit=self.playerA.coinCommit, opCashCommit=self.playerA.cashCommit, opWins=self.playerA.wins)

            print("===================================")
            print("Player A commit coins:", self.playerA.coinCommit)
            print("Player A commit cash:", self.playerA.cashCommit)
            print("Player B commit coins:", self.playerB.coinCommit)
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
            if saveVerbose:
                self.logs += f"Night: {self.night}\n"
                self.logs += f"===================================\n"
                self.logs += f"Player A coinage: {self.playerA.coinage}\n"
                self.logs += f"Player A cash: {self.playerA.cash}\n"
                self.logs += f"Player B coinage: {self.playerB.coinage}\n"
                self.logs += f"Player B cash: {self.playerB.cash}\n"
            self.playerA.resolveDecision(saveVerbose, night=self.night, opCoin=self.playerB.coinage, opCash=self.playerB.cash, opCoinCommit=self.playerB.coinCommit, opCashCommit=self.playerB.cashCommit, opWins=self.playerB.wins)
            self.playerB.resolveDecision(saveVerbose, night=self.night, opCoin=self.playerA.coinage, opCash=self.playerA.cash, opCoinCommit=self.playerA.coinCommit, opCashCommit=self.playerA.cashCommit, opWins=self.playerA.wins)


            if saveVerbose:
                self.logs += f"===================================\n"
                self.logs += f"Player A commit coins: {self.playerA.coinCommit}\n"
                self.logs += f"Player A commit cash: {self.playerA.cashCommit}\n"
                self.logs += f"Player B commit coins: {self.playerB.coinCommit}\n"
                self.logs += f"Player B commit cash: {self.playerB.cashCommit}\n"
                self.logs += f"===================================\n"
            bucketA = self.playerA.coinCommit - self.playerB.cashCommit
            bucketB = self.playerB.coinCommit - self.playerA.cashCommit
            if bucketA < 0:
                self.playerBOverCash += abs(bucketA)
                bucketA = 0
            if bucketB < 0:
                self.playerAOverCash += abs(bucketB)
                bucketB = 0

            if bucketA > bucketB:
                self.playerA.wins += 1
            elif bucketB > bucketA:
                self.playerB.wins += 1
            if saveVerbose:
                self.logs += f"Player A wins: {self.playerA.wins}\n"
                self.logs += f"Player B wins: {self.playerB.wins}\n"