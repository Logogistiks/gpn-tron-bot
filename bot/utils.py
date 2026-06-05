"""Outsourced utility functions."""

import os
from random import choice

DIRECTIONS: tuple[str] = ("up", "right", "down", "left") # do not change order

def file(path: str) -> str: # this is because i openend the repo directory in vscode, not the bot directory, it should work nevertheless
    """Returns the absolute path of the file."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), path)

def getAuth() -> dict[str, str]:
    """Returns the last entry in the auth file as {"user", "pass"}"""
    with open(file("auth.csv")) as f:
        return {k: v for k, v in zip(["user", "pass"], f.readlines()[-1].split(";"))}

def log(message: str, silent: bool=False):
    """Logs a message to the log file and prints it to the console if not silent."""
    with open(file("log.txt"), "a") as f:
        f.write(message + "\n")
    if not silent:
        print(message.replace("\n", ""))

def logClear() -> None:
    """Clears the log file."""
    with open(file("log.txt"), "w") as f:
        f.write("")

def splash(fname: str="splashes.txt") -> str:
    """Returns a random splash message from the splashes file."""
    if not os.path.exists(file(fname)):
        return "I am a bot"
    with open(file(fname), "r") as f:
        content = f.readlines()
        return "I am a bot" if not content else choice(content).replace("\n", "")

def reverseDir(dir: str) -> str:
    """Returns the opposite direction of the given direction."""
    return DIRECTIONS[(DIRECTIONS.index(dir) + 2) % 4] # depends on the defined order of DIRECTIONS

if __name__ == "__main__":
    print("This file is not meant to be run directly")