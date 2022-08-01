import sys
from socket import socket
from threading import Thread
from typing import Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLabel, QMainWindow,
                             QPushButton, QVBoxLayout, QWidget)

from constant import BOARD_SIZE, Action, getColor

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


def getGridBtnStyle(color: str):
    return "QPushButton { background-color: " + color + "; border: 1px solid black; }"


# PyQt5 GUI based on https://realpython.com/python-pyqt-gui-calculator
class GUI(QMainWindow):
    """Create a subclass of QMainWindow to setup the GUI"""

    buttonGrid = []

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
            buttonRow = []
            for col in range(BOARD_SIZE):
                btn = QPushButton(text=f"{row},{col}")
                btn.setFixedSize(60, 60)
                btn.setStyleSheet(gridBtnStyle)
                buttonsLayout.addWidget(btn, row, col)
                buttonRow.append(btn)

                # Setup pressed (mouseDown) and released (mouseUp) events
                # Note: setupMouseEvents creates a closure on btn, row, col (so that b, r, c are local vars)
                def setupMouseEvents(b, r, c):
                    btn.pressed.connect(lambda: self.onButtonPressed(b, r, c))
                    btn.released.connect(lambda: self.onButtonReleased(b, r, c))

                setupMouseEvents(btn, row, col)
            self.buttonGrid.append(buttonRow)

        # Add buttonsLayout to the general layout
        self.generalLayout.addLayout(buttonsLayout)

    def onButtonPressed(self, btn: QPushButton, row: int, col: int):
        self.setDisplayText(f"{row},{col} pressed")
        if self.player is None:
            btn.setStyleSheet(gridBtnStyleClicked)
            return
        command = f"{Action.CHOOSE} {row} {col}"
        self.player.send(command.encode("ascii"))

    def onButtonReleased(self, btn: QPushButton, row: int, col: int):
        self.setDisplayText(f"{row},{col} released")

    def setDisplayText(self, text):
        self.display.setText(text)

    # Receive commands from the server
    # and update the UI accordingly
    def onReceive(self):
        while self.player:
            try:
                command = self.player.recv(1024).decode("ascii")
                print(command)
                action, *rest = command.split(" ")
                if action == Action.CLAIM:
                    row, col, playerId = [int(v) for v in rest]
                    self.buttonGrid[int(row)][int(col)].setStyleSheet(
                        getGridBtnStyle(getColor(playerId))
                    )
            except:
                print("Error!")
                self.player.close()
                break


def runWithoutPlayer():
    # Create an instance of QApplication
    app = QApplication(sys.argv)

    # Show the GUI
    view = GUI()
    view.show()

    # Execute the app's main loop
    sys.exit(app.exec_())


def runWithPlayer(player: socket):
    # Create an instance of QApplication
    app = QApplication(sys.argv)

    # Show the GUI
    view = GUI(player)
    view.show()

    # New thread to listen to server
    # and update the UI
    thread = Thread(target=view.onReceive)
    thread.start()

    # Execute the app's main loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    runWithoutPlayer()
