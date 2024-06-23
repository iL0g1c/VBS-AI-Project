class Player:
    def __init__(self, Coinage, Cash, PlayerType):
        self.coinage = Coinage
        self.cash = Cash
        self.wins = 0
        self.playerType = PlayerType
        self.totalCommited = 0
        self.coinCommit = 0
        self.cashCommit = 0
    def resolveDecision(self):
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
            return (self.coinCommit, self.cashCommit)
        elif (self.playerType == "AI"):
            pass
        else:
            return "ERROR NOT VALID PLAYER TYPE"