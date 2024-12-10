import sys
import glob
import json
import random 
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QMessageBox, QInputDialog
)
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QUrl
from PyQt5 import QtMultimedia


def get_random_int(start, end, excluded_numbers):
    # Generate a random integer until it is not in the excluded list
    while True:
        num = random.randint(start, end)
        if num not in excluded_numbers:
            return num

class WordGuessGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jogue os Dados!")
        self.setGeometry(100, 100, 600, 400)

        self.player = QtMultimedia.QMediaPlayer()
        self.gifs_abertura = glob.glob('abertura/*')
        self.gifs_comemoracao = glob.glob('comemoracao/*')
        self.letters = "Letras que já sairam:"

        self.load_data()
        self.total_puzzles = len(self.data)
        self.used_puzzles = []
        self.current_puzzle = get_random_int(0, self.total_puzzles, self.used_puzzles)
        self.used_puzzles.append(self.current_puzzle)

        self.init_ui()
        self.load_puzzle()

    def load_data(self):
        with open("game.json", "r") as file:
            self.data = json.load(file)

    def init_ui(self):
        # Set up layout
        self.layout = QVBoxLayout()

        # Add animated background
        self.background_label = QLabel(self)
        self.background_movie = QMovie(random.choice(self.gifs_abertura))  # Path to your GIF
        self.background_label.setMovie(self.background_movie)
        self.background_movie.start()

        # Set the background label to cover the entire widget
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.setScaledContents(True)

        # Overlay content
        self.content_widget = QWidget(self)
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_widget.setStyleSheet("background: transparent;")  # Transparent background

        # Hint display
        self.hint_label = QLabel("", self.content_widget)
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        self.content_layout.addWidget(self.hint_label)

        # Word display area
        self.word_layout = QVBoxLayout()
        self.content_layout.addLayout(self.word_layout)

        # Input area
        self.input_layout = QHBoxLayout()
        self.letter_input = QLineEdit(self.content_widget)
        self.letter_input.setMaxLength(1)
        self.letter_input.setPlaceholderText("Guess a letter")
        self.letter_input.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: black;
            border: 2px solid black;
            background-color: white;
            padding: 5px;
            """
        )
        self.input_layout.addWidget(self.letter_input)

        self.submit_button = QPushButton("Submit", self.content_widget)
        self.submit_button.clicked.connect(self.check_guess)
        self.submit_button.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: black;
            border: 2px solid black;
            background-color: white;
            padding: 5px 10px;
            """
        )   
        self.input_layout.addWidget(self.submit_button)

        self.content_layout.addLayout(self.input_layout)

         # Add a "Guess" button
        self.guess_button = QPushButton("Chutar", self.content_widget)
        self.guess_button.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: black;
            border: 2px solid black;
            background-color: white;
            padding: 5px 10px;
            """
        )
        self.guess_button.clicked.connect(self.guess_word)
        #self.next_button.setEnabled(False)
        self.guess_button.setEnabled(True)
        self.content_layout.addWidget(self.guess_button)

        # Add a next button
        self.next_button = QPushButton("Proxima palavra", self.content_widget)
        self.next_button.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: black;
            border: 2px solid black;
            background-color: white;
            padding: 5px 10px;
            """
        )
        self.next_button.clicked.connect(self.next_puzzle)
        #self.next_button.setEnabled(False)
        self.next_button.setEnabled(True)
        self.content_layout.addWidget(self.next_button)

         # Letters display
        self.letters_display = QLabel("", self.content_widget)
        self.letters_display.setAlignment(Qt.AlignCenter)
        self.letters_display.setStyleSheet(
            """
            font-size: 18px;
            font-weight: bold;
            color: black;
            border: 2px solid black;
            background-color: white;
            padding: 5px 10px;
            """
        )
        self.content_layout.addWidget(self.letters_display)

        # Finalize layout
        self.layout.addWidget(self.content_widget)
        self.setLayout(self.layout)

    def resizeEvent(self, event):
        # Adjust background size when the window is resized
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        super().resizeEvent(event)

    
    def load_puzzle(self):
    # Clear previous words
        for i in reversed(range(self.word_layout.count())):
           print('Item', i)
           item = self.word_layout.itemAt(i)
           print(item)
           for a in reversed(range(item.count())):
               letra = item.itemAt(a)
               if letra.widget():
                print('Oi')
                letra.widget().deleteLater()
           #if self.word_layout.itemAt(i).widget() is not None:
                #self.word_layout.itemAt(i).widget().deleteLater()
            #self.word_layout.itemAt(i).widget().deleteLater()

        # Load the current puzzle
        puzzle = self.data[self.current_puzzle]
        self.hint_label.setText(puzzle["hint"])
        self.letters = "Letras que já sairam:"
        self.letters_display.setText(self.letters)

        # Create labels for each word
        self.word_labels = []
        self.word_states = []
        for word in puzzle["words"]:
            special_characters = 0
            for letra in word:
                if letra in [' ', '-']:
                    special_characters += 1
            word_layout = QHBoxLayout()
            word_label = []
            word_state = ["_"] * len(word)

            for letter in word:
                if letter not in [' ', '-']:
                    label = QLabel("_", self.content_widget)
                    label.setAlignment(Qt.AlignCenter)
                    label.setFixedSize(40, 40)  # Size of each box
                    label.setStyleSheet(
                        """
                        font-size: 18px;
                        font-weight: bold;
                        color: black;
                        border: 2px solid black;
                        background-color: white;
                        """
                    )
                    word_layout.addWidget(label)
                    word_label.append(label)
                else:
                    label = QLabel("", self.content_widget)
                    label.setAlignment(Qt.AlignCenter)
                    label.setFixedSize(40, 40)  # Size of each box
                    label.setStyleSheet(
                        """
                        font-size: 18px;
                        font-weight: bold;
                        color: black;
                        border: 2px solid black;
                        background-color: yellow;
                        """
                    )
                    word_layout.addWidget(label)
                    word_label.append(label)

            self.word_layout.addLayout(word_layout)
            self.word_labels.append(word_label)
            self.word_states.append(word_state)


    def check_guess(self):
        guess = self.letter_input.text().upper()
        self.letter_input.clear()

        if (not guess.isalpha() or len(guess) != 1) and (guess not in [' ', '-']):
            QMessageBox.warning(self, "Invalid Input", "Please enter a single letter.")
            return

        correct_guess = False
        for i, word in enumerate(self.data[self.current_puzzle]["words"]):
            for j, letter in enumerate(word):
                if letter == guess and self.word_states[i][j] == "_":
                    self.word_states[i][j] = guess
                    self.word_labels[i][j].setText(guess)
                    correct_guess = True

        if correct_guess:
            url = QUrl.fromLocalFile('correct.mp3')
            self.player.setMedia(QtMultimedia.QMediaContent(url))
            self.player.play()
            if all("".join(state) == word for state, word in zip(self.word_states, self.data[self.current_puzzle]["words"])):
                #QMessageBox.information(self, "Well Done!", "You completed this puzzle!")
                self.background_movie = QMovie(random.choice(self.gifs_comemoracao))
                self.background_label.setMovie(self.background_movie)
                self.background_movie.start()
                url = QUrl.fromLocalFile('claps.mp3')
                self.player.setMedia(QtMultimedia.QMediaContent(url))
                self.player.play()
                self.next_button.setEnabled(True)
        else:
            url = QUrl.fromLocalFile('wrong.mp3')
            self.player.setMedia(QtMultimedia.QMediaContent(url))
            self.player.play()
            self.letters += " " + guess
            self.letters_display.setText(self.letters)

    def guess_word(self):
        palavras, done1 = QInputDialog.getText(self, 'Palavras separadas por ||', 'Palavras separadas por ||')
        palavras = palavras.upper()
        print(palavras)
        puzzle = self.data[self.current_puzzle]
        palavras_puzzle = puzzle['words']
        palavras_puzzle_string = ""
        n = len(palavras_puzzle)
        for i, p in enumerate(palavras_puzzle):
            if i != n - 1:
                palavras_puzzle_string+=p+"||"
            else:
                palavras_puzzle_string+=p
        print(palavras_puzzle_string)
        if palavras == palavras_puzzle_string:
            url = QUrl.fromLocalFile('claps.mp3')
            self.player.setMedia(QtMultimedia.QMediaContent(url))
            self.player.play()
            self.background_movie = QMovie(random.choice(self.gifs_comemoracao))
            self.background_label.setMovie(self.background_movie)
            self.background_movie.start()
            self.next_button.setEnabled(True)
        else:
            url = QUrl.fromLocalFile('wrong.mp3')
            self.player.setMedia(QtMultimedia.QMediaContent(url))
            self.player.play()

    def next_puzzle(self):
        self.current_puzzle = get_random_int(0, self.total_puzzles, self.used_puzzles)
        self.used_puzzles.append(self.current_puzzle)
        self.background_movie = QMovie(random.choice(self.gifs_abertura))
        self.background_label.setMovie(self.background_movie)
        self.background_movie.start()
        self.load_puzzle()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = WordGuessGame()
    game.show()
    sys.exit(app.exec_())
