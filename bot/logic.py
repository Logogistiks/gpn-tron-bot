"""Handles the game logic."""

# local
from utils import randMove

class Player:
    def __init__(self, id: str, name: str, posX: str=None, posY: str=None) -> None:
        """Creates a player object."""
        self.id = id
        self.name = name
        self.pos = [(posX, posY)] if not None in (posX, posY) else []
        self.dir = None
        self.messages = []

    def updatePos(self, newPosX: str, newPosY: str) -> None: # todo: urgently refactor logic structure
        """Updates the player's position and direction."""
        if self.pos: #not first move
            diffX = int(newPosX) - int(self.pos[-1][0])
            diffY = int(newPosY) - int(self.pos[-1][1])
            if abs(diffX) == 1: # in board
                if diffX > 0:
                    self.dir = "right"
                elif diffX < 0:
                    self.dir = "left"
            else: # loop around
                if diffX < 0:
                    self.dir = "right"
                elif diffX > 0:
                    self.dir = "left"
            if abs(diffY) == 1: # in board
                if diffY > 0:
                    self.dir = "down"
                elif diffY < 0:
                    self.dir = "up"
            else: # loop around
                if diffY < 0:
                    self.dir = "down"
                elif diffY > 0:
                    self.dir = "up"
        self.pos.append((newPosX, newPosY))

    def getPos(self) -> tuple[int, int]:
        """Returns the player's current position."""
        return self.pos[-1]

    def addMsg(self, msg: str) -> None:
        """Adds a message to the player's message history."""
        self.messages.append(msg)

    def nextMove(self) -> str: # nextMove is intentionally a method of the Player class to add ability to simulate moves of all players
        """Returns the next move for the player."""
        return randMove(self.dir) #todo: implement better logic

class GameHandler:
    def __init__(self, sizeX: str, sizeY: str, id: str) -> None:
        """Creates a game object."""
        self.sizeX = int(sizeX)
        self.sizeY = int(sizeY)
        self.map = [[" "]*int(sizeX)]*int(sizeY)
        self.players: dict[str, Player] = {}
        self.myID = id
        self.wins = 0
        self.losses = 0

    def addPlayer(self, id: str, name: str, posX: str=None, posY: str=None) -> None:
        """Adds a player to the game."""
        if not None in (posX, posY):
            self.players[id] = Player(id, name, posX, posY)
        else:
            self.players[id] = Player(id, name)

    def remPlayer(self, id: str) -> None:
        """Removes a player from the game."""
        self.players.pop(id, None)

    def updatePlayerPos(self, id: str, posX: str, posY: str) -> None:
        """Updates a player's position."""
        self.players[id].updatePos(posX, posY)

    def getMe(self) -> Player:
        """Returns the player object of the bot."""
        return self.players[self.myID]

    def getNpcs(self) -> dict[str, Player]:
        """Returns all the other players except the bot."""
        return {k: v for k, v in self.players.items() if k != self.myID}