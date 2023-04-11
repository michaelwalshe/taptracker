import csv
import sys
import time
from dataclasses import astuple, dataclass, fields
from datetime import datetime
from pathlib import Path
from typing import Type
from types import TracebackType

from pynput.keyboard import Key, KeyCode, Listener, HotKey

from .params import KEY_FILE, KEY_HAND_MAP, UUID, IS_RUNNING
from . import connections


@dataclass
class KeyInfo:
    """Simple class to store key press info with sensible defaults."""

    id: str = UUID
    timestamp: datetime = datetime.now()
    press_ts: float = -1
    release_ts: float = -1
    key: str = ""
    hand: str = "U"
    hold_time: float = -1

    def field_names(self):
        return tuple(f.name for f in fields(self))

    def __iter__(self):
        return iter(astuple(self))


def append_keystrokes(info: list[KeyInfo], key_file: Path = KEY_FILE):
    """Add info about keystrokes to local data file

    Args:
    ----
        info: List of KeyInfo to save
        key_file: File to either create or append to
    """
    # Check if database created, if not add header row
    write_header = not key_file.exists()
    mode = "w" if write_header else "a"

    with key_file.open(mode, newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(KeyInfo().field_names())
        writer.writerows(info)


def get_name(key: Key | KeyCode) -> str:
    """Get the simple name of a key like object"""
    try:
        if isinstance(key, KeyCode):
            name = key.char.lower()
        elif isinstance(key, Key):
            name = key.name.lower()
    except AttributeError:
        name = ""
    return name


def check_running():
    if IS_RUNNING.exists():
        raise RuntimeError("The process is already running")
    else:
        IS_RUNNING.touch()


def stop_running():
    IS_RUNNING.unlink(missing_ok=True)


def stop_tracking():
    """Exit Python on global hotkey"""
    Listener().stop()
    stop_running()
    print("Stopped tracking...")


def handle_exception(
    exc_type: Type[BaseException],
    exc_value: BaseException,
    exc_traceback: TracebackType,
) -> None:
    """Deletes IS_RUNNING if exception found"""
    stop_running()
    sys.__excepthook__(exc_type, exc_value, exc_traceback)


def track():
    print("Running taptracker, to exit press Ctrl + Alt + Shift + Esc")
    check_running()
    sys.excepthook = handle_exception

    # List of all keys that have been pressed and released, as KeyInfo
    key_presses: list[KeyInfo] = []
    # Keys that are currently pressed, as str: KeyInfos
    current_keys: dict[str, KeyInfo] = {}

    # Global hotkey to exit taptracker
    hotkey = HotKey(HotKey.parse("<ctrl>+<alt>+<shift>+<esc>"), stop_tracking)

    def on_press(key: Key | KeyCode):
        """Inner function that records initial info when key is pressed

        Accesses current_keys, hotkey from outer scope
        """
        hotkey.press(listener.canonical(key))

        name = get_name(key)

        current_keys[name] = KeyInfo(
            timestamp=datetime.now(),
            press_ts=time.perf_counter(),
            key=name,
            hand=KEY_HAND_MAP.get(name, "U"),
        )

        if key == Key.esc:
            raise SystemExit()

    def on_release(key: Key | KeyCode):
        """Inner function that records final info when key released and stores

        Accesses current_keys, key_presses, hotkey from outer scope. If more than 50
        keys have been pressed and stored, then appends key_presses to KEY_FILE
        and resets key_presses
        """
        hotkey.release(listener.canonical(key))

        nonlocal key_presses
        name = get_name(key)

        key_info = current_keys.pop(name, None)

        if key_info is not None:
            key_info.release_ts = time.perf_counter()
            key_info.hold_time = key_info.release_ts - key_info.press_ts
            key_presses.append(key_info)

        if len(key_presses) > 25:
            append_keystrokes(key_presses)
            key_presses = []

    listener = Listener(on_press=on_press, on_release=on_release)
    listener.start()


def upload():
    connections.refresh_access_token()
    connections.create_cas_session()
    connections.upload_key_press(KEY_FILE)
    # KEY_FILE.unlink()


def report():
    from taptracker import processing

    connections.refresh_access_token()

    if KEY_FILE.exists():
        key_stats = processing.process(KEY_FILE)
    else:
        raise RuntimeError(f"No key press data found in {KEY_FILE}")

    classification, prob = connections.model_score_presses(
        key_stats, "gb_predict_parkinsons"
    )

    return (
        f"Based on your typing patterns and this model, it is likely {classification}"
        " that you are showing symptoms of Parkinson's disease. This is based on"
        f" the estimated likelihood of {prob:.2%}."
    )


if __name__ == "__main__":
    track()
