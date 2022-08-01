import sys
from socket import socket
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from constant import BOARD_SIZE, Action

gridBtnStyle = """
    QPushButton {
        background-color : white;
        border: 1px solid black;
    }
"""
gridBtnStyleClicked = """
    QPushButton {
        background-color : yellow;
        border: 1px solid black;
    }
"""


# PyQt5 GUI based on https://realpython.com/python-pyqt-gui-calculator
class GUI(QMainWindow):
    """Create a subclass of QMainWindow to setup the GUI"""

    def __init__(self, player: Optional[socket] = None):
        """View initializer"""
        super().__init__()
        # Set main window properties
        self.setWindowTitle("Deny and Conquer")
        # Set the central widget and general layout
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        # Create the display and the grid of buttons
        self._createDisplay()
        self._createButtons()
        self.player = player

    def _createDisplay(self):
        """Create the display"""
        # Create the display widget
        self.display = QLabel(text="none clicked yet")
        # Set display properties
        self.display.setAlignment(Qt.AlignRight)
        # Add the display to the general layout
        self.generalLayout.addWidget(self.display)

    def _createButtons(self):
        """Create the buttons"""

        buttonsLayout = QGridLayout()
        buttonsLayout.setSpacing(5)

        # Create buttons and add them to the grid layout
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                btn = QPushButton(text=f"{row},{col}")
                btn.setFixedSize(60, 60)
                btn.setStyleSheet(gridBtnStyle)
                buttonsLayout.addWidget(btn, row, col)

                # Setup pressed (mouseDown) and released (mouseUp) events
                # Note: setupMouseEvents creates a closure on btn, row, col (so that b, r, c are local vars)
                def setupMouseEvents(b, r, c):
                    btn.pressed.connect(lambda: self.onButtonPressed(b, r, c))
                    btn.released.connect(lambda: self.onButtonReleased(b, r, c))

                setupMouseEvents(btn, row, col)

        # Add buttonsLayout to the general layout
        self.generalLayout.addLayout(buttonsLayout)

    def onButtonPressed(self, btn: QPushButton, row: int, col: int):
        self.setDisplayText(f"{row},{col} pressed")
        if self.player is None: 
            btn.setStyleSheet(gridBtnStyleClicked)
            return
        self.player.send(f"{Action.CHOOSE} {row} {col}".encode("utf-8"))

    def onButtonReleased(self, btn: QPushButton, row: int, col: int):
        self.setDisplayText(f"{row},{col} released")
        if self.player is None: return
        self.player.send(f"{Action.RELEASE} {row} {col}".encode("utf-8"))

    def setDisplayText(self, text):
        self.display.setText(text)


def run():
    # Create an instance of QApplication
    app = QApplication(sys.argv)
    # Show the GUI
    view = GUI()
    view.show()
    # Execute the app's main loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
