from PySide2.QtWidgets import (QApplication, QWidget, QVBoxLayout, QPushButton, QGridLayout, QHBoxLayout, QLabel,
                               QFrame, QScrollArea, QMessageBox, QLineEdit, QSizePolicy, QComboBox, QCompleter)
from PySide2.QtGui import QIcon, QFont, QPixmap
from PySide2.QtCore import Qt, QSize, QRegExp
from film_finder import read_data
from functools import partial
from thefuzz import fuzz, process
import urllib
import os
from textwrap import fill
import re
from pre_launch import pre_launch_viewer


class Window(QWidget):
    def __init__(self):
        super().__init__()

        # init window settings
        self.setWindowTitle('Film Library')
        self.setGeometry(100, 50, 1200, 800)
        self.grid_amount = 3
        self.scale = 0.15

        # init button settings
        self.wrapper = None
        self.search_bar = None
        self.search_menu = None
        self.groupBox = None
        self.grid_layout = None
        self.tokens = {'Title': 'title', 'Director': 'directors', 'Genre': 'genres', 'Year': 'year', 'Actors': 'actors',
                       'Characters': 'characters', 'Writer': 'writers', 'Country': 'country', 'Keywords': 'keywords'}
        self.grid_alignment = (Qt.AlignLeft | Qt.AlignTop)

        # init data
        self.data = read_data()
        self.search_results = self.data
        self.searching = False
        self._grid = None
        self.search_mode = 'Title'
        self.keywords = pre_launch_viewer()

        # create layout
        self.layout = QVBoxLayout()
        self.create_search_bar()
        self.create_grid_layout(self.data)
        self.layout.addLayout(self.create_search_bar())
        self.layout.addWidget(self.groupBox)
        self.setLayout(self.layout)
        self.movies = self.wrapper.findChildren(QFrame, QRegExp('film_.+'))

    def _add_films_to_grid(self, film_data):
        """
        Creates a QFrame containing an image and label for each film in the library

        :param film_data:
            The data from the json file containing the library

        :return:
            None
        """

        # TODO: should this be merged with the create_grid_layout method?
        # make posters folder if it doesn't already exist
        _dir = os.path.dirname(os.path.abspath(__file__))
        poster_folder = os.path.join(_dir, 'posters')
        if not os.path.isdir(poster_folder):
            os.mkdir(poster_folder)

        for i, (k, v) in enumerate(film_data.items()):
            frame = QFrame(self.groupBox)
            vbox = QVBoxLayout()

            # check if poster is saved, use poster on disk for pixmap
            poster_file = os.path.join(poster_folder, f'{k}.png')
            if not os.path.isfile(poster_file):
                # save poster to disk
                url = v['poster']
                img_data = urllib.request.urlopen(url).read()
                with open(poster_file, 'wb') as handler:
                    handler.write(img_data)
            pixmap = QPixmap()
            pixmap.load(poster_file)

            # setup poster button
            poster_button = QPushButton(QIcon(pixmap), '')
            poster_button.setFlat(True)
            poster_button.setIconSize(QSize(int(2000 * self.scale), int(3000 * self.scale)))

            # connect buttons to method, using the partial method to link each button individually
            poster_button.clicked.connect(partial(self.show_film_info, film_id=k))

            vbox.addWidget(poster_button)

            # setup text
            film = QLabel(v['title'])
            film.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
            film.setFont(QFont('Sanserif', 13))
            vbox.addWidget(film)

            # add additional info
            info = QLabel('info')
            info.setAlignment(Qt.AlignHCenter | Qt.AlignBottom)
            info.setFont(QFont('Sanserif', 11))
            info.setObjectName('info')
            info.hide()
            vbox.addWidget(info)

            # setup frame
            frame.setLayout(vbox)
            frame.setFrameShape(QFrame.Panel)
            frame.setFrameShadow(QFrame.Raised)
            frame.setObjectName(k)

            # set horizontal and vertical position on the grid, add this to the dictionary for later
            horizontal = i % self.grid_amount
            vertical = i / self.grid_amount
            self.grid_layout.addWidget(frame, vertical, horizontal, alignment=self.grid_alignment)
            v['orig_pos'] = (vertical, horizontal)
            frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def create_search_bar(self):
        """
        Creates a search bar and menu containing the search types

        :return:
            The hbox containing the search bar and menu
        """
        hbox = QHBoxLayout()
        # create search bar
        self.search_bar = QLineEdit('')
        self.search_bar.textChanged.connect(self.search)

        # create search menu with an item for each entry in the self.token dict
        self.search_menu = QComboBox()
        for x in self.tokens.keys():
            self.search_menu.addItem(x)
        # call the update_search_mode method whenever the search menu is changed
        self.search_menu.currentTextChanged.connect(self.update_search_mode)

        # add widgets to the hbox
        hbox.addWidget(self.search_bar)
        hbox.addWidget(self.search_menu)

        return hbox

    def create_grid_layout(self, film_data):
        """
        Creates the grid layout for the films and the scroll bar

        :param film_data:
            The data from the json file containing the library

        :return:
        """
        self.groupBox = QFrame()

        # setup scrollbar
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.wrapper = QWidget(self.groupBox)
        scroll.setWidget(self.wrapper)
        self.layout.addWidget(scroll)

        # add grid layout to dummy wrapper
        self.grid_layout = QGridLayout(self.wrapper)

        # add films to the grid
        self._add_films_to_grid(film_data)

    def update_search_mode(self):
        """
        Updates the search mode based on the value of the search menu

        :return:
            None
        """

        # update search mode
        idx = self.search_menu.currentIndex()
        self.search_mode = self.search_menu.itemText(idx)
        self.search_bar.setText('')

        # update film text
        token = self.tokens[self.search_mode]

        for movie in self.movies:
            if token == 'actors' or token == 'characters':
                return
            else:
                info = self.data[movie.objectName()][token]
            if isinstance(info, list):
                info = ', '.join(info)
            else:
                info = str(info)

            # find the info label associated with this movie and set it
            info_box = movie.findChildren(QLabel, QRegExp('info'))[0]
            info_box.setText(info)

        # setup completer
        completer = QCompleter([''])
        if token == 'keywords':
            completer = QCompleter([x for x in self.keywords.keys()])
        self.search_bar.setCompleter(completer)

    def show_film_info(self, film_id):
        """
        Creates a message box containing information about the film

        :param film_id:
            The ID number associated with the selected film

        :return:
            None
        """

        # TODO: Have this pop up also contain further actions such as marking a film as seen

        # find film data for selected film
        film_data = self.data[film_id]

        # if film has a tagline prepare it
        tagline = ''
        if len(film_data['tagline'])>0:
            tagline = f'\t{film_data["tagline"]}\n\n'

        # create the info text
        info = f'''{tagline}
                Year: {film_data['year']}\n
                Directed By: {', '.join(film_data['directors'])}\n
                Written By: {', '.join(film_data['writers'])}\n
                Genre: {', '.join(film_data['genres'])} 
                '''

        # launch the message box
        QMessageBox.about(self, film_data['title'], info)

    def search(self):
        """
        Searches for the film based on the search text and search type

        :return:
            None
        """

        # init search attributes
        self.searching = True
        self.search_results = self.data
        text = self.search_bar.text()

        # grab the search token for the search mode
        token = self.tokens[self.search_mode]

        # deactivate if text is blank
        if len(text) == 0:
            self.searching = False
            for movie in self.movies:
                # reset position to initial position
                pos = self.data[movie.objectName()]['orig_pos']
                self.grid_layout.addWidget(movie, pos[0], pos[1], alignment=self.grid_alignment)
                # hide info box for all films
                movie.findChildren(QLabel, QRegExp('info'))[0].hide()
                movie.show()
            return

        # search for string results
        _search_results = {}

        # find which films match the search term, using the fuzzywuzzy library for better results on non-exact terms
        for k, v in self.search_results.items():
            search_dict = True
            tolerance = 50
            ratio = 0

            # get the relevant data to search based on the token
            if token == 'actors':
                film_data_to_search = list(v['actors'].keys())
            elif token == 'characters':
                film_data_to_search = list(v['actors'].values())
            elif token == 'keywords':
                film_data_to_search = v['keywords']
            else:
                film_data_to_search = v[token]
                search_dict = False

            str_text = str(text)
            if search_dict:
                # for dict searches get the matches and the ratio from the process.extract method
                tolerance = 80
                search = process.extract(str_text, film_data_to_search, limit=1000)
                matches = [x for x, r in search if r >= tolerance]

                if len(matches) == 0:
                    ratio = 0
                else:
                    ratio = max([r for x, r in search])
                    # if match found update the text box (the results are dynamic, so it has to be done at search time)
                    movie = [x for x in self.movies if x.objectName() == f'film_{v["id"]}'][0]
                    info = ', '.join(matches)
                    # using textwrap to make sure boxes with lots of info don't grow horizontally
                    info = fill(info, 48)

                    # find info box for this film
                    info_box = movie.findChildren(QLabel, QRegExp('info'))[0]
                    info_box.setText(info.title())
            elif token == 'year':
                # check if searching for a decade
                pattern = r'^(?:\d{1}|\d{3})0s$'
                if re.fullmatch(pattern, str_text):
                    if len(str_text) == 3:
                        # assume the 20th century if not specified (i.e. 20s would refer to 1920s not 2020s)
                        str_text = '19' + str_text

                    # automatically succeed if century and decade match
                    ratio = 100 if str_text[1:3] == str(film_data_to_search)[1:3] else 0

                    # subtract by the year in the decade to sort ascending
                    ratio -= int(str(film_data_to_search)[-1])
                else:
                    # if a film is within 4 years of the year searched add it to the results
                    try:
                        ratio = 54-(abs(int(film_data_to_search)-int(text)))
                    except ValueError:
                        self.search_bar.setText('')
            else:
                # search strings and lists normally
                ratio = fuzz.token_set_ratio(film_data_to_search, str_text)

            if ratio >= tolerance:
                v['ratio'] = ratio
                v['frame'] = [x for x in self.movies if x.objectName() == k][0]
                _search_results[k] = v

        # sort search results by how much it matched
        _search_results = dict(sorted(_search_results.items(), key=lambda item: (-item[1]['ratio'], item[1]['title'])))

        self.search_results = _search_results

        # only show movies from search results
        for movie in self.movies:
            movie.show()
            # do not show subtitle if searching by title
            if token != 'title':
                movie.findChildren(QLabel, QRegExp('info'))[0].show()
            else:
                movie.findChildren(QLabel, QRegExp('info'))[0].hide()
            if movie.objectName() not in self.search_results:
                movie.hide()

        # layout relevant movies based on their search order
        for i, (k, v) in enumerate(self.search_results.items()):
            frame = v['frame']
            horizontal = i % self.grid_amount
            vertical = i / self.grid_amount
            self.grid_layout.addWidget(frame, vertical, horizontal, alignment=self.grid_alignment)
