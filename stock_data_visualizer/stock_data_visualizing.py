"""
Creates GUI for the visualization.
"""

import sys
from PySide2.QtCore import Qt
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


class MainWindow(QMainWindow):
    """
    Main window controller class
    """

    def __init__(self, app, title=None, user_file=None):
        super().__init__()
        self._main_widget = QWidget()
        self._app = app

        # Perform variable initialization
        # TODO: Add user file as a command line argument
        self._active_user_file = user_file

        # Perform setting up different widgets and actions
        # self._add_main_icon()
        self._add_main_title(title)
        self._create_actions()
        self._create_menus()
        self._create_tabs()

        layout = QVBoxLayout()
        layout.addWidget(self._tabs)

        self._main_widget.setLayout(layout)
        self.setCentralWidget(self._main_widget)

    # Private

    def _add_main_icon(self):
        # TODO: Add main icon
        raise NotImplementedError()

    def _add_main_title(self, title=""):
        self.setWindowTitle(title)

    def _create_tabs(self):
        self._tabs = QTabWidget()

        # Create first tab contents
        tab1_dummy = QTextEdit()
        tab1_dummy.setPlaceholderText("First tab contents")
        self._tabs.addTab(tab1_dummy, "Tab One Dummy")

        # Create second tab contents
        tab2_dummy = QTextEdit()
        tab2_dummy.setPlaceholderText("Second tab contents")
        self._tabs.addTab(tab2_dummy, "Tab Two Dummy")

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

    def _open_event(self):
        file_name, _ = QFileDialog.getOpenFileName(self)
        if file_name:
            self.active_user_file = file_name

    def _about_event(self):
        # TODO: Add icons
        main_window_title = self.windowTitle()

        popup_title = "About"
        popup_body = f"""
            <b>{main_window_title}</b> is a tool for evaluating stock data.
            """

        QMessageBox.about(
            self,
            popup_title,
            popup_body,
        )

    # Public

    def closeEvent(self, event):
        """
        Closing event that works for the default exit button and the custom ones
        """
        # TODO: Add icons
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
    """Create base functionality, main window, and show it on fullscreen"""

    def __init__(self, title=None, x=None, y=None):
        app = QApplication(sys.argv)
        main_window = MainWindow(app, title)

        if x == None or y == None:
            main_window.showMaximized()
        else:
            main_window.resize(x, y)
            main_window.show()

        # Return whatever the base application gives on return
        sys.exit(app.exec_())
