import socket
from random import choice

def getAuth():
    with open("auth.csv") as f:
        return f.readlines()[-1].split(";")

def log(message: str, silent: bool=False):
    with open("log.txt", "a") as f:
        f.write(message + "\n")
    if not silent:
        print(message)

def logClear():
    with open("log.txt", "w") as f:
        f.write("")

def splash():
    with open("splashes.txt", "r") as f:
        return choice(f.readlines())

class Connection:
    def __init__(self, host: str, port: int):
        self.socket = socket.create_connection((host, port))

    def end(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        log("connection closed")

    def readStream(self, buffer: int=1024):
        decoded = self.socket.recv(buffer).decode() # "cmd1|p11|p12\ncmd2|p21|p22\n"
        cmdlst = decoded.split("\n")[:-1] # ["cmd1|p11|p12", "cmd2|p21|p22"]
        log(f"read stream < {cmdlst} >")
        return list(map(lambda x:x.split("|"), cmdlst)) # [["cmd1", "p11", "p12"], ["cmd2", "p21", "p22"]]

    def writeStream(self, *args):
        msg = "|".join(args) + "\n"
        self.socket.send(msg.encode())
        log(f"written stream < {msg} >")

class GameManager:
    def __init__(self, mapX: str, mapY: str, id: str):
        self.mapX = int(mapX)
        self.mapY = int(mapY)
        self.myID = id
        self.players = {}
        self.wins = 0
        self.losses = 0

    def addPlayer(self, id: str, name: str=None, posX: str=None, posY: str=None):
        self.players[id] = Player(name, posX, posY)

    def remPlayer(self, id: str):
        if id in self.players:
            del self.players[id]

    def getMe(self):
        return self.players[self.myID]

    def getNpcs(self):
        return {k:v for k,v in self.players.items() if k != self.myID}

    def nextMove(self):
        return choice(["up", "down", "left", "right"])

class Player:
    def __init__(self, name: str, posX: str, posY: str):
        self.name = name
        self.posX = []
        self.posY = []
        self.updatePos(posX, posY)
        self.messages = []

    def updatePos(self, posX: str, posY: str):
        self.posX.append(posX)
        self.posY.append(posY)

    def addMsg(self, msg: str):
        self.messages.append(msg)

def main():
    while True:
        tcp = Connection(HOST, PORT)
        log("connection established")
        tcp.writeStream("join", USER, PASS)

        while True:
            msglst = tcp.readStream() # [['motd', 'You can find...']]
            for msg in msglst:
                match msg[0]:
                    case "error":
                        pass
                    case "motd":
                        pass
                    case "game":
                        try: del game
                        except: pass
                        game = GameManager(*msg[1:])
                        tcp.writeStream("chat", splash())
                    case "pos":
                        game.players[msg[1]].updatePos(*msg[2:])
                    case "player":
                        game.addPlayer(msg[1], msg[2])
                    case "tick":
                        tcp.writeStream("move", game.nextMove())
                    case "die":
                        try:
                            for id in msg[1:]:
                                game.remPlayer(id)
                        except: pass
                    case "message":
                        game.players[msg[1]].addMsg(msg[2])
                    case "win":
                        game.wins = msg[1]
                        game.losses = msg[2]
                    case "lose":
                        game.wins = msg[1]
                        game.losses = msg[2]

HOST = "localhost"
PORT = 4000
USER, PASS = getAuth()
logClear()

while True:
    main()