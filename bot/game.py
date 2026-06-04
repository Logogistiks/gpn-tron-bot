# https://github.com/freehuntx/gpn-tron/blob/master/PROTOCOL.md
# https://github.com/freehuntx/gpn-tron/blob/master/ERRORCODES.md

from random import random
from time import sleep
from colorama import Fore

# local
from utils import log, getAuth, logClear, splash
from connection import Connection
from logic import GameHandler

def main(host: str, port: int, chat: bool=False, chatProb: float=0.1) -> None:
    if not 0 <= chatProb <= 1:
        raise ValueError("chatProb must be between 0 and 1")
    logClear()
    tcp = Connection(host, port)
    log("connection established")
    print(getAuth().values())
    tcp.writeStream("join", *getAuth().values())

    try:
        while True:
            for msg in tcp.readStream():
                match msg[0]: # order like in docs
                    case "motd":
                        pass # ignore
                    case "error":
                        log(f"{Fore.LIGHTRED_EX}ERROR{Fore.WHITE} {msg[1]}")
                    case "game":
                        game = GameHandler(*msg[1:]) # overwrite game object
                    case "pos":
                        game.updatePlayerPos(*msg[1:])
                    case "player":
                        game.addPlayer(*msg[1:])
                    case "tick":
                        newMove = game.nextMove()
                        tcp.writeStream("move", newMove)
                        if (chat and random() < chatProb) or (chat and chatProb == 1): # handle edge case
                            sleep(0.05)
                            tcp.writeStream("chat", splash())
                    case "die":
                        for id in msg[1:]:
                            game.remPlayer(id)
                    case "message":
                        game.players[msg[1]].addMsg(msg[2])
                    case "win":
                        pass # ignore, stream dead until next game
                    case "lose":
                        pass # ignore, stream dead until next game
    except KeyboardInterrupt:
        tcp.end()
        log("connection closed")

if __name__ == "__main__":
    main(host="151.216.211.107", port=4000, chat=True, chatProb=0.05)