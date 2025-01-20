from PySide2.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QGridLayout, QHBoxLayout, QLabel,
                               QFrame, QScrollArea, QMessageBox, QLineEdit, QSizePolicy, QComboBox, QCompleter)
from PySide2.QtGui import QIcon, QFont, QPixmap
from PySide2.QtCore import Qt, QSize, QRegExp
from film_finder import log_film, read_data

FORMAT_ICONS = {
            'dvd': 'icons/dvd_logo.png',
            'bluray': 'icons/bluray_logo.png',
            '4k': 'icons/ultra_hd_bluray_logo.png'
        }


class Window(QWidget):
    def __init__(self, film_id, data, update_search_mode):
        super().__init__()

        # init data
        self.data = data
        self.film_id = film_id
        self.film_data = data[self.film_id]
        self.format = self.film_data['format']
        self.region = self.film_data['region']
        self.update_search_mode = update_search_mode

        # init buttons
        self.format_button = None
        self.region_button = None

        # init layout
        self.layout = QVBoxLayout()
        self.add_info()
        self.add_buttons()

        self.setLayout(self.layout)

    def add_info(self):
        # find film data for selected film
        film_data = self.film_data

        # if film has a tagline prepare it
        tagline = ''
        if len(film_data['tagline'])>0:
            tagline = f'\t{film_data["tagline"]}\n\n'

        # create the info text
        info_txt = f'''{tagline}
                Year: {film_data['year']}\n
                Directed By: {', '.join(film_data['directors'])}\n
                Written By: {', '.join(film_data['writers'])}\n
                Genre: {', '.join(film_data['genres'])} 
                '''

        info = QLabel(info_txt)

        title = f"{film_data['title']} - {film_data['year']}"
        self.setWindowTitle(title)
        self.layout.addWidget(info)

    def add_buttons(self):
        hbox = QHBoxLayout()

        self.format_button = QPushButton()
        self.change_format_icon(False)
        self.format_button.clicked.connect(lambda: self.change_format_icon(True))
        hbox.addWidget(self.format_button)

        region_button = QPushButton()
        region_icon = QIcon()
        region_icon.addPixmap(QPixmap('icons/ultra_hd_bluray_logo.png'))
        region_button.setIcon(region_icon)
        region_button.setIconSize(QSize(160, 90))
        hbox.addWidget(region_button)

        self.layout.addLayout(hbox)

    def change_format_icon(self, cycle=True):
        # init icon
        format_icon = QIcon()

        if cycle:
            # get next format option in the dict
            format_list = list(FORMAT_ICONS)
            index = format_list.index(self.format.lower())
            index = index + 1 if (index + 1) < len(format_list) else 0
            self.format = format_list[index]

            # update the format option to internal data in this window, main window, and json file
            data = read_data()[self.film_id]
            data = {self.film_id: data}
            data[self.film_id].update({'format': self.format})
            log_film(data)
            self.data[self.film_id].update({'format': self.format})
            # reinit the format text
            self.update_search_mode()

        # set format icon
        format_icon.addPixmap(QPixmap(FORMAT_ICONS[self.format.lower()]))
        self.format_button.setIcon(format_icon)
        self.format_button.setIconSize(QSize(160, 90))


