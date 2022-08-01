# PyQt5 GUI based on https://realpython.com/python-pyqt-gui-calculator

import sys

from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout

nrows = 8
ncols = 8
gridBtnStyle = '''
    QPushButton {
        background-color : white;
        border: 1px solid black;
    }
'''
gridBtnStyleClicked = '''
    QPushButton {
        background-color : yellow;
        border: 1px solid black;
    }
'''


class GUI(QMainWindow):

    """Create a subclass of QMainWindow to setup the GUI"""

    def __init__(self):
        """View initializer"""
        super().__init__()
        # Set main window properties
        self.setWindowTitle('Deny and Conquer')
        # Set the central widget and general layout
        self.generalLayout = QVBoxLayout()
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)
        # Create the display and the grid of buttons
        self._createDisplay()
        self._createButtons()

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
        buttonsLayout.setSpacing(10)

        # Create buttons and add them to the grid layout
        for row in range(nrows):
            for col in range(ncols):
                btn = QPushButton(text=f'{row},{col}')
                btn.setFixedSize(60, 60)
                btn.setStyleSheet(gridBtnStyle)
                buttonsLayout.addWidget(btn, row, col)

                # Setup pressed (mouseDown) and released (mouseUp) events
                # Note: setupMouseEvents creates a closure on btn, row, col (so that b, r, c are local vars)
                def setupMouseEvents(b, r, c):
                    btn.pressed.connect(
                        lambda: self.onButtonPressed(b, r, c))
                    btn.released.connect(
                        lambda: self.onButtonReleased(b, r, c))
                setupMouseEvents(btn, row, col)

        # Add buttonsLayout to the general layout
        self.generalLayout.addLayout(buttonsLayout)


    def onButtonPressed(self, btn: QPushButton, row: int, col: int):
        self.setDisplayText(f'{row},{col} pressed')
        btn.setStyleSheet(gridBtnStyleClicked)

    def onButtonReleased(self, btn: QPushButton, row: int, col: int):
        self.setDisplayText(f'{row},{col} released')


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


if __name__ == '__main__':
    run()
