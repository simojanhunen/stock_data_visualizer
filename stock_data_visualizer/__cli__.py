"""
CLI interface for stock_data_visualizer project.
"""

import io
import os
import sys
import ctypes
import pathlib

from __base__ import WINDOW_TITLE, VERSION_FILE, CONFIG_FILE
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


def os_specific_adaptation() -> pathlib.Path:
    """
    Adapt to underlying operating system
    """
    # Get project user data directory
    home_dir = pathlib.Path.home()
    project_name = "stock_data_visualizer"
    platform_specific_home = ""

    if sys.platform == "win32":
        # Enables changing the taskbar icon in Windows environment
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(WINDOW_TITLE)

        platform_specific_home = home_dir / "AppData/Roaming"
    elif sys.platform == "linux":
        platform_specific_home = home_dir / ".local/share"
    elif sys.platform == "darwin":
        platform_specific_home = home_dir / "Library/Application Support"

    project_user_data_dir = platform_specific_home / project_name

    try:
        project_user_data_dir.mkdir(parents=True)
    except FileExistsError:
        pass

    return project_user_data_dir


def main():
    """
    Main function
    """

    # Any and all operating system specific adaptation is done prior to running the app
    user_data_dir = os_specific_adaptation()
    user_config_file = user_data_dir / CONFIG_FILE
    print(f"Config file: {user_config_file}")

    # Read version
    version = read_version(VERSION_FILE)
    print(f"App version: {version}")

    # Run main application
    MainApplication(
        title=WINDOW_TITLE,
        version=version,
        user_config_file=user_config_file,
        x=800,
        y=800,
    )
