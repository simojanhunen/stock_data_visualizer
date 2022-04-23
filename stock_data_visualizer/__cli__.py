"""CLI interface for stock_data_visualizer project.
"""

import io
import os

from __base__ import WINDOW_TITLE
from stock_data_visualizing import MainWindow, MainApplication


def read_version(*paths, **kwargs):
    """Read the contents of a text file.
    >>> read("VERSION")
    '0.0.0'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def main():
    """
    Main function
    """

    # Read version
    version = read_version("VERSION")
    print(f"App version: {version}")

    # Run main application
    MainApplication(WINDOW_TITLE)
