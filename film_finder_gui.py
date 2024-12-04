from PySide2.QtWidgets import QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QLineEdit, QFrame
from PySide2.QtGui import QIcon, QFont, QPixmap
from PySide2.QtCore import Qt
import film_finder
import urllib

# TODO: Add icon to window


class Window(QWidget):
    def __init__(self):
        super().__init__()

        # init run variables
        self.searching = False
        self.iteration = 0
        self.limit = -1
        self.scale = self.screen().size().height()/1080
        self.win_width = 1200*self.scale
        self.win_height = 800*self.scale
        self.last_screen = self.screen()

        # window settings
        self.setWindowTitle('Movie Tracker')
        self.setGeometry(100, 50, self.win_width, self.win_height*.5)

        # init widget variables
        self.search_bar = None
        self.search_button = None
        self.poster_label = None
        self.poster_scale = 0.23
        self.title_label = None
        self.director_label = None
        self.previous = None
        self.confirm = None
        self.next = None

        # init data variables
        self.film_id = None
        self.film_data = None
        self.film_title = None
        self.film_year = None
        self.film_director = None
        self.poster_image = 'poster.PNG'

        # create layout
        poster = self.display_poster_area()
        search_box = self.add_movie_textbox()
        film_info = self.display_film_info()
        self.nav_buttons = self.add_navigation_buttons()

        vbox = QVBoxLayout()
        vbox.addWidget(poster)
        vbox.addLayout(film_info)
        vbox.addLayout(search_box)
        vbox.addWidget(self.nav_buttons)

        self.setLayout(vbox)
        self._resize()

    # utility methods
    def _resize(self):
        """
        Resizes the window relative to the monitor size.
        Uses a larger size when search mode is active, and a smaller size when it's inactive.

        :return:
            None
        """
        # get current coordinates
        coords = self.geometry().getCoords()
        win_x = coords[0]
        win_y = coords[1]

        # update variables based on screen resolution
        self.last_screen = self.screen()
        self.scale = self.screen().size().height()/1080
        self.win_width = 1200*self.scale
        self.win_height = 800*self.scale

        # create mults for searching
        size_mult = 1 if self.searching else .5
        show_poster = 1 if self.searching else 0

        # set window size
        self.setMinimumWidth(self.win_width)
        self.setMinimumHeight(self.win_height*size_mult)
        self.setGeometry(win_x, win_y, self.win_width, self.win_height*size_mult)

        # update poster size
        pixmap = self.poster_label.pixmap()
        self.poster_label.setPixmap(pixmap.scaled(2000 * self.poster_scale * self.scale * show_poster,
                                                  3000 * self.poster_scale * self.scale * show_poster))

    def _leave_search(self):
        """
        Resets the UI layout when search is completed

        :return:
            None
        """
        # hide buttons used for searching and resize
        self.searching = False
        self.nav_buttons.hide()
        self.poster_label.hide()
        self._resize()

        # reinit variables for the searched film
        self.film_data = None
        self.film_title = None
        self.film_year = None
        self.film_director = None
        self.title_label.setText('')
        self.director_label.setText('Enter a film below to add it to the collection!')

    # widget setup methods
    def display_poster_area(self):
        """
        Creates a QLabel object to contain the poster for the searched film
        :return:
            self.poster_label, the QLabel object for the poster
        """
        self.poster_label = QLabel()

        # create empty pixmap and assign it to the label
        pixmap = QPixmap()
        self.poster_label.setPixmap(pixmap)
        self.poster_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # hide the label until the user searches for a film
        self.poster_label.hide()
        return self.poster_label

    def display_film_info(self):
        """
        Creates a vbox layout containing labels for the film title and director name

        :return:
            The created vbox
        """
        vbox = QVBoxLayout()

        # create a label for the title with a larger font
        self.title_label = QLabel(self.film_title)
        self.title_label.setFont(QFont('Sanserif', 18))
        self.title_label.setAlignment(Qt.AlignHCenter)

        # create a label for the director name with a smaller label, init as a prompt to the user
        self.director_label = QLabel('Enter a film below to add it to the collection!')
        self.director_label.setFont(QFont('Sanserif', 13))
        self.director_label.setAlignment(Qt.AlignHCenter)

        # add labels to the vbox
        vbox.addWidget(self.title_label)
        vbox.addWidget(self.director_label)
        return vbox

    def add_movie_textbox(self):
        """
        Creates the search bar and a search button in an hbox
        Connects the return key and the search button to the search method

        :return:
            The created hbox layout
        """
        hbox = QHBoxLayout()
        # init line edit and search button
        self.search_bar = QLineEdit('')
        self.search_button = QPushButton(text='Search')

        # connect line edit and search button to search method
        self.search_button.clicked.connect(self.reset_and_search)
        self.search_bar.returnPressed.connect(self.reset_and_search)

        # add widgets to hbox
        hbox.addWidget(self.search_bar)
        hbox.addWidget(self.search_button)

        return hbox

    def add_navigation_buttons(self):
        """
        Creates previous, next, and confirm buttons to be used when searching for a film

        :return:
            None
        """
        frame = QFrame()
        hbox = QHBoxLayout()

        # create buttons, disable previous until the found film is not the first in the search
        self.previous = QPushButton(text='Previous')
        self.confirm = QPushButton(text='Confirm')
        self.next = QPushButton(text='Next')
        self.previous.setEnabled(False)

        # connect buttons to the navigate method films, lambda is used to pass the button info to the method
        self.previous.clicked.connect(lambda: self.navigate_films(self.previous))
        self.next.clicked.connect(lambda: self.navigate_films(self.next))
        # connect confirm button to the confirm film method
        self.confirm.clicked.connect(self.confirm_film)

        # add buttons to hbox
        hbox.addWidget(self.previous)
        hbox.addWidget(self.confirm)
        hbox.addWidget(self.next)
        frame.setLayout(hbox)
        frame.hide()
        return frame

    # button function methods
    def search_film(self):
        """
        Calls the search_film_async method to look for the searched film

        :return:
            Bool based on if a film was found or not
        """
        # enable search mode
        self.searching = True
        self.nav_buttons.show()
        self.poster_label.show()
        self._resize()

        # look up film, if no film is found return False
        img, film_data = film_finder.search_film_async(self.search_bar.text(), self.iteration)

        if not img or not film_data:
            self._leave_search()
            return False

        # update image from poster url
        data = urllib.request.urlopen(img).read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        self.poster_label.setPixmap(pixmap)
        self.poster_label.setPixmap(pixmap.scaled(2000 * self.poster_scale * self.scale,
                                                  3000 * self.poster_scale * self.scale))
        self.poster_label.setAlignment(Qt.AlignHCenter | Qt.AlignTop)

        # store film data
        self.film_data = film_data

        # isolate film data for this film (strips the first level dict)
        self.film_id = next(iter(film_data))
        _film_data = film_data[self.film_id]

        # update film variables
        self.film_title = _film_data['title']
        self.film_year = _film_data['year']
        self.film_director = ','.join(_film_data['directors'])

        # update text
        self.title_label.setText(f'{self.film_title}, {self.film_year}')
        self.director_label.setText(self.film_director)

        return True

    def navigate_films(self, button):
        """
        Increments the found film by 1 (positive or negative) in the list of search results

        :param button:
            The button pushed to call this method.
        :return:
            None
        """

        # check if increment should be positive or negative, if going backwards ensure next button is enabled
        inc_value = 1
        if button.text() == 'Previous':
            inc_value = -1
            self.next.setEnabled(True)

        # add inc_value to the iteration, do not go below 0
        self.iteration += inc_value
        self.iteration = max(0, self.iteration)

        # if iteration is greater than 0 enable previous button, otherwise disable
        if self.iteration == 0:
            self.previous.setEnabled(False)
        else:
            self.previous.setEnabled(True)

        # if button pressed does not result in a new film disable next button and set limit to this value
        success = self.search_film()
        if not success:
            self.next.setEnabled(False)
            self.iteration -= 1
            self.limit = self.iteration

        # disable next button if iteration is equal to the limit
        if self.limit == self.iteration:
            self.next.setEnabled(False)

    def reset_and_search(self):
        """
        Used for a fresh search, resets all values before searching

        :return:
            None
        """
        self.iteration = 0
        self.limit = -1
        self.previous.setEnabled(False)
        self.next.setEnabled(True)
        self.search_film()

    def confirm_film(self):
        """
        Logs the found film in the library and resets the search mode to False

        :return:
            None
        """
        film_finder.log_film(self.film_data)

        self._leave_search()
