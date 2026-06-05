"""Handles the game logic."""

from random import choice
from time import time
from copy import deepcopy

class Player:
    def __init__(self, pID: str, name: str, posX: str=None, posY: str=None) -> None:
        """Creates a player object."""
        self.pID = pID
        self.name = name
        self.pos = [(posX, posY)] if not None in (posX, posY) else []
        self.dir = None
        self.messages = []

    def updatePos(self, newPosX: str, newPosY: str, sizeX: int, sizeY: int) -> None:
        """Updates the player's position and direction."""
        if self.pos: #not first move
            dx = int(newPosX) - int(self.pos[-1][0])
            dy = int(newPosY) - int(self.pos[-1][1])
            if dx == 1 or dx == -sizeX:
                self.dir = "right"
            if dx == -1 or dx == sizeX:
                self.dir = "left"
            if dy == 1 or dy == -sizeY:
                self.dir = "down"
            if dy == -1 or dy == sizeY:
                self.dir = "up"
        self.pos.append((newPosX, newPosY))

    def getPos(self) -> tuple[str, str]:
        """Returns the player's current position."""
        return self.pos[-1]

    def addMsg(self, msg: str) -> None:
        """Adds a message to the player's message history."""
        self.messages.append(msg)

class GameHandler:
    def __init__(self, sizeX: str, sizeY: str, pID: str) -> None:
        """Creates a game object."""
        self.sizeX = int(sizeX)
        self.sizeY = int(sizeY)
        self.grid = [[" " for _ in range(int(sizeX))] for _ in range(int(sizeY))]
        self.players: dict[str, Player] = {}
        # per-player spiral state: { rotation: 1|-1, leg_steps: int, steps_in_leg: int, legs_done: int }
        self.spiral_state: dict[str, dict] = {}
        self.myID = pID
        self.startTime = time()

    def currentTickTime(self) -> float:
        """Returns the length of a tick at the current elapsed time in seconds.
        This is the time you have to calculate your move."""
        BASETICKRATE = 1
        TICKINCREASEINTERVAL = 10
        return 1 / (BASETICKRATE + int((time() - self.startTime) / TICKINCREASEINTERVAL))

    def addPlayer(self, pID: str, name: str, posX: str=None, posY: str=None) -> None:
        """Adds a player to the game."""
        if not None in (posX, posY):
            self.players[pID] = Player(pID, name, posX, posY)
            self.grid[int(posY)][int(posX)] = pID
        else:
            self.players[pID] = Player(pID, name)
        # initialize spiral state (start clockwise)
        self.spiral_state[pID] = {"rotation": 1, "leg_steps": 1, "steps_in_leg": 0, "legs_done": 0}

    def remPlayer(self, pID: str) -> None:
        """Removes a player from the game."""
        self.players.pop(pID, None)
        # clean up spiral state
        self.spiral_state.pop(pID, None)
        for y in range(self.sizeY):
            for x in range(self.sizeX):
                if self.grid[y][x] == pID:
                    self.grid[y][x] = " "

    def updatePlayerPos(self, pID: str, posX: str, posY: str) -> None:
        """Updates a player's position."""
        self.players[pID].updatePos(posX, posY, self.sizeX, self.sizeY)
        self.grid[int(posY)][int(posX)] = pID

    def getMe(self) -> Player:
        """Returns the player object of the bot."""
        return self.players[self.myID]

    def getNpcs(self) -> dict[str, Player]:
        """Returns all the other players except the bot."""
        return {k: v for k, v in self.players.items() if k != self.myID}

    def calcnewPos(self, posX: str, posY: str, dir: str) -> tuple[str, str]:
        """Calculates the new position of a player."""
        x, y = int(posX), int(posY)
        if dir == "up":
            return x, (y - 1) % self.sizeY
        if dir == "right":
            return (x + 1) % self.sizeX, y
        if dir == "down":
            return x, (y + 1) % self.sizeY
        if dir == "left":
            return (x - 1) % self.sizeX, y

    def nextMove(self, pID: str=None) -> str: # has ability to simulate moves of other players
        """Moves the player and returns the move."""
        if pID is None:
            pID = self.myID
        newMove = self.strat_spiral(pID)
        self.players[pID].dir = newMove
        return newMove

    def strat_avoid(self, pID: str=None) -> str:
        """A simple strategy that tries to avoid other players by making moves in the direction with the most free cells.
        First the quadrants with respect to the player are checked as an overall metric for the grid, then based on the quadrant one of the two corresponding directions is chosen."""
        if pID is None:
            pID = self.myID
        quadrants = self.getFreeCells_Quadrants(pID)
        directions = self.getFreeCells_Directions(pID)
        bestQuadrant: tuple[str, str] = max(quadrants, key=quadrants.get)
        if directions[bestQuadrant[0]] == 0 and directions[bestQuadrant[1]] == 0: # edge case where no move can be done in the best quadrant
            return self.randMove(pID)
        return bestQuadrant[0] if directions[bestQuadrant[0]] >= directions[bestQuadrant[1]] else bestQuadrant[1]

    def strat_spiral(self, pID: str=None) -> str:
        """A simple strategy that tries to move in a spiral pattern and switches between clockwise and counterclockwise if the way is blocked."""
        if pID is None:
            pID = self.myID
        player = self.players[pID]
        # ensure we have spiral state
        state = self.spiral_state.setdefault(pID, {"rotation": 1, "leg_steps": 1, "steps_in_leg": 0, "legs_done": 0})
        if player.dir is None:
            player.dir = "right"

        order = ["up", "right", "down", "left"]  # clockwise index order
        idx = order.index(player.dir)
        rot = state["rotation"]
        leg_steps = state["leg_steps"]

        def can_move(direction: str) -> bool:
            nx, ny = self.calcnewPos(player.getPos()[0], player.getPos()[1], direction)
            return self.grid[ny][nx] == " "

        # If we haven't completed the current leg, try to go straight first
        if state["steps_in_leg"] < leg_steps:
            if can_move(player.dir):
                state["steps_in_leg"] += 1
                return player.dir
            # straight blocked: attempt to turn according to rotation
            turn_dir = order[(idx + (1 if rot == 1 else -1)) % 4]
            if can_move(turn_dir):
                player.dir = turn_dir
                state["steps_in_leg"] = 1
                state["legs_done"] += 1
                if state["legs_done"] % 2 == 0:
                    state["leg_steps"] += 1
                return turn_dir
            # try flipping rotation
            rot = -rot
            state["rotation"] = rot
            turn_dir2 = order[(idx + (1 if rot == 1 else -1)) % 4]
            if can_move(turn_dir2):
                player.dir = turn_dir2
                state["steps_in_leg"] = 1
                state["legs_done"] += 1
                if state["legs_done"] % 2 == 0:
                    state["leg_steps"] += 1
                return turn_dir2
            return self.randMove(pID)

        # leg complete: try to turn according to rotation
        turn_dir = order[(idx + (1 if rot == 1 else -1)) % 4]
        if can_move(turn_dir):
            player.dir = turn_dir
            state["steps_in_leg"] = 1
            state["legs_done"] += 1
            if state["legs_done"] % 2 == 0:
                state["leg_steps"] += 1
            return turn_dir

        # flip rotation and try other turn
        rot = -rot
        state["rotation"] = rot
        turn_dir2 = order[(idx + (1 if rot == 1 else -1)) % 4]
        if can_move(turn_dir2):
            player.dir = turn_dir2
            state["steps_in_leg"] = 1
            state["legs_done"] += 1
            if state["legs_done"] % 2 == 0:
                state["leg_steps"] += 1
            return turn_dir2

        # both turns blocked: try straight as last resort
        if can_move(player.dir):
            state["steps_in_leg"] += 1
            return player.dir

        return self.randMove(pID)

    def getFreeCells_Directions(self, pID: str=None) -> dict[str, int]:
        """Returns the number of free cells in each direction respective to a player. \\
        Returned is a dict with keys being (up, right, down, left)."""
        if pID is None:
            pID = self.myID
        px, py = self.players[pID].getPos()
        px, py = int(px), int(py)
        freeCells = {"up": 0, "right": 0, "down": 0, "left": 0}
        for i in range(1, py): # up
            if self.grid[py - i][px] != " ":
                break
            freeCells["up"] += 1
        for i in range(1, self.sizeX - px): # right
            if self.grid[py][px + i] != " ":
                break
            freeCells["right"] += 1
        for i in range(1, self.sizeY - py): # down
            if self.grid[py + i][px] != " ":
                break
            freeCells["down"] += 1
        for i in range(1, px): # left
            if self.grid[py][px - i] != " ":
                break
            freeCells["left"] += 1
        return freeCells

    def getFreeCells_Quadrants(self, pID: str=None) -> dict[tuple[str, str], int]:
        """Returns the number of free cells in each Quadrant respective to a player. \\
        Returned is a dict with keys being 2-tuples for the Quadrants (top-left, top-right, bottom-right, bottom-left)."""
        if pID is None:
            pID = self.myID
        px, py = self.players[pID].getPos()
        px, py = int(px), int(py)
        freeCells = {("up", "left"): 0, ("up", "right"): 0, ("down", "right"): 0, ("down", "left"): 0}
        for x in range(self.sizeX):
            for y in range(self.sizeY):
                if self.grid[y][x] != " ":
                    continue
                if x < px and y < py:
                    freeCells[("up", "left")] += 1
                if x > px and y < py:
                    freeCells[("up", "right")] += 1
                if x > px and y > py:
                    freeCells[("down", "right")] += 1
                if x < px and y > py:
                    freeCells[("down", "left")] += 1
        return freeCells

    def randMove(self, pID: str) -> str:
        possibleMoves = self.getPossibleMoves(pID)
        return choice(possibleMoves) if possibleMoves else "up" # theres nothing we can do

    def getPossibleMoves(self, pID: str) -> list[str]:
        """Returns a list of possible moves for a player."""
        x, y = self.players[pID].getPos()
        x, y = int(x), int(y)
        possibleMoves = []
        if self.grid[(y-1) % self.sizeY][x] == " ":
            possibleMoves.append("up")
        if self.grid[y][(x-1) % self.sizeX] == " ":
            possibleMoves.append("left")
        if self.grid[(y+1) % self.sizeY][x] == " ":
            possibleMoves.append("down")
        if self.grid[y][(x+1) % self.sizeX] == " ":
            possibleMoves.append("right")
        return possibleMoves

if __name__ == "__main__":
    print("This file is not meant to be run directly")