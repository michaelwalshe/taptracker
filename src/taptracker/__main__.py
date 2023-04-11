import argparse
from typing import Optional

import taptracker
from taptracker.gui import gui


def main(argv: Optional[str] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--track",
        action="store_true",
        help=(
            "Start taptracker and record key press info. "
            "No identifying information is stored"
        ),
    )
    parser.add_argument(
        "--upload", action="store_true", help="Upload the local taptracker data to CAS"
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="Run the SAS Viya model for taptracker and determine Parkinsons ",
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help=(
            "Launch the visual interface"
        ),
    )
    args = parser.parse_args(argv)

    if args.gui and any((args.track, args.report, args.upload)):
        raise ValueError("Cannot open GUI and use CLI")
    if args.track and args.report:
        raise ValueError("Cannot specify both --track and --report")

    if args.gui:
        gui()
    elif args.track:
        taptracker.track()
    elif args.upload:
        taptracker.upload()
    elif args.report:
        taptracker.report()
    else:
        parser.print_help()


if __name__ == "__main__":
    raise SystemExit(main())
