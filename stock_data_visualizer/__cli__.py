"""
CLI interface for stock_data_visualizer project.
"""

import io
import os
import platform

from __base__ import WINDOW_TITLE, VERSION_FILE
from visualizing import MainWindow, MainApplication


def read_version(*paths, **kwargs):
    """
    Read the contents of a text file, e.g.,
    >>> read("VERSION")
    '0.0.0'
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def os_specific_adaptation():
    """
    Set the Python process as unique one instead of a general Python executable when Windows OS is used
    """
    if platform.system() == "Windows":
        import ctypes

        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(WINDOW_TITLE)


def main():
    """
    Main function
    """

    # Any and all operating system specific adaptation is done prior to running the app
    os_specific_adaptation()

    # Read version
    version = read_version(VERSION_FILE)
    print(f"App version: {version}")

    # Run main application
    MainApplication(WINDOW_TITLE, version)
