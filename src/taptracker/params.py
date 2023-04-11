import importlib.resources
import uuid
from pathlib import Path

# SAS hackathon site global vars
CLIENT_ID = "taptracker"
CLIENT_SECRET = "goobly"
BASE_URL = "https://xaas-20791154275.engage.sas.com/"
CAS_SERVER = "https://xaas-20791154275.engage.sas.com:443/cas-shared-default-http/"

# Unique identifier for this PC
UUID = str(uuid.UUID(int=uuid.getnode()))[-12:]
if UUID[0].isnumeric():
    UUID = f"a{UUID[1:]}"

# Package local files
DATA = Path(importlib.resources.files("taptracker").joinpath("data"))

# API tokens
REFRESH_TOKEN_FILE = DATA / "refresh_token.txt"

# Package directory file to save key info to
KEY_FILE = DATA / "key_presses.csv"

# Theme and image files
THEME_FILE = DATA / "ctk_theme.json"
LOGO_FILE = DATA / "MARQUE-MAIN-LOGO.png"

# Whether the process is currently running
IS_RUNNING = DATA / ".is_running"

# Mapping of each key character to left or right side of keyboard
KEY_HAND_MAP = {
    "tab": "L",
    "caps_lock": "L",
    "shift_l": "L",
    "ctrl_l": "L",
    "f1": "L",
    "f2": "L",
    "f3": "L",
    "f4": "L",
    "f5": "L",
    "`": "L",
    "cmd": "L",
    "alt": "L",
    "1": "L",
    "2": "L",
    "3": "L",
    "4": "L",
    "5": "L",
    "¬": "L",
    "|": "L",
    "!": "L",
    '"': "L",
    "£": "L",
    "$": "L",
    "%": "L",
    "q": "L",
    "w": "L",
    "e": "L",
    "r": "L",
    "t": "L",
    "y": "L",
    "a": "L",
    "s": "L",
    "d": "L",
    "f": "L",
    "g": "L",
    "z": "L",
    "x": "L",
    "c": "L",
    "v": "L",
    "b": "L",
    "u": "R",
    "i": "R",
    "o": "R",
    "p": "R",
    "h": "R",
    "j": "R",
    "k": "R",
    "l": "R",
    "n": "R",
    "m": "R",
    "6": "R",
    "7": "R",
    "8": "R",
    "9": "R",
    "0": "R",
    "^": "R",
    "&": "R",
    "*": "R",
    "(": "R",
    ")": "R",
    "-": "R",
    "=": "R",
    "[": "R",
    "]": "R",
    ";": "R",
    "'": "R",
    "#": "R",
    ",": "R",
    ".": "R",
    "/": "R",
    "_": "R",
    "+": "R",
    "{": "R",
    "}": "R",
    ":": "R",
    "@": "R",
    "~": "R",
    "<": "R",
    ">": "R",
    "?": "R",
    "enter": "R",
    "backspace": "R",
    "alt_r": "R",
    "ctrl_r": "R",
    "alt_gr": "R",
    "up": "R",
    "down": "R",
    "left": "R",
    "right": "R",
    "shift_r": "R",
    "insert": "R",
    "home": "R",
    "delete": "R",
    "end": "R",
    "page_down": "R",
    "page_up": "R",
    "print_screen": "R",
    "scroll_lock": "R",
    "pause": "R",
    "num_lock": "R",
}
