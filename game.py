class Game:
    def __init__(self, PlayerA, playerB):
        self.playerA = PlayerA
        self.playerB = playerB
        self.night = 0
        self.winner = None
    def start(self):
        while self.night < 5:
            self.resolveNight()
        if self.playerA.wins > self.playerB.wins:
            self.winner = "Player A"
        elif self.playerB.wins > self.playerA.wins:
            self.winner = "Player B"
        else:
            if self.playerA.totalCommited > self.playerB.totalCommited:
                self.winner = "Player A"
            elif self.playerB.totalCommited > self.playerA.totalCommited:
                self.winner = "Player B"

    def resolveNight(self):
        self.night += 1
        print("Night", self.night)
        print("===================================")
        print("Player A coinage:", self.playerA.coinage)
        print("Player B coinage:", self.playerB.coinage)
        print("Player A cash:", self.playerA.cash)
        print("Player B cash:", self.playerB.cash)
        print("===================================\n")
        
        print("Player A's turn")
        self.playerA.resolveDecision()
        print("Player B's turn")
        self.playerB.resolveDecision()

        print("===================================")
        print("Player A commit coins:", self.playerA.coinCommit)
        print("Player B commit coins:", self.playerB.coinCommit)
        print("Player A commit cash:", self.playerA.cashCommit)
        print("Player B commit cash:", self.playerB.cashCommit)
        print("===================================\n")

        bucketA = self.playerA.coinCommit - self.playerB.cashCommit
        bucketB = self.playerB.coinCommit - self.playerA.cashCommit

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