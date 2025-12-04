from film_finder_gui import Window as Search_gui
from film_viewer_gui import Window as Viewer_gui
from pre_launch import pre_launch_main
from PySide2.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QProgressDialog
import sys
import time

class Window(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Film Tracker')
        self.setGeometry(1000, 400, 400, 100)

        # init launched application
        self.app = None

        self.layout = QHBoxLayout()
        self.add_push_buttons()
        self.setLayout(self.layout)

    def add_push_buttons(self):
        # creates push buttons to launch film finder and library viewer
        finder_button = QPushButton('Launch Film Finder')
        finder_button.clicked.connect(self.launch_film_finder)
        self.layout.addWidget(finder_button)

        viewer_button = QPushButton('Launch Library Viewer')
        viewer_button.clicked.connect(self.launch_library_viewer)
        self.layout.addWidget(viewer_button)

    def launch_film_finder(self):
        # launches the film finder window
        # TODO: Combine these methods into one? Might not be necessary.
        if self.app:
            self.app.close()
        self.app = Search_gui()
        self.app.show()

    def launch_library_viewer(self):
        # launches the library viewer window
        if self.app:
            self.app.close()
        progress = QProgressDialog('Loading film data...', None, 0, 98)
        progress.setFixedSize(300, 100)
        progress.show()
        self.app = Viewer_gui(progress)
        progress.canceled.connect(self.app.close)
        self.app.show()


pre_launch_main()
myapp = QApplication(sys.argv)
with open("style_default.qss", "r") as f:
    style_sheet = f.read()
    myapp.setStyleSheet(style_sheet)

window = Window()
window.show()

myapp.exec_()
sys.exit()
