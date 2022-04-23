"""
Creates GUI for the visualization.
"""

import sys
import os

from PySide2.QtCore import Qt, QSize
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QTabWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QAction,
    QMenu,
    QMessageBox,
    QFileDialog,
)

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from handling import StockDataHandling, StockTimeFrame


class MainWindow(QMainWindow):
    """
    Main window controller class
    """

    def __init__(self, app, title=None, version=None, user_file=None):
        super().__init__()
        self._app = app
        self._sdh = StockDataHandling()
        self._main_widget = QWidget()
        self.setCentralWidget(self._main_widget)
        self._main_layout = QVBoxLayout(self._main_widget)

        # Perform variable initialization
        self._active_user_file = (
            user_file  # TODO: Add user file as a command line argument
        )
        self._icons = self._create_icon_dict()
        self._version = version

        # Perform setting up different widgets and actions
        self.setWindowIcon(self._icons["logo"])
        self._add_main_title(title)
        self._create_actions()
        self._create_menus()
        self._create_tabs()

        # Create main layout
        self._tabs = QTabWidget()
        self._tabs.addTab(self._config_tab, "Configuration")
        self._tabs.addTab(self._analyze_tab, "Analyze")
        self._main_layout.addWidget(self._tabs)

        # Sub-layouts
        self._config_tab_layout = QVBoxLayout(self._config_tab)
        self._analyze_tab_layout = QVBoxLayout(self._analyze_tab)

        # NOTE: Stock example
        stock_example = FigureCanvas(Figure())
        self._analyze_tab_layout.addWidget(stock_example)
        self._stock_example_plt = stock_example.figure.subplots()
        stock_df = self._sdh.get_yahoo_stock("SXR8.DE", StockTimeFrame.YTD)
        self._stock_example_plt.plot(stock_df.index, stock_df["Close"])

    def _add_main_title(self, title=""):
        self.setWindowTitle(title)

    def _create_tabs(self):
        # Create first tab contents
        self._config_tab = QWidget()

        # Create second tab contents
        self._analyze_tab = QWidget()

    def _create_actions(self):
        # TODO: Add icons
        self._exit_act = QAction(
            "E&xit",
            self,
            statusTip="Exit application",
            triggered=self.close,
        )

        self._open_act = QAction(
            "&Open",
            self,
            statusTip=" ",
            triggered=self._open_event,
        )

        self._about_act = QAction(
            "&About", self, statusTip=" ", triggered=self._about_event
        )

    def _create_menus(self):
        # File menu
        self._file_menu = self.menuBar().addMenu("&File")
        self._file_menu.addAction(self._open_act)
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._exit_act)
        self._file_menu.setLayoutDirection(Qt.LeftToRight)

        self.menuBar().addSeparator()

        # Settings menu
        self._settings_menu = self.menuBar().addMenu("Settings")
        self._settings_menu.setLayoutDirection(Qt.LeftToRight)

        self.menuBar().addSeparator()

        # Help menu
        self._help_menu = self.menuBar().addMenu("Help")
        self._help_menu.setLayoutDirection(Qt.LeftToRight)
        self._help_menu.addAction(self._about_act)

    def _create_icon_dict(self):
        # Assets are located in this directory
        asset_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "assets")

        logo = QIcon(os.path.join(asset_dir, "logo512.png"))

        icons = {
            "logo": logo,
        }

        return icons

    def _open_event(self):
        file_name, _ = QFileDialog.getOpenFileName(self)
        if file_name:
            self.active_user_file = file_name

    def _about_event(self):
        main_window_title = self.windowTitle()

        popup_title = "About"
        popup_body = f"""
            <b>{main_window_title}</b> is a tool for evaluating stock data.
            """

        if self._version is not None:
            version_body = f"""
                <br><br><i>Software version {self._version}</i>
                """
            popup_body += version_body

        QMessageBox.about(
            self,
            popup_title,
            popup_body,
        )

    def closeEvent(self, event):
        """
        Closing event that works for the default exit button and the custom ones
        """
        popup = QMessageBox()
        title = self.windowTitle()
        reply = popup.question(
            self,
            title,
            "Are you sure you want to quit?",
            popup.Yes,
            popup.No,
        )
        if reply == popup.Yes:
            event.accept()
        else:
            event.ignore()


class MainApplication:
    """
    Create base functionality, main window, and show it on fullscreen
    """

    def __init__(self, title=None, version=None, x=None, y=None):
        app = QApplication(sys.argv)
        main_window = MainWindow(app, title, version)

        if x == None or y == None:
            main_window.showMaximized()
        else:
            main_window.resize(x, y)
            main_window.show()

        # Return whatever the base application gives on return
        sys.exit(app.exec_())
