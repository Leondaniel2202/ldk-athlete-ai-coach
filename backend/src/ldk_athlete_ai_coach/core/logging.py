"""Logging configuration helpers for the application."""

import logging


def configure_logging(*, debug: bool = False) -> None:
    """Configure global logging for the application runtime.

    Args:
        debug: Whether to enable debug-level logging.

    """
    logging.basicConfig(
        level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        force=True,
    )
