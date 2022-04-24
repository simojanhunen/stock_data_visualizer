"""
Creates GUI for the visualization.
"""

import sys
import os
import pandas as pd

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
    QHBoxLayout,
    QAction,
    QMenu,
    QMessageBox,
    QFileDialog,
    QListWidget,
    QSizePolicy,
    QInputDialog,
)

from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

from handling import StockDataHandling, StockTimeFrame


class MainWindow(QMainWindow):
    """
    Main window controller class
    """

    def __init__(self, app, title=None, version=None, user_config_file=None):
        super().__init__()
        self._app = app
        self._sdh = StockDataHandling()
        self._main_widget = QWidget()
        self.setCentralWidget(self._main_widget)
        self._main_layout = QVBoxLayout(self._main_widget)

        # Perform variable initialization
        self._active_user_file = user_config_file
        pre_config_stocks = self._check_user_config()
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

        # Stock configuration
        self._config_tab_top_layout = QHBoxLayout()
        self._config_tab_layout.addLayout(self._config_tab_top_layout)

        self._add_stock_button = QPushButton("Add", self)
        self._add_stock_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._add_stock_button.resize(32, 32)
        self._add_stock_button.clicked.connect(self._create_stock_entry)
        self._config_tab_top_layout.addWidget(self._add_stock_button)

        self._stock_list = QListWidget(self)
        self._stock_list.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Ignored)
        self._stock_list.resize(512, 512)
        self._init_stock_list(pre_config_stocks)
        self._config_tab_layout.addWidget(self._stock_list)

        self._update_analyze_graphs()

    def _init_stock_list(self, stocks):
        if stocks:
            for stock in stocks:
                self._stock_list.addItem(stock)

    def _update_analyze_graphs(self, timeframe=StockTimeFrame.YTD, normalized=None):
        # Get list of stock tickers
        sought_stocks = [
            str(self._stock_list.item(index).text())
            for index in range(self._stock_list.count())
        ]

        if not sought_stocks:
            pass
        else:
            for i in reversed(range(self._analyze_tab_layout.count())):
                self._analyze_tab_layout.itemAt(i).widget().setParent(None)

            analyze_line_graph = FigureCanvas(Figure())
            self._analyze_line_graph_plt = analyze_line_graph.figure.subplots()

            # Get stock data from yahoo and concanate the data to one dataframe
            sought_stock_data = [
                self._sdh.get_yahoo_stock(ticker, timeframe) for ticker in sought_stocks
            ]
            stock_df = pd.concat(sought_stock_data, axis=1, keys=sought_stocks)

            # Normalize stock data if so desired
            if normalized:
                sought_stock_data = [
                    self._sdh.normalize_stock_data(stock) for stock in sought_stock_data
                ]

            for stock in sought_stock_data:
                try:
                    self._analyze_line_graph_plt.plot(stock.index, stock["Close"])
                except KeyError:
                    pass

            self._analyze_line_graph_plt.legend(sought_stocks, loc="best")
            self._analyze_tab_layout.addWidget(analyze_line_graph)

    def _create_stock_entry(self):
        self._stock_input_popup, status = QInputDialog.getText(
            self, "Question", "Stock symbol:"
        )
        self._stock_list.addItem(str(self._stock_input_popup))
        self._update_analyze_graphs()

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
            self._save_user_config()
            event.accept()
        else:
            event.ignore()

    def _check_user_config(self):
        if os.path.exists(self._active_user_file):
            with open(self._active_user_file, "r") as file:
                return [line.rstrip() for line in file]
        else:
            print("Config file doesn't exist!")
            return None

    def _save_user_config(self):
        try:
            stocks = [
                str(self._stock_list.item(index).text())
                for index in range(self._stock_list.count())
            ]
            with open(self._active_user_file, "w") as file:
                file.writelines("%s\n" % stock for stock in stocks)
        except IOError:
            pass


class MainApplication:
    """
    Create base functionality, main window, and show it on fullscreen
    """

    def __init__(self, title=None, version=None, user_config_file=None, x=None, y=None):
        app = QApplication(sys.argv)
        main_window = MainWindow(
            app=app, title=title, version=version, user_config_file=user_config_file
        )

        if x == None or y == None:
            main_window.showMaximized()
        else:
            main_window.resize(x, y)
            main_window.show()

        # Return whatever the base application gives on return
        sys.exit(app.exec_())
