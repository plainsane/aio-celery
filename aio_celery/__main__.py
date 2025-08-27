from __future__ import annotations

import asyncio
import logging
import sys

from . import __version__
from .cli import create_parser, create_worker_parser
from .worker import run


def main() -> None:
    parser = create_parser()
    parser = create_worker_parser(parser)
    args = parser.parse_args()

    if args.version:
        print(__version__)  # noqa: T201
        return

    if args.subcommand is None:
        parser.print_help()
        return

    if args.concurrency < 1:
        print(  # noqa: T201
            "concurrency must be larger than 1",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        asyncio.run(run(args))
    except KeyboardInterrupt:
        logging.getLogger(__name__).warning("Worker process interrupted.")


if __name__ == "__main__":
    main()
