"""
Creates GUI for the visualization.
"""

import sys
import os
import pandas as pd
import qdarktheme

from PySide2.QtCore import Qt, QSize, QEvent
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QHBoxLayout,
    QAction,
    QMessageBox,
    QFileDialog,
    QSizePolicy,
    QInputDialog,
    QDialog,
    QGroupBox,
    QWhatsThis,
    QCheckBox,
    QLabel,
)


from matplotlib.figure import Figure
from matplotlib.backends.qt_compat import QtWidgets
from matplotlib.backends.backend_qtagg import (
    FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)

from handling import StockDataHandling, StockTimeFrame, get_stock_validity


class CustomListItem(QWidget):
    def __init__(self, text, active=True):
        super().__init__()

        layout = QHBoxLayout(self)

        self.checkbox = QCheckBox()
        self.checkbox.setChecked(active)
        self.checkbox.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.text = QTextEdit(text)
        self.text.setFixedSize(128, 24)
        self.text.setReadOnly(True)
        self.text.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.text.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

        self.remove_button = QPushButton("Remove")
        self.remove_button.setFixedSize(96, 24)
        self.remove_button.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
        self.remove_button.clicked.connect(self.remove_item)

        layout.addWidget(self.checkbox)
        layout.addWidget(self.text)
        layout.addWidget(self.remove_button)
        layout.addStretch()

    def is_checked(self):
        return self.checkbox.isChecked()

    def get_text(self):
        return self.text.toPlainText()

    def remove_item(self):
        self.setParent(None)


