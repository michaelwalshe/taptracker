import argparse
from typing import Optional

import taptracker


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
    args = parser.parse_args(argv)

    if args.track and args.report:
        raise ValueError("Cannot specify both --track and --report")

    if args.track:
        print("Running taptracker, to exit press Ctrl + Alt + Shift + Esc")
        taptracker.track()
    elif args.upload:
        taptracker.upload()
    elif args.report:
        taptracker.report()
    else:
        parser.print_help()


if __name__ == "__main__":
    raise SystemExit(main())
