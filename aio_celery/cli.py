from __future__ import annotations

import argparse

from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create the base argument parser for aio_celery CLI."""
    parser = argparse.ArgumentParser(
        prog="aio_celery",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "CLI for aio_celery\n\n"
            "Examples\n"
            "--------\n"
            "$ %(prog)s worker proj:app\n"
            "$ %(prog)s worker -Q high,low proj:app\n"
            "$ %(prog)s worker --concurrency=50000 proj:app\n"
        ),
    )
    parser.add_argument(
        "-V",
        "--version",
        dest="version",
        action="store_true",
        help="print current aio_celery version and exit",
    )
    return parser


def create_worker_parser(parent_parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Add worker subcommand and arguments to the parser."""
    subparsers = parent_parser.add_subparsers(
        title="Available subcommands",
        metavar="",
        dest="subcommand",
    )
    worker = subparsers.add_parser(
        "worker",
        help="Run worker",
        description="Run worker",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    worker.add_argument(
        "app",
        help=(
            "Where to search for application instance. "
            "This string must be specified in 'module.module:variable' format."
        ),
    )
    worker.add_argument(
        "-c",
        "--concurrency",
        type=int,
        default=10_000,
        help="Maximum simultaneous async tasks",
    )
    worker.add_argument(
        "-Q",
        "--queues",
        help="Comma separated list of queues",
    )
    worker.add_argument(
        "-l",
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "FATAL"],
        default="INFO",
        help="Logging level",
    )
    worker.add_argument(
        "--no-configure-logging",
        action="store_false",
        dest="configure_logging",
        help="Use this parameter if your application configures custom logging.",
    )
    worker.add_argument(
        "--dlx",
        help="Dead letter exchange name to use for failed messages",
    )
    worker.add_argument(
        "--ack-timeout",
        type=int,
        help="Consumer timeout in seconds for message acknowledgment",
    )
    return parent_parser