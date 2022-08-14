import sys
from socket import socket
from typing import List

from PyQt5.QtCore import Qt, QThread, QTimer, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from constant import BOARD_SIZE, TIME_TO_HOLD, Action, getColor, getLabel
from game import Player

# Global style for all buttons
style = """
    QPushButton {
        border: 1px solid black;
        background-color : white;
    }
"""


class StyledButton:
    def __init__(self, button: QPushButton):
        self.button = button
        self.border = -1
        self.background = -1

    def setBorder(self, border: int):
        self.border = border

    def setBackground(self, background: int):
        self.background = background

    def applyStyle(self):
        borderStyle = (
            "" if self.border < 0 else f"border: 5px solid {getColor(self.border)};"
        )
        self.button.setStyleSheet(
            f"{borderStyle}" f"background-color: {getColor(self.background)};"
        )


# PyQt5 GUI based on https://realpython.com/python-pyqt-gui-calculator
class GUI(QMainWindow):
    """Create a subclass of QMainWindow to setup the GUI"""

    def __init__(self, player: Player):
        """View initializer"""
        super().__init__()
        # Set up the player
        self.player = player

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
        self.setStyleSheet(style)

        # UI Thread
        self.uiThread = UIThread(player.socket)
        self.uiThread.signaler.connect(self.handleAction)

        # Timer thread
        self.timer: QTimer()

    def _createDisplay(self):
        """Create the display"""
        # Create the display widget
        label = QLabel(text=f"You are playing as {getLabel(self.player.id)}")
        # Set display properties
        label.setAlignment(Qt.AlignLeft)
        # Add the display to the general layout
        self.generalLayout.addWidget(label)

    def _createButtons(self):
        """Create the buttons"""
        self.buttonGrid: List[List[StyledButton]] = []
        buttonsLayout = QGridLayout()
        buttonsLayout.setSpacing(5)

        # Create buttons and add them to the grid layout
        for row in range(BOARD_SIZE):
            buttonRow = []
            for col in range(BOARD_SIZE):
                btn = QPushButton()
                btn.setFixedSize(60, 60)
                buttonsLayout.addWidget(btn, row, col)
                buttonRow.append(StyledButton(btn))

                # Setup pressed (mouseDown) and released (mouseUp) events
                # Note: setupMouseEvents creates a closure on btn, row, col (so that b, r, c are local vars)
                def setupMouseEvents(b, r, c):
                    btn.pressed.connect(lambda: self.onButtonPressed(b, r, c))
                    btn.released.connect(lambda: self.onButtonReleased(b, r, c))

                setupMouseEvents(btn, row, col)
            self.buttonGrid.append(buttonRow)

        # Add buttonsLayout to the general layout
        self.generalLayout.addLayout(buttonsLayout)

    def onButtonPressed(self, _: QPushButton, row: int, col: int):
        command = f"{Action.HOLD} {row} {col}|"
        self.player.socket.send(command.encode("ascii"))

        # Start the timer
        self.timer = QTimer()
        self.timer.setSingleShot(True)

        def callback():
            self.player.socket.send(f"{Action.CLAIM} {row} {col}|".encode("ascii"))

        self.timer.timeout.connect(callback)
        self.timer.start(TIME_TO_HOLD)

    def onButtonReleased(self, _: QPushButton, row: int, col: int):
        remaining = self.timer.remainingTime()
        self.timer.stop()
        if remaining > 0:
            self.player.socket.send(f"{Action.RELEASE} {row} {col}|".encode("ascii"))

    def handleAction(self, action: str, row: int, col: int, playerId: int):
        button = self.buttonGrid[row][col]
        if action == Action.CLAIM:
            button.setBorder(-1)
            button.setBackground(playerId)
        elif action == Action.HOLD:
            button.setBorder(playerId)
        elif action == Action.RELEASE:
            button.setBorder(-1)
        elif action == Action.WIN:
            if playerId != -1:
                text = f"Game ended: {getColor(playerId)} wins"
            else:
                text = "Game ended: it's a tie"
            label = QLabel(text=text)
            label.setAlignment(Qt.AlignCenter)
            self.generalLayout.addWidget(label)
        button.applyStyle()


# A thread for listening the incoming command from the server
# and emitting events to the main thread to update the UI
class UIThread(QThread):
    signaler = pyqtSignal(str, int, int, int)

    def __init__(self, client: socket):
        super().__init__()
        self.client = client

    def run(self):
        while True:
            try:
                commands = self.client.recv(1024).decode("ascii").strip('|').split('|')
                for command in commands:
                    print(command)
                    tokens = command.split(" ")
                    if len(tokens) == 4:
                        action, *rest = tokens
                        row, col, playerId = [int(v) for v in rest]
                        self.signaler.emit(action, row, col, playerId)
                    elif len(tokens) == 2: # handle action "win playerId"
                        action, *rest = tokens
                        playerId = [int(v) for v in rest][0]
                        self.signaler.emit(action, 0, 0, playerId)
                    else:       
                        print("Invalid command", command)
                        continue
                
            except Exception as e:
                print(f"Error!: {e}")
                self.client.close()
                break


def run(player: socket):
    # Create an instance of QApplication
    app = QApplication(sys.argv)
    # Show the GUI
    view = GUI(player)
    view.show()

    # Start the UI thread
    view.uiThread.start()

    # Execute the app's main loop
    sys.exit(app.exec_())
