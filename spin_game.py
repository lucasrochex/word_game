import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QLineEdit, QPushButton, QMessageBox
)
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt


class WordGuessGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jogue os Dados!")
        self.setGeometry(100, 100, 600, 400)

        self.load_data()
        self.current_puzzle = 0

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
        self.background_movie = QMovie("roda.gif")  # Path to your GIF
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
        self.input_layout.addWidget(self.letter_input)

        self.submit_button = QPushButton("Submit", self.content_widget)
        self.submit_button.clicked.connect(self.check_guess)
        self.input_layout.addWidget(self.submit_button)

        self.content_layout.addLayout(self.input_layout)

        # Add a next button
        self.next_button = QPushButton("Next Puzzle", self.content_widget)
        self.next_button.clicked.connect(self.next_puzzle)
        self.next_button.setEnabled(False)
        self.content_layout.addWidget(self.next_button)

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
            self.word_layout.itemAt(i).widget().deleteLater()

        # Load the current puzzle
        puzzle = self.data[self.current_puzzle]
        self.hint_label.setText(puzzle["hint"])

        # Create labels for each word
        self.word_labels = []
        self.word_states = []
        for word in puzzle["words"]:
            word_layout = QHBoxLayout()
            word_label = []
            word_state = ["_"] * len(word)

            for letter in word:
                label = QLabel("_", self.content_widget)
                label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
                word_layout.addWidget(label)
                word_label.append(label)

            self.word_layout.addLayout(word_layout)
            self.word_labels.append(word_label)
            self.word_states.append(word_state)

    def check_guess(self):
        guess = self.letter_input.text().lower()
        self.letter_input.clear()

        if not guess.isalpha() or len(guess) != 1:
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
            if all("".join(state) == word for state, word in zip(self.word_states, self.data[self.current_puzzle]["words"])):
                QMessageBox.information(self, "Well Done!", "You completed this puzzle!")
                self.next_button.setEnabled(True)

    def next_puzzle(self):
        self.current_puzzle += 1
        if self.current_puzzle >= len(self.data):
            QMessageBox.information(self, "Congratulations!", "You've completed all puzzles!")
            self.close()
        else:
            self.next_button.setEnabled(False)
            self.load_puzzle()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = WordGuessGame()
    game.show()
    sys.exit(app.exec_())
