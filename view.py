import sys
from socket import socket
from threading import Thread
from typing import List, Optional

from PyQt5.QtCore import QRunnable, Qt, QThreadPool, pyqtSlot
from PyQt5.QtWidgets import (QApplication, QGridLayout, QLabel, QMainWindow,
                             QPushButton, QVBoxLayout, QWidget)

from constant import BOARD_SIZE, Action, getColor

style = """
    QPushButton {
        border: 1px solid black;
        background-color : white;
    }
"""

# PyQt5 GUI based on https://realpython.com/python-pyqt-gui-calculator
# Multithreading on PyQt5 on https://www.pythonguis.com/tutorials/multithreading-pyqt-applications-qthreadpool/
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
        self.setStyleSheet(style)
        # Threading
        self.player = player
        self.threadPool = QThreadPool()

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
        self.buttonGrid: List[List[QPushButton]] = []
        buttonsLayout = QGridLayout()
        buttonsLayout.setSpacing(5)

        # Create buttons and add them to the grid layout
        for row in range(BOARD_SIZE):
            buttonRow = []
            for col in range(BOARD_SIZE):
                btn = QPushButton(text=f"{row},{col}")
                btn.setFixedSize(60, 60)
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
            btn.setStyleSheet("background-color: yellow")
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
                    button = self.buttonGrid[row][col]
                    button.setStyleSheet(f"background-color: {getColor(playerId)}")
            except:
                print("Error!")
                self.player.close()
                break
    
    def show(self) -> None:
        super().show()
        if self.player:
            uiWorker = UIWorker(self)
            self.threadPool.start(uiWorker)

# A worker for updating the UI upon incoming commands from server
class UIWorker(QRunnable):
    def __init__(self, gui: GUI):
        super(UIWorker, self).__init__()
        self.gui = gui

    @pyqtSlot()
    def run(self):
        return self.gui.onReceive()

def run(player: Optional[socket] = None):
    # Create an instance of QApplication
    app = QApplication(sys.argv)
    # Show the GUI
    view = GUI(player)
    view.show()
    # Execute the app's main loop
    sys.exit(app.exec_())

if __name__ == "__main__":
    run()