class CustomList(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.header_layout = QVBoxLayout()
        self.list_layout = QVBoxLayout()

        self.layout.addLayout(self.header_layout)
        self.layout.addLayout(self.list_layout)
        self.layout.addStretch()

        self._create_header()

    def _create_header(self):
        layout = QHBoxLayout()

        active = QLabel("<u>A</u>ctive")
        active.setFixedWidth(60)
        symbol = QLabel("<u>S</u>tock symbol")

        layout.addWidget(active)
        layout.addWidget(symbol)
        layout.addStretch()
        self.header_layout.addLayout(layout)

    def add_item(self, text):
        new_item = CustomListItem(text=text)
        self.list_layout.addWidget(new_item)

    def get_items(self):
        items = []
        for i in range(self.list_layout.count()):
            item = self.list_layout.itemAt(i).widget()
            items.append(item)
        return items

    def get_item_names(self):
        items = []
        for i in range(self.list_layout.count()):
            item = self.list_layout.itemAt(i).widget().get_text()
            items.append(item)
        return items


class InfoPopup:
    """
    Info/about popup controller
    """

    def __init__(self, parent, title, text):
        QMessageBox.about(
            parent,
            title,
            text,
        )


class GraphPopup(QDialog):
    """
    Graph popup controller
    """

    def __init__(self, parent, name, graph, toolbar, x=900, y=600):
        super().__init__(parent)
        self.resize(x, y)
        self.setWindowTitle(name)
        self.popup_layout = QVBoxLayout(self)
        self.popup_layout.addWidget(toolbar)
        self.popup_layout.addWidget(graph)

    def event(self, event):
        if event.type() == QEvent.EnterWhatsThisMode:
            QWhatsThis.leaveWhatsThisMode()
            InfoPopup(
                self, "Info", "A graph based on your selection of configuration values."
            )
            return True
        else:
            return QDialog.event(self, event)


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

        # Set dark theme
        self._app.setStyleSheet(qdarktheme.load_stylesheet("dark"))

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

        # Group boxes
        self._actions_group = QGroupBox("Actions", self)
        self._config_group = QGroupBox("Stock configuration", self)

        # Group box layouts
        self._actions_group_layout = QHBoxLayout(self._actions_group)
        self._config_group_layout = QVBoxLayout(self._config_group)

        self._main_layout.addWidget(self._actions_group)
        self._main_layout.addSpacing(6)
        self._main_layout.addWidget(self._config_group)

        self._set_stylesheets()

        # Actions
        self._add_stock_button = QPushButton("Add", self)
        self._add_stock_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._add_stock_button.resize(32, 32)
        self._add_stock_button.clicked.connect(self._create_stock_entry)

        self._analyze_button = QPushButton("Draw", self)
        self._analyze_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._analyze_button.resize(32, 32)
        self._analyze_button.clicked.connect(self._draw_graphs)

        self._actions_group_layout.addStretch()
        self._actions_group_layout.addWidget(self._add_stock_button)
        self._actions_group_layout.addWidget(self._analyze_button)
        self._actions_group_layout.addStretch()

        # Configuration
        self._custom_list_widget = CustomList(self)
        self._init_stock_list(pre_config_stocks)

        self._config_group_layout.addWidget(self._custom_list_widget)
        self._config_group_layout.addStretch()

    def _set_stylesheets(self):
        self._main_widget.setStyleSheet(
            """QGroupBox {
            border: 1px solid gray;
            border-radius: 6px;
            margin-top: 0.5em;
            }

            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px 0 3px;
            }
            """
        )

    def _init_stock_list(self, stocks):
        if stocks:
            for stock in stocks:
                self._custom_list_widget.add_item(stock)

    def _draw_graphs(self):
        # Get list of stock tickers
        sought_stocks = [
            stock.get_text()
            for stock in self._custom_list_widget.get_items()
            if stock.is_checked()
        ]

        if len(sought_stocks) == 0:
            InfoPopup(self, "Note", "One or more stocks have to be added!")
        elif len(sought_stocks) > 16:
            InfoPopup(
                self,
                "Note",
                "Maximum amount of analyzed stocks is <b>16</b>, please reduce the number of stocks active in your stock configuration.",
            )
        else:
            # Create the graph based on selection and create toolbar accordingly
            graph = self._create_analyze_graphs(sought_stocks)
            toolbar = NavigationToolbar(graph, self)
            toolbar.setStyleSheet("font-size: 12px;")
            graph_popup = GraphPopup(self, self.windowTitle(), graph, toolbar)
            graph_popup.show()

    def _create_analyze_graphs(
        self, sought_stocks=None, timeframe=StockTimeFrame.YTD, normalized=None
    ):
        if sought_stocks:
            fig = Figure(facecolor="#202124")
            plt = fig.add_subplot(1, 1, 1)
            canvas = FigureCanvas(fig)

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
                    plt.plot(stock.index, stock["Close"])
                except KeyError:
                    pass

            # Set colors and texts for the figure
            plt.legend(
                sought_stocks,
                loc="best",
                labelcolor="white",
                shadow=True,
                facecolor="#3F4042",
            )

            plt.set_facecolor("#3F4042")
            plt.set_title("Stock development during chosen time frame", color="white")
            plt.set_xlabel("Date")
            plt.set_ylabel("Stock value $")
            plt.xaxis.label.set_color("white")
            plt.yaxis.label.set_color("white")
            plt.tick_params(axis="x", colors="white")
            plt.tick_params(axis="y", colors="white")

            # Show grid lines
            plt.grid(axis="both", color="gray", linestyle="-")

            # Hide every second xtick label for readability
            for n, label in enumerate(plt.xaxis.get_ticklabels()):
                if n % 2 != 0:
                    label.set_visible(False)

            return canvas

    def _create_stock_entry(self):
        self._stock_input_popup, status = QInputDialog.getText(
            self, "Question", "Stock symbol"
        )

        stock_input = str(self._stock_input_popup).upper()

        if stock_input in self._custom_list_widget.get_item_names():
            InfoPopup(
                self,
                "Note",
                f"The stock symbol '<b>{stock_input}</b>' you're trying to add has been already added!",
            )
            return

        if get_stock_validity(stock_input):
            self._custom_list_widget.add_item(stock_input)
        else:
            InfoPopup(
                self,
                "Note",
                "The stock symbol you're trying to add is not a valid stock symbol!",
            )

    def _remove_active_stock_entry(self):
        pass

    def _add_main_title(self, title=""):
        self.setWindowTitle(title)

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

        InfoPopup(self, popup_title, popup_body)

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
                stock.get_text()
                for stock in self._custom_list_widget.get_items()
                if stock.is_checked()
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

        main_window.resize(x, y)
        main_window.show()

        # Return whatever the base application gives on return
        sys.exit(app.exec_())
