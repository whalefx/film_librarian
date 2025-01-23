from PySide2.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QGridLayout, QHBoxLayout, QLabel,
                               QFrame, QScrollArea, QMessageBox, QLineEdit, QSizePolicy, QComboBox, QCompleter, QBoxLayout)
from PySide2.QtGui import QIcon, QFont, QPixmap
from PySide2.QtCore import Qt, QSize, QRegExp
from film_finder import log_film, read_data
from textwrap import fill

FORMAT_ICONS = {
            'dvd': 'icons/dvd_logo.png',
            'bluray': 'icons/bluray_logo.png',
            '4k': 'icons/ultra_hd_bluray_logo.png'
        }

FORMAT_OPTIONS = {
    'dvd': (1, 2),
    'bluray': ('A', 'B'),
    '4k': (None,)
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
        self.locked = True

        # init buttons
        self.format_button = None
        self.region_button = None
        self.lock_button = None

        # init layout
        self.layout = QVBoxLayout()
        self.add_lock()
        self.add_info()
        self.add_buttons()

        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignCenter)

        self.setMaximumSize(QSize(self.size()))

    def add_lock(self):
        layout = QHBoxLayout()
        # create lock button
        self.lock_button = QPushButton()
        self.lock_button.clicked.connect(self.lock_changes)
        self.lock_button.setFlat(True)
        self.lock_button.setFixedSize(QSize(25, 25))

        layout.addWidget(self.lock_button)
        layout.setAlignment(self.lock_button, (Qt.AlignLeft | Qt.AlignTop))

        self.lock_changes(init=True)

        self.layout.addLayout(layout)

    def add_info(self):
        def wrap(text, label=None):
            data = film_data[text]

            if isinstance(data, list):
                data = ', '.join(data)
            else:
                data = str(data)

            _text = fill(data, 60, subsequent_indent='\t\t')

            if label:
                _text = f'{label:.>30}{_text}'
            return _text

        # find film data for selected film
        film_data = self.film_data

        # if film has a tagline prepare it
        tagline = ''
        if len(film_data['tagline']) > 0:
            tagline = f'\t{wrap("tagline")}\n\n'

        # create the info text
        info_txt = f'''{tagline}
                Year: {film_data["year"]}\n
                Directed By: {wrap("directors")}\n
                Written By: {wrap("writers")}\n
                Genre: {wrap("genres")} 
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
        self.format_button.setFlat(True)
        hbox.addWidget(self.format_button)

        self.region_button = QPushButton()
        self.change_region_icon(False)
        self.region_button.clicked.connect(lambda: self.change_region_icon(True))
        self.region_button.setFlat(True)
        hbox.addWidget(self.region_button)

        self.layout.addLayout(hbox)

    def change_format_icon(self, cycle=True):

        # init icon
        format_icon = QIcon()

        if cycle and not self.locked:
            # get next format option in the dict
            format_list = list(FORMAT_ICONS)
            index = format_list.index(self.format.lower())
            index = index + 1 if (index + 1) < len(format_list) else 0
            self.format = format_list[index]

            # update the format option to internal data in this window, main window, and json file
            data = read_data()[self.film_id]
            data = {self.film_id: data}

            self.region = FORMAT_OPTIONS[self.format][0]

            updated_data = {'format': self.format, 'region': self.region}

            data[self.film_id].update(updated_data)
            log_film(data)
            self.data[self.film_id].update(updated_data)

            # reinit the format text
            self.update_search_mode()
            self.change_region_icon(False)

        # set format icon
        format_icon.addPixmap(QPixmap(FORMAT_ICONS[self.format.lower()]))
        self.format_button.setIcon(format_icon)
        self.format_button.setIconSize(QSize(160, 90))

    def change_region_icon(self, cycle):
        # init icon
        region_icon = QIcon()

        region_options = FORMAT_OPTIONS[self.format]

        if cycle and not self.locked:
            index = region_options.index(self.region)
            index = index + 1 if (index + 1) < len(region_options) else 0

            self.region = region_options[index]

            # update the region information to internal data in this window, main window, and json file
            data = read_data()[self.film_id]
            data = {self.film_id: data}

            updated_data = {'region': self.region}

            data[self.film_id].update(updated_data)
            log_film(data)
            self.data[self.film_id].update(updated_data)

            # reinit the format text
            self.update_search_mode()

        if self.format == 'dvd':
            image = f'icons/dvd_region{self.region}.png'
        elif self.format == 'bluray':
            image = f'icons/bluray_region{self.region}.png'
        elif self.format == '4k':
            image = f'icons/4k_regionfree.png'

        # set region icon
        region_icon.addPixmap(QPixmap(image))
        self.region_button.setIcon(region_icon)
        self.region_button.setIconSize(QSize(160, 90))

    def lock_changes(self, init=False):
        if not init:
            self.locked = not self.locked

        icon = QIcon()

        if self.locked:
            icon.addPixmap(QPixmap('icons/locked.png'))
        else:
            icon.addPixmap(QPixmap('icons/unlocked.png'))

        self.lock_button.setIcon(icon)
        self.lock_button.setIconSize(QSize(15, 15))

